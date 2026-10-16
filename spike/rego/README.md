# Rego spike (review-ezo.2)

Throwaway port of five hard rules from `harness/rules/*.cypher` to Rego, to decide go/no-go on ADR-001 before the full port. Not the spec layout: phase 2a sets that up.

There are two variants of the same rules. `rules/` (**scoped**) is the first port, over ADR-001's `{document, imports: {alias: doc}}`: each rule resolves references itself. `resolved/` (**resolve-then-check**) resolves once, into a graph, and the rules read only the graph. See [Resolve-then-check](#resolve-then-check) for the comparison.

```bash
brew install opa                                                   # 1.21.2
uv run --no-project --python 3.12 --with ruamel.yaml python spike/rego/run.py resolved   # or: scoped
opa test spike/rego/resolved spike/rego/model.json -v              # or: spike/rego/rules
cd harness && uv run python ../spike/rego/gen_model.py             # regenerate model.json from erd.md
```

| File | What |
|---|---|
| `rules/lib/ref.rego` | Scopes, the id index, `resolve(scope, ref)`, DOC-2 `stage`, every link in the document |
| `rules/lib/report.rego` | Collects `violation` from every `data.intent.rules.*` package, applies ruleWaivers, splits findings and waived |
| `rules/{grc,dfd,risk,ref}.rego` | One package per area; each rule is one `violation` body with OPA METADATA (title = ID, description, custom.severity, custom.hint) |
| `rules/spike_test.rego` | `opa test` cases for GRC-31 on its own and for waivers |
| `model.json` | Item types and link fields, generated from erd.md (stand-in for the JSON Schema) |
| `resolved/lib/graph.rego` | Resolve: every fetched document into `items[<doc>:<id>]` with resolved `links` and `stage`; reports REF-1 |
| `resolved/{grc,dfd,risk,ref}.rego`, `resolved/lib/report.rego`, `resolved/spike_test.rego` | The same rules, report and tests, over the graph |
| `fixtures/` | `GRC-10-transitive` (a baseline two imports away) and `transitive-adopted` (the same, adopted, through a diamond), with their governance documents in `fixtures/lib/` |
| `run.py` | Builds the variant's input per document, runs `opa eval`, compares with `# breaks:`/`# also:` |

## Results (2026-10-15)

`run.py` runs all four reporting rules over every example: 8 valid and all 96 invalid. A document passes when the spike's rules report exactly the `(rule, pointer)` pairs its header lists for them, and nothing on valid documents. **104 passed, 0 failed.**

| Rule | Invalid example | Fires at | Elsewhere |
|---|---|---|---|
| GRC-10 | `GRC-10.yaml` | `/products/p` ✓ | nothing |
| GRC-10 | `GRC-10-import.yaml` (profile in `../shiftly-governance.yaml`) | `/products/p` ✓ | |
| GRC-31 | none (derived, reports nothing) | 5 unit tests: import chain, exclude narrowing only importers, cycle, GRC-10 per control, alias adoption | n/a |
| DFD-8 | `DFD-8.yaml` | `/dataFlows/f` ✓ | nothing |
| RISK-4 | `RISK-4.yaml` | `/threats/t` ✓ | nothing |
| REF-3 | `REF-3.yaml` | `/metrics/m` ✓ | nothing |
| REF-3 | `REF-3-import.yaml` (stage from `../shiftly.yaml`, DOC-2) | `/metrics/m` ✓ | |

Not vacuous: the valid examples use every rule's input (products select profiles in 5 of them, threats with appliesTo in 3, flows that represent relationships in 4, ratified documents in 7). Deleting openemr's adoptions and threat reviews makes GRC-10 fire 18 times and RISK-4 29 times. Evaluating openemr (582 lines) takes 0.12 s, including `opa` startup.

## Readability

- A rule body reads as a list of conditions: `some id, flow in input.document.dataFlows`, `relationship := input.document.relationships[rid]`, `not represents_end(e, relationship)`. Excluding comments and metadata, the rule bodies are about as long as the Cypher (REF-3 7 lines vs 10, RISK-4 13 vs 11, DFD-8 11 vs 8). GRC-10 is 9 lines plus about 35 lines of GRC-31 helpers, against 16 lines of Cypher. The Cypher inlines GRC-31; the Rego names it as its own derived rule.
- Cypher's path patterns are more compact. `(e)-[:REPRESENTS]->(x)<-[:IN*0..]-()<-[:LEAVES|ENTERS]-(r)` becomes an explicit containment adjacency map plus `graph.reachable`.
- Without a graph database, references are plain strings, so every hop goes through `ref.resolve(scope, ref)`. The library hides the details, and type checks become `p.key == "profiles"` where Cypher used `:Profile`.
- The tooling helps. `opa check --strict` caught an unused argument, `opa fmt` keeps the style uniform, and `opa test` gives derived rules and waivers their own tests. Metadata is attached to each `violation` body, so one package can hold many rules, each with its own ID, severity and hint, and `rego.metadata.rule()` returns that metadata to the finding.

## ruleWaivers

Waivers are handled once, in `report.rego`. Rules know nothing about them. A finding is waived when its severity is `warning` and the item at its pointer has `ruleWaivers[<rule ID>]`. `report.waived` carries the rationale, and `report.findings` holds the rest. An error is never waived, because DOC-3 reports any waiver of an error rule. This matches the harness. None of the five rules is a warning, so `test_waiver_applies_to_warning_only` checks the path with a stand-in warning rule and error rule injected through `with data.intent.rules`. One constraint: the lookup reads the pointer as `/<type>/<id>`, so a rule that reports at a field pointer could not be waived. Today every rule reports at the item.

## Imports

The caller resolves imports. `run.py` builds `{document, imports: {alias: doc}}`, finding each imported file beside the document or among the examples by file stem, as the harness does. In the rules, ids are read relative to the document they appear in: `resolve("", "gov:x")` goes into import `gov`, while a selection's `names` inside `gov` resolves inside `gov`. GRC-10-import and REF-3-import both pass that way. Coverage stays local (REF-5) because rules iterate `input.document` only.

## Expressiveness gaps and decisions for phase 2

1. **Transitive imports (decision needed).** With the flat shape, an `alias:id` written inside an imported document names one of *that* document's imports, and the input doesn't include those. A profile in `gov` that imports `corp:baseline` therefore can't be followed, and GRC-31 stops one hop out. No example needs this yet; shiftly-governance has no imports. Options: (a) a recursive shape, `imports: {alias: {document, imports}}`, where `resolve` takes a path of aliases; (b) flat but keyed by document id, plus a per-document alias map. Recommendation: (a). It is the same idea one level down, and the caller already walks imports recursively.
2. **No recursive rules.** GRC-31 ("includes when it, or a profile it imports, includes it, and it does not exclude it") can't be written as stated. It is computed per control as reachability (`graph.reachable`) over the import graph with that control's excluders removed. It is equivalent, terminates on cycles and is tested, but it is less direct than the definition. Expect the same pattern for nested trust boundaries and containment closures.
3. **Rules need link metadata.** REF-3 has to know which fields of each type are links, and which may target an external reference. The spike generates `model.json` from erd.md. In phase 2b the JSON Schema must provide this, for example a shared `$defs/reference` that link fields `$ref`, with `data.model` generated from the schema at build time.
4. **Loader behaviour sits outside Rego.** Unquoted YAML dates must stay strings (`run.py` uses `default=str`; a core should use the YAML 1.2 core schema), and duplicate keys are rejected by the parser. Both belong in the core's conformance notes, not the rules.
5. **One small divergence.** The Cypher GRC-10 still counted an imported control that resolved to nothing (an `:Imported` stub). The Rego skips it and leaves it to REF-1. No example tells the two apart.
6. **Derived rules have no conformance case.** GRC-31 reports nothing on its own, so the suite can't test it. `opa test` files should ship in `rules/draft/` next to the rules.

## Recommendation

**Go.** All five rules ported, and every example matches. The hardest parts (closure over profile imports, cross-document resolution, containment chains, waivers) each fit in a few lines over a small shared library. Before the full port (phase 2c), decide gap 1 and settle gap 3 in the schema work (2b).

## Resolve-then-check

The first port showed most of the gaps above coming from one design choice: rules ran on the authoring format, where references are strings, aliases are local to their document and links are ordinary fields. In the harness, those ~110 lines of loading were done by `harness.py` before any Cypher ran. The second variant moves that work into one Rego package that every rule reads.

**Input.** `{document: <id>, documents: {<id>: doc}, aliases: {<id>: {<alias>: <id>}}}`. The caller fetches the whole import closure, one version per document id (`run.py` stops with an error on two versions of one document), and records which fetched document each alias names. That is the same walk it already did to fetch the imports.

**Resolve** (`resolved/lib/graph.rego`, 58 lines of code). Every item of every fetched document becomes `items["<doc>:<id>"] = {doc, type, id, stage, item, links: [{verb, to, ref}]}`. Stage is resolved (DOC-2) and absent on external references. Every link's `to` is the global id of an item, because a reference that names nothing is not a link: it is a REF-1 finding. Only this package reads aliases, raw link fields or `data.model`. **Check:** if REF-1 found anything, the report holds only those findings, as a compiler stops after name resolution. Otherwise it holds every rule's findings.

### Results

| | scoped | resolved |
|---|---|---|
| 104 examples (8 valid, 96 invalid) | pass | pass |
| `fixtures/GRC-10-transitive` | **FAIL** (misses GRC-10: silent false negative) | pass |
| `fixtures/transitive-adopted` (diamond) | pass | pass |
| REF-1 (3 invalid examples) | not ported | ported in the resolve step, pass |
| `opa test` (GRC-31, waivers) | 6/6 | 6/6 |
| openemr, findings / time | 0 / 0.02 s | 0 / 0.02 s |

### What the rules look like

Lines of code (no comments or blanks): GRC 41 → 31, DFD 23 → 18, RISK 27 → 26, REF 12 → 12. The resolve step (58) is bigger than the scoped helper library (33) because it now does everything, REF-1 included. Mentions of scope, `split`, `contains` or `refs` in the rules: 19 → 0.

DFD-8, scoped:

```rego
some rid in ref.refs(flow, "represents")
relationship := input.document.relationships[rid]
some eid in ref.refs(flow, "connects")
e := local(eid).item

# REF-2/REF-5: skip ends and relationship ends that are imported or unresolved
every x in ref.refs(e, "represents") { local(x) }
every z in ends(relationship) { local(z) }

not represents_end(e, relationship)
```

DFD-8, resolved:

```rego
some relationship in g.out(flow, "represents")
some e in g.out(flow, "connects")
not represents_end(e, relationship)
```

REF-3, resolved: a ratified local item, one of its links, a proposed target. The import case needs no code of its own.

```rego
some s, item in g.items
g.local(s)
item.stage == "ratified"
some l in item.links
g.items[l.to].stage == "proposed"
```

### Behaviour changes (decisions)

1. **Rules stop at resolution errors.** Without this, one bad reference cascades: pointing openemr's `p-clinical` at a missing system gave 1 REF-1 plus 5 DFD-8 findings, because the broken link is missing from the graph. With it, only REF-1 is reported. The cost: a document with a typo shows nothing else until the typo is fixed. The alternative, every rule skipping items with broken links, is the scoped variant's guards again.
2. **DFD-8 now follows imported elements.** The scoped port, like the Cypher, skipped a flow end or relationship end that was imported. With a graph, containment chains into imported documents are just edges, so the check simply runs. REF-5 confines *coverage* rules to the checked document, and they still do (`g.local_of`), but DFD-8 is not a coverage rule. No example tells the two behaviours apart.
3. **An import the caller could not fetch** still resolves nothing and is not reported, as in the harness. Since the caller must now provide the closure, an unfetched import could instead be a resolution error of its own.
4. **One version per document in a closure.** Two imports that reach different versions of one document are a caller error. Today's examples never do this; the imports must already share a major version.

### What it does not fix

GRC-31 is still reachability rather than recursion (gap 2): that comes from profile excludes, not imports. Loader behaviour (gap 4) still belongs to the core. The link table (gap 3) is still needed, but only by the resolve step, so it has one consumer to design for in phase 2b.

### Recommendation

Adopt resolve-then-check for phase 2: amend ADR-001's input contract to the shape above, make the graph package the only reader of aliases and link fields, and port the other 83 rules against `g.items` / `g.out` / `g.local_of`. Decide changes 1–3 above first.
