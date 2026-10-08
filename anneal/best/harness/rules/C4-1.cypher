// id: C4-1
// severity: warning
// hint: give every person, system, container and component a name and a short description
MATCH (n:Item {doc: $doc})
WHERE n:Person OR n:System OR n:Container OR n:Component
WITH n, [f IN ['name', 'description'] WHERE trim(coalesce(n[f], '')) = ''] AS missing
WHERE size(missing) > 0
MATCH (e:EntityType {name: n.type})
RETURN '/' + e.key + '/' + n.id AS pointer, 'missing ' + reduce(s = '', f IN missing | s + CASE s WHEN '' THEN '' ELSE ' and ' END + f) AS detail
