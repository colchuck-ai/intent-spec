"""Seam 4 (one-time, deleted with erd.md): model.md says exactly what erd.md says."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import harness as h

ERD = h.ROOT / "erd.md"
MODEL = h.ROOT / "model.md"


def test_same_entities_attributes_and_links():
    old, new = h.parse_erd(ERD), h.parse_model(MODEL).entities
    assert set(new) == set(old)
    for name, e in old.items():
        n = new[name]
        assert n.attrs == e.attrs, name
        rows = {r["name"]: r for r in h.attr_rows(e)}
        assert n.required == {k: r["required"] for k, r in rows.items()}, name
        assert n.values == {k: r["values"] for k, r in rows.items() if r["values"]}, name
        assert {v: (l.targets, l.many, l.required) for v, l in n.links.items()} == \
               {v: (l.targets, l.many, l.required) for v, l in e.links.items()}, name


def test_same_relationship_lines():
    erd_lines = {re.sub(r"\s+", " ", l.strip()) for l in ERD.read_text().splitlines() if h.LINK_RE.match(l)}
    overview = h.overview(h.parse_model(MODEL))
    assert {re.sub(r"\s+", " ", l.strip()) for l in overview.splitlines() if h.LINK_RE.match(l)} == erd_lines


def test_same_rules_and_derivations():
    m = h.parse_model(MODEL)
    assert {k: r.severity for k, r in m.rules.items()} == h.parse_rule_ids(ERD)
    derived = set(re.findall(r"%%\s*derived\s+([A-Z0-9]+-\d+):", ERD.read_text()))
    assert set(m.derivations) == derived
    retired = re.search(r"%% Retired: (.*?) \(", ERD.read_text()).group(1)
    assert m.retired == [x.strip() for x in retired.split(",")]


def test_same_rule_and_derivation_statements():
    text = ERD.read_text()
    old = dict(re.findall(r"%%\s*(?:rule|derived)\s+([A-Z0-9]+-\d+)(?:\s*\(should\))?:\s*(.*)", text))
    m = h.parse_model(MODEL)
    new = {k: r.statement for k, r in {**m.rules, **m.derivations}.items()}
    assert new == old
