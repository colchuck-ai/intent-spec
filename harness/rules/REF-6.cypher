// id: REF-6
// severity: error
// hint: link to an item of a type the ERD draws for this verb (see the :EntityType meta-graph)
MATCH (s:Item {doc: $doc})-[r]->(t:Item)
WHERE r.verb <> 'replacedBy'
MATCH (e:EntityType {name: s.type})
WHERE NOT EXISTS { MATCH (e)-[:LINK {verb: r.verb}]->(:EntityType {name: t.type}) }
RETURN '/' + e.key + '/' + s.id AS pointer,
       r.verb + ' -> ' + t.id + ' (' + t.type + ') is not a type this link allows' AS detail
