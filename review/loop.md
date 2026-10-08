# Annealing loop

The model is improved by simulated annealing, as the [README](../README.md#how-we-get-there) explains. This file is the runbook: who does what, in what order, and which commands make each mechanical step deterministic.

Each round is a beads molecule poured from the `anneal-round` formula. Beads hold findings, moves and decisions. `../anneal/state.json` holds the annealing state. Git holds both. The orchestrator keeps nothing in memory, so the loop can stop at any point and resume from git and beads alone.

## Determinism

The harness (`uv run anneal.py <command>` from `../harness`) does every step that doesn't need judgment: the draws, the panel sample, energy, the threshold decision, the temperature, the best copy and the stop check. Agents do only what needs judgment: writing examples, reviewing, triage, proposing moves, making fixes and re-reviewing them. A human decides anything that touches an invariant or departs from an established model.

Never compute energy, pick a product or reviewer, or decide keep or revert by hand. If a command is missing or fails, stop and report.

### Commands

| Command | Does |
|---|---|
| `status` | Prints the round, step, temperature, energy history, best energy and the next action. |
| `begin` | Starts the next round: draws the probe and the panel with the round's seed, writes them to `state.json`, pours the molecule and creates one review step per panelist. Re-running it for a begun round prints the same draw. |
| `measure` | After triage: computes energy on the benchmark and on the probe, applies the uphill rule to last round's moves, sets this round's temperature, updates the best copy and runs the stop check. Prints every decision. |
| `move start <bead>` | Before a fixer starts: records the size, departures and harness errors at the current commit. |
| `move judge <bead>` | After the fixer and critic: computes ΔE, compares it with the threshold, and keeps or reverts the move's commits. Prints `kept`, `kept uphill` or `reverted`, with the arithmetic. |
| `end` | Closes the round: the probe joins the benchmark, the round's numbers go into `state.json`, and the summary goes onto the molecule. |
| `reset-to-best` | Copies `../anneal/best/` over the current model, rules and examples. Run it only on a human's decision. |

### Energy

`measure` and `move judge` compute energy the same way:

```
E(S) = 10·P1 + 3·P2 + 1·P3     open findings with triage:accept on examples in S, deferred included
     + 10·errors               harness errors on examples in S
     + 0.5·size                entities + links + rules in ../erd.md
     + 50·departures           `%% departure` lines in ../erd.md
```

S is a set of examples. Comparisons between rounds always use the same S, the benchmark as it stood at the earlier round, so that adding a probe never looks like progress or regress. Rejected and duplicate findings count for nothing, so triage rejects anything out of scope instead of deferring it.

A departure is any place the model leaves JTBD, C4, DFD3 or HCGF. Each one is declared in `../erd.md` as `%% departure DEP-n: <model>: <what changed> because <evidence>`, added by the move that makes it. An undeclared departure is a P1 finding.

### Temperature

| Temperature | Threshold: keep when ΔE is | Move sizes allowed | Explorer |
|---|---|---|---|
| hot | ≤ +10 | local, additive, structural, unifying | yes |
| warm | ≤ +3 | local, additive, structural | yes |
| cool | ≤ 0 | local, additive | no |
| frozen | < 0 | local | no |

The search starts hot. `measure` cools one step each round, or reheats one step (never above hot) when the probe's energy per example exceeds 1.5 times the benchmark's. It stops the search when the temperature is frozen, benchmark energy didn't fall since the previous round, and the probe's energy per example is within 1.25 times the benchmark's. These parameters live in `state.json` under `config`, and changing them is a process change.

### Probes

Probes come from `../anneal/products-2026-10-08.json`, a snapshot of [awesome-selfhosted-data](https://github.com/awesome-selfhosted/awesome-selfhosted-data) at a pinned commit (CC BY-SA 3.0). A product is eligible when it is not archived, has a source code URL, has at least 1,000 stars, was updated within a year of the snapshot and isn't already an example. `begin` first draws the next tag from a seeded shuffle of the tags that still have eligible products, then draws a product within that tag. Products are drawn without replacement. The tags stratify the draw, so probes spread across domains instead of following popularity.

### Panel

The core reviewers review every round: product-management, architecture, threat-modeling, governance, agent-user and simplicity-advocate. `begin` adds a seeded sample of three specialists from jobs-to-be-done, job-executor, devops, risk-management, hcgf, compliance and model-portability. Every panelist reviews the probe and two benchmark examples drawn for them, preferring examples they haven't seen.

## Labels

| Label | On | Meaning |
|---|---|---|
| `finding`, `round:<n>`, `persona:<p>`, `example:<e>`, `kind:<gap\|friction\|bad\|excess>`, `goal:<simple\|complete\|accurate\|composable\|agent-friendly>` | findings | Who found what, where, and which goal it fails |
| `triage:accept`, `triage:defer`, `triage:human` | findings | The triage decision |
| `move`, `size:<local\|additive\|structural\|unifying>`, `source:<finding\|explorer>` | moves | An accepted finding becomes a move when triage gives it a size. Explorer moves are created as moves. |
| `critic-of:<move>` | findings | Filed by the critic against a move |
| `resolves:<finding>` | moves | Extra findings a move claims to resolve, beyond itself |
| `move:kept`, `move:uphill`, `move:reverted` | moves | Set by `move judge` |

## Orchestrator

Keep your own context small. Subagents reply with one line, and bead content stays in beads.

Keep `../journal.md` current: it is raw material for a blog post about how intent-spec was built. Append an entry, following the format at the top of that file, when a human decides a gate, an invariant or the process changes, the temperature reheats, the model is reset to best, an uphill move is reverted, a result challenges the approach, or a round ends. Commit it on main.

On every start or resume:

```bash
cd ../harness
docker compose up -d        # on this machine: DOCKER_CONTEXT=desktop-linux docker compose up -d
uv run harness.py load      # rebuild the graph from the YAML in git
uv run anneal.py status
```

Then check these in order:

1. **Uncommitted changes outside `.beads/` and `.obsidian/`:** stop and ask the human. Never discard changes.
2. **Your context is nearing 25%:** pause and ask the human whether to stop. Resuming in a fresh session loses nothing.
3. **Otherwise, act on the step `status` names:**
   - **No round open:** run `uv run anneal.py begin`.
   - **Author ready:** dispatch one subagent with the Author section.
   - **Review steps ready:** dispatch one subagent per review step, in parallel, with the Review section.
   - **Triage ready:** dispatch one subagent with the Triage section.
   - **Measure ready:** run `uv run anneal.py measure`. If it says the search is frozen, report the best model's energy and stop. If it says to compare with best, stop and show the human both energies.
   - **Explore ready** (hot or warm only; `measure` skips it otherwise): dispatch one subagent with the Explorer section.
   - **Anneal ready:** dispatch one subagent with the Move runner section.
   - **End ready:** run `uv run anneal.py end`, append the round to the journal, and start again from the top.

Open human gates don't stop the loop. Gated moves wait, and the move runner skips them. Report open gates at every step boundary, with the moves they block.

## Author

You write the probe example that `begin` drew. The step's description names the product and its tag.

1. Claim the step. Read `../README.md`, `../erd.md`, `examples/README.md` and two existing examples for style.
2. Research the product from its own public material: website, docs, source repository, security and privacy pages. Cite sources in the example's comments. Model what the product intends, not what you guess.
3. Write `examples/<id>.yaml` at the stage that fits the product. End it with a "Couldn't express" section, as the other examples do. Add it to `examples/README.md`.
4. Run `uv run harness.py load <id>` and `uv run harness.py check <id>` from `../harness`. Fix the example, not the model, until there are no errors. Leave warnings: they are evidence for reviewers.
5. Commit on main with the message `<step>: probe <id>`, close the step, and reply with the number of warnings.

## Review

You are given one review step. Its description names your persona and examples.

1. Claim the step. If it already has child findings from an interrupted run, close each with the reason "superseded by rerun".
2. Read `../README.md`, `../erd.md`, `prompt.md`, your persona, `examples/README.md` and your examples. Run `uv run harness.py check <your examples>` and query the graph as evidence. Don't file what the checker already reports.
3. Review as `prompt.md` describes, then file each finding as a child of the step:
   ```bash
   bd create --parent <step> --type task --priority P<1-3> \
     --labels finding,round:<n>,persona:<persona>,kind:<kind>,goal:<goal>,example:<name> \
     --title "<target>: <claim>" \
     --description "Target: ...
   Evidence: ...
   Proposal: ..."
   ```
   Use one `example:` label for each example the finding draws on. If the finding is about a rule, plant the violation in a scratch copy and include the YAML, so it can become a regression test.
4. Put your "Good" observations in the step's notes. They are not findings.
5. Close the step and reply with the number of findings you filed.

## Triage

1. Claim the triage step. Work only on this round's findings, and `critic-of:` findings left open from earlier rounds, that have no `triage:` label, so a rerun continues where the last one stopped.
2. Look for earlier decisions on the same idea among closed findings (`bd list --label finding --status closed --json`). Reject repeats of earlier rejections unless the finding brings new evidence.
3. Decide each finding:
   - **Duplicate:** close it with "duplicate of <id>". Raise the survivor's priority if the duplicate's was higher, and copy over its persona and example labels.
   - **Reject:** close it with "rejected: <why>". Anything out of scope (INV-1) or unjustified by an example (INV-10) is rejected, not deferred.
   - **Defer:** add `triage:defer` and run `bd defer <id>` with a reason. Deferred findings still count towards energy.
   - **Accept:** add `triage:accept`, `move`, `source:finding` and a `size:` label for the smallest change that would resolve it. The move runner skips moves whose size the round's temperature doesn't allow.
   - **Needs a human:** accept it as above, add `triage:human`, and run `bd gate create --type=human --blocks <id> --reason "<INV-n, departure or process>: <decision needed>"`. Use this only if the move would create, change, delete or contradict an invariant, add a departure, or change this process (personas, prompt, formula, this file, `state.json` config).
4. **Plan the moves.** Where accepted findings overlap (same entity, link, rule or example section):
   - **One builds on another:** `bd dep add <later> <earlier>`, with a comment "after <earlier>: <why>". Put structural moves before additive ones.
   - **Same area, no order:** `bd dep add <a> <b> --type related`.
   - **Same change:** treat them as duplicates.

   Don't create cycles, and skip dependencies that already exist.
5. Close the step and reply with counts for each decision and the number of dependencies added.

## Explorer

You propose moves that no finding asked for. The search only runs you while hot or warm.

1. Claim the step. Read `../README.md`, `../erd.md`, the round's findings and `uv run anneal.py status`.
2. Propose up to three moves the temperature allows, favouring moves that could take the model somewhere the findings never would:
   - Remove an entity or link and see whether the examples can still say everything.
   - Merge two entities that mean the same thing across disciplines (INV-12).
   - Split an entity that is doing two jobs.
   - Re-anchor something to what its source model actually says (INV-9).
3. Test each one in a scratch copy first: plant it, load the examples and check them. Drop it if it breaks something a fixer couldn't repair within the move.
4. File each surviving move as a child of the step with labels `move,source:explorer,size:<size>,round:<n>`. Its description gives the change, the scratch-copy evidence and the energy you expect it to save. Gate it as Triage step 3 describes if it adds a departure or touches an invariant.
5. Close the step and reply with the number of moves filed.

## Move runner

You run the round's moves one at a time so the orchestrator doesn't have to.

1. Loop: take the first bead from `bd ready --label move --label round:<n>` whose size the temperature allows and that no open gate blocks. If there is none, close the anneal step and stop.
2. Run `uv run anneal.py move start <bead>`.
3. Dispatch one fixer subagent with the Fix section and wait. Then dispatch one critic subagent with the Critic section and wait. Never run two moves at once.
4. Run `uv run anneal.py move judge <bead>`. It keeps or reverts the move.
5. Check that the working tree is clean apart from `.beads/`. If it isn't, or a fixer escalated, stop.
6. When the loop ends, reply with one line: "kept <n> (uphill <u>), reverted <r>; stopped: <reason or queue empty>; escalated: <ids>".

## Fix

You are given one move.

1. Claim it. Read it, its comments, any resolved gate, and every bead it depends on or relates to (`bd dep list <id>` and `bd dep list <id> --direction=up`), including the commits that resolved them. A human's decision is recorded as a comment, and it overrides the proposal. Build on earlier moves and never undo a kept one.
2. Make the change the move's size describes, and no larger, across `../erd.md`, `../harness/rules/` and `examples/`. Keep the examples consistent with the ERD. If the move departs from JTBD, C4, DFD3 or HCGF, it needs a resolved gate, and you declare the departure in `../erd.md`. If it changes a rule's meaning, update its `.cypher` file and its invalid example in `examples/invalid/`.
3. If the change turns out to need a larger size, an invariant change or an undeclared departure, open a gate as Triage step 3 describes and reply "escalated". Leave any edits uncommitted; the orchestrator will see the dirty tree and bring in the human.
4. Verify from `../harness`: run `uv run harness.py load`, `uv run harness.py check` and `uv run harness.py test`. Nothing new may fail, and `uv run harness.py export` must leave no unintended diff.
5. Commit on main with the message `<id>: <summary>`. Don't close the move: `move judge` does. Reply "done" or "escalated".

## Critic

You re-review one move after its fixer commits it. You estimate the part of ΔE that needs judgment, and you do it by filing beads, not by arithmetic.

1. Read the move, its commit (`git log --grep <id>`), and the findings it targets: itself, plus any `resolves:` labels.
2. Take the persona that filed the target finding. For an explorer move, take the simplicity advocate and the persona closest to the changed area. Re-review every example the commit touched, plus the probe.
3. For each target finding, decide whether the move resolves it. If it does, close it with "resolved by <sha>". If it doesn't, comment why and leave it open.
4. File anything new the move broke or made awkward as a finding with the label `critic-of:<move>`, along with the usual finding labels. Don't file things that were already wrong before the move.
5. Reply with "resolved <n>, new <m>".

## Human

To decide a gated move:

- **To reject it:** resolve the gate, then close the move with a reason.
- **To approve it, with or without changes:** add your decision as a comment with `bd comments add <id> "..."`, then run `bd gate resolve <gate>`. The move becomes ready for the move runner in the current or next round.

To reset the model to the best copy after `measure` asks for a comparison, run `uv run anneal.py reset-to-best` and commit. To change the energy weights, the temperature thresholds or the schedule, edit `config` in `../anneal/state.json` and record why in the journal.
