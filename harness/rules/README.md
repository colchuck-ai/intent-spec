# Writing rules

Each rule in `../../erd.md` (`%% rule SECTION-n: ...`) is one file here, `SECTION-n.cypher`, holding one Cypher query.

## File format

```cypher
// id: PRODUCT-2
// severity: error
// hint: one line telling the author how to fix it
MATCH ...
RETURN '/<key>/' + n.id AS pointer, '<what is wrong>' AS detail
```

- **severity** is `warning` for a rule marked `(should)` and `error` for every other rule.
- The query receives `$doc` and returns one row per problem. `pointer` is the item's JSON pointer `/<key>/<id>` (erd.md, reference serialization). Get `<key>` from `(:EntityType {name: n.type}).key`, or write it literally when the type is fixed. `detail` is optional.
- Match only items in the document: `(n:Item {doc: $doc})`, or a label such as `(:Product {doc: $doc})`.

## Mapping reminders

- Labels are entity names in PascalCase (`THREAT_REVIEW` becomes `:ThreatReview`). Every item also has `:Item` and `type` (`'THREAT_REVIEW'`).
- Relationship types are verbs in UPPER_SNAKE (`in` becomes `:IN`, `replacedBy` becomes `:REPLACED_BY`), and `r.verb` holds the original verb. One verb can reach several entity types, so add the target label when it matters.
- Attributes are node properties. Maps (such as `notDeployed`) are stored as JSON strings; APOC is not installed, so use string functions on them.
- Containment is a link: "X contains Y" in rule prose means `(y)-[:IN]->(x)`.
- **Stage [DOC-2]:** an item's stage is `coalesce(n.stage, d.stage)` with `d = (:Document {doc: $doc})`. Use this whenever a rule names a stage.
- **Derivations** (`%% derived SECTION-n`) are not files. Write their logic into each rule that cites them, with a comment naming the derivation ID.
- Imported targets are `(:Ref:Imported {ref: 'alias:id'})` and external references are `(:ExternalReference)` items. Per REF-2 and REF-5, rules that inspect a link's target skip both, unless they follow imports.
- **Following imports:** when the imported document is loaded, the stub has `-[:RESOLVES_TO]->` the item there (see `../README.md`). Follow it with `OPTIONAL MATCH (x)-[:RESOLVES_TO]->(xi) WITH coalesce(xi, x) AS t`, or `()-[:RESOLVES_TO*0..1]->(t:Label)`. Never count an item from another document toward coverage (REF-5): match the items a coverage rule iterates with `doc: $doc`.

## Rules that cannot be checked here

A rule that compares two versions of a document, such as DOC-1 (compare with the previous version) or RISK-5, gets no file. Say so when you hand back.

## Testing a rule

The seven example documents are shared, so never change their nodes. To test:

1. Copy an example YAML into the scratchpad as `t-<your-batch>-<example>.yaml`. The file name becomes its `doc`.
2. `uv run harness.py load <path>`
3. Plant violations with Cypher on that doc only, then run `uv run harness.py check --rules <ids> t-<your-batch>-<example>`. Every rule must fire at least once on a planted violation and stay silent on a clean copy.
4. Remove your doc: `MATCH (n {doc: 't-...'}) DETACH DELETE n`.

Finally, run your rules on all seven examples: `uv run harness.py check --rules <ids> home-assistant mastodon openemr plausible-growth plausible-mvp shiftly vaultwarden`. When a rule flags an example, decide which side is wrong:

- **The rule is wrong:** fix the rule.
- **The example or the ERD is wrong:** don't edit either. File a bead from `intent-spec/review`:
  `bd create --type task --priority P2 --labels harness-finding,rule:<ID> --title "<doc> <pointer>: <problem>" --description "<rule text, what the graph shows, suggested fix>"`
