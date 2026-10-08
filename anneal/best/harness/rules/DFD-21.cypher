// id: DFD-21
// severity: error
// hint: rely on the containers, nodes or controls that enforce the boundary; rely on a system only when it is external
MATCH (b:TrustBoundary {doc: $doc})-[:RELIES]->(s:System)
WHERE coalesce(s.external, false) <> true
RETURN '/trustBoundaries/' + b.id AS pointer, 'relies on internal system ' + s.id AS detail
