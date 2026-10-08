// id: DFD-3
// severity: warning
// hint: model the depicted system as processes and data stores, not as an external entity; represent another system or a person instead
MATCH (d:DataFlowDiagram {doc: $doc})-[:INCLUDES]->(ee:ExternalEntity)-[:REPRESENTS]->(s:System)
WHERE EXISTS { MATCH (d)-[:DEPICTS]->(s) }
   OR EXISTS { MATCH (d)-[:DEPICTS]->(:Container)-[:IN]->(s) }
RETURN '/externalEntities/' + ee.id AS pointer,
       'represents ' + s.id + ', the system that ' + d.id + ' depicts' AS detail
