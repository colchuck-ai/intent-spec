# Review

An expert panel reviews intent-spec through example documents. Its findings are filed in beads, triaged, and the accepted ones are applied to the model.

1. Write or update the examples in `examples/`.
2. Each persona in `personas/` reviews its assigned examples using `prompt.md`.
3. File each finding as a bead.
4. Triage: merge duplicates, then accept, reject or defer. A rejection records why.
5. Apply accepted changes to the ERD, schema, rules and examples together.

Stop when a round produces no new P1 findings and the number of P2s keeps falling.
