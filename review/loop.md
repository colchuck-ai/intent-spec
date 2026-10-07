# Review loop

Each round is a beads molecule poured from the `review-round` formula:

```bash
bd mol pour review-round --var round=<n>
```

Beads hold all the state. The orchestrating session dispatches subagents and reads bead state. It never holds findings or reasoning itself, so the loop can stop at any point and resume from beads and git alone.

## Orchestrator

Keep your own context small. Subagents return one-line receipts, and bead content stays in beads.

On every start or resume, check these in order:

1. **Working tree has uncommitted changes outside `.beads/` and `.obsidian/`:** stop and ask the human. Never discard changes. Beads and Obsidian update their own files.
2. **`bd gate list` shows an open human gate:** stop and show the human the gates and the findings they block.
3. **Your context is nearing 30%:** pause and ask the human whether to stop. Resuming in a fresh session loses nothing.
4. **Otherwise, run `bd mol current <round>` and act on the first match.** Read step state from the molecule, not from `phase:` labels: findings inherit their parent step's labels, so a label query returns findings too.
   - **Review steps ready or in progress:** dispatch one subagent per step, in parallel. Give it the step ID and tell it to follow the Review section below.
   - **Triage ready:** dispatch one subagent with the Triage section.
   - **Fix ready:** run `bd ready --label triage:accept`, then dispatch one fixer at a time, each with one bead ID and the Fix section. When no open finding labelled `triage:accept` remains, close the fix step.
   - **Summarize ready:** dispatch one subagent with the Summarize section.
   - **All steps closed:** report the summary and stop.

## Review

You are given one review step. Its description names your persona and examples.

1. Claim the step with `bd update <step> --claim`. If it already has child findings from an interrupted run, close each one with the reason "superseded by rerun".
2. Read `../README.md`, `../erd.md`, `prompt.md`, your persona, `examples/README.md` and your examples.
3. Review as `prompt.md` describes, then file each finding as a child of the step:
   ```bash
   bd create --parent <step> --type task --priority P<1-3> \
     --labels finding,round:<n>,persona:<persona>,kind:<gap|friction|bad|excess>,example:<name> \
     --title "<target>: <claim>" \
     --description "Target: ...
   Evidence: ...
   Proposal: ..."
   ```
   Use one `example:` label for each example the finding draws on.
4. Put your "Good" observations in the step's notes with `bd update <step> --notes "..."`. They are not findings.
5. Close the step, then reply with only the number of findings you filed.

## Triage

1. Claim the triage step. Work only on findings labelled `finding,round:<n>` that have no `triage:` label, so a rerun continues where the last one stopped.
2. Before deciding, look for earlier decisions on the same idea among closed findings from previous rounds. Their close reasons are in `bd list --label finding --status closed --json`.
3. Decide each finding:
   - **Duplicate:** close it with the reason "duplicate of <id>". Raise the surviving finding's priority if the duplicate was higher, and add the duplicate's persona and example labels to it.
   - **Reject:** close it with the reason "rejected: <why>". Reject repeats of earlier rejections unless the finding brings new evidence.
   - **Defer:** add the label `triage:defer` and run `bd defer <id>` with a reason.
   - **Accept:** add the label `triage:accept`.
   - **Needs a human:** add the labels `triage:accept` and `triage:human`, then run `bd gate create --type=human --blocks <id> --reason "<INV-n or process>: <decision needed>"`. Use this only if accepting the finding would:
     - create, change or delete an invariant in `../README.md`,
     - contradict an invariant, or
     - change the review process (personas, prompt, formula, this file).
4. **Plan the fixes.** Compare the open accepted findings for overlap: the same entity, link, rule or example section.
   - **One fix builds on another:** run `bd dep add <later> <earlier>`, then comment on the later finding with "after <earlier>: <why>". Put structural changes (renames, flattening, removed or moved entities, edits across every example) before additive ones.
   - **Same area, no order:** run `bd dep add <a> <b> --type related`.
   - **Same change:** treat them as duplicates (step 3).
   - Don't create cycles. Two findings that conflict need one decision, so record it, or open a human gate if an invariant is involved.

   Planning must be safe to rerun, so skip dependencies that already exist.
5. When no untriaged findings remain and the plan is done, close the step. Reply with counts for each decision and the number of dependencies added.

## Fix

You are given one accepted finding.

1. Claim it. Check `git log --grep <id>`: if a commit already exists, close the finding with the reason "fixed in <sha>" and stop.
2. Read the finding, its comments, any resolved gate, and every finding it depends on or is related to (`bd dep list <id>` and `bd dep list <id> --direction=up`), including the commits that fixed them. A human's decision is recorded as a comment on the finding, and it overrides the proposal. Build on earlier fixes and never undo them. If this finding has become obsolete, close it with a reason instead of committing.
3. Make the smallest change that resolves the finding across `../erd.md`, `examples/` and, only when a gate approved it, `../README.md`. Keep the examples consistent with the ERD.
4. If the change turns out to touch an invariant or the review process, create a human gate on the finding as Triage step 3 describes and reply "escalated". Leave any edits you've already made uncommitted; the orchestrator will see the dirty tree and bring in the human.
5. Commit on main with the message `<id>: <summary>`, then close the finding with the reason "fixed in <sha>". Reply with "fixed" or "escalated".

## Summarize

1. Claim the step. Count this round's findings by priority (`round:<n>`) and by decision, and compare them with the previous round.
2. Apply the stopping rule: stop when a round has no new P1 findings and fewer P2 findings than the round before.
3. Write the summary to the step's notes: counts, the stopping-rule result, notable rejections and open deferrals. Close the step and reply with the stopping-rule result.

## Human

To decide a gated finding:

- **To reject it:** resolve the gate, then close the finding with a reason. bd refuses to close a finding while its gate is open.
- **To approve it, with or without changes:** add your decision as a comment with `bd comments add <id> "..."`, then run `bd gate resolve <gate>`. The finding becomes ready for a fixer.
