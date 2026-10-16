"""Generate model.json (entity keys and link fields) from erd.md for the Rego spike.

Stand-in for what the JSON Schema will provide in phase 2b: which fields of each
item type are links, and which links may target an external reference.
Run from harness/: uv run python ../spike/rego/gen_model.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "harness"))
from harness import BASE_LINKS, parse_erd  # noqa: E402

entities = parse_erd()
types, links, external = {}, {}, {}
for e in entities.values():
    if e.name in ("DOCUMENT", "IMPORT"):
        continue
    types[e.key] = e.name
    links[e.key] = sorted(set(e.links) | set(BASE_LINKS))
    external[e.key] = sorted(v for v, l in e.links.items() if "EXTERNAL_REFERENCE" in l.targets)
out = Path(__file__).resolve().parent / "model.json"
out.write_text(json.dumps({"model": {"types": types, "links": links, "external": external}}, indent=1, sort_keys=True) + "\n")
print(f"wrote {out} ({len(types)} types)")
