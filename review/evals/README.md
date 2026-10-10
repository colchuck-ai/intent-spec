# Evals

Fixed rubrics for the parts of `../../model.md` that need judgment. `harness.py lint` checks the file's shape; these check its meaning.

Each round, `uv run anneal.py eval` (from `../../harness`) lists the elements added or changed since the best copy. An eval agent applies every rubric here to each listed element and files each failure as a finding (see `../loop.md`, Eval). The rubric text is fixed, so the same element gets the same questions every time.

Every rubric answers in the same format, one block per element:

```
<RUBRIC> <ELEMENT>: pass | fail
evidence: "<quoted text from model.md, or from the cited source>"
why: <one sentence; required on fail>
```

A failure is filed with `--labels finding,source:eval,eval:<rubric>,round:<n>,goal:<goal>` and the rubric's priority. Quote the evidence; a failure without a quote is not filed.

| Rubric | Checks | Goal | Priority |
|---|---|---|---|
| [definition](definition.md) | The definition defines, rather than restating the name | accurate | P3 |
| [placement](placement.md) | Each rule sits under the element it is checked from, and the element under the right area | agent-friendly | P3 |
| [rule-query](rule-query.md) | The Cypher query means what the rule's statement says | accurate | P2 |
| [anchor](anchor.md) | The Anchor word matches the source model's own definition | accurate | P2 |
| [link-reading](link-reading.md) | "<dependent> <verb> <anchor>" reads as a true sentence | simple | P3 |
| [one-concept](one-concept.md) | No other element means the same thing (INV-12) | simple | P2 |
