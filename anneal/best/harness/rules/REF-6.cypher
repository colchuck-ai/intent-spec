// id: REF-6
// severity: error
// hint: link to an item of a type the ERD draws for this verb (see the :EntityType meta-graph)
// Imports are followed: an alias:id target resolves (RESOLVES_TO) to the item in a loaded document.
MATCH (s:Item {doc: $doc})-[r]->(x)
WHERE r.verb IS NOT NULL AND r.verb <> 'replacedBy'
OPTIONAL MATCH (x)-[:RESOLVES_TO]->(xi)
WITH s, r, x, coalesce(xi, x) AS t
WHERE t:Item
MATCH (e:EntityType {name: s.type})
WHERE NOT EXISTS { MATCH (e)-[:LINK {verb: r.verb}]->(:EntityType {name: t.type}) }
RETURN '/' + e.key + '/' + s.id AS pointer,
       r.verb + ' -> ' + coalesce(x.ref, t.id) + ' (' + t.type + ') is not a type this link allows' AS detail
