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
| Target that resolves to nothing | `(:Ref:Unresolved {ref})` stub, reported by REF-1 |
| ERD entity types and links | `(:EntityType {name, key, label})-[:LINK {verb, many, required}]->(:EntityType)` |

All seven examples share one database (Community edition allows one), so every node carries `doc`, the name of the file it came from (e.g. `plausible-mvp`). Filter on it in queries.

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

The query receives `$doc` and returns one row per problem, with `pointer` (the JSON pointer `/<key>/<id>` from INV-2) and optionally `detail`. `check` exits non-zero when an error-severity rule finds anything.

## Agents

Agents can use `cypher-shell` inside the container (`docker exec -it intent-spec-neo4j cypher-shell -u neo4j -p intentspec`) or connect to `bolt://localhost:7687` with any Neo4j driver or MCP server.
