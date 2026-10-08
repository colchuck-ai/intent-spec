// id: C4-25
// severity: warning
// hint: store the relationship at one of the container's components (the container-level one is then implied), or drop the container-level one
// For each end at an application container with components, look for a stored relationship on the same side
// whose end is one of those components and whose other end is, or lifts to, this relationship's other end (C4-12).
MATCH (r:Relationship {doc: $doc})-[:LEAVES]->(s), (r)-[:ENTERS]->(t)
UNWIND [['leaves', s, t], ['enters', t, s]] AS side
WITH r, side[0] AS verb, side[1] AS c, side[2] AS other
WHERE c:Container AND c.kind = 'application' AND EXISTS { MATCH (:Component)-[:IN]->(c) }
  AND NOT EXISTS {
    MATCH (r2:Relationship {doc: $doc})-[e1]->(k:Component)-[:IN]->(c), (r2)-[e2]->(o2)
    WHERE r2 <> r AND e1.verb = verb AND e2.verb <> verb AND e2.verb IN ['leaves', 'enters']
      AND (o2 = other OR EXISTS { MATCH (o2)-[:IN*1..2]->(other) })
  }
RETURN '/relationships/' + r.id AS pointer,
       'no stored relationship at a component of ' + c.id + ' implies it' AS detail
