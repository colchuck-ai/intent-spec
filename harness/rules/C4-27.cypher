// id: C4-27
// severity: warning
// hint: satisfy the requirement with an element deployed in this environment, or take its satisfier out of the diagram's notDeployed
MATCH (dg:DeploymentDiagram {doc: $doc})-[:COVERS]->(env:Environment)-[:SERVES]->(p)
// notDeployed is stored as a JSON string map; its keys are every 4th token when split on unescaped quotes
WITH dg, env, p, CASE WHEN dg.notDeployed IS NULL THEN []
                 ELSE split(replace(replace(dg.notDeployed, '\\\\', ''), '\\"', ''), '"') END AS toks
WITH dg, env, p, [i IN range(0, size(toks) - 1) WHERE i % 4 = 1 | toks[i]] AS notDeployed
MATCH (d:Document {doc: $doc}), (q:Requirement {doc: $doc})
WHERE coalesce(q.stage, d.stage) = 'ratified'   // DOC-2: an item's stage, or else the document's
  // PRODUCT-8: a requirement applies to the products it scopes; when it scopes none, to every product that
  // targets the job of an outcome it serves, is governed by an adoption it implements, or a treatment it executes applies to
  AND (EXISTS { MATCH (q)-[:SCOPES]->(p) }
       OR (NOT EXISTS { MATCH (q)-[:SCOPES]->() }
           AND (EXISTS { MATCH (q)-[:SERVES]->(:Outcome)-[:IN]->(:Job)<-[:TARGETS]-(p) }
                OR EXISTS { MATCH (q)-[:IMPLEMENTS]->(:Adoption)-[:GOVERNS]->(p) }
                // RISK-17: a treatment applies to the products it scopes, or to every product in the document when it scopes none
                OR EXISTS { MATCH (q)-[:EXECUTES]->(tr:Treatment)
                            WHERE EXISTS { MATCH (tr)-[:SCOPES]->(p) }
                               OR (p:Product AND NOT EXISTS { MATCH (tr)-[:SCOPES]->() }) })))
  AND NOT EXISTS {
    MATCH (x:Item {doc: $doc})-[:SATISFIES]->(q)
    WHERE (x:System)
       OR (x:Container AND NOT x.id IN notDeployed)
       OR (x:Component AND NOT EXISTS { MATCH (x)-[:IN]->(c:Container) WHERE c.id IN notDeployed })
       // C4-22: a node's environment is that of the outermost node containing it
       OR (x:DeploymentNode AND EXISTS { MATCH (x)-[:IN*0..]->(root:DeploymentNode)-[:BELONGS]->(env)
                                       WHERE NOT EXISTS { MATCH (root)-[:IN]->() } })
  }
WITH DISTINCT q, dg
RETURN '/requirements/' + q.id AS pointer,
       'applies to a product served by ' + dg.id + "'s environment but is satisfied only by elements in its notDeployed or nodes outside it, or by none" AS detail
