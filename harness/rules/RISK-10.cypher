// id: RISK-10
// severity: error
// hint: for each product the review's DFDs cover, cite a control that product adopts in mode system, procedure or inherited, or a requirement that applies to it and is satisfied by a system realizing it (or a container or component in one); otherwise record the review as risk
MATCH (r:ThreatReview {doc: $doc, disposition: 'covered'})
// RISK-9: a review's products are the products of every DFD that includes, or shows, an element it inspects
//   DFD-20: a DFD shows every data flow whose two ends it includes
// RISK-8: a DFD's products are those realized by the system it depicts, or by the system containing the container it depicts
WITH r, COLLECT {
  MATCH (r)-[:INSPECTS]->(e)
  MATCH (d:DataFlowDiagram {doc: $doc})
  WHERE (d)-[:INCLUDES]->(e)
     OR (e:DataFlow AND EXISTS { MATCH (e)-[:CONNECTS]->() }
         AND NOT EXISTS { MATCH (e)-[:CONNECTS]->(end) WHERE NOT (d)-[:INCLUDES]->(end) })
  MATCH (d)-[:DEPICTS]->(x)-[:IN*0..1]->(s:System)-[:REALIZES]->(p)
  WHERE x:System OR x:Container
  RETURN DISTINCT p
} AS products
UNWIND products AS p
WITH r, p
WHERE NOT EXISTS {
    // a cited control adopted in mode system, procedure or inherited by p
    MATCH (r)-[:CITES]->(c)<-[:ADOPTS]-(a:Adoption)-[:GOVERNS]->(p)
    WHERE (c:Control OR c:Imported) AND a.mode IN ['system', 'procedure', 'inherited']
  }
  AND NOT EXISTS {
    MATCH (r)-[:CITES]->(q:Requirement)
    // satisfied by a system that realizes p, or by a container or component in one
    WHERE EXISTS { MATCH (q)<-[:SATISFIES]-(:Item)-[:IN*0..2]->(:System)-[:REALIZES]->(p) }
      // PRODUCT-8: a requirement applies to the products it scopes; when it scopes none, to every product that
      // targets the job of an outcome it serves, governed by an adoption it implements, or that a treatment it executes applies to
      AND CASE WHEN EXISTS { MATCH (q)-[:SCOPES]->() }
               THEN EXISTS { MATCH (q)-[:SCOPES]->(p) }
               ELSE EXISTS { MATCH (q)-[:SERVES]->(:Outcome)-[:IN]->(:Job)<-[:TARGETS]-(p) }
                 OR EXISTS { MATCH (q)-[:IMPLEMENTS]->(:Adoption)-[:GOVERNS]->(p) }
                 // RISK-17: a treatment applies to the products it scopes, or to every product in the document when it scopes none
                 OR EXISTS { MATCH (q)-[:EXECUTES]->(t:Treatment)
                             WHERE (t)-[:SCOPES]->(p)
                                OR (NOT EXISTS { MATCH (t)-[:SCOPES]->() } AND p:Product AND p.doc = $doc) }
          END
  }
RETURN '/threatReviews/' + r.id AS pointer,
       'covered, but no cited control or requirement covers product ' + coalesce(p.id, p.ref) AS detail
