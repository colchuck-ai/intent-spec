"""Load intent-spec documents into Neo4j, check rules as Cypher, and export back to YAML.

The YAML documents in git stay the source of truth. Neo4j is a working copy you can
rebuild: load a document, look at it or change it in Neo4j Browser, then export it
back into the YAML file (comments and order are kept, so the change shows as a
normal git diff).

The mapping comes from ../erd.md, so it follows the model without code changes:
- every item becomes a node labelled :Item and its entity type (e.g. :Container),
  with properties id, doc (the document id) and type (e.g. CONTAINER)
- every link field becomes a relationship named after its verb (in -> :IN), with
  the original verb in r.verb and list position in r.idx
- the ERD itself is loaded as :EntityType nodes joined by :LINK relationships
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
ERD = ROOT / "erd.md"
EXAMPLES = ROOT / "review" / "examples"
RULES = Path(__file__).resolve().parent / "rules"

URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.environ.get("NEO4J_USER", "neo4j"), os.environ.get("NEO4J_PASSWORD", "intentspec"))

HEADER = ["intentSpec", "id", "version", "stage"]
# Base fields every item may have that hold a reference (see erd.md "References").
BASE_LINKS = {"replacedBy": False}
# Plural exceptions listed in erd.md "Serialization".
PLURALS = {
    "PERSON": "people",
    "POLICY": "policies",
    "PROCESS": "processes",
    "EXTERNAL_ENTITY": "externalEntities",
    "TRUST_BOUNDARY": "trustBoundaries",
}


# ---------------------------------------------------------------- ERD model


@dataclass
class Link:
    source: str
    verb: str
    targets: list[str]
    many: bool
    required: bool


@dataclass
class Entity:
    name: str
    attrs: dict[str, str] = field(default_factory=dict)  # name -> type (e.g. string, enum[], map)
    links: dict[str, Link] = field(default_factory=dict)  # verb -> link

    @property
    def key(self) -> str:
        if self.name in PLURALS:
            return PLURALS[self.name]
        words = self.name.lower().split("_")
        return words[0] + "".join(w.capitalize() for w in words[1:]) + "s"

    @property
    def label(self) -> str:
        return "".join(w.capitalize() for w in self.name.split("_"))


LINK_RE = re.compile(r"^\s*([A-Z_]+)\s+(\S{2})--(\S{2})\s+([A-Z_]+)\s*:\s*(\w+)")
ENTITY_RE = re.compile(r"^\s*([A-Z_]+)\s*(\{)?\s*$")
ATTR_RE = re.compile(r"^\s*(\w+(?:\[\])?)\s+(\w+)(?:\s+\".*\")?\s*$")


def parse_erd(path: Path = ERD) -> dict[str, Entity]:
    entities: dict[str, Entity] = {}
    current: Entity | None = None
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%%") or stripped.startswith("```") or stripped == "erDiagram":
            continue
        if current is not None:
            if stripped == "}":
                current = None
            elif m := ATTR_RE.match(line):
                current.attrs[m.group(2)] = m.group(1)
            continue
        if m := LINK_RE.match(line):
            src, _, right, tgt, verb = m.groups()
            ent = entities.setdefault(src, Entity(src))
            entities.setdefault(tgt, Entity(tgt))
            link = ent.links.get(verb)
            if link is None:
                ent.links[verb] = Link(src, verb, [tgt], "{" in right, right.startswith("|"))
            else:
                link.targets.append(tgt)
            continue
        if m := ENTITY_RE.match(line):
            current = entities.setdefault(m.group(1), Entity(m.group(1)))
            if not m.group(2):
                current = None
    return entities


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


def load_meta(session, entities: dict[str, Entity]) -> None:
    session.run("MATCH (e:EntityType) DETACH DELETE e")
    session.run(
        "UNWIND $rows AS r CREATE (:EntityType {name: r.name, key: r.key, label: r.label, attrs: r.attrs})",
        rows=[{"name": e.name, "key": e.key, "label": e.label, "attrs": list(e.attrs)} for e in entities.values()],
    )
    rows = [
        {"src": l.source, "tgt": t, "verb": l.verb, "many": l.many, "required": l.required}
        for e in entities.values() for l in e.links.values() for t in l.targets
    ]
    session.run(
        "UNWIND $rows AS r MATCH (a:EntityType {name: r.src}), (b:EntityType {name: r.tgt}) "
        "CREATE (a)-[:LINK {verb: r.verb, many: r.many, required: r.required}]->(b)",
        rows=rows,
    )


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
        print(f"  warning: {doc}: top-level keys not in the ERD kept as-is: {extra_top}", file=sys.stderr)
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
            if k in ("id", "doc", "type", "_json", "_empty", "_order"):
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

    entity_keys = {e.key for e in entities.values()}
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


def check(session, docs: list[str], only: set[str] | None = None) -> int:
    failures = 0
    rules = [r for r in load_rules() if not only or r.id in only]
    for doc in docs:
        for rule in rules:
            try:
                rows = session.run(rule.query, doc=doc).data()
            except Exception as exc:  # a broken rule file must not stop the others
                failures += 1
                print(f"{doc}: rule-error {rule.id} {rule.file.name}: {exc}".splitlines()[0])
                continue
            for row in rows:
                failures += rule.severity == "error"
                detail = row.get("detail", "")
                print(f"{doc}: {rule.severity} {rule.id} {row['pointer']} {detail}".rstrip())
                if rule.hint:
                    print(f"    hint: {rule.hint}")
    return failures


# ---------------------------------------------------------------- CLI


def main() -> None:
    p = argparse.ArgumentParser(prog="harness", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, helptext in [
        ("load", "load documents (default: every example) into Neo4j, replacing what is there"),
        ("export", "write loaded documents back to their YAML files"),
        ("check", "run the Cypher rules in harness/rules against loaded documents"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("docs", nargs="*", help="example names (e.g. openemr) or YAML paths")
        if name == "check":
            sp.add_argument("--rules", help="comma-separated rule ids to run (default: all)")
    sub.add_parser("meta", help="load only the ERD meta-graph")
    args = p.parse_args()

    entities = parse_erd()
    with GraphDatabase.driver(URI, auth=AUTH, notifications_min_severity="OFF") as driver, driver.session() as s:
        if args.cmd == "meta":
            load_meta(s, entities)
            print(f"loaded {len(entities)} entity types")
            return
        if args.cmd == "load":
            load_meta(s, entities)
            paths = [doc_path(d) for d in args.docs] or all_docs()
            for path in paths:
                print(f"loaded {load_doc(s, path, entities)} from {path.relative_to(ROOT)}")
            return
        docs = [Path(d).stem for d in args.docs] or [
            r["doc"] for r in s.run("MATCH (d:Document) RETURN d.doc AS doc ORDER BY doc")]
        if args.cmd == "export":
            for doc in docs:
                print(f"exported {doc} to {export_doc(s, doc, entities).relative_to(ROOT)}")
        elif args.cmd == "check":
            only = set(args.rules.split(",")) if args.rules else None
            sys.exit(1 if check(s, docs, only) else 0)


if __name__ == "__main__":
    main()
