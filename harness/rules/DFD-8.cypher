// id: DFD-8
// severity: error
// hint: make each end of the flow represent an end of every relationship the flow represents (or the container or system enclosing it), or drop the relationship from represents
MATCH (f:DataFlow {doc: $doc})-[:REPRESENTS]->(r:Relationship)
MATCH (f)-[:CONNECTS]->(e:Item)
WHERE NOT e:ExternalReference
  // REF-2/REF-5: skip ends or relationship ends whose targets are imported
  AND NOT EXISTS { MATCH (e)-[:REPRESENTS]->(:Ref) }
  AND NOT EXISTS { MATCH (r)-[:LEAVES|ENTERS]->(:Ref) }
  // the relationship's end, or something it is inside (component in container in system), is what e represents
  AND NOT EXISTS { MATCH (e)-[:REPRESENTS]->(x)<-[:IN*0..]-(:Item)<-[:LEAVES|ENTERS]-(r) }
RETURN '/dataFlows/' + f.id AS pointer,
       'end ' + e.id + ' represents no end of relationship ' + r.id + ' or element containing one' AS detail
