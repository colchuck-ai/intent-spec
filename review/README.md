# Review

The model is improved by simulated annealing (see the [main README](../README.md#how-we-get-there)). Each round draws a fresh probe product and a sampled panel of reviewer personas. The panel reviews the probe and some benchmark examples, and the accepted findings become moves that are kept or reverted by their change in energy. Beads tracks every round, `../anneal/state.json` holds the annealing state, `../harness/anneal.py` does every mechanical step, and subagents do the rest.

- `loop.md`: the runbook, covering the orchestrator, author, reviewers, triage, explorer, move runner, fixer, critic and humans
- `prompt.md`: the shared review prompt
- `personas/`: the 13 reviewer profiles: six core, seven sampled specialists
- `examples/`: the benchmark examples and the probes; `examples/invalid/` holds one rule-breaking document per rule
- `.beads/formulas/anneal-round.formula.toml`: the round template, poured by `anneal.py begin`
