// id: REF-3
// severity: error
// hint: ratify the target too, or keep the linking item proposed
// Imports are followed: an alias:id target resolves (RESOLVES_TO) to the item in a loaded document, and its
// stage is its own or else that document's [DOC-2]. A target that resolves to no item is skipped (REF-1).
MATCH (d:Document {doc: $doc}), (s:Item {doc: $doc})-[r]->(x)
WHERE r.verb IS NOT NULL
  AND coalesce(s.stage, d.stage) = 'ratified'   // DOC-2
OPTIONAL MATCH (x)-[:RESOLVES_TO]->(xi)
WITH s, r, x, coalesce(xi, x) AS t
WHERE t:Item AND NOT t:ExternalReference
MATCH (td:Document {doc: t.doc})
WHERE coalesce(t.stage, td.stage) = 'proposed'
MATCH (e:EntityType {name: s.type})
RETURN '/' + e.key + '/' + s.id AS pointer, r.verb + ' -> ' + coalesce(x.ref, t.id) + ', which is proposed' AS detail
