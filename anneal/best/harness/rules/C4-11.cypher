// id: C4-11
// severity: error
// hint: point the relationship at two different elements, neither containing the other
MATCH (r:Relationship {doc: $doc})-[:LEAVES]->(s), (r)-[:ENTERS]->(t)
WHERE s = t
   OR EXISTS { MATCH (s)-[:IN*1..2]->(t) }
   OR EXISTS { MATCH (t)-[:IN*1..2]->(s) }
RETURN '/relationships/' + r.id AS pointer,
       CASE WHEN s = t THEN 'leaves and enters the same element ' + coalesce(s.id, s.ref)
            ELSE 'one end contains the other: ' + coalesce(s.id, s.ref) + ', ' + coalesce(t.id, t.ref) END AS detail
