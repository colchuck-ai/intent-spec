"""Seam 2: `harness.py lint <model.md>` reports each shape defect with its check ID and location."""
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
FIX = HARNESS / "tests" / "fixtures" / "model"
CLEAN = (FIX / "clean.md").read_text()


def lint(text: str, tmp_path: Path) -> tuple[int, list[str]]:
    path = tmp_path / "model.md"
    path.write_text(text)
    p = subprocess.run(
        [sys.executable, "harness.py", "lint", str(path), "--rules", str(FIX / "rules"), "--invalid", str(FIX / "invalid")],
        cwd=HARNESS, capture_output=True, text=True)
    return p.returncode, [l for l in p.stdout.splitlines() if l.strip()]


def plant(old: str, new: str) -> str:
    assert old in CLEAN, old
    return CLEAN.replace(old, new, 1)


def test_clean_model_passes(tmp_path):
    assert lint(CLEAN, tmp_path) == (0, [])


def test_missing_conventions_section(tmp_path):
    text = plant("## Conventions\n", "## Notes\n")
    code, out = lint(text, tmp_path)
    assert code == 1 and "MD-SECTIONS model: missing section Conventions" in out


def test_sections_out_of_order(tmp_path):
    overview = CLEAN[CLEAN.index("## Overview"):CLEAN.index("## Conventions")]
    text = CLEAN.replace(overview, "").replace("## Product\n", overview + "## Product\n", 1)
    code, out = lint(text, tmp_path)
    assert code == 1 and "MD-SECTIONS model: Overview must come first, then Conventions" in out


def test_element_without_anchor(tmp_path):
    code, out = lint(plant("Anchor: exact — JTBD job.\n", ""), tmp_path)
    assert code == 1 and out == ["MD-ELEMENT JOB: no Anchor line"]


def test_element_without_definition(tmp_path):
    code, out = lint(plant("A company-level selection of controls.\n", ""), tmp_path)
    assert code == 1 and out == ["MD-ELEMENT PROFILE: no definition"]


def test_element_without_links_table(tmp_path):
    code, out = lint(plant("Links: none.\n", ""), tmp_path)
    assert code == 1 and out == ["MD-ELEMENT JOB_EXECUTOR: no Links table (or 'Links: none.')"]


def test_element_name_pattern(tmp_path):
    code, out = lint(plant("### JOB_EXECUTOR\n", "### Job executor\n").replace("| JOB_EXECUTOR |", "| Job executor |"), tmp_path)
    assert code == 1 and "MD-NAME Job executor: element names match ^[A-Z_]+$" in out


def test_duplicate_element(tmp_path):
    code, out = lint(CLEAN + "\n### PROFILE\n\nAgain.\n\nAnchor: added.\n\nAttributes: none.\n\nLinks: none.\n", tmp_path)
    assert code == 1 and "MD-NAME PROFILE: element appears more than once" in out


def test_attribute_table_header(tmp_path):
    text = plant("| Attribute | Type | Required | Meaning |\n|---|---|---|---|\n| statement",
                 "| Attribute | Kind | Required | Meaning |\n|---|---|---|---|\n| statement")
    code, out = lint(text, tmp_path)
    assert code == 1 and "MD-TABLE JOB: Attributes header must be | Attribute | Type | Required | Meaning |" in out


def test_required_vocabulary(tmp_path):
    code, out = lint(plant("| owner | string | yes |", "| owner | string | maybe |"), tmp_path)
    assert code == 1 and out == ["MD-TABLE PROFILE.owner: Required is yes, no, one or more, or starts with 'when ' or 'unless '"]


def test_type_vocabulary(tmp_path):
    code, out = lint(plant("| owner | string | yes |", "| owner | strng | yes |"), tmp_path)
    assert code == 1 and out == ["MD-TABLE PROFILE.owner: unknown type strng"]


def test_cardinality_vocabulary(tmp_path):
    code, out = lint(plant("| imports | PROFILE | zero or more |", "| imports | PROFILE | lots |"), tmp_path)
    assert code == 1 and "MD-TABLE PROFILE.imports: Cardinality is exactly one, zero or one, zero or more or one or more, optionally '; each target has <one of those>'" in out


def test_link_target_must_exist(tmp_path):
    code, out = lint(plant("| targets | JOB | zero or more |", "| targets | JOB or JOBS | zero or more |"), tmp_path)
    assert code == 1 and "MD-TARGET PRODUCT.targets: no element JOBS" in out


def test_link_verb_is_one_word(tmp_path):
    code, out = lint(plant("| imports | PROFILE |", "| narrows down | PROFILE |"), tmp_path)
    assert code == 1 and "MD-VERB PROFILE.narrows down: a link verb is one word" in out


def test_duplicate_rule_id(tmp_path):
    code, out = lint(plant("- **G-32** (warning)", "- **P-1** (warning)"), tmp_path)
    assert code == 1 and "MD-RULE P-1: ID used more than once" in out


def test_retired_rule_id_reused(tmp_path):
    code, out = lint(plant("- **P-2** (error)", "- **P-9** (error)").replace("Not checked by a query: P-2.", "Not checked by a query: P-9."), tmp_path)
    assert code == 1 and out == ["MD-RULE P-9: retired ID reused"]


def test_malformed_rule_item(tmp_path):
    code, out = lint(plant("- **G-32** (warning):", "- **G-32** (fatal):"), tmp_path)
    assert code == 1 and "MD-RULE PROFILE: malformed rule item: - **G-32** (fatal): profile imports have no cycles" in out


def test_citation_must_resolve(tmp_path):
    code, out = lint(plant("at least one job [DOC-2]", "at least one job [DOC-7]"), tmp_path)
    assert code == 1 and out == ["MD-CITE P-1: cites unknown ID DOC-7"]


def test_rule_without_query_or_invalid_example(tmp_path):
    text = plant("- **P-2** (error)", "- **P-3** (error)")
    code, out = lint(text, tmp_path)
    assert code == 1
    assert "MD-QUERY P-3: no query file in the rules directory" in out
    assert "MD-QUERY P-3: no invalid example names it" in out


def test_query_without_rule(tmp_path):
    code, out = lint(plant("- **G-32** (warning): profile imports have no cycles\n", ""), tmp_path)
    assert code == 1 and "MD-QUERY G-32: query file has no rule in the model" in out


def test_unchecked_rule_needs_no_query(tmp_path):
    code, out = lint(plant("Not checked by a query: P-2.", "Not checked by a query: P-2, P-1."), tmp_path)
    assert code == 1 and out == ["MD-QUERY P-1: listed as not checked by a query, but has a query file"]


def test_anchor_vocabulary(tmp_path):
    code, out = lint(plant("Anchor: exact — JTBD job.", "Anchor: same — JTBD job."), tmp_path)
    assert code == 1 and out == ["MD-ANCHOR JOB: anchor is exact, close, broad, narrow, related, added or departure, not same"]


def test_departure_needs_decision(tmp_path):
    code, out = lint(plant("Anchor: exact — JTBD job.", "Anchor: departure — JTBD job, but stored per product."), tmp_path)
    assert code == 1 and out == ["MD-ANCHOR JOB: a departure names its decision as (decision: <bead id>)"]


def test_declared_departure_passes(tmp_path):
    text = plant("Anchor: exact — JTBD job.", "Anchor: departure — JTBD job, but stored per product (decision: review-abc).")
    assert lint(text, tmp_path) == (0, [])


def test_stale_overview(tmp_path):
    code, out = lint(plant("  PROFILE }o--o{ PROFILE: imports\n", ""), tmp_path)
    assert code == 1 and out == ["MD-OVERVIEW Overview: differs from the link tables; run harness.py render"]


def test_overview_markers_missing(tmp_path):
    code, out = lint(plant("<!-- /overview -->\n", ""), tmp_path)
    assert code == 1 and out == ["MD-OVERVIEW Overview: no generated block between <!-- overview: ... --> and <!-- /overview -->"]
