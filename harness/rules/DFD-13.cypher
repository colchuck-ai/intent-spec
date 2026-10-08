// id: DFD-13
// severity: error
// hint: enclose the element in only its innermost boundary; nest boundaries with in
MATCH (b:TrustBoundary {doc: $doc})-[:ENCLOSES]->(n:Item)
WITH n, collect(DISTINCT b.id) AS bs
WHERE size(bs) > 1
MATCH (e:EntityType {name: n.type})
RETURN '/' + e.key + '/' + n.id AS pointer, 'enclosed directly by ' + size(bs) + ' boundaries: ' + reduce(s = '', x IN bs | s + CASE WHEN s = '' THEN '' ELSE ', ' END + x) AS detail
