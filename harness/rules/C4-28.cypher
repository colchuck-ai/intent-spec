// id: C4-28
// severity: warning
// hint: add an environment that serves the product, or keep the product proposed
MATCH (d:Document {doc: $doc}), (p:Product {doc: $doc})
WHERE coalesce(p.stage, d.stage) = 'ratified'   // DOC-2: an item's stage, or else the document's
  AND EXISTS { MATCH (:System {doc: $doc})-[:REALIZES]->(p) }
  AND NOT EXISTS { MATCH (:Environment {doc: $doc})-[:SERVES]->(p) }
RETURN '/products/' + p.id AS pointer, 'ratified product realized by a system is served by no environment' AS detail
