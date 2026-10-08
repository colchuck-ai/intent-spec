// id: DFD-14
// severity: error
// hint: break the cycle so that boundary containment (in) forms a tree
MATCH (b:TrustBoundary {doc: $doc})
WHERE EXISTS { MATCH (b)-[:IN*1..]->(b) }
RETURN '/trustBoundaries/' + b.id AS pointer, 'is inside itself through in' AS detail
