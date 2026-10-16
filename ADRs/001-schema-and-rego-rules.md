# ADR-001: The spec is a JSON Schema plus Rego rules; language cores run it

- **Status:** accepted
- **Date:** 2026-10-15
- **Tracking:** beads epic `review-ezo`

## Context

intent-spec is a unified data model for describing software products across product, engineering, security and GRC. Until now the model lived in `erd.md` (a Mermaid ERD with rules as comments), with rules implemented as Cypher over a Neo4j harness. Two framings were tried and dropped in October 2026:

- "The model is the deliverable, storage is not" (INV-11). It left the model without a hard, executable target, and the work drifted into describing the model rather than checking it.
- A single `model.md` (structure, meaning and rules per element), built test-first and reverted the same week: it needed its own lint, renderer and LLM evals just to stay well-formed. A LinkML prototype was also rejected as the source format: twice as long as the ERD, it expressed about a quarter of the rules, and it miscompiled one silently.

The human chose a technological constraint instead, on the bet that an executable target makes the model converge better.

## Decision

1. **The spec is three language-agnostic parts, versioned together, in this repository:**
   - a **JSON Schema 2020-12** for syntactic checks, which is the source of truth for structure (the Mermaid ERD is generated from it, and definitions live in its descriptions);
   - **semantic rules in Rego** (Open Policy Agent), one package per area, each rule with OPA metadata: ID, severity, description, hint;
   - a **conformance suite**: valid documents that must pass, and invalid documents that each declare the rule ID or schema path they break and the JSON pointer (`expect: [{rule, pointer}]`).
2. **Code is authoritative.** When a rule's Rego and its description disagree, the Rego defines the rule; descriptions explain the general case.
3. **Language cores** (first `intent-core-python`, later others) live in their own repositories. A core parses YAML (rejecting duplicate keys), validates against the schema, runs the Rego rules, and passes the conformance suite, which it pulls in as a git submodule. Modeled on `ai-resource-spec` and `ai-resource-core-go`.
4. **Versioning by directory** (`schema/draft/`, `rules/draft/`, `tests/draft/`, `spec/draft/`). Documents declare `intentSpec: draft`. The spec stays `draft` during annealing; v1 is cut when annealing freezes. After v1, breaking changes need a new major version.
5. **Imports without a lockfile.** Rules receive `{document, imports: {alias: doc}}`; the caller resolves imported documents. An imported document must share the importer's major version.
6. **Invariants:** INV-2 (two layers; invalid examples name what they break) and INV-3 (flat maps, `/<type>/<id>` pointers) restored; INV-11 retired; INV-4 (lockfile) stays retired.
7. **Departures** from JTBD, C4, DFD3 or HCGF are listed in `departures.yaml` (ID, model, what, why), which annealing's energy counts. Anchors are not stored as data.
8. **The Neo4j harness and Cypher rules are removed** once the Rego rules pass the suite. Annealing runs entirely in this repository; cores are not needed for it.

## Options considered

- **Rules per language, spec holds only a catalog and tests** (the JSON Schema Test Suite model). Rejected: every rule rewritten per language, drift between cores, and the spec could not check its own semantic tests without a reference implementation.
- **Rules in Python inside the spec.** Rejected once multiple language cores were wanted: Python would be authoritative only for Python.
- **CEL** for rules: no recursion, so closures (profile imports, nested trust boundaries) don't fit. **SHACL/SPARQL**: requires RDF. **Keep Cypher**: requires a database to validate any document.

## Consequences

- The spec's CI can check both layers itself: a JSON Schema validator for syntax, `opa eval` for semantics, against the suite.
- A typical annealing move (schema + rule + fixtures) stays inside one repository.
- Cores are thin and can start late, after the model settles.
- Rego becomes a skill contributors and agents need. A spike on five hard rules (GRC-10, GRC-31, DFD-8, RISK-4, REF-3) decides go/no-go before the full port.
