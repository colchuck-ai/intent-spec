// id: C4-8
// severity: error
// hint: link a system, container, component or deployment node to the requirement with satisfies, or keep the requirement proposed
MATCH (d:Document {doc: $doc}), (q:Requirement {doc: $doc})
WHERE coalesce(q.stage, d.stage) = 'ratified'   // DOC-2: an item's stage, or else the document's
  AND NOT EXISTS { MATCH (x:Item {doc: $doc})-[:SATISFIES]->(q) WHERE x:System OR x:Container OR x:Component OR x:DeploymentNode }
// Exempt: it serves only outcomes of purchase jobs (at least one), and executes no treatment and implements no adoption.
// Per REF-2 and REF-5, imported outcomes and jobs are skipped when inspecting kinds.
OPTIONAL MATCH (q)-[:SERVES]->(o:Outcome)-[:IN]->(j:Job)
WITH q, collect(coalesce(j.kind, 'core')) AS kinds
WHERE NOT (size(kinds) > 0 AND all(k IN kinds WHERE k = 'purchase')
           AND NOT EXISTS { MATCH (q)-[:EXECUTES]->() }
           AND NOT EXISTS { MATCH (q)-[:IMPLEMENTS]->() })
RETURN '/requirements/' + q.id AS pointer, 'ratified requirement is satisfied by no system, container, component or deployment node' AS detail
