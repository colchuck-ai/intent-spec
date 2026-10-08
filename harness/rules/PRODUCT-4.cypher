// id: PRODUCT-4
// severity: error
// hint: scope products only on an outcome with a disposition, and only products that target the outcome's job
MATCH (o:Outcome {doc: $doc})-[:SCOPES]->(p)
WHERE o.disposition IS NULL
   // REF-5: only local products are checked against the job
   OR (p:Product AND NOT EXISTS { MATCH (o)-[:IN]->(j) WHERE (p)-[:TARGETS]->(j) })
RETURN '/outcomes/' + o.id AS pointer,
       CASE WHEN o.disposition IS NULL
            THEN 'scopes ' + coalesce(p.id, p.ref) + ' without a disposition'
            ELSE 'scopes ' + p.id + ', which does not target its outcome\'s job' END AS detail
