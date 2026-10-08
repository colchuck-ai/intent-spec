// id: C4-27
// severity: warning
// hint: satisfy the requirement with a system, container or component, or with a deployment node in this environment
MATCH (dg:DeploymentDiagram {doc: $doc})-[:COVERS]->(env:Environment)-[:SERVES]->(p)
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
    // containers in the diagram's notDeployed (e.g. a script run in the visitor's browser) and their components count
    WHERE x:System OR x:Container OR x:Component
       // C4-22: a node's environment is that of the outermost node containing it
       OR (x:DeploymentNode AND EXISTS { MATCH (x)-[:IN*0..]->(root:DeploymentNode)-[:BELONGS]->(env)
                                       WHERE NOT EXISTS { MATCH (root)-[:IN]->() } })
  }
WITH DISTINCT q, dg
RETURN '/requirements/' + q.id AS pointer,
       'applies to a product served by ' + dg.id + "'s environment but is satisfied only by deployment nodes outside it, or by none" AS detail
