// id: C4-2
// severity: warning
// hint: add a technology (e.g. HTTPS, SQL); only a relationship between two components of the same container may omit it
MATCH (n:Item {doc: $doc})
WHERE (n:Container OR n:Component) AND trim(coalesce(n.technology, '')) = ''
MATCH (e:EntityType {name: n.type})
RETURN '/' + e.key + '/' + n.id AS pointer, 'missing technology' AS detail
UNION
// A stored relationship's ends lie in the same container only when both are components of one container;
// every other pair (different containers, different systems, or a person, system or infrastructure node end) crosses a boundary.
MATCH (r:Relationship {doc: $doc})-[:LEAVES]->(s), (r)-[:ENTERS]->(t)
WHERE trim(coalesce(r.technology, '')) = ''
  AND NOT (s:Component AND t:Component AND EXISTS { MATCH (s)-[:IN]->(c:Container)<-[:IN]-(t) })
RETURN '/relationships/' + r.id AS pointer,
       'missing technology on a relationship from ' + coalesce(s.id, s.ref) + ' to ' + coalesce(t.id, t.ref) AS detail
