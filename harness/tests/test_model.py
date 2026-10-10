"""Seam 1: parse_model reads model.md into entities, attributes, links, rules and derivations."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import harness as h

FIX = Path(__file__).resolve().parent / "fixtures" / "model"


def test_parse_model_reads_elements_and_attributes():
    m = h.parse_model(FIX / "clean.md")
    assert list(m.entities) == ["PRODUCT", "JOB", "JOB_EXECUTOR", "SELECTION", "PROFILE"]
    job = m.entities["JOB"]
    assert job.attrs == {"statement": "string", "kind": "enum", "tags": "string[]"}
    assert job.required == {"statement": True, "kind": False, "tags": True}
    assert job.values == {"kind": ["core", "related"]}
    assert job.area == "Product"
    assert job.anchor == "exact"
    assert m.entities["PRODUCT"].attrs == {}


def test_parse_model_reads_links_with_cardinality():
    m = h.parse_model(FIX / "clean.md")
    t = m.entities["PRODUCT"].links["targets"]
    assert (t.source, t.targets, t.many, t.required) == ("PRODUCT", ["JOB"], True, False)
    mot = m.entities["JOB"].links["motivates"]
    assert (mot.targets, mot.many, mot.required) == (["JOB_EXECUTOR"], False, True)
    sel = m.entities["SELECTION"].links["in"]
    assert (sel.targets, sel.many, sel.required, sel.left) == (["PROFILE"], False, True, "}|")
    assert m.entities["JOB_EXECUTOR"].links == {}


def test_parse_model_reads_rules_derivations_and_convention_lists():
    m = h.parse_model(FIX / "clean.md")
    assert {k: r.severity for k, r in m.rules.items()} == {"DOC-3": "error", "P-1": "error", "P-2": "error", "G-32": "warning"}
    assert m.rules["P-1"].element == "PRODUCT"
    assert m.rules["DOC-3"].element == ""
    assert m.rules["P-1"].statement == "every ratified product targets at least one job [DOC-2]"
    assert list(m.derivations) == ["DOC-2", "G-31"]
    assert m.derivations["G-31"].element == "PROFILE"
    assert m.retired == ["P-9"]
    assert m.unchecked == ["P-2"]
    assert m.generated == ["SCHEMA-LINK"]
