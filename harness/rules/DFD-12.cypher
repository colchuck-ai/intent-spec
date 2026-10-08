// id: DFD-12
// severity: error
// hint: add relies naming the container, infrastructure node, deployment node, control or system that enforces the boundary
MATCH (b:TrustBoundary {doc: $doc})
WHERE NOT EXISTS { MATCH (b)-[:RELIES]->() }
RETURN '/trustBoundaries/' + b.id AS pointer, 'relies on nothing to enforce it' AS detail
