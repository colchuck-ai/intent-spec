// id: PRODUCT-1
// severity: error
// hint: a ratified product targets at least one job; add targets, or keep the product proposed
MATCH (d:Document {doc: $doc}), (p:Product {doc: $doc})
WHERE coalesce(p.stage, d.stage) = 'ratified'   // DOC-2: an item's stage, or else the document's
  AND NOT EXISTS { MATCH (p)-[:TARGETS]->(:Job) }
RETURN '/products/' + p.id AS pointer, 'ratified product targets no job' AS detail
