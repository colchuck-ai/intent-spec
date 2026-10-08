// id: SCHEMA-ENUM
// severity: error
// hint: use one of the values the ERD lists for this attribute
MATCH (e:EntityType)-[:HAS_ATTR]->(a:Attr) WHERE a.values IS NOT NULL
MATCH (n:Item {doc: $doc, type: e.name}) WHERE n[a.name] IS NOT NULL
WITH e, a, n, CASE WHEN a.list THEN n[a.name] ELSE [n[a.name]] END AS given
UNWIND given AS v
WITH e, a, n, v WHERE NOT v IN a.values
RETURN '/' + e.key + '/' + n.id AS pointer,
       a.name + ': ' + toString(v) + ' is not one of ' + reduce(s = '', x IN a.values | s + CASE s WHEN '' THEN '' ELSE ' | ' END + x) AS detail
