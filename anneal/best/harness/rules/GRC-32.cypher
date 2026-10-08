// id: GRC-32
// severity: error
// hint: remove one of the profile imports that forms the cycle
MATCH (p:Profile {doc: $doc})
WHERE EXISTS { MATCH (p)-[:IMPORTS*1..]->(p) }
RETURN '/profiles/' + p.id AS pointer, 'profile imports itself through a cycle' AS detail
