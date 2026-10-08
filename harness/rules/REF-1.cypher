// id: REF-1
// severity: error
// hint: point the link at an item declared in this document, or at alias:id for an alias in imports
MATCH (s:Item {doc: $doc})-[r]->(x:Ref {doc: $doc})
MATCH (e:EntityType {name: s.type})
WHERE x:Unresolved
   OR NOT EXISTS { MATCH (:Document {doc: $doc})-[:HAS]->(:Import {alias: split(x.ref, ':')[0]}) }
RETURN '/' + e.key + '/' + s.id AS pointer, r.verb + ' -> ' + x.ref + ' does not resolve' AS detail
