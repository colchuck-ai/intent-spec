"""Seam 5: the harness commands stay green on every example (needs Neo4j; skipped when it is down)."""
import socket
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parent.parent


def neo4j_up() -> bool:
    try:
        socket.create_connection(("localhost", 7687), timeout=1).close()
        return True
    except OSError:
        return False


pytestmark = pytest.mark.skipif(not neo4j_up(), reason="Neo4j is not running")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "harness.py", *args], cwd=HARNESS, capture_output=True, text=True)


def test_check_finds_no_errors_or_unwaived_warnings():
    assert run("load").returncode == 0
    p = run("check")
    assert p.returncode == 0, p.stdout
    assert not [l for l in p.stdout.splitlines() if ": warning " in l or ": error " in l], p.stdout


def test_every_invalid_example_breaks_exactly_its_rule():
    p = run("test")
    assert p.returncode == 0, p.stdout
    assert "96 passed, 0 failed, 96 invalid examples" in p.stdout


def test_export_round_trips_every_example():
    assert run("load").returncode == 0
    assert run("export").returncode == 0
    diff = subprocess.run(["git", "diff", "--quiet", "--", "../review/examples/*.yaml"], cwd=HARNESS)
    assert diff.returncode == 0
