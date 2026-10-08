// id: PRODUCT-2
// severity: error
// hint: give the job at least one ratified outcome, or keep the products that target it proposed
MATCH (d:Document {doc: $doc}), (p:Product {doc: $doc})-[:TARGETS]->(j:Job {doc: $doc})
WHERE coalesce(p.stage, d.stage) = 'ratified'   // DOC-2
  AND NOT EXISTS {
    MATCH (o:Outcome {doc: $doc})-[:IN]->(j)
    WHERE coalesce(o.stage, d.stage) = 'ratified'
  }
WITH j, collect(p.id) AS products
RETURN '/jobs/' + j.id AS pointer,
       'targeted by ratified ' + reduce(s = '', x IN products | s + CASE s WHEN '' THEN '' ELSE ', ' END + x) +
       ' but has no ratified outcome' AS detail
