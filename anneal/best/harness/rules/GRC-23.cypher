// id: GRC-23
// severity: warning
// hint: add a control that enforces this standard
MATCH (s:Standard {doc: $doc})
WHERE NOT EXISTS { MATCH (:Control {doc: $doc})-[:ENFORCES]->(s) }
RETURN '/standards/' + s.id AS pointer, 'standard is enforced by no control' AS detail
