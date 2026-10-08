// id: C4-6
// severity: warning
// hint: move the components into an application container, or change the container's kind to application
MATCH (c:Container {doc: $doc})<-[:IN]-(k:Component {doc: $doc})
WHERE coalesce(c.kind, '') <> 'application'
WITH c, collect(k.id) AS comps
RETURN '/containers/' + c.id AS pointer,
       coalesce(c.kind, 'unset') + ' container contains components ' + reduce(s = '', x IN comps | s + CASE s WHEN '' THEN '' ELSE ', ' END + x) AS detail
