"""Run the mechanical steps of the annealing loop (review/loop.md) deterministically.

Commands: status, begin, measure, move start|judge|next, end, reset-to-best.
State lives in ../anneal/state.json, the best model so far in ../anneal/best/,
findings and moves in beads (review/.beads). Every draw uses
random.Random(f"{seed}:{round}:{purpose}"), so it replays exactly.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import harness as h

ROOT = h.ROOT
ANNEAL = ROOT / "anneal"
STATE = ANNEAL / "state.json"
BEST = ANNEAL / "best"
REVIEW = ROOT / "review"
FORMULA = "anneal-round"

TEMPS = ["frozen", "cool", "warm", "hot"]  # coldest first
SIZES = ["local", "additive", "structural", "unifying"]
DEPARTURE_RE = re.compile(r"^\s*%%\s*departure\s+DEP-\d+", re.M)
STEPS = ["author", "review", "triage", "measure", "explore", "anneal", "end"]


# ---------------------------------------------------------------- pure parts (unit-tested)


def rng(seed: str, round_: int, purpose: str) -> random.Random:
    return random.Random(f"{seed}:{round_}:{purpose}")


def finding_weight(priority: int, w: dict) -> float:
    return {1: w["P1"], 2: w["P2"], 3: w["P3"]}.get(priority, 0)


def energy(parts: dict, w: dict) -> float:
    """E from its parts: P1, P2, P3 (counts), errors, size, departures."""
    return (w["P1"] * parts["P1"] + w["P2"] * parts["P2"] + w["P3"] * parts["P3"]
            + w["errors"] * parts["errors"] + w["size"] * parts["size"] + w["departures"] * parts["departures"])


def per_example(parts: dict, n: int, w: dict) -> float:
    """The part of energy that belongs to examples (findings and errors), averaged over n examples."""
    if n == 0:
        return 0.0
    return (w["P1"] * parts["P1"] + w["P2"] * parts["P2"] + w["P3"] * parts["P3"] + w["errors"] * parts["errors"]) / n


def accept(delta: float, temp: str, thresholds: dict) -> bool:
    """Threshold accepting: keep when ΔE is at or below the threshold; strictly below when the threshold is strict."""
    t = thresholds[temp]
    return delta < t["max"] if t.get("strict") else delta <= t["max"]


def size_allowed(size: str, temp: str, allowed: dict) -> bool:
    return size in allowed[temp]


def next_temperature(temp: str, probe_per: float, bench_per: float, reheat: float) -> str:
    """Cool one step, or reheat one step (capped at hot) when the probe's energy per example
    exceeds `reheat` times the benchmark's."""
    i = TEMPS.index(temp)
    if bench_per > 0 and probe_per > reheat * bench_per or bench_per == 0 and probe_per > 0:
        return TEMPS[min(i + 1, len(TEMPS) - 1)]
    return TEMPS[max(i - 1, 0)]


def is_frozen(temp: str, e_now: float, e_prev: float | None, probe_per: float, bench_per: float, stop: float) -> bool:
    """Stop when frozen, benchmark energy didn't fall, and the probe generalizes."""
    if temp != "frozen" or e_prev is None or e_now < e_prev:
        return False
    return probe_per <= stop * bench_per if bench_per > 0 else probe_per == 0


def eligible(products: list[dict], rule: dict, modeled: set[str]) -> list[dict]:
    out = []
    for p in products:
        if p["id"] in modeled or (p.get("source") or "").rstrip("/") in modeled:
            continue
        if rule.get("not_archived") and p.get("archived"):
            continue
        if rule.get("has_source") and not p.get("source"):
            continue
        if (p.get("stars") or 0) < rule.get("min_stars", 0):
            continue
        if (p.get("updated") or "") < rule.get("updated_since", ""):
            continue
        out.append(p)
    return out


def draw_probe(products: list[dict], rule: dict, modeled: set[str], drawn_tags: list[str],
               seed: str, round_: int) -> tuple[str, dict]:
    """Tag-stratified draw without replacement: tags not yet drawn come first; then a product within the tag."""
    pool = eligible(products, rule, modeled)
    tags = sorted({t for p in pool for t in p["tags"]})
    if not tags:
        raise SystemExit("no eligible products left")
    fresh = [t for t in tags if t not in drawn_tags] or tags
    order = fresh[:]
    rng(seed, round_, "tag").shuffle(order)
    tag = order[0]
    candidates = sorted((p for p in pool if tag in p["tags"]), key=lambda p: p["id"])
    return tag, rng(seed, round_, "product").choice(candidates)


def draw_panel(core: list[str], specialists: list[str], k: int, benchmark: list[str],
               seen: dict[str, set[str]], per: int, seed: str, round_: int) -> dict[str, list[str]]:
    """Core reviewers plus k sampled specialists; each gets `per` benchmark examples, unseen ones first."""
    sampled = sorted(rng(seed, round_, "specialists").sample(sorted(specialists), k))
    panel = {}
    for persona in core + sampled:
        r = rng(seed, round_, f"examples:{persona}")
        ranked = sorted(benchmark, key=lambda e: (e in seen.get(persona, set()), r.random()))
        panel[persona] = ranked[:per]
    return panel


def delta_energy(resolved: list[int], new: list[int], pre: dict, post: dict, w: dict) -> dict:
    """ΔE for a move: new findings minus resolved ones, plus the mechanical changes."""
    parts = {
        "resolved": -sum(finding_weight(p, w) for p in resolved),
        "new": sum(finding_weight(p, w) for p in new),
        "errors": w["errors"] * (post["errors"] - pre["errors"]),
        "size": w["size"] * (post["size"] - pre["size"]),
        "departures": w["departures"] * (post["departures"] - pre["departures"]),
    }
    parts["total"] = sum(parts.values())
    return parts


# ---------------------------------------------------------------- state, beads, git


def load_state() -> dict:
    return json.loads(STATE.read_text())


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


def bd(*args: str, parse: bool = True):
    out = subprocess.run(["bd", *args, *(["--json"] if parse else [])], cwd=REVIEW,
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"bd {' '.join(args)} failed: {out.stderr.strip()}")
    if not parse:
        return out.stdout.strip()
    text = out.stdout.strip()
    return json.loads(text) if text else []


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


def labels_with(issue: dict, prefix: str) -> list[str]:
    return [l[len(prefix):] for l in issue.get("labels", []) if l.startswith(prefix)]


def counted_findings(examples: set[str]) -> list[dict]:
    """Open findings that count towards energy: accepted or deferred, on an example in the set."""
    rows = bd("list", "--label", "finding", "--all", "--limit", "0")
    rows += [r for r in bd("list", "--label-pattern", "critic-of:*", "--all", "--limit", "0")
             if "finding" not in r.get("labels", [])]
    out, ids = [], set()
    for r in rows:
        if r["id"] in ids or r["status"] == "closed":
            continue
        labels = set(r.get("labels", []))
        if not labels & {"triage:accept", "triage:defer"}:
            continue
        if set(labels_with(r, "example:")) & examples:
            out.append(r)
            ids.add(r["id"])
    return out


def count_priorities(rows: list[dict]) -> dict:
    return {f"P{p}": sum(1 for r in rows if r.get("priority") == p) for p in (1, 2, 3)}


def model_size() -> dict:
    entities = h.parse_erd()
    links = sum(len(l.targets) for e in entities.values() for l in e.links.values())
    rules = len(h.parse_rule_ids())
    return {"entities": len(entities), "links": links, "rules": rules, "size": len(entities) + links + rules}


def departures() -> int:
    return len(DEPARTURE_RE.findall(h.ERD.read_text()))


def harness_errors(examples: list[str]) -> int:
    """Reload every example into Neo4j and count error-severity problems on the given ones."""
    entities = h.parse_erd()
    rules = h.load_rules()
    errors = 0
    with h.GraphDatabase.driver(h.URI, auth=h.AUTH, notifications_min_severity="OFF") as driver, \
            driver.session() as s:
        h.load_meta(s, entities)
        for path in h.all_docs():
            h.load_doc(s, path, entities)
        h.link_imports(s)
        for doc in examples:
            for rule, pointer, _, rationale in h.findings(s, doc, rules):
                if pointer is None or (rule.severity == "error" and rationale is None):
                    errors += 1
    return errors


def measure_set(examples: list[str], w: dict, errors: int | None = None) -> dict:
    rows = counted_findings(set(examples))
    parts = count_priorities(rows)
    parts["errors"] = harness_errors(examples) if errors is None else errors
    parts["size"] = model_size()["size"]
    parts["departures"] = departures()
    parts["E"] = energy(parts, w)
    parts["per_example"] = per_example(parts, len(examples), w)
    parts["examples"] = sorted(examples)
    return parts


def mechanical(examples: list[str]) -> dict:
    return {"size": model_size()["size"], "departures": departures(), "errors": harness_errors(examples),
            "head": git("rev-parse", "HEAD")}


# ---------------------------------------------------------------- molecule


def steps_of(mol: str) -> dict[str, dict]:
    """The molecule's step beads keyed by step name (from their phase: label)."""
    out = {}
    for r in bd("list", "--parent", mol, "--all", "--limit", "0"):
        for phase in labels_with(r, "phase:"):
            if phase in STEPS:
                out[phase] = r
    return out


def current_step(state: dict) -> str | None:
    rnd = state["rounds"].get(str(state["round"]))
    if not rnd or rnd.get("complete"):
        return None
    steps = steps_of(rnd["molecule"])
    if "review" in steps and steps["review"]["status"] != "closed":
        children = bd("list", "--parent", steps["review"]["id"], "--all", "--limit", "0")
        if children and all(c["status"] == "closed" for c in children):
            bd("close", steps["review"]["id"], "--reason", "all panel reviews closed", parse=False)
            steps = steps_of(rnd["molecule"])
    for name in STEPS:
        if name in steps and steps[name]["status"] != "closed":
            return name
    return "done"


def close_step(state: dict, name: str, reason: str) -> None:
    rnd = state["rounds"][str(state["round"])]
    step = steps_of(rnd["molecule"]).get(name)
    if step and step["status"] != "closed":
        bd("close", step["id"], "--reason", reason, parse=False)


# ---------------------------------------------------------------- commands


def cmd_status(state: dict) -> None:
    r = state["round"]
    rnd = state["rounds"].get(str(r), {})
    step = current_step(state)
    print(f"round {r}{' (complete)' if not rnd or rnd.get('complete') else ''}; temperature {state['temperature']}")
    if rnd.get("probe"):
        print(f"probe: {rnd['probe']['id']} ({rnd['probe']['tag']})")
    print(f"benchmark: {', '.join(state['benchmark'])}")
    for k, v in sorted(state["rounds"].items(), key=lambda kv: int(kv[0])):
        if "bench" in v:
            print(f"  round {k}: E={v['bench']['E']:.1f} probe/ex={v['probe_energy']['per_example']:.1f} "
                  f"bench/ex={v['bench']['per_example']:.1f} temp={v['temperature']}")
    best = state.get("best") or {}
    print(f"best: {best.get('E', 'none')} (round {best.get('round', '-')})")
    if state.get("frozen"):
        print("next: search is frozen; report the best model and stop")
    elif step is None:
        print("next: uv run anneal.py begin")
    elif step == "measure":
        print("next: uv run anneal.py measure")
    elif step == "end":
        print("next: uv run anneal.py end")
    elif step == "done":
        print("next: uv run anneal.py end")
    else:
        print(f"next: dispatch the {step} step (loop.md)")


def seen_examples() -> dict[str, set[str]]:
    seen: dict[str, set[str]] = {}
    for r in bd("list", "--label", "finding", "--all", "--limit", "0"):
        for p in labels_with(r, "persona:"):
            seen.setdefault(p, set()).update(labels_with(r, "example:"))
    return seen


def cmd_begin(state: dict, dry_run: bool) -> None:
    prev = state["rounds"].get(str(state["round"]))
    if prev and not prev.get("complete"):
        rnd = prev
        print(f"round {state['round']} already begun")
        print(json.dumps({"probe": rnd["probe"], "panel": rnd["panel"]}, indent=2))
        return
    if state.get("frozen"):
        raise SystemExit("the search is frozen")
    r = state["round"] + 1
    cfg = state["config"]
    snap = json.loads((ROOT / cfg["products"]).read_text())
    tag, product = draw_probe(snap["products"], cfg["eligibility"], set(state["modeled_products"]),
                              state["drawn_tags"], state["seed"], r)
    probe = {"id": product["id"], "name": product["name"], "tag": tag, "source": product["source"],
             "website": product.get("website"), "description": product["description"]}
    panel = draw_panel(cfg["panel"]["core"], cfg["panel"]["specialists"], cfg["panel"]["sample"],
                       state["benchmark"], seen_examples(), cfg["panel"]["examples_each"], state["seed"], r)
    print(json.dumps({"round": r, "temperature": state["temperature"], "probe": probe, "panel": panel}, indent=2))
    if dry_run:
        return
    out = bd("mol", "pour", FORMULA, "--var", f"round={r}", "--var", f"probe={probe['id']}", parse=False)
    m = re.search(r"\b([a-z]+-mol-[a-z0-9]+)\b", out)
    if not m:
        raise SystemExit(f"could not find the molecule id in: {out}")
    mol = m.group(1)
    steps = steps_of(mol)
    bd("update", steps["author"]["id"], "--description",
       f"Probe: {probe['name']} ({probe['id']}), tag {tag}. Source: {probe['source']}. "
       f"Website: {probe.get('website')}. {probe['description']} Write examples/{probe['id']}.yaml. "
       "Follow loop.md, Author.", parse=False)
    reviews = {}
    for persona, examples in panel.items():
        reviews[persona] = bd("create", "--parent", steps["review"]["id"], "--type", "task",
                              "--title", f"Round {r} review: {persona}",
                              "--labels", f"phase:review,persona:{persona},round:{r}",
                              "--description", f"Persona: personas/{persona}.md. Examples: "
                              f"{', '.join([probe['id']] + examples)}. Follow loop.md, Review.",
                              "--silent", parse=False)
    state["round"] = r
    state["drawn_tags"].append(tag)
    state["modeled_products"].append(product["id"])
    state["rounds"][str(r)] = {"molecule": mol, "probe": probe, "panel": panel, "reviews": reviews,
                               "temperature": state["temperature"], "moves": {}}
    save_state(state)
    print(f"poured {mol}")


def cmd_measure(state: dict) -> None:
    r = state["round"]
    rnd = state["rounds"][str(r)]
    if current_step(state) != "measure":
        raise SystemExit(f"measure is not the current step ({current_step(state)})")
    cfg = state["config"]
    w = cfg["weights"]
    bench = measure_set(state["benchmark"], w)
    probe = measure_set([rnd["probe"]["id"]], w)
    rnd["bench"], rnd["probe_energy"] = bench, probe
    print(f"benchmark E={bench['E']:.1f} {json.dumps({k: bench[k] for k in ('P1', 'P2', 'P3', 'errors', 'size', 'departures')})}")
    print(f"probe per example={probe['per_example']:.1f}, benchmark per example={bench['per_example']:.1f}")

    prev = state["rounds"].get(str(r - 1), {})
    e_prev = None
    if "bench" in prev:
        same = measure_set(prev["bench"]["examples"], w)
        e_prev = prev["bench"]["E"]
        rnd["bench_on_prev_set"] = same["E"]
        print(f"on round {r - 1}'s benchmark: E={same['E']:.1f} (was {e_prev:.1f})")
        if same["E"] >= e_prev:
            for move, rec in prev.get("moves", {}).items():
                if rec.get("decision") == "kept uphill":
                    revert_move(move, rec, f"uphill move from round {r - 1}: benchmark energy did not fall")
                    rec["decision"] = "reverted uphill"
        rising = [v for v in (state["rounds"].get(str(r - 2), {}).get("bench", {}).get("E"), e_prev) if v is not None]
        if len(rising) == 2 and rising[0] < rising[1] <= same["E"]:
            print("energy rose for two rounds: compare with best and ask the human (loop.md, Human)")

    # Temperature for this round's moves.
    if prev.get("temperature") and "bench" in prev:
        state["temperature"] = next_temperature(prev["temperature"], probe["per_example"],
                                                bench["per_example"], cfg["reheat"])
    rnd["temperature"] = state["temperature"]
    print(f"temperature: {state['temperature']}")

    best = state.get("best")
    if best and best.get("E") is not None:
        mine = measure_set(best["examples"], w)["E"]
        better = mine < best["E"]
    else:
        mine, better = bench["E"], True
    if better:
        copy_model(BEST)
        state["best"] = {"E": mine, "round": r, "examples": bench["examples"] if not best else best["examples"],
                         "commit": git("rev-parse", "HEAD")}
        print(f"best updated: E={mine:.1f}")

    if is_frozen(state["temperature"], rnd.get("bench_on_prev_set", bench["E"]), e_prev,
                 probe["per_example"], bench["per_example"], cfg["stop"]):
        state["frozen"] = True
        print("frozen: stop and report the best model")
    save_state(state)
    close_step(state, "measure", f"E={bench['E']:.1f}, temperature {state['temperature']}")
    if state["temperature"] not in cfg["explore_at"]:
        close_step(state, "explore", f"skipped: explorer does not run at {state['temperature']}")


def copy_model(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    (dest / "harness").mkdir(parents=True)
    (dest / "review").mkdir()
    shutil.copy2(h.ERD, dest / "erd.md")
    shutil.copytree(h.RULES, dest / "harness" / "rules")
    shutil.copytree(h.EXAMPLES, dest / "review" / "examples")


def cmd_reset(_: dict) -> None:
    if not (BEST / "erd.md").exists():
        raise SystemExit("no best copy")
    shutil.copy2(BEST / "erd.md", h.ERD)
    shutil.rmtree(h.RULES)
    shutil.copytree(BEST / "harness" / "rules", h.RULES)
    shutil.rmtree(h.EXAMPLES)
    shutil.copytree(BEST / "review" / "examples", h.EXAMPLES)
    print("reset to best; review the diff and commit")


def move_sets(state: dict) -> list[str]:
    rnd = state["rounds"][str(state["round"])]
    return state["benchmark"] + [rnd["probe"]["id"]]


def cmd_move_next(state: dict) -> None:
    rnd = state["rounds"][str(state["round"])]
    allowed = state["config"]["sizes"][state["temperature"]]
    for r in bd("ready", "--label", "move", "--limit", "0"):
        sizes = labels_with(r, "size:")
        if r["id"] in rnd["moves"] or not sizes or sizes[0] not in allowed:
            continue
        print(r["id"])
        return
    print("none")


def cmd_move_start(state: dict, bead: str) -> None:
    rnd = state["rounds"][str(state["round"])]
    rnd["moves"][bead] = {"pre": mechanical(move_sets(state))}
    save_state(state)
    print(json.dumps(rnd["moves"][bead]["pre"]))


def revert_move(bead: str, rec: dict, why: str) -> None:
    shas = git("log", "--format=%H", f"--grep={bead}", f"{rec['pre']['head']}..HEAD").split()
    for sha in shas:  # newest first
        git("revert", "--no-edit", sha)
    issue = bd("show", bead)
    issue = issue[0] if isinstance(issue, list) else issue
    for r in bd("list", "--label", f"critic-of:{bead}", "--all", "--limit", "0"):
        if r["status"] != "closed":
            bd("close", r["id"], "--reason", "move reverted", parse=False)
    for fid in rec.get("resolved_ids", []):
        bd("reopen", fid, parse=False)
    bd("label", "add", bead, "move:reverted", parse=False)
    bd("comments", "add", bead, f"reverted: {why}", parse=False)
    if "finding" not in issue.get("labels", []) and issue["status"] != "closed":
        bd("close", bead, "--reason", f"reverted: {why}", parse=False)
    print(f"reverted {len(shas)} commit(s) for {bead}")


def cmd_move_judge(state: dict, bead: str, dry_run: bool) -> None:
    rnd = state["rounds"][str(state["round"])]
    rec = rnd["moves"].get(bead)
    if not rec or "pre" not in rec:
        raise SystemExit(f"run move start {bead} first")
    w = state["config"]["weights"]
    issue = bd("show", bead)
    issue = issue[0] if isinstance(issue, list) else issue
    targets = [bead] + labels_with(issue, "resolves:")
    resolved, resolved_ids = [], []
    for t in targets:
        ti = bd("show", t)
        ti = ti[0] if isinstance(ti, list) else ti
        if ti["status"] == "closed" and (ti.get("close_reason") or "").startswith("resolved by") \
                and "finding" in ti.get("labels", []):
            resolved.append(ti["priority"])
            resolved_ids.append(t)
    new = [r["priority"] for r in bd("list", "--label", f"critic-of:{bead}", "--all", "--limit", "0")
           if r["status"] != "closed"]
    post = mechanical(move_sets(state))
    d = delta_energy(resolved, new, rec["pre"], post, w)
    temp = state["temperature"]
    keep = accept(d["total"], temp, state["config"]["thresholds"])
    decision = ("kept uphill" if d["total"] > 0 else "kept") if keep else "reverted"
    print(f"ΔE = {d['total']:+.1f}  (resolved {d['resolved']:+.1f}, new {d['new']:+.1f}, errors {d['errors']:+.1f}, "
          f"size {d['size']:+.1f}, departures {d['departures']:+.1f}); threshold at {temp}: "
          f"{state['config']['thresholds'][temp]}")
    print(decision)
    if dry_run:
        return
    rec.update({"post": post, "delta": d, "decision": decision, "resolved_ids": resolved_ids})
    if keep:
        bd("label", "add", bead, "move:kept", parse=False)
        if decision == "kept uphill":
            bd("label", "add", bead, "move:uphill", parse=False)
        if "finding" not in issue.get("labels", []) and issue["status"] != "closed":
            bd("close", bead, "--reason", f"kept: ΔE {d['total']:+.1f}", parse=False)
    else:
        revert_move(bead, rec, f"ΔE {d['total']:+.1f} above the {temp} threshold")
    save_state(state)


def cmd_end(state: dict) -> None:
    r = state["round"]
    rnd = state["rounds"][str(r)]
    if current_step(state) not in ("end", "done"):
        raise SystemExit(f"end is not the current step ({current_step(state)})")
    probe = rnd["probe"]["id"]
    if probe not in state["benchmark"] and (h.EXAMPLES / f"{probe}.yaml").exists():
        state["benchmark"].append(probe)
    decisions = [m.get("decision", "pending") for m in rnd["moves"].values()]
    summary = (f"round {r}: E={rnd.get('bench', {}).get('E', 0):.1f}, temperature {rnd['temperature']}, "
               f"probe {probe} per example {rnd.get('probe_energy', {}).get('per_example', 0):.1f}; moves "
               + ", ".join(f"{d} {decisions.count(d)}" for d in sorted(set(decisions))))
    rnd["complete"] = True
    rnd["summary"] = summary
    save_state(state)
    bd("update", rnd["molecule"], "--notes", summary, parse=False)
    close_step(state, "end", summary)
    print(summary)


def main() -> None:
    p = argparse.ArgumentParser(prog="anneal", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    b = sub.add_parser("begin")
    b.add_argument("--dry-run", action="store_true", help="print the draw without writing state or pouring")
    sub.add_parser("measure")
    mv = sub.add_parser("move")
    mv.add_argument("action", choices=["next", "start", "judge"])
    mv.add_argument("bead", nargs="?")
    mv.add_argument("--dry-run", action="store_true", help="judge: print the arithmetic without acting")
    sub.add_parser("end")
    sub.add_parser("reset-to-best")
    sub.add_parser("energy", help="print the energy of the current model on the benchmark")
    args = p.parse_args()
    state = load_state()
    if args.cmd == "status":
        cmd_status(state)
    elif args.cmd == "begin":
        cmd_begin(state, args.dry_run)
    elif args.cmd == "measure":
        cmd_measure(state)
    elif args.cmd == "move":
        if args.action == "next":
            cmd_move_next(state)
        elif not args.bead:
            sys.exit("move start|judge needs a bead id")
        elif args.action == "start":
            cmd_move_start(state, args.bead)
        else:
            cmd_move_judge(state, args.bead, args.dry_run)
    elif args.cmd == "end":
        cmd_end(state)
    elif args.cmd == "reset-to-best":
        cmd_reset(state)
    elif args.cmd == "energy":
        e = measure_set(state["benchmark"], state["config"]["weights"])
        print(json.dumps({**e, **model_size()}, indent=2))


if __name__ == "__main__":
    main()
