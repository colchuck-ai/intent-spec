// id: C4-5
// severity: error
// hint: an external system realizes no product; remove realizes or make the system internal
MATCH (s:System {doc: $doc})-[:REALIZES]->(p)
WHERE coalesce(s.external, false)
RETURN '/systems/' + s.id AS pointer, 'external system realizes ' + coalesce(p.id, p.ref) AS detail
