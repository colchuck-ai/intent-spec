"""Run the spike's Rego rules over the examples and compare with what they declare.

Two variants of the same rules, side by side:
  scoped    rules/    input {document, imports: {alias: doc}}; each rule resolves references itself
  resolved  resolved/ input {document: id, documents: {id: doc}, aliases: {id: {alias: id}}};
                      lib/graph.rego resolves once (and reports REF-1), rules read the graph

For each document: parse YAML (duplicate keys rejected), fetch its imports beside it or
among the examples by file stem (as the harness does), build the input, and evaluate
data.intent.report with opa. A document expects exactly the findings its `# breaks:` /
`# also:` lines list for the variant's rules; a document without them expects none.

uv run --no-project --python 3.12 --with ruamel.yaml python spike/rego/run.py [scoped|resolved]
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parents[1] / "review" / "examples"
FIXTURES = HERE / "fixtures"
VARIANTS = {
    "scoped": (HERE / "rules", {"GRC-10", "DFD-8", "RISK-4", "REF-3"}),
    "resolved": (HERE / "resolved", {"GRC-10", "DFD-8", "RISK-4", "REF-3", "REF-1"}),
}
SHOW = {"GRC-10", "GRC-10-import", "GRC-10-transitive", "DFD-8", "RISK-4", "REF-3", "REF-3-import",
        "REF-1", "REF-1-alias", "REF-1-import"}
EXPECT_RE = re.compile(r"^#\s*(breaks|also):\s*(\S+)\s+(\S+)\s*$")

yaml = YAML(typ="safe")  # YAML 1.2 core schema; rejects duplicate keys


def load(path: Path) -> dict:
    return yaml.load(path.read_text())


def stem(source: str) -> str:
    return re.sub(r"\.(ya?ml|json)$", "", str(source).rstrip("/").rsplit("/", 1)[-1])


def fetch(path: Path, doc: dict):
    """Yield (alias, path, doc) for each import the caller can find."""
    for alias, imp in (doc.get("imports") or {}).items():
        source = str((imp or {}).get("source", ""))
        for cand in (path.parent / source, EXAMPLES / f"{stem(source)}.yaml"):
            if source and cand.is_file():
                yield alias, cand.resolve(), load(cand)
                break


def scoped_input(path: Path, doc: dict) -> dict:
    return {"document": doc, "imports": {alias: d for alias, _, d in fetch(path, doc)}}


def resolved_input(path: Path, doc: dict) -> dict:
    """Every document in the import closure by id, one version each, and each one's alias table."""
    documents, aliases, files = {doc["id"]: doc}, {}, {doc["id"]: path.resolve()}
    todo = [(path, doc)]
    while todo:
        p, d = todo.pop()
        table = aliases.setdefault(d["id"], {})
        for alias, q, imported in fetch(p, d):
            iid = imported["id"]
            if iid in files and files[iid] != q:
                raise SystemExit(f"{path}: two versions of document {iid}: {files[iid]} and {q}")
            table[alias] = iid
            if iid not in documents:
                documents[iid], files[iid] = imported, q
                todo.append((q, imported))
    return {"document": doc["id"], "documents": documents, "aliases": aliases}


def evaluate(variant: str, path: Path) -> dict:
    doc = load(path)
    build = resolved_input if variant == "resolved" else scoped_input
    # default=str: YAML timestamps (unquoted dates) stay strings, as erd.md Serialization asks
    payload = json.dumps(build(path, doc), default=str)
    res = subprocess.run(
        ["opa", "eval", "--stdin-input", "-d", str(VARIANTS[variant][0]), "-d", str(HERE / "model.json"),
         "--format", "json", "data.intent.report"],
        input=payload, capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)["result"][0]["expressions"][0]["value"]


def expected(path: Path, rules: set) -> set:
    return {(m.group(2), m.group(3)) for line in path.read_text().splitlines()
            if (m := EXPECT_RE.match(line)) and m.group(2) in rules}


def main() -> int:
    variant = sys.argv[1] if len(sys.argv) > 1 else "resolved"
    rules = VARIANTS[variant][1]
    paths = sorted(EXAMPLES.glob("*.yaml")) + sorted((EXAMPLES / "invalid").glob("*.yaml")) + sorted(FIXTURES.glob("*.yaml"))
    failed = 0
    for path in paths:
        report = evaluate(variant, path)
        actual = {(f["rule"], f["pointer"]) for f in report["findings"]}
        want = expected(path, rules)
        problems = [f"missing {r} {p}" for r, p in sorted(want - actual)]
        problems += [f"unexpected {r} {p}" for r, p in sorted(actual - want)]
        name = path.relative_to(HERE if path.is_relative_to(HERE) else EXAMPLES)
        waived = "".join(f" [waived {w['rule']} {w['pointer']}]" for w in report["waived"])
        if problems:
            failed += 1
            print(f"FAIL {name}: " + "; ".join(problems))
            for f in report["findings"]:
                print(f"     {f['rule']} {f['pointer']} {f['detail']}")
        elif want or path.stem in SHOW:
            details = "; ".join(f"{f['rule']} {f['pointer']} {f['detail']}" for f in sorted(report["findings"], key=str))
            print(f"ok   {name}: {details or 'no findings'}{waived}")
        elif waived:
            print(f"ok   {name}:{waived}")
    print(f"{variant}: {len(paths) - failed} passed, {failed} failed ({len(paths)} documents)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
