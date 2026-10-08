// id: C4-4
// severity: error
// hint: remove the containers from the external system, or make the system internal
MATCH (s:System {doc: $doc})<-[:IN]-(c:Container {doc: $doc})
WHERE coalesce(s.external, false)
RETURN '/systems/' + s.id AS pointer, 'external system contains container ' + c.id AS detail
