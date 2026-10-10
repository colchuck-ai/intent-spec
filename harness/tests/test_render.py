"""Seam 3: `harness.py render <model.md>` writes the overview diagram from the link tables."""
import subprocess
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
CLEAN = (HARNESS / "tests" / "fixtures" / "model" / "clean.md").read_text()

EXPECTED = """```mermaid
erDiagram
  PRODUCT }o--o{ JOB: targets
  JOB }o--|| JOB_EXECUTOR: motivates
  SELECTION }|--|| PROFILE: in
  PROFILE }o--o{ PROFILE: imports
```"""


def render(path: Path) -> int:
    return subprocess.run([sys.executable, "harness.py", "render", str(path)], cwd=HARNESS).returncode


def blank_overview(text: str) -> str:
    start = text.index("```mermaid")
    end = text.index("```", start + 3) + 3
    return text[:start] + "```mermaid\n```" + text[end:]


def test_render_writes_overview_from_links(tmp_path):
    path = tmp_path / "model.md"
    path.write_text(blank_overview(CLEAN))
    assert render(path) == 0
    assert EXPECTED in path.read_text()
    assert path.read_text() == CLEAN


def test_render_twice_changes_nothing(tmp_path):
    path = tmp_path / "model.md"
    path.write_text(CLEAN)
    render(path)
    render(path)
    assert path.read_text() == CLEAN
