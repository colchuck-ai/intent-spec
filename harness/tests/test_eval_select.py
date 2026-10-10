"""Seam 7: `anneal.py eval --old A --new B` lists the elements to evaluate: those added or changed."""
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
CLEAN = (HARNESS / "tests" / "fixtures" / "model" / "clean.md").read_text()


def select(old: str, new: str, tmp_path: Path) -> list[str]:
    (tmp_path / "old.md").write_text(old)
    (tmp_path / "new.md").write_text(new)
    p = subprocess.run([sys.executable, "anneal.py", "eval", "--old", str(tmp_path / "old.md"), "--new", str(tmp_path / "new.md")],
                       cwd=HARNESS, capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout.split()


def test_unchanged_model_selects_nothing(tmp_path):
    assert select(CLEAN, CLEAN, tmp_path) == []


def test_changed_and_added_elements_are_selected(tmp_path):
    new = CLEAN.replace("| owner | string | yes | who decides changes |", "| owner | string | yes | who approves changes |")
    new = new.replace("## Governance\n", "## Governance\n\n### CATALOG\n\nA list of controls.\n\nAnchor: added — x.\n\nAttributes: none.\n\nLinks: none.\n\n")
    new = new.replace("The person or group who does the job.\n", "")
    new = new.replace("### SELECTION", "### SELECTION_X")
    assert select(CLEAN, new, tmp_path) == ["JOB_EXECUTOR", "CATALOG", "SELECTION_X", "PROFILE"]
