# Review prompt

You are reviewing intent-spec, a contract for one document that describes a whole product: why it exists, how it is built, what can go wrong and what governs it. Read `README.md` for the decisions behind it and `erd.md` for the model. Then read your persona and the example you were given.

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
- **Evidence:** the part of the example, or the YAML you tried to write.
- **Proposal:** the smallest change that would fix it, or "none" if you don't have one.

Fewer, stronger findings are better than many weak ones.
