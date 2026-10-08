// id: DFD-9
// severity: error
// hint: set leaves to the end whose element the represented relationships leave, or fix the relationships' direction
MATCH (f:DataFlow {doc: $doc})-[:LEAVES]->(e:Item)-[:REPRESENTS]->(x:Item)
MATCH (f)-[:REPRESENTS]->(r:Relationship)
WHERE NOT EXISTS { MATCH (r)-[:LEAVES]->(:Ref) }   // REF-2/REF-5
  AND NOT EXISTS { MATCH (r)-[:LEAVES]->(:Item)-[:IN*0..]->(x) }
RETURN '/dataFlows/' + f.id AS pointer,
       'leaves ' + e.id + ' (' + x.id + ') but relationship ' + r.id + ' does not leave ' + x.id + ' or an element inside it' AS detail
