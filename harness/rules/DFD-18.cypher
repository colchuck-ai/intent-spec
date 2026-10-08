// id: DFD-18
// severity: warning
// hint: make the process represent a container of the depicted system, a component of the depicted container, or an infrastructure node in an environment that hosts the system; or connect it by a shown flow to a process that does
// A process is anchored when it represents a container of the depicted system, a component of the
// depicted container, or an infrastructure node on a node whose environment (C4-22: that of the
// outermost node containing it) hosts an instance of sys (the depicted system, or the depicted
// container's system) or of one of sys's containers.
MATCH (d:DataFlowDiagram {doc: $doc})-[:DEPICTS]->(t:Item)
WHERE d.level = 'detail'
OPTIONAL MATCH (t)-[:IN]->(cs:System)
WITH d, t, CASE WHEN t:System THEN t ELSE cs END AS sys
MATCH (d)-[:INCLUDES]->(p:Process)
WHERE NOT EXISTS { MATCH (p)-[:REPRESENTS]->(:Ref) }   // REF-2: skip imported targets
  AND NOT (
       EXISTS { MATCH (p)-[:REPRESENTS]->(c:Container)-[:IN]->(t) WHERE t:System }
    OR EXISTS { MATCH (p)-[:REPRESENTS]->(:Component)-[:IN]->(t) WHERE t:Container }
    OR EXISTS {
         MATCH (p)-[:REPRESENTS]->(:InfrastructureNode)-[:IN]->(:DeploymentNode)-[:IN*0..]->(top:DeploymentNode)-[:BELONGS]->(env:Environment)
         WHERE NOT EXISTS { MATCH (top)-[:IN]->(:DeploymentNode) }
           AND EXISTS {
             MATCH (env)<-[:BELONGS]-(top2:DeploymentNode)<-[:IN*0..]-(:DeploymentNode)<-[:IN]-(i)-[:INSTANTIATES]->(y)
             WHERE NOT EXISTS { MATCH (top2)-[:IN]->(:DeploymentNode) }
               AND ((i:SystemInstance AND y = sys) OR (i:ContainerInstance AND EXISTS { MATCH (y)-[:IN]->(sys) }))
           }
       }
    // or it connects a shown data flow (DFD-20: the DFD includes both ends) to an anchored process
    OR EXISTS {
         MATCH (p)<-[:CONNECTS]-(:DataFlow)-[:CONNECTS]->(q:Process)
         WHERE q <> p AND EXISTS { MATCH (d)-[:INCLUDES]->(q) }
           AND (
                EXISTS { MATCH (q)-[:REPRESENTS]->(:Ref) }
             OR EXISTS { MATCH (q)-[:REPRESENTS]->(c:Container)-[:IN]->(t) WHERE t:System }
             OR EXISTS { MATCH (q)-[:REPRESENTS]->(:Component)-[:IN]->(t) WHERE t:Container }
             OR EXISTS {
                  MATCH (q)-[:REPRESENTS]->(:InfrastructureNode)-[:IN]->(:DeploymentNode)-[:IN*0..]->(top:DeploymentNode)-[:BELONGS]->(env:Environment)
                  WHERE NOT EXISTS { MATCH (top)-[:IN]->(:DeploymentNode) }
                    AND EXISTS {
                      MATCH (env)<-[:BELONGS]-(top2:DeploymentNode)<-[:IN*0..]-(:DeploymentNode)<-[:IN]-(i)-[:INSTANTIATES]->(y)
                      WHERE NOT EXISTS { MATCH (top2)-[:IN]->(:DeploymentNode) }
                        AND ((i:SystemInstance AND y = sys) OR (i:ContainerInstance AND EXISTS { MATCH (y)-[:IN]->(sys) }))
                    }
                }
           )
       }
  )
RETURN '/dataFlowDiagrams/' + d.id AS pointer,
       'process ' + p.id + ' represents nothing in the depicted ' + toLower(t.type) + ' and connects no shown flow to a process that does' AS detail
