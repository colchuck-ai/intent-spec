// id: C4-3
// severity: error
// hint: add the system's containers, or keep the system proposed while it stops at its system context
MATCH (d:Document {doc: $doc}), (s:System {doc: $doc})
WHERE coalesce(s.stage, d.stage) = 'ratified'   // DOC-2: an item's stage, or else the document's
  AND NOT coalesce(s.external, false)
  AND EXISTS { MATCH (s)-[:REALIZES]->() }
  AND NOT EXISTS { MATCH (:Container {doc: $doc})-[:IN]->(s) }
RETURN '/systems/' + s.id AS pointer, 'ratified internal system realizes a product but contains no container' AS detail
