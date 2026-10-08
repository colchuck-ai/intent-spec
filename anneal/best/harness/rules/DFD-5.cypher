// id: DFD-5
// severity: error
// hint: a data store represents a data-store container; use a process for an application container
MATCH (ds:DataStore {doc: $doc})-[:REPRESENTS]->(c:Container)
WHERE coalesce(c.kind, '') <> 'data-store'
RETURN '/dataStores/' + ds.id AS pointer,
       'represents container ' + c.id + ' of kind ' + coalesce(c.kind, '(none)') AS detail
