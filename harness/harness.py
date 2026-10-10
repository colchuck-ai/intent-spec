"""Load intent-spec documents into Neo4j, check rules as Cypher, and export back to YAML.

The YAML documents in git stay the source of truth. Neo4j is a working copy you can
rebuild: load a document, look at it or change it in Neo4j Browser, then export it
back into the YAML file (comments and order are kept, so the change shows as a
normal git diff).

The mapping comes from ../model.md, so it follows the model without code changes:
- every item becomes a node labelled :Item and its entity type (e.g. :Container),
  with properties id, doc (the document id) and type (e.g. CONTAINER)
- every link field becomes a relationship named after its verb (in -> :IN), with
  the original verb in r.verb and list position in r.idx
- the model itself is loaded as :EntityType nodes joined by :LINK relationships
- an alias:id reference becomes a :Ref:Imported stub; when the import's source names another
  loaded document (by file stem), the stub -[:RESOLVES_TO]-> that document's item
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from neo4j import GraphDatabase
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "model.md"
EXAMPLES = ROOT / "review" / "examples"
INVALID = EXAMPLES / "invalid"
RULES = Path(__file__).resolve().parent / "rules"

URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "intentspec"))

HEADER = ["intentSpec", "id", "version", "stage"]
# Base fields every item may have that hold a reference (see model.md Conventions, "Items").
BASE_LINKS = {"replacedBy": False}
# Base field mapping a warning rule ID to the rationale for waiving it on the item (model.md DOC-3).
WAIVERS = "ruleWaivers"
# Plural exceptions listed in model.md "Reference serialization".
PLURALS = {
    "PERSON": "people",
    "POLICY": "policies",
    "PROCESS": "processes",
    "EXTERNAL_ENTITY": "externalEntities",
    "TRUST_BOUNDARY": "trustBoundaries",
}


# ---------------------------------------------------------------- model


@dataclass
class Link:
    source: str
    verb: str
    targets: list[str]
    many: bool
    required: bool
    left: str = "}o"  # Mermaid source-side marker: how many sources each target has


@dataclass
class Entity:
    name: str
    attrs: dict[str, str] = field(default_factory=dict)  # name -> type (e.g. string, enum[], map)
    links: dict[str, Link] = field(default_factory=dict)  # verb -> link
    required: dict[str, bool] = field(default_factory=dict)  # attribute name -> required
    values: dict[str, list[str]] = field(default_factory=dict)  # enum attribute name -> allowed values
    area: str = ""
    anchor: str = ""

    @property
    def key(self) -> str:
        if self.name in PLURALS:
            return PLURALS[self.name]
        words = self.name.lower().split("_")
        return words[0] + "".join(w.capitalize() for w in words[1:]) + "s"

    @property
    def label(self) -> str:
        return "".join(w.capitalize() for w in self.name.split("_"))


# ---------------------------------------------------------------- model.md

NON_AREAS = {"Overview", "Conventions", "Reference serialization"}
ANCHOR_RE = re.compile(r"^Anchor:\s*(\w+)")
ANCHOR_WORDS = ["exact", "close", "broad", "narrow", "related", "added", "departure"]
ENUM_TYPE_RE = re.compile(r"^enum(\[\])?\s*\((.*)\)$")
# Cardinality words to Mermaid markers: target side, then source side ("each target has ...").
RIGHT = {"exactly one": "||", "zero or one": "o|", "zero or more": "o{", "one or more": "|{"}
LEFT = {"exactly one": "||", "zero or one": "|o", "zero or more": "}o", "one or more": "}|"}


RULE_ITEM_RE = re.compile(r"^- \*\*([A-Z0-9]+-\d+)\*\*(?: \((error|warning)\))?:\s*(.*)$")
ID_LIST_RE = re.compile(r"^(Retired|Not checked by a query|Generated checks):\s*(.*?)\.?$")


@dataclass
class RuleDef:
    id: str
    severity: str  # error | warning; empty for a derivation
    statement: str
    element: str  # the element it sits under; empty at area or Conventions level
    area: str


@dataclass
class Model:
    entities: dict[str, Entity] = field(default_factory=dict)
    rules: dict[str, RuleDef] = field(default_factory=dict)
    derivations: dict[str, RuleDef] = field(default_factory=dict)
    retired: list[str] = field(default_factory=list)
    unchecked: list[str] = field(default_factory=list)
    generated: list[str] = field(default_factory=list)


def table_rows(lines: list[str], i: int) -> tuple[list[list[str]], int]:
    """The rows of the Markdown table starting at lines[i] (header and separator skipped)."""
    rows = []
    j = i + 2
    while j < len(lines) and lines[j].startswith("|"):
        rows.append([c.strip() for c in re.split(r"(?<!\\)\|", lines[j].strip())[1:-1]])
        j += 1
    return rows, j


def parse_model(path: Path) -> Model:
    m = Model()
    lines = path.read_text().splitlines()
    area, current, listing = "", None, ""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            area, current, listing = line[3:].strip(), None, ""
        elif line in ("**Rules**", "**Derived**", "**Guidance**"):
            listing = line.strip("*")
        elif listing in ("Rules", "Derived") and (rm := RULE_ITEM_RE.match(line)):
            rid, sev, text = rm.groups()
            target = m.rules if listing == "Rules" else m.derivations
            target[rid] = RuleDef(rid, sev or "", text, current.name if current else "", area)
        elif lm := ID_LIST_RE.match(line):
            ids = [x.strip() for x in lm.group(2).split(",") if x.strip()]
            {"Retired": m.retired, "Not checked by a query": m.unchecked, "Generated checks": m.generated}[lm.group(1)].extend(ids)
        elif line.startswith("### ") and area not in NON_AREAS:
            listing = ""
            current = m.entities.setdefault(line[4:].strip(), Entity(line[4:].strip()))
            current.area = area
        elif current is not None and (am := ANCHOR_RE.match(line)):
            current.anchor = am.group(1)
        elif current is not None and line.startswith("| Attribute |"):
            rows, i = table_rows(lines, i)
            for name, typ, req, _meaning in rows:
                if em := ENUM_TYPE_RE.match(typ):
                    current.attrs[name] = "enum" + (em.group(1) or "")
                    current.values[name] = [v.strip() for v in em.group(2).split(",")]
                else:
                    current.attrs[name] = typ
                current.required[name] = req in ("yes", "one or more")
            continue
        elif current is not None and line.startswith("| Link |"):
            rows, i = table_rows(lines, i)
            for verb, targets, card, _meaning in rows:
                right, _, left = card.partition("; each target has ")
                marker = RIGHT[right.strip()]
                link = current.links.setdefault(
                    verb, Link(current.name, verb, [], "{" in marker, marker.startswith("|"), LEFT[left.strip() or "zero or more"]))
                link.targets += [t.strip() for t in targets.split(" or ")]
            continue
        i += 1
    return m


# ---------------------------------------------------------------- render

OVERVIEW_RE = re.compile(r"(<!-- overview:[^\n]*-->\n)(.*?)(<!-- /overview -->)", re.S)


def overview(m: Model) -> str:
    """The overview ERD: every link, plus any element no link touches."""
    lines = []
    for e in m.entities.values():
        for l in e.links.values():
            right = ("|" if l.required else "o") + ("{" if l.many else "|")
            lines += [f"  {e.name} {l.left}--{right} {t}: {l.verb}" for t in l.targets]
    linked = {e.name for e in m.entities.values() if e.links} | \
             {t for e in m.entities.values() for l in e.links.values() for t in l.targets}
    lines += [f"  {n}" for n in m.entities if n not in linked]
    return "```mermaid\nerDiagram\n" + "\n".join(lines) + "\n```\n"


def render(path: Path) -> bool:
    """Rewrite the overview block in place; True if it changed."""
    text = path.read_text()
    new = OVERVIEW_RE.sub(lambda mt: mt.group(1) + overview(parse_model(path)) + mt.group(3), text, count=1)
    if new != text:
        path.write_text(new)
    return new != text


# ---------------------------------------------------------------- lint


def lint(path: Path, rules_dir: Path, invalid_dir: Path) -> list[str]:
    """Shape problems in model.md, one line each: '<CHECK-ID> <location>: <message>'."""
    lines = path.read_text().splitlines()
    out: list[str] = []
    sections = [l[3:].strip() for l in lines if l.startswith("## ")]
    for name in ("Overview", "Conventions"):
        if name not in sections:
            out.append(f"MD-SECTIONS model: missing section {name}")
    if sections[:2] != ["Overview", "Conventions"] and {"Overview", "Conventions"} <= set(sections):
        out.append("MD-SECTIONS model: Overview must come first, then Conventions")
    if not [s for s in sections if s not in NON_AREAS]:
        out.append("MD-SECTIONS model: no area sections")
    sections_ = element_sections(lines)
    seen: set[str] = set()
    for name, _ in sections_:
        if not re.fullmatch(r"[A-Z_]+", name):
            out.append(f"MD-NAME {name}: element names match ^[A-Z_]+$")
        if name in seen:
            out.append(f"MD-NAME {name}: element appears more than once")
        seen.add(name)
    for name, body in sections_:
        out += lint_tables(name, body)
        for i, l in enumerate(body):
            if l.strip() == LINK_HEADER:
                for row in table_rows(body, i)[0]:
                    if len(row) != 4:
                        continue
                    verb, targets = row[0], row[1]
                    if not re.fullmatch(r"[a-z][A-Za-z]*", verb):
                        out.append(f"MD-VERB {name}.{verb}: a link verb is one word")
                    for t in targets.split(" or "):
                        if t.strip() not in seen:
                            out.append(f"MD-TARGET {name}.{verb}: no element {t.strip()}")
    out += lint_rules(lines)
    out += lint_queries(lines, rules_dir, invalid_dir)
    block = OVERVIEW_RE.search(path.read_text())
    if not block:
        out.append("MD-OVERVIEW Overview: no generated block between <!-- overview: ... --> and <!-- /overview -->")
    elif not any(o.startswith("MD-TABLE") for o in out) and block.group(2) != overview(parse_model(path)):
        out.append("MD-OVERVIEW Overview: differs from the link tables; run harness.py render")
    for name, body in sections_:
        prose = [l for l in body if l.strip() and not l.startswith(("|", "- ", "**", "Anchor:", "Attributes: none", "Links: none"))]
        if not prose:
            out.append(f"MD-ELEMENT {name}: no definition")
        anchors = [m for l in body if (m := ANCHOR_RE.match(l))]
        if not anchors:
            out.append(f"MD-ELEMENT {name}: no Anchor line")
        for a in anchors:
            word = a.group(1)
            if word not in ANCHOR_WORDS:
                out.append(f"MD-ANCHOR {name}: anchor is {', '.join(ANCHOR_WORDS[:-1])} or {ANCHOR_WORDS[-1]}, not {word}")
            elif word == "departure" and not re.search(r"\(decision: [\w-]+\)", a.string):
                out.append(f"MD-ANCHOR {name}: a departure names its decision as (decision: <bead id>)")
        for kind in ("Attributes", "Links"):
            header = "| Attribute |" if kind == "Attributes" else "| Link |"
            if not any(l.startswith(header) or l.startswith(f"{kind}: none") for l in body):
                out.append(f"MD-ELEMENT {name}: no {kind} table (or '{kind}: none.')")
    return out


ATTR_HEADER = "| Attribute | Type | Required | Meaning |"
LINK_HEADER = "| Link | Target | Cardinality | Meaning |"
TYPE_RE = re.compile(r"^(string|int|date|boolean|map|enum\s*\([^)]*\))(\[\])?$|^enum\[\]\s*\([^)]*\)$")
CARD_WORDS = "exactly one|zero or one|zero or more|one or more"
CARD_RE = re.compile(rf"^({CARD_WORDS})(; each target has ({CARD_WORDS}))?$")


def lint_tables(name: str, body: list[str]) -> list[str]:
    out = []
    for i, l in enumerate(body):
        if not (l.startswith("| Attribute") or l.startswith("| Link")) or (i and body[i - 1].startswith("|")):
            continue
        kind, header = ("Attributes", ATTR_HEADER) if l.startswith("| Attribute") else ("Links", LINK_HEADER)
        if l.strip() != header:
            out.append(f"MD-TABLE {name}: {kind} header must be {header}")
            continue
        rows, _ = table_rows(body, i)
        for row in rows:
            if len(row) != 4:
                out.append(f"MD-TABLE {name}: {kind} row needs 4 cells: {'|'.join(row)}")
                continue
            if kind == "Attributes":
                attr, typ, req, _ = row
                if not TYPE_RE.match(typ):
                    out.append(f"MD-TABLE {name}.{attr}: unknown type {typ}")
                if req not in ("yes", "no", "one or more") and not req.startswith(("when ", "unless ")):
                    out.append(f"MD-TABLE {name}.{attr}: Required is yes, no, one or more, or starts with 'when ' or 'unless '")
            else:
                verb, _, card, _ = row
                if not CARD_RE.match(card):
                    out.append(f"MD-TABLE {name}.{verb}: Cardinality is exactly one, zero or one, zero or more or one or more, "
                               "optionally '; each target has <one of those>'")
    return out


def rule_items(lines: list[str]) -> list[tuple[str, str, str]]:
    """(location, list kind, line) for every bullet under a **Rules** or **Derived** heading."""
    out, loc, listing = [], "", ""
    for l in lines:
        if l.startswith("## ") or l.startswith("### "):
            loc, listing = l.lstrip("#").strip(), ""
        elif l in ("**Rules**", "**Derived**", "**Guidance**"):
            listing = l.strip("*")
        elif l.startswith("- ") and listing in ("Rules", "Derived"):
            out.append((loc, listing, l))
    return out


def lint_rules(lines: list[str]) -> list[str]:
    out, seen, statements = [], set(), {}
    retired = [x.strip() for l in lines if (m := ID_LIST_RE.match(l)) and m.group(1) == "Retired"
               for x in m.group(2).split(",")]
    for loc, listing, l in rule_items(lines):
        m = RULE_ITEM_RE.match(l)
        if not m or (listing == "Rules") != bool(m.group(2)):
            out.append(f"MD-RULE {loc}: malformed rule item: {l}")
            continue
        rid = m.group(1)
        if rid in seen:
            out.append(f"MD-RULE {rid}: ID used more than once")
        if rid in retired:
            out.append(f"MD-RULE {rid}: retired ID reused")
        seen.add(rid)
        statements[rid] = m.group(3)
    for rid, text in statements.items():
        for cited in re.findall(r"\[([A-Z0-9]+-\d+)\]", text):
            if cited not in seen:
                out.append(f"MD-CITE {rid}: cites unknown ID {cited}")
    return out


def lint_queries(lines: list[str], rules_dir: Path, invalid_dir: Path) -> list[str]:
    lists = {m.group(1): [x.strip() for x in m.group(2).split(",") if x.strip()]
             for l in lines if (m := ID_LIST_RE.match(l))}
    unchecked, generated = set(lists.get("Not checked by a query", [])), set(lists.get("Generated checks", []))
    rules = [m.group(1) for _, kind, l in rule_items(lines) if kind == "Rules" and (m := RULE_ITEM_RE.match(l))]
    queries = {dict(re.findall(r"^//\s*(\w+):\s*(.+)$", f.read_text(), re.M)).get("id", f.stem)
               for f in rules_dir.glob("*.cypher")}
    broken = {m.group(1) for f in invalid_dir.glob("*.yaml")
              if (m := re.match(r"#\s*breaks:\s*(\S+)", f.read_text()))}
    out = []
    for rid in rules:
        if rid in unchecked:
            if rid in queries:
                out.append(f"MD-QUERY {rid}: listed as not checked by a query, but has a query file")
            continue
        if rid not in queries:
            out.append(f"MD-QUERY {rid}: no query file in the rules directory")
        if rid not in broken:
            out.append(f"MD-QUERY {rid}: no invalid example names it")
    for q in sorted(queries - set(rules) - generated):
        out.append(f"MD-QUERY {q}: query file has no rule in the model")
    for g in sorted(generated - broken):
        out.append(f"MD-QUERY {g}: no invalid example names it")
    return out


def element_sections(lines: list[str]) -> list[tuple[str, list[str]]]:
    """(name, body lines) for every ### element under an area section."""
    out, area, name, body = [], "", None, []
    for l in lines + ["## end"]:
        if l.startswith("## ") or l.startswith("### "):
            if name is not None:
                out.append((name, body))
            name, body = None, []
            if l.startswith("## "):
                area = l[3:].strip()
            elif area not in NON_AREAS:
                name = l[4:].strip()
        elif name is not None:
            body.append(l)
    return out


def rel_type(verb: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", verb).upper()


# ---------------------------------------------------------------- YAML


def yaml_rt() -> YAML:
    y = YAML()  # round-trip, YAML 1.2: unquoted dates stay strings
    y.preserve_quotes = True
    y.width = 4096
    y.indent(mapping=2, sequence=4, offset=2)
    return y


def doc_path(name: str) -> Path:
    p = Path(name)
    if p.suffix in (".yaml", ".yml") and p.exists():
        return p.resolve()
    return EXAMPLES / f"{name}.yaml"


def all_docs() -> list[Path]:
    return sorted(EXAMPLES.glob("*.yaml"))


def plain(v):
    """Convert ruamel values to plain Python values."""
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [plain(x) for x in v]
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, int):
        return int(v)
    if isinstance(v, float):
        return float(v)
    return str(v)


# ---------------------------------------------------------------- load


def to_property(v):
    """Neo4j properties hold scalars or lists of scalars; anything else is stored as JSON."""
    if isinstance(v, dict) or (isinstance(v, list) and any(isinstance(x, (dict, list)) for x in v)):
        return json.dumps(v), True
    return v, False


def attr_rows(e: Entity) -> list[dict]:
    """Attribute metadata from the model: type, required, and enum values."""
    return [{"name": name, "type": typ, "list": typ.endswith("[]"), "required": e.required.get(name, False),
             "values": e.values.get(name)} for name, typ in e.attrs.items()]


def load_meta(session, entities: dict[str, Entity]) -> None:
    """Load the model as :EntityType nodes. MERGE keeps it readable while another process loads."""
    session.run(
        "UNWIND $rows AS r MERGE (e:EntityType {name: r.name}) SET e.key = r.key, e.label = r.label, e.attrs = r.attrs",
        rows=[{"name": e.name, "key": e.key, "label": e.label, "attrs": list(e.attrs)} for e in entities.values()],
    )
    session.run("MATCH (e:EntityType) WHERE NOT e.name IN $names DETACH DELETE e", names=list(entities))
    links = [
        {"src": l.source, "tgt": t, "verb": l.verb, "many": l.many, "required": l.required}
        for e in entities.values() for l in e.links.values() for t in l.targets
    ]
    session.run(
        "UNWIND $rows AS r MATCH (a:EntityType {name: r.src}), (b:EntityType {name: r.tgt}) "
        "MERGE (a)-[l:LINK {verb: r.verb}]->(b) SET l.many = r.many, l.required = r.required",
        rows=links,
    )
    session.run(
        "MATCH (a:EntityType)-[l:LINK]->(b:EntityType) "
        "WHERE NOT {src: a.name, tgt: b.name, verb: l.verb} IN $keys DELETE l",
        keys=[{"src": r["src"], "tgt": r["tgt"], "verb": r["verb"]} for r in links],
    )
    attrs = [dict(r, entity=e.name) for e in entities.values() for r in attr_rows(e)]
    session.run(
        "UNWIND $rows AS r MATCH (e:EntityType {name: r.entity}) "
        "MERGE (e)-[:HAS_ATTR]->(a:Attr {entity: r.entity, name: r.name}) "
        "SET a.type = r.type, a.list = r.list, a.required = r.required, a.values = r.values",
        rows=attrs,
    )
    session.run(
        "MATCH (a:Attr) WHERE NOT {entity: a.entity, name: a.name} IN $keys DETACH DELETE a",
        keys=[{"entity": r["entity"], "name": r["name"]} for r in attrs],
    )
    rules = {k: r.severity for k, r in parse_model(MODEL).rules.items()}
    session.run(
        "UNWIND $rows AS r MERGE (x:Rule {id: r.id}) SET x.severity = r.severity",
        rows=[{"id": k, "severity": v} for k, v in rules.items()],
    )
    session.run("MATCH (x:Rule) WHERE NOT x.id IN $ids DETACH DELETE x", ids=list(rules))


def load_doc(session, path: Path, entities: dict[str, Entity]) -> str:
    data = plain(yaml_rt().load(path))
    # Key by file name: two files may hold versions of the same document id (plausible-mvp, plausible-growth).
    doc = path.stem
    by_key = {e.key: e for e in entities.values() if e.name not in ("DOCUMENT", "IMPORT")}
    session.run("MATCH (n {doc: $doc}) DETACH DELETE n", doc=doc)

    header = {k: data[k] for k in HEADER if k in data}
    extra_top = [k for k in data if k not in HEADER and k != "imports" and k not in by_key]
    session.run(
        "CREATE (d:Document {doc: $doc}) SET d += $props, d.file = $file, d.keyOrder = $order",
        doc=doc, props=header, file=str(path), order=list(data),
    )
    if extra_top:
        print(f"  warning: {doc}: top-level keys not in the model kept as-is: {extra_top}", file=sys.stderr)
        session.run("MATCH (d:Document {doc: $doc}) SET d.extra = $extra", doc=doc,
                    extra=json.dumps({k: data[k] for k in extra_top}))
    for alias, imp in (data.get("imports") or {}).items():
        session.run(
            "MATCH (d:Document {doc: $doc}) CREATE (d)-[:HAS]->(:Import {doc: $doc, alias: $alias}) ",
            doc=doc, alias=alias,
        )
        session.run("MATCH (i:Import {doc: $doc, alias: $alias}) SET i += $props", doc=doc, alias=alias,
                    props=json.loads(json.dumps(imp)))

    nodes, rels = [], []
    for key, items in data.items():
        ent = by_key.get(key)
        if ent is None or not isinstance(items, dict):
            continue
        for item_id, fields in items.items():
            fields = fields or {}
            props, json_props, empty, order = {}, [], [], list(fields)
            for f, v in fields.items():
                link = ent.links.get(f)
                if link is not None or f in BASE_LINKS:
                    targets = v if isinstance(v, list) else [v]
                    if targets == []:
                        empty.append(f)  # an explicit empty list has no relationship to carry it
                    for i, t in enumerate(targets):
                        rels.append({"src": item_id, "verb": f, "type": rel_type(f), "tgt": str(t),
                                     "idx": i if isinstance(v, list) else None})
                    continue
                pv, is_json = to_property(v)
                props[f] = pv
                if f == WAIVERS and isinstance(v, dict):
                    props["_waived"] = list(v)  # waived rule IDs as a list, for DOC-3
                if is_json:
                    json_props.append(f)
            nodes.append({"id": item_id, "label": ent.label, "type": ent.name, "props": props,
                          "json": json_props, "empty": empty, "order": order})

    for label in {n["label"] for n in nodes}:
        session.run(
            f"UNWIND $rows AS r CREATE (n:Item:`{label}` {{id: r.id, doc: $doc, type: r.type}}) "
            "SET n += r.props, n._json = r.json, n._empty = r.empty, n._order = r.order",
            rows=[n for n in nodes if n["label"] == label], doc=doc,
        )
    by_type: dict[str, list] = {}
    for r in rels:
        by_type.setdefault(r["type"], []).append(r)
    for rtype, rows in by_type.items():
        # Local targets resolve to items in the same document. Other targets become :Ref
        # stubs: :Imported for alias:id, :Unresolved otherwise (for the rules to report).
        session.run(
            f"UNWIND $rows AS r "
            f"MATCH (s:Item {{doc: $doc, id: r.src}}), (t:Item {{doc: $doc, id: r.tgt}}) "
            f"CREATE (s)-[rel:`{rtype}` {{verb: r.verb}}]->(t) SET rel.idx = r.idx",
            rows=rows, doc=doc,
        )
        session.run(
            f"UNWIND $rows AS r "
            f"MATCH (s:Item {{doc: $doc, id: r.src}}) "
            f"WHERE NOT EXISTS {{ MATCH (:Item {{doc: $doc, id: r.tgt}}) }} "
            f"MERGE (x:Ref {{doc: $doc, ref: r.tgt}}) "
            f"CREATE (s)-[rel:`{rtype}` {{verb: r.verb}}]->(x) SET rel.idx = r.idx",
            rows=rows, doc=doc,
        )
    session.run("MATCH (x:Ref {doc: $doc}) WHERE x.ref CONTAINS ':' SET x:Imported", doc=doc)
    session.run("MATCH (x:Ref {doc: $doc}) WHERE NOT x.ref CONTAINS ':' SET x:Unresolved", doc=doc)
    return doc


def source_stem(source: str) -> str:
    """The file stem an import's source names, e.g. ../shiftly-governance.yaml -> shiftly-governance."""
    name = str(source).rstrip("/").rsplit("/", 1)[-1]
    for ext in (".yaml", ".yml", ".json"):
        if name.endswith(ext):
            return name[: -len(ext)]
    return name


def link_imports(session) -> None:
    """Follow imports between co-loaded documents, with no lockfile.

    An import whose source names a loaded document (by file stem) gets (:Import)-[:LOADED_AS]->(:Document),
    and each alias:id stub of that import gets -[:RESOLVES_TO]-> the item with that id in that document.
    A stub left without RESOLVES_TO although its import is LOADED_AS names nothing there (REF-1).
    Neither relationship has a verb, so export ignores both. Rebuilt from scratch after every load.
    """
    session.run("MATCH ()-[r:RESOLVES_TO|LOADED_AS]->() DELETE r")
    rows = [
        {"doc": r["doc"], "alias": r["alias"], "target": source_stem(r["source"])}
        for r in session.run("MATCH (i:Import) WHERE i.source IS NOT NULL RETURN i.doc AS doc, i.alias AS alias, i.source AS source")
    ]
    session.run(
        "UNWIND $rows AS r MATCH (i:Import {doc: r.doc, alias: r.alias}), (d:Document {doc: r.target}) "
        "WHERE r.target <> r.doc MERGE (i)-[:LOADED_AS]->(d)",
        rows=rows,
    )
    session.run(
        "MATCH (x:Ref:Imported) "
        "WITH x, split(x.ref, ':')[0] AS alias "
        "MATCH (:Document {doc: x.doc})-[:HAS]->(:Import {alias: alias})-[:LOADED_AS]->(d:Document) "
        "MATCH (t:Item {doc: d.doc, id: substring(x.ref, size(alias) + 1)}) "
        "MERGE (x)-[:RESOLVES_TO]->(t)"
    )


def import_paths(path: Path) -> list[Path]:
    """Files a document imports, found beside it by source, or among the examples by file stem."""
    data = plain(yaml_rt().load(path)) or {}
    found = []
    for imp in (data.get("imports") or {}).values():
        source = str((imp or {}).get("source", ""))
        stem = source_stem(source)
        for cand in (path.parent / source, path.parent / f"{stem}.yaml", EXAMPLES / f"{stem}.yaml"):
            if source and cand.is_file():
                found.append(cand.resolve())
                break
    return found


def load_with_imports(session, path: Path, entities: dict[str, Entity], seen: set[Path] | None = None) -> list[str]:
    """Load a document and, first, everything it imports (transitively). Returns the loaded doc names."""
    seen = set() if seen is None else seen
    path = path.resolve()
    if path in seen:
        return []
    seen.add(path)
    docs = []
    for dep in import_paths(path):
        docs += load_with_imports(session, dep, entities, seen)
    docs.append(load_doc(session, path, entities))
    return docs


# ---------------------------------------------------------------- export


def read_graph(session, doc: str) -> dict:
    d = session.run("MATCH (d:Document {doc: $doc}) RETURN d", doc=doc).single()
    if d is None:
        raise SystemExit(f"{doc} is not loaded")
    header = dict(d["d"])
    imports = {
        r["i"]["alias"]: {k: v for k, v in dict(r["i"]).items() if k not in ("doc", "alias")}
        for r in session.run("MATCH (:Document {doc: $doc})-[:HAS]->(i:Import) RETURN i", doc=doc)
    }
    items: dict[str, dict] = {}
    for r in session.run(
        """
        MATCH (n:Item {doc: $doc})
        OPTIONAL MATCH (n)-[rel]->(t) WHERE rel.verb IS NOT NULL
        WITH n, rel, t ORDER BY rel.verb, rel.idx
        RETURN n, collect(CASE WHEN rel IS NULL THEN NULL
                          ELSE {verb: rel.verb, idx: rel.idx, tgt: coalesce(t.id, t.ref)} END) AS links
        """,
        doc=doc,
    ):
        n = dict(r["n"])
        fields = {}
        for k, v in n.items():
            if k in ("id", "doc", "type", "_json", "_empty", "_order", "_waived"):
                continue
            fields[k] = json.loads(v) if k in (n.get("_json") or []) else v
        for l in r["links"]:
            if l["idx"] is None and l["verb"] not in fields:
                fields[l["verb"]] = l["tgt"]
            else:
                cur = fields.get(l["verb"])
                if not isinstance(cur, list):
                    cur = [] if cur is None else [cur]
                cur.append(l["tgt"])
                fields[l["verb"]] = cur
        for f in n.get("_empty") or []:
            fields.setdefault(f, [])
        order = n.get("_order") or []
        fields = dict(sorted(fields.items(), key=lambda kv: order.index(kv[0]) if kv[0] in order else len(order)))
        items[n["id"]] = {"type": n["type"], "fields": fields}
    return {"header": header, "imports": imports, "items": items}


def sync_value(parent, key, new) -> None:
    """Set parent[key] = new, keeping ruamel styling when the value is unchanged."""
    if key in parent and plain(parent[key]) == new:
        return
    if isinstance(new, list) and key in parent and isinstance(parent[key], CommentedSeq):
        seq = CommentedSeq(new)
        if parent[key].fa.flow_style():
            seq.fa.set_flow_style()
        parent[key] = seq
    elif isinstance(new, list) and all(isinstance(x, str) for x in new):
        seq = CommentedSeq(new)
        seq.fa.set_flow_style()
        parent[key] = seq
    else:
        parent[key] = new


def move_trailing_comment(section, old_id: str, new_id: str) -> None:
    """Move the blank line or comment that ended a section from its old last item to the new one."""
    def last_slot(mapping, key):
        item = mapping[key]
        if isinstance(item, CommentedMap) and len(item) and not item.fa.flow_style():
            return item, list(item)[-1]
        return mapping, key

    src, src_key = last_slot(section, old_id)
    token = src.ca.items.pop(src_key, None)
    if token is not None:
        dst, dst_key = last_slot(section, new_id)
        dst.ca.items[dst_key] = token


def export_doc(session, doc: str, entities: dict[str, Entity]) -> Path:
    g = read_graph(session, doc)
    path = Path(g["header"]["file"])
    y = yaml_rt()
    data = y.load(path)

    for k in HEADER:
        if k in g["header"]:
            sync_value(data, k, g["header"][k])
    if g["imports"] or "imports" in data:
        sync_value(data, "imports", g["imports"])

    by_type = {e.name: e for e in entities.values()}
    wanted: dict[str, dict] = {}
    for item_id, item in g["items"].items():
        wanted.setdefault(by_type[item["type"]].key, {})[item_id] = item["fields"]

    # The header and imports are not items (DOCUMENT and IMPORT pluralise to "documents" and "imports").
    entity_keys = {e.key for e in entities.values() if e.name not in ("DOCUMENT", "IMPORT")}
    for key in list(data):
        if key not in entity_keys or not isinstance(data[key], dict):
            continue
        section = data[key]
        for item_id in list(section):
            if item_id not in wanted.get(key, {}):
                del section[item_id]
    for key, items in wanted.items():
        if key not in data:
            data[key] = CommentedMap()
        section = data[key]
        existing = list(section)
        for item_id, fields in items.items():
            if item_id not in section or (section[item_id] is None and fields):
                section[item_id] = CommentedMap()
            item = section[item_id]
            if item is None:
                continue
            for f in list(item):
                if f not in fields:
                    del item[f]
            for f, v in fields.items():
                sync_value(item, f, v)
        added = [i for i in section if i not in existing]
        if added and existing:
            move_trailing_comment(section, existing[-1], added[-1])

    with path.open("w") as fh:
        y.dump(data, fh)
    return path


# ---------------------------------------------------------------- rules


@dataclass
class Rule:
    id: str
    severity: str
    hint: str
    query: str
    file: Path


def load_rules() -> list[Rule]:
    rules = []
    for f in sorted(RULES.glob("*.cypher")):
        text = f.read_text()
        meta = dict(re.findall(r"^//\s*(\w+):\s*(.+)$", text, re.M))
        rules.append(Rule(meta.get("id", f.stem), meta.get("severity", "error"), meta.get("hint", ""), text, f))
    return rules


def load_waivers(session, doc: str) -> dict[str, dict[str, str]]:
    """Pointer -> {rule ID: rationale} for every item in the document with ruleWaivers."""
    rows = session.run(
        f"MATCH (n:Item {{doc: $doc}}) WHERE n.{WAIVERS} IS NOT NULL "
        f"MATCH (e:EntityType {{name: n.type}}) RETURN '/' + e.key + '/' + n.id AS pointer, n.{WAIVERS} AS w",
        doc=doc,
    )
    out = {}
    for r in rows:
        try:
            w = json.loads(r["w"])
        except (TypeError, ValueError):
            continue
        if isinstance(w, dict):
            out[r["pointer"]] = {str(k): str(v) for k, v in w.items()}
    return out


def findings(session, doc: str, rules: list[Rule]):
    """Yield (rule, pointer, detail, rationale) per problem; rationale is set when a warning is waived.

    A rule whose query fails yields (rule, None, error message, None).
    """
    waivers = load_waivers(session, doc)
    for rule in rules:
        try:
            rows = session.run(rule.query, doc=doc).data()
        except Exception as exc:  # a broken rule file must not stop the others
            yield rule, None, str(exc).splitlines()[0], None
            continue
        for row in rows:
            # Only a warning can be waived; a waiver of an error rule is itself reported by DOC-3.
            rationale = waivers.get(row["pointer"], {}).get(rule.id) if rule.severity == "warning" else None
            yield rule, row["pointer"], row.get("detail", ""), rationale


def check(session, docs: list[str], only: set[str] | None = None) -> int:
    failures = 0
    rules = [r for r in load_rules() if not only or r.id in only]
    for doc in docs:
        for rule, pointer, detail, rationale in findings(session, doc, rules):
            if pointer is None:
                failures += 1
                print(f"{doc}: rule-error {rule.id} {rule.file.name}: {detail}")
            elif rationale is not None:
                print(f"{doc}: waived {rule.id} {pointer} {detail}".rstrip())
                print(f"    rationale: {rationale}")
            else:
                failures += rule.severity == "error"
                print(f"{doc}: {rule.severity} {rule.id} {pointer} {detail}".rstrip())
                if rule.hint:
                    print(f"    hint: {rule.hint}")
    return failures


EXPECT_RE = re.compile(r"^#\s*(breaks|also):\s*(\S+)\s+(\S+)\s*$")


def test(session, entities: dict[str, Entity], paths: list[Path]) -> int:
    """Run each invalid example as a rule regression test.

    The first line of the file is `# breaks: <RULE-ID> <pointer>`; further `# also: <RULE-ID> <pointer>` lines
    list other expected findings. The test passes when the unwaived findings (errors and warnings) on the
    document are exactly those, and no rule fails to run.
    """
    rules = load_rules()
    rule_ids = {r.id for r in rules}
    failed = 0
    for path in paths:
        lines = path.read_text().splitlines()
        first = EXPECT_RE.match(lines[0]) if lines else None
        expected = {(m.group(2), m.group(3)) for line in lines if (m := EXPECT_RE.match(line))}
        problems = []
        if first is None or first.group(1) != "breaks":
            problems.append("first line is not '# breaks: <RULE-ID> <pointer>'")
        problems += [f"unknown rule {rid}" for rid, _ in sorted(expected) if rid not in rule_ids]
        doc = path.stem
        try:
            load_with_imports(session, path, entities)
            link_imports(session)
            actual = set()
            for rule, pointer, detail, rationale in findings(session, doc, rules):
                if pointer is None:
                    problems.append(f"rule-error {rule.id}: {detail}")
                elif rationale is None:
                    actual.add((rule.id, pointer))
        finally:
            session.run("MATCH (n {doc: $doc}) DETACH DELETE n", doc=doc)
        problems += [f"missing {r} {p}" for r, p in sorted(expected - actual)]
        problems += [f"unexpected {r} {p}" for r, p in sorted(actual - expected)]
        if problems:
            failed += 1
            print(f"FAIL {show(path)}: " + "; ".join(problems))
        else:
            print(f"ok   {show(path)}: {first.group(2)} {first.group(3)}")
    print(f"{len(paths) - failed} passed, {failed} failed, {len(paths)} invalid examples")
    return failed


# ---------------------------------------------------------------- CLI


def show(path: Path) -> str:
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)



def main() -> None:
    p = argparse.ArgumentParser(prog="harness", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, helptext in [
        ("load", "load documents (default: every example) into Neo4j, replacing what is there"),
        ("export", "write loaded documents back to their YAML files"),
        ("check", "run the Cypher rules in harness/rules against loaded documents"),
        ("test", "run each invalid example (default: review/examples/invalid) and expect exactly the rule it names"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("docs", nargs="*", help="example names (e.g. openemr) or YAML paths")
        if name == "check":
            sp.add_argument("--rules", help="comma-separated rule ids to run (default: all)")
    sub.add_parser("meta", help="load only the model meta-graph")
    lp = sub.add_parser("lint", help="check model.md keeps its shape")
    lp.add_argument("model", nargs="?", default=str(MODEL))
    lp.add_argument("--rules", default=str(RULES), help="directory of rule queries")
    lp.add_argument("--invalid", default=str(INVALID), help="directory of invalid examples")
    rp = sub.add_parser("render", help="rewrite model.md's overview diagram from its link tables")
    rp.add_argument("model", nargs="?", default=str(MODEL))
    args = p.parse_args()

    if args.cmd == "render":
        print("rendered overview" if render(Path(args.model)) else "overview unchanged")
        return
    if args.cmd == "lint":
        problems = lint(Path(args.model), Path(args.rules), Path(args.invalid))
        for line in problems:
            print(line)
        sys.exit(1 if problems else 0)

    entities = parse_model(MODEL).entities
    with GraphDatabase.driver(URI, auth=AUTH, notifications_min_severity="OFF") as driver, driver.session() as s:
        if args.cmd == "meta":
            load_meta(s, entities)
            print(f"loaded {len(entities)} entity types")
            return
        if args.cmd == "load":
            load_meta(s, entities)
            paths = [doc_path(d) for d in args.docs] or all_docs()
            for path in paths:
                print(f"loaded {load_doc(s, path, entities)} from {show(path)}")
            link_imports(s)
            return
        if args.cmd == "test":
            load_meta(s, entities)
            paths = [Path(d).resolve() if Path(d).suffix else INVALID / f"{d}.yaml" for d in args.docs] \
                or sorted(INVALID.glob("*.yaml"))
            sys.exit(1 if test(s, entities, paths) else 0)
        docs = [Path(d).stem for d in args.docs] or [
            r["doc"] for r in s.run("MATCH (d:Document) RETURN d.doc AS doc ORDER BY doc")]
        if args.cmd == "export":
            for doc in docs:
                print(f"exported {doc} to {show(export_doc(s, doc, entities))}")
        elif args.cmd == "check":
            only = set(args.rules.split(",")) if args.rules else None
            sys.exit(1 if check(s, docs, only) else 0)


if __name__ == "__main__":
    main()
