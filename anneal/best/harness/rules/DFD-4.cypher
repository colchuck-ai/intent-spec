// id: DFD-4
// severity: error
// hint: a process represents an internal system or an application container; use an external entity for an external system, a data store for a data-store container
MATCH (p:Process {doc: $doc})-[:REPRESENTS]->(x:Item)
WHERE (x:System AND coalesce(x.external, false) = true)
   OR (x:Container AND coalesce(x.kind, '') <> 'application')
RETURN '/processes/' + p.id AS pointer,
       CASE WHEN x:System THEN 'represents external system ' + x.id
            ELSE 'represents container ' + x.id + ' of kind ' + coalesce(x.kind, '(none)') END AS detail
