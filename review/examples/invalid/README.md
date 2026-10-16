# Invalid examples

Rule regression tests for the harness. Each document here breaks one rule in `../../../erd.md` (or one of the harness's SCHEMA checks) and is otherwise valid, kept as small as the rule allows. They are not examples of the model, and `load` and `check` never read them.

The first line names the rule and the pointer where it fires:

```yaml
# breaks: GRC-10 /products/p
# also: GRC-8 /selections/s2
```

Each optional `# also:` line names one more finding the document expects, for example a second pointer where the same rule fires.

`cd harness && uv run harness.py test` loads each document with the documents it imports, checks it, and passes only when its unwaived findings, errors and warnings alike, are exactly the ones its header lists. It then removes the document from the graph.

## Files

- `<RULE-ID>.yaml` for every rule file in `harness/rules`, including `SCHEMA-ATTR`, `SCHEMA-ENUM` and `SCHEMA-LINK`.
- A suffix marks a second branch of a rule worth guarding:
  - `-import`: the rule follows an import into a loaded document (GRC-10, GRC-28, REF-1, REF-3, REF-4, REF-6). These import `../shiftly-governance.yaml`, `../shiftly.yaml` or `../plausible-growth.yaml`.
  - `REF-1-alias`: an `alias:id` whose alias is not in imports.
  - `SCHEMA-ATTR-document`: a missing document header field.
  - `SCHEMA-LINK-many`: a to-one link with two targets.

## Rules without a file

| Rule | Why |
|---|---|
| DOC-1 | Removing or renaming an id is a breaking change: it compares two versions of a document, not one. |
| RISK-5 | A deprecated target keeps its reviews: it compares two versions of a document, not one. |
| REF-2 | A behaviour, not a check: where allowed, an external reference satisfies cardinality and other rules skip it. Every rule that inspects a target applies it. |
| REF-5 | A behaviour, not a check: coverage rules count only items declared in the document. Every coverage rule applies it by matching only items with the document's own `doc`. |
