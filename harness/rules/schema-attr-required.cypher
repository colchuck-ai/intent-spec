// id: SCHEMA-ATTR
// severity: error
// hint: add the attribute; the ERD marks it required (or "one or more" for a list)
MATCH (e:EntityType)-[:HAS_ATTR]->(a:Attr {required: true})
MATCH (n:Item {doc: $doc, type: e.name})
WHERE n[a.name] IS NULL OR (a.list AND size(n[a.name]) = 0)
RETURN '/' + e.key + '/' + n.id AS pointer, 'missing required attribute ' + a.name AS detail
UNION
MATCH (:EntityType {name: 'DOCUMENT'})-[:HAS_ATTR]->(a:Attr {required: true})
MATCH (d:Document {doc: $doc})
WHERE d[a.name] IS NULL
RETURN '/' + a.name AS pointer, 'missing required document field' AS detail
