// id: DFD-19
// severity: warning
// hint: include the other end of one of the element's data flows in the DFD, or drop the element from includes
MATCH (d:DataFlowDiagram {doc: $doc})-[:INCLUDES]->(e:Item)
WHERE (e:DataStore OR e:ExternalEntity)
  // DFD-20: a DFD shows a data flow when it includes both of the flow's ends
  AND NOT EXISTS {
    MATCH (e)<-[:CONNECTS]-(f:DataFlow)
    WHERE NOT EXISTS { MATCH (f)-[:CONNECTS]->(z) WHERE NOT EXISTS { MATCH (d)-[:INCLUDES]->(z) } }
  }
RETURN '/dataFlowDiagrams/' + d.id AS pointer, e.id + ' connects no data flow the DFD shows' AS detail
