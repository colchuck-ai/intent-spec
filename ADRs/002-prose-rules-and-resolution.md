# ADR-002: Rules are prose with a conformance suite; resolution is its own chapter; an unshipped reference checker runs them

- **Status:** accepted
- **Date:** 2026-10-17
- **Supersedes:** ADR-001 decisions 1 (rules in Rego), 3 (cores only run the spec's rules), 5 (rule input `{document, imports}`) and 8 (harness removed once Rego passes)
- **Tracking:** beads epic `review-ezo`; evidence in `spike/rego/` (review-ezo.2)

## Context

ADR-001 made Rego the authoritative rule language so that every language core would run the same rule code. The phase 1 spike (`spike/rego/README.md`) ported five hard rules and passed every example. It also showed that the difficulty is not in the rules. The documents are a graph serialized as a tree, and before any rule can run, something has to:

- tell links from attributes
- read links backwards
- fill in implicit values (DOC-2 stage, containment and profile closures)
- resolve aliases that only mean something inside their own document
- type polymorphic targets
- apply the cross-cutting exceptions (REF-2, REF-5, waivers)

The first port lost transitive imports and passed a document it should have failed. The second needed a resolve step in Rego, and Rego is weakest at exactly that work.

Projects with this shape (a schema, semantic rules and imports that must be resolved) tend to use the same layers. Examples are JSON Schema, Protobuf, OpenAPI, ECMAScript, WebAssembly and OSCAL:

1. syntax as a schema
2. resolution as its own specified phase, producing a resolved form (OSCAL's profile resolution, protoc's descriptor set, a bundled OpenAPI document)
3. semantic rules in prose against the resolved form
4. per-language implementations that agree through a shared conformance suite

Shared executable policy code, when it exists, is a linter on top of a spec, not the spec itself.

Annealing changes the model many times a day, and a change usually touches a rule's statement, the schema, a test case and the code that checks it. Spreading those across two repositories (spec and core) makes every change a coordinated release, so annealing has to happen in one repository.

## Decision

1. **The spec has three parts, versioned together by directory** (`draft/`, then `v1/`), in this repository:
   - **Schema:** JSON Schema 2020-12 for one authored document. It is the source of truth for structure; the ERD is generated from it. Link fields share one reference definition, so tools can find every link.
   - **Rules:** a catalog (`rules/draft/rules.yaml`) with one entry per rule:
     - ID
     - area
     - severity (error, or warning for a *should* rule)
     - kind (`rule` or `derived`)
     - phase (`resolution` or `semantic`)
     - normative statement
     - hint

     The statement is normative. Prose chapters (`spec/draft/*.md`) explain the general case and cite rules by ID.
   - **Conformance suite** (`tests/draft/`):
     - `valid/`: documents that must pass
     - `invalid/`: single documents that each declare `expect: [{rule | schemaPath, pointer}]`
     - `resolution/`: sets of documents, each with the expected resolved document or the expected resolution findings
2. **Two phases, with a hard line between them.**
   - **Resolution** (`spec/draft/resolution.md`) turns a document and its imports into one resolved document. The resolution phase owns:
     - fetching imports, aliases and major-version agreement
     - one version per document within a resolution
     - reference resolution (REF-1) and target types (REF-6)
     - every cycle check (GRC-15, GRC-32, DFD-14)
     - DOC-2 stage defaults
   - **Semantic rules** are stated against a single resolved document and never mention imports.
3. **The resolved document** uses the same schema as an authored document, with three changes:
   - Imported items are keyed `<document-id>:<id>`, and references to them are rewritten to match.
   - Every item states its stage.
   - Nothing is left in `imports`.

   Local ids contain no colon, so "items declared in this document" (REF-5) is just "items whose id has no prefix". A finding's pointer always names an item of the document the author is editing.
4. **The suite is authoritative, not code.** When an implementation and the catalog disagree, the catalog statement defines the rule, and a conformance case is added to pin the disagreement down. Every rule has a conformance case, or a recorded reason it has none.
5. **An unshipped reference checker lives in this repository** (`reference/`), following WebAssembly's spec interpreter:
   - It parses, validates against the schema, resolves following `resolution.md` step by step, and checks each semantic rule in a function named after its ID.
   - It is plain Python over the resolved document, with no database or framework. It aims to be correct and readable, not fast.
   - It is never released: no package version, no published artifact, no stability promise. It is not normative, and it exists to prove the catalog and the suite agree.
   - `make test` runs the static checks and then the reference against the whole suite.
6. **Annealing happens in this repository only.** A model change is one commit: the catalog statement, schema, prose, test cases and reference code together, checked by `make test`. No core is needed.
7. **Language cores are products in their own repositories** (`intent-core-python` first). Each one:
   - parses, rejecting duplicate keys and keeping dates as strings
   - validates, resolves and checks
   - passes the suite, pulled in as a git submodule pinned to a spec tag

   A core has its own semver and declares which spec versions it supports. It may port the reference's code but is not bound to it. When a core and the reference disagree, a conformance case settles it.
8. **Unchanged from ADR-001:** versioning by directory; v1 cut when annealing freezes; INV-2 and INV-3; INV-11 retired; no lockfile; `departures.yaml`.

## Options considered

- **Rego rules over the authored document** (ADR-001). Spiked: it works, but each rule redoes resolution, and transitive imports were silently lost.
- **Rego rules over a resolve step written in Rego** (spike variant 2). It passed everything, but the resolve step is the hardest code in the system and Rego handles it worst.
- **The shipped core inside this repository** (the Protobuf model; core under `core/python/`, released with its own tag prefix). It avoids duplication, but makes the spec repository belong to one language, and packaging, CLI and performance work would land among annealing changes. Rejected in favour of a small unshipped reference.
- **Annealing across spec and core repositories**, with paired commits. Rejected: every model change becomes a two-repository change.
- **Keep the Neo4j harness as the reference.** Rejected: it keeps docker and Cypher, and the rules would still be rewritten for every core.
- **Suite in its own repository** (JSON-Schema-Test-Suite, test262). Rejected while annealing, because nearly every change touches statement, schema and cases together. Revisit after v1, when outside implementers need the tests on their own.

## Consequences

- The rules are written at least twice: once in `reference/`, and once in each core. Each core is checked against the suite, not against the reference's code.
- The Neo4j harness stays as the checker until `reference/` passes the suite, and is then removed (rules ported from Cypher to Python first).
- The reference has to stay small and readable. It is the executable reading of the catalog that annealing agents and reviewers rely on. Anything wanted for a product goes in a core.
- Resolution is the hardest part, and every core implements it again. The resolution cases (transitive imports, diamonds, cycles, collisions, version mismatch) are what keep implementations in agreement, so they must be thorough.
- The Rego spike stays in git history as the evidence for this ADR, and `spike/` is deleted once phase 2a lands.
