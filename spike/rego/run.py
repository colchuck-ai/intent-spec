"""Run the spike's Rego rules over the examples and compare with what they declare.

For each document: parse YAML (duplicate keys rejected), fetch its imports beside it or
among the examples by file stem (as the harness does), build {document, imports}, and
evaluate data.intent.report with opa. An invalid example expects exactly the findings its
`# breaks:` / `# also:` lines list for the spike's rules; a valid example expects none.

uv run --with ruamel.yaml python spike/rego/run.py   (from the repo root)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from ruamel.yaml import YAML

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parents[1] / "review" / "examples"
SPIKE = {"GRC-10", "DFD-8", "RISK-4", "REF-3"}
INVALID_FOR = ["GRC-10", "GRC-10-import", "DFD-8", "RISK-4", "REF-3", "REF-3-import"]
EXPECT_RE = re.compile(r"^#\s*(breaks|also):\s*(\S+)\s+(\S+)\s*$")

yaml = YAML(typ="safe")  # YAML 1.2 core schema; rejects duplicate keys


def load(path: Path) -> dict:
    return yaml.load(path.read_text())


def stem(source: str) -> str:
    return re.sub(r"\.(ya?ml|json)$", "", str(source).rstrip("/").rsplit("/", 1)[-1])


def imports(path: Path, doc: dict) -> dict:
    out = {}
    for alias, imp in (doc.get("imports") or {}).items():
        source = str((imp or {}).get("source", ""))
        for cand in (path.parent / source, EXAMPLES / f"{stem(source)}.yaml"):
            if source and cand.is_file():
                out[alias] = load(cand)
                break
    return out


def evaluate(path: Path) -> dict:
    doc = load(path)
    # default=str: YAML timestamps (unquoted dates) stay strings, as erd.md Serialization asks
    payload = json.dumps({"document": doc, "imports": imports(path, doc)}, default=str)
    res = subprocess.run(
        ["opa", "eval", "--stdin-input", "-d", str(HERE / "rules"), "-d", str(HERE / "model.json"),
         "--format", "json", "data.intent.report"],
        input=payload, capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)["result"][0]["expressions"][0]["value"]


def expected(path: Path) -> set:
    return {(m.group(2), m.group(3)) for line in path.read_text().splitlines()
            if (m := EXPECT_RE.match(line)) and m.group(2) in SPIKE}


def main() -> int:
    valid = sorted(EXAMPLES.glob("*.yaml"))
    invalid = sorted((EXAMPLES / "invalid").glob("*.yaml"))
    failed = 0
    for path in valid + invalid:
        report = evaluate(path)
        actual = {(f["rule"], f["pointer"]) for f in report["findings"]}
        want = expected(path) if path.parent.name == "invalid" else set()
        problems = [f"missing {r} {p}" for r, p in sorted(want - actual)]
        problems += [f"unexpected {r} {p}" for r, p in sorted(actual - want)]
        name = path.relative_to(EXAMPLES)
        waived = "".join(f" [waived {w['rule']} {w['pointer']}]" for w in report["waived"])
        if problems:
            failed += 1
            print(f"FAIL {name}: " + "; ".join(problems))
            for f in report["findings"]:
                print(f"     {f['rule']} {f['pointer']} {f['detail']}")
        elif want or path.stem in INVALID_FOR:
            details = "; ".join(f"{f['rule']} {f['pointer']} {f['detail']}" for f in sorted(report["findings"], key=str))
            print(f"ok   {name}: {details}{waived}")
        elif waived:
            print(f"ok   {name}:{waived}")
    total = len(valid) + len(invalid)
    print(f"{total - failed} passed, {failed} failed ({len(valid)} valid, {len(invalid)} invalid)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
