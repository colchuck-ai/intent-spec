# Review prompt

You are reviewing intent-spec, a unified data model for describing a software product across product management, engineering, security, and governance, risk and compliance: its entities, the links between them and the rules they obey. Read `README.md` for its goals and invariants and `model.md` for the model. Then read your persona and the examples you were given.

The examples are YAML documents, but YAML is only a test fixture: the model is the deliverable, not the file format. Findings about the serialization (key names, pluralization, pointers, file layout) are out of scope; report what the model can or can't say.

Judge every finding against the model's five goals, and name the one it fails:

- **simple:** the fewest entities, links and rules that can still express real products.
- **complete:** able to express what many kinds of products need to say.
- **accurate:** faithful to JTBD, C4, DFD3 and HCGF, departing only where unification is worth it.
- **composable:** governance defined once and adopted by many products; one product implemented across many repos.
- **agent-friendly:** easy for agents to read, query and edit, with stable IDs and rules that say what's wrong and how to fix it.

Judge the model from your own perspective. Use the example as evidence, not as the thing under review: if the example is wrong, say whether the model made it easy to get wrong.

Report what you found under these headings, and leave out any that are empty:

- **Good:** what the model lets you express well.
- **Friction:** what you can express, but only awkwardly or with loss.
- **Gaps:** what you need to express and can't.
- **Bad:** what is wrong, misleading or ambiguous.
- **Excess:** what you would remove.

For each finding, give:

- **Priority:**
  - P1: you can't do your job with the model, or it forces a wrong model.
  - P2: a workaround exists, but it is lossy or awkward.
  - P3: naming, wording or polish.
- **Target:** the entity, link or rule it concerns.
- **Goal:** the goal it fails, as the `goal:` label.
- **Evidence:** the part of the example, or the YAML you tried to write.
- **Proposal:** the smallest change that would fix it, or "none" if you don't have one.

Fewer, stronger findings are better than many weak ones.
