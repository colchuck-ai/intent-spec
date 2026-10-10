import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import anneal as a

W = {"P1": 10, "P2": 3, "P3": 1, "errors": 10, "size": 0.5, "departures": 50}
T = {"hot": {"max": 10}, "warm": {"max": 3}, "cool": {"max": 0}, "frozen": {"max": 0, "strict": True}}


def test_energy_arithmetic():
    parts = {"P1": 2, "P2": 18, "P3": 1, "errors": 1, "size": 254, "departures": 1}
    assert a.energy(parts, W) == 20 + 54 + 1 + 10 + 127 + 50
    assert a.per_example(parts, 4, W) == (20 + 54 + 1 + 10) / 4
    assert a.per_example(parts, 0, W) == 0


def test_delta_energy():
    pre = {"errors": 0, "size": 254, "departures": 0}
    post = {"errors": 0, "size": 260, "departures": 1}
    d = a.delta_energy(resolved=[1, 2], new=[3], pre=pre, post=post, w=W)
    assert d["total"] == -13 + 1 + 3 + 50


def test_thresholds_per_temperature():
    assert a.accept(10, "hot", T) and not a.accept(10.5, "hot", T)
    assert a.accept(3, "warm", T) and not a.accept(4, "warm", T)
    assert a.accept(0, "cool", T) and not a.accept(0.5, "cool", T)
    assert a.accept(-0.5, "frozen", T) and not a.accept(0, "frozen", T)


def test_schedule_cools_reheats_and_caps():
    assert a.next_temperature("hot", 5, 5, 1.5) == "warm"
    assert a.next_temperature("cool", 5, 5, 1.5) == "frozen"
    assert a.next_temperature("frozen", 5, 5, 1.5) == "frozen"
    assert a.next_temperature("cool", 8, 5, 1.5) == "warm"   # probe 1.6x: reheat
    assert a.next_temperature("hot", 100, 5, 1.5) == "hot"   # capped


def test_stop_check():
    assert a.is_frozen("frozen", 100, 100, 6, 5, 1.25)
    assert not a.is_frozen("cool", 100, 100, 6, 5, 1.25)       # not frozen yet
    assert not a.is_frozen("frozen", 90, 100, 6, 5, 1.25)      # still falling
    assert not a.is_frozen("frozen", 100, 100, 7, 5, 1.25)     # probe doesn't generalize
    assert not a.is_frozen("frozen", 100, None, 0, 5, 1.25)    # nothing to compare


RULE = {"not_archived": True, "has_source": True, "min_stars": 1000, "updated_since": "2025-10-08"}


def products():
    base = {"archived": False, "source": "https://x", "stars": 5000, "updated": "2026-10-01"}
    return [
        {**base, "id": "a", "tags": ["CRM"]},
        {**base, "id": "b", "tags": ["CRM", "Health"]},
        {**base, "id": "c", "tags": ["Health"]},
        {**base, "id": "old", "tags": ["CRM"], "updated": "2024-01-01"},
        {**base, "id": "arch", "tags": ["CRM"], "archived": True},
        {**base, "id": "small", "tags": ["CRM"], "stars": 10},
        {**base, "id": "nosrc", "tags": ["CRM"], "source": None},
        {**base, "id": "done", "tags": ["CRM"], "source": "https://github.com/done/done/"},
    ]


def test_eligibility():
    ids = {p["id"] for p in a.eligible(products(), RULE, {"https://github.com/done/done"})}
    assert ids == {"a", "b", "c"}


def test_draws_replay():
    one = a.draw_probe(products(), RULE, set(), [], "s", 3)
    two = a.draw_probe(products(), RULE, set(), [], "s", 3)
    assert one == two
    p1 = a.draw_panel(["x", "y"], ["s1", "s2", "s3", "s4"], 2, ["e1", "e2", "e3"], {}, 2, "s", 3)
    p2 = a.draw_panel(["x", "y"], ["s1", "s2", "s3", "s4"], 2, ["e1", "e2", "e3"], {}, 2, "s", 3)
    assert p1 == p2 and len(p1) == 4 and all(len(v) == 2 for v in p1.values())


def test_without_replacement_and_tag_spread():
    modeled, tags, seen = {"done"}, [], set()
    for r in range(3):
        tag, p = a.draw_probe(products(), RULE, modeled, tags, "s", r)
        assert p["id"] not in seen
        seen.add(p["id"]); modeled.add(p["id"]); tags.append(tag)
    assert seen == {"a", "b", "c"}
    assert set(tags[:2]) == {"CRM", "Health"}   # undrawn tags come first


def test_panel_prefers_unseen():
    p = a.draw_panel(["x"], [], 0, ["e1", "e2", "e3"], {"x": {"e1", "e2"}}, 1, "s", 1)
    assert p["x"] == ["e3"]


FIX = Path(__file__).resolve().parent / "fixtures" / "model"


def test_model_size_counts_elements_links_and_rules():
    assert a.model_size(FIX / "clean.md") == {"entities": 5, "links": 4, "rules": 4, "size": 13}


def test_departures_count_declared_anchor_departures(tmp_path):
    assert a.departures(FIX / "clean.md") == 0
    text = (FIX / "clean.md").read_text().replace(
        "Anchor: exact — JTBD job.", "Anchor: departure — JTBD job, stored per product (decision: review-abc).")
    path = tmp_path / "model.md"
    path.write_text(text)
    assert a.departures(path) == 1
