# Plan: spec, conformance suite and reference checker

How intent-spec moves from `erd.md` plus the Neo4j harness to the layout in [ADR-002](ADRs/002-prose-rules-and-resolution.md) and then into annealing round 3. Tracked by the beads epic `review-ezo`. Each phase below is one bead, and its scope, done-when and checkpoint are the bead's description. When the plan changes, change this file first and then the beads.

## Target layout

```
intent-spec/
  schema/draft/             JSON Schema 2020-12 for one authored document; the ERD is generated from it
  rules/draft/rules.yaml    catalog: id, area, severity, kind (rule|derived), phase (resolution|semantic), statement, hint
  spec/draft/*.md           prose chapters citing rules by ID; resolution.md defines the resolved document
  tests/draft/
    valid/                  documents that must pass
    invalid/                one document each, header expect: [{rule | schemaPath, pointer}]
    resolution/             sets of documents, each with the expected resolved document or findings
  reference/                unshipped Python checker: load, validate, resolve.py, rules/<area>.py
  anneal/  review/          annealing tooling (not shipped)
  Makefile                  make test: static checks, then the reference over the whole suite
```

A model change is one commit: catalog statement, schema, prose, test cases and reference code together. Language cores (`intent-core-python` first) are products in their own repositories. They pull in the suite at a spec tag and are never needed for annealing.

## Phases

Order: 2a → 2b → 2c → 2d → 2e (ref/doc first, then the other areas) → 3 → 4 → 5. The core can start any time after 2e.

| Phase | Bead | Title | Checkpoint |
|---|---|---|---|
| 1 | review-ezo.2 | Rego spike (close: no-go on Rego; led to ADR-002) | done |
| 2a | review-ezo.3 | Layout, rule catalog, conformance suite | |
| 2b | review-ezo.4 | JSON Schema from erd.md; ERD generated | human: review the schema |
| 2c | review-ezo.5 | Resolution chapter and resolution cases | human: review the resolved form |
| 2d | review-ezo.10 | Reference checker: loader, schema validation, resolver | |
| 2e | review-ezo.11 | Reference rules (parent of six area beads) | human: readability after ref/doc |
| 2e.1 | review-ezo.11.1 | Reference rules: ref and doc | human: readability |
| 2e.2 | review-ezo.11.2 | Reference rules: product and metric | |
| 2e.3 | review-ezo.11.3 | Reference rules: C4 | |
| 2e.4 | review-ezo.11.4 | Reference rules: DFD | |
| 2e.5 | review-ezo.11.5 | Reference rules: risk | |
| 2e.6 | review-ezo.11.6 | Reference rules: GRC | |
| 3 | review-ezo.6 | Retire the Neo4j harness; anneal.py runs make test | |
| 4 | review-ezo.7 | Docs and process | |
| 5 | review-ezo.9 | Round 3 prep, then begin round 3 | human: approve before round 3 |
| later | review-ezo.8 | intent-core-python (new repo, product) | human: confirm before creating the repo |

### 2a. Layout, rule catalog, conformance suite (review-ezo.3)

- Create `schema/draft/`, `rules/draft/`, `spec/draft/`, `tests/draft/{valid,invalid,resolution}/`, `reference/` and `departures.yaml`.
- Write `rules/draft/rules.yaml` from erd.md's `%% rule` and `%% derived` comments. That's 88 rules and 25 derived rules, each with id, area, severity, kind, statement, and a hint taken from its `harness/rules/*.cypher`.
- Tag each rule's phase. Resolution: REF-1, REF-6, GRC-15, GRC-32, DFD-14 and DOC-2. Everything else is semantic. Record any rule whose phase is unclear for the 2c checkpoint.
- Move the valid examples into `tests/draft/valid/` and the invalid ones into `tests/draft/invalid/`, turning the `# breaks:` / `# also:` lines into an `expect:` header. Move the spike's transitive and diamond fixtures into `tests/draft/resolution/`.
- Carry the "rules without a file" table (DOC-1, RISK-5, REF-2, REF-5) into the catalog as `noCase` reasons.
- `make test`, static checks only:
  - the catalog is well-formed
  - every `expect` names a catalog rule or a schema path
  - every rule has a case or a `noCase` reason
- Keep the harness working on the moved files until phase 3. Delete `spike/`.
- **Done when** `make test` passes its static checks and the harness's `test` still passes.

### 2b. JSON Schema from erd.md; ERD generated (review-ezo.4)

- One-time conversion of every entity, attribute (type, enum, required, conditional shapes where JSON Schema can express them) and link. A link holds a single reference or a list, uses the `alias:id` pattern, and allows external references only where erd.md draws them.
- Every link field uses one shared `$defs/reference`, so tools (the resolver, the ERD generator) can find links.
- Check equivalence against erd.md's parsed entities, links and attributes. Generate the Mermaid ERD from the schema; erd.md becomes generated output.
- `make test` adds schema validation:
  - valid examples pass
  - the SCHEMA-LINK, SCHEMA-ATTR and SCHEMA-ENUM cases fail at their expected schema paths
- **Done when** that passes. **Checkpoint:** human reviews the schema.

### 2c. Resolution chapter and resolution cases (review-ezo.5)

- `spec/draft/resolution.md` defines resolution step by step:
  - fetch the import closure, with one version per document id and imports sharing the importer's major version
  - check aliases
  - key imported items `<document-id>:<id>` and rewrite references to them
  - fill in every item's stage (DOC-2)
  - REF-1, REF-6 and cycle checks (GRC-15, GRC-32, DFD-14)
  - map findings back to pointers in the author's document
- `tests/draft/resolution/` gets one case per rule, plus at least these:
  - a transitive import
  - a diamond
  - a profile import cycle
  - an id collision across documents
  - an unknown alias
  - a major-version mismatch
  - an unfetched import
- The resolved document's shape is written down in resolution.md, and in the schema if it differs from the authored schema.
- Settle the phase of any rule recorded as unclear in 2a.
- **Done when** every resolution-phase rule has a case. **Checkpoint:** human reviews the resolved form.

### 2d. Reference checker: loader, schema validation, resolver (review-ezo.10)

- The `reference/` package:
  - a YAML loader that rejects duplicate keys and keeps unquoted dates as strings
  - JSON Schema validation
  - `resolve.py`, following resolution.md step by step, with each step a function named after the section it implements
- The reference stays unshipped: no package version, no published artifact.
- `make test` runs the reference over `tests/draft/resolution/` and the schema cases, comparing exact findings with `expect`. A small runner shared with 2e.
- **Done when** every resolution case and schema case passes.

### 2e. Reference rules (review-ezo.11 and children)

The semantic rules move from Cypher to `reference/rules/<area>.py`:
- one function per rule, named after its ID (`def grc_10(doc)`), reading only the resolved document
- derived rules as shared helpers named after their IDs (`grc_31`)
- ruleWaivers handled once, in the runner, as DOC-3 says

Port test-first: each invalid case is the red test for its rule. The parent bead closes when all six children are closed and `make test` passes the whole suite, with valid examples showing no errors and no unwaived warnings.

| Child | Area | Rules (erd.md prefixes, semantic phase only) | Notes |
|---|---|---|---|
| 2e.1 | ref and doc | DOC-3, REF-3, REF-4 | First, because it is cross-cutting. **Checkpoint:** human reviews readability of the reference and its runner before the other areas |
| 2e.2 | product and metric | PRODUCT-1..6, METRIC-1; derived PRODUCT-7, PRODUCT-8 | |
| 2e.3 | C4 | C4 rules (17); derived C4-12..17, C4-20, C4-22 | |
| 2e.4 | DFD | DFD rules except DFD-14; derived DFD-11, DFD-15, DFD-20 | |
| 2e.5 | risk | RISK rules; derived RISK-8, RISK-9, RISK-11, RISK-17 | |
| 2e.6 | GRC | GRC rules except GRC-15 and GRC-32; derived GRC-6, GRC-17, GRC-19..21, GRC-27, GRC-31 | Uses RISK-17 from 2e.5 |

2e.2–2e.6 each depend on 2e.1, and 2e.6 also depends on 2e.5. Each child is **done when** every invalid case for its area passes and its rules report nothing on the valid examples.

### 3. Retire the Neo4j harness (review-ezo.6)

- Delete `docker-compose.yml`, `harness/rules/*.cypher`, `harness.py` (load, check, test, export) and the harness tests.
- `anneal.py` measures:
  - errors from `make test`
  - size from schema definitions, links and catalog rules
  - departures from `departures.yaml`

  Update the contents of `anneal/best/` to the new layout. Test the `anneal.py` counts at their seam.
- **Done when** the annealing loop runs end to end without Neo4j.

### 4. Docs and process (review-ezo.7)

- loop.md: fixers and critics verify with `make test`, and a Fix edits catalog, schema, prose, cases and reference together in one commit.
- review/prompt.md: the product is the spec (schema, catalog, suite).
- Restore `personas/schema-designer.md` in place of model-portability (INV-11 is retired).
- Rewrite or remove the READMEs for examples, review and harness. README: "What ships" and the transition note per ADR-002. Journal entry.

### 5. Round 3 prep, then begin round 3 (review-ezo.9)

Unchanged:
- treat imported documents as part of their importer in anneal.py's benchmark units (shiftly plus shiftly-governance)
- one-time re-triage of the 21 deferred findings under the current rules, rejecting what is out of scope
- checker-filed findings carry `example:` labels
- re-measure the baseline and reset the best copy

**Checkpoint:** human approves before `anneal.py begin` for round 3.

### Later. intent-core-python (review-ezo.8)

A product in its own repository, modeled on ai-resource-core-go:
- the suite as a git submodule pinned to a spec tag, shipped as package data
- loader, schema validation, resolver and rules (it may port `reference/`)
- CLI `intent-spec validate doc.yaml` reporting rule ID or schema path, pointer, severity and hint
- conformance tests from the suite

Not on the critical path, and doesn't block round 3. **Checkpoint:** human confirms before creating `colchuck-ai/intent-core-python`.
