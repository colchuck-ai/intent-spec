# Neo4j harness

Load intent-spec documents into a local Neo4j database so people and agents can see and query them as a graph, check rules as Cypher, and export changes back to YAML.

The YAML files in git are the source of truth. The database is a working copy you can rebuild at any time:

1. `load` a document into Neo4j.
2. Look at it or change it in Neo4j Browser, or with Cypher from an agent.
3. `export` it back into its YAML file. Comments and key order are kept, so the change shows up as an ordinary git diff.

## Setup

Requires Docker and [uv](https://docs.astral.sh/uv/).

```bash
cd harness
docker compose up -d           # Neo4j 5 Community; Browser at http://localhost:7474 (neo4j / intentspec)
uv run harness.py load         # load every example in review/examples, plus the ERD meta-graph
uv run harness.py check        # run the rules in rules/*.cypher
uv run harness.py export       # write loaded documents back to their YAML files
uv run harness.py test         # run the invalid examples in review/examples/invalid as rule regression tests
```

If `docker` can't reach the daemon although Docker Desktop is running, run `docker context use desktop-linux` (or prefix commands with `DOCKER_CONTEXT=desktop-linux`).

Each command also takes document names, for example `uv run harness.py load openemr`, or a path to a YAML file.

## How a document becomes a graph

The mapping is read from `../erd.md`, so it follows the model without code changes.

| YAML | Graph |
|---|---|
| Document header (`id`, `version`, `stage`, ...) | `(:Document {doc, ...})` |
| Import alias | `(:Document)-[:HAS]->(:Import {alias, source, version})` |
| Item `/containers/core` | `(:Item:Container {doc, id: 'core', type: 'CONTAINER', ...attributes})` |
| Link field `in: home-assistant` | `-[:IN {verb: 'in'}]->`, with `idx` for list order |
| `alias:id` target | `(:Ref:Imported {ref})` stub |
| Import whose `source` names a loaded document by file stem (`source: shiftly-governance.yaml` names `shiftly-governance`) | `(:Import)-[:LOADED_AS]->(:Document)` |
| `alias:id` target of such an import | the stub, then `-[:RESOLVES_TO]->(:Item {doc: <that document>, id})` |
| Target that resolves to nothing | `(:Ref:Unresolved {ref})` stub, reported by REF-1 |
| ERD entity types and links | `(:EntityType {name, key, label})-[:LINK {verb, many, required}]->(:EntityType)` |

All the examples share one database (Community edition allows one), so every node carries `doc`, the name of the file it came from (e.g. `plausible-mvp`). Filter on it in queries.

### Imports between loaded documents

There is no lockfile. When an import's `source` names another document loaded in the same graph, `load` connects each `alias:id` stub to the item with that id in that document (`RESOLVES_TO`), so rules can follow it. For example, `shiftly` imports `shiftly-governance` as `gov`, selects the profile `gov:shiftly-baseline` and adopts `gov:volunteer-data-minimisation`. The links are rebuilt after every `load`, so load the imported document too (`load` with no arguments loads every example).

- The rules that follow imports are GRC-10 (a selected profile's controls), GRC-28 (a control's influencers), REF-3 and REF-4 (the target's stage, its own or else its document's) and REF-6 (the target's type). REF-1 reports an `alias:id` whose import's document is loaded but declares no such id.
- When the imported document is not loaded, the stub stays unresolved and these rules skip it, as before.
- Imported items never count as local (REF-5): coverage rules match items with `doc: $doc`, and `RESOLVES_TO` only ever leaves a stub.
- `export` writes only the items of the document it exports. `RESOLVES_TO` and `LOADED_AS` have no `verb`, so they never reach a YAML file.

## Queries to try

```cypher
// The whole of one product
MATCH (n:Item {doc: 'home-assistant'}) RETURN n

// The model itself
MATCH (a:EntityType)-[l:LINK]->(b:EntityType) RETURN a, l, b

// From a threat to the outcomes it puts at risk
MATCH p = (:Threat {doc: 'openemr'})<-[:REVIEWS]-(:ThreatReview)-[:RAISES]->(:Risk)-[:ENDANGERS]->(:Outcome) RETURN p

// What implements each adopted control
MATCH (a:Adoption {doc: 'openemr'})-[:ADOPTS]->(c:Control)
OPTIONAL MATCH (a)-[:FOLLOWS]->(p:Procedure)
RETURN c.id, a.mode, collect(p.id)
```

## Rules

Each rule is a file in `rules/` holding one Cypher query. Its header names the rule:

```cypher
// id: PRODUCT-1
// severity: error
// hint: what to do about it
```

The query receives `$doc` and returns one row per problem, with `pointer` (the JSON pointer `/<key>/<id>` from erd.md's reference serialization) and optionally `detail`. `check` exits non-zero when an error-severity rule finds anything.

## Rule regression tests

Each file in `../review/examples/invalid` is a small document that breaks one rule. Its first line names the rule and where it fires, `# breaks: <RULE-ID> <pointer>`; further `# also: <RULE-ID> <pointer>` lines name any other finding it expects. `test` loads each file with the documents it imports, checks it, and passes only when its unwaived findings (errors and warnings) are exactly those. It then deletes the file's nodes, prints one line per file and a summary, and exits non-zero when any file fails. Pass names (e.g. `uv run harness.py test GRC-10`) to run some. The invalid examples are kept out of `load` and `check`, which read only the top level of `review/examples`.

An item's `ruleWaivers` map (rule ID to rationale) waives a warning-severity rule on that item: `check` prints it as `waived` with the rationale instead of as a warning. Waivers never silence an error-severity rule; DOC-3 reports any waiver of one, or of an unknown rule ID. Rule IDs and severities are loaded from `../erd.md` as `(:Rule {id, severity})` nodes.

## Agents

Agents can use `cypher-shell` inside the container (`docker exec -it intent-spec-neo4j cypher-shell -u neo4j -p intentspec`) or connect to `bolt://localhost:7687` with any Neo4j driver or MCP server.
