// id: C4-19
// severity: error
// hint: at this diagram's level both ends of the step's relationship lift to the same element; follow a relationship that crosses the diagram's level, or change what the diagram depicts
MATCH (st:DynamicStep {doc: $doc})-[:IN]->(dd:DynamicDiagram)
MATCH (st)-[:FOLLOWS]->(r:Relationship)-[:LEAVES]->(s), (r)-[:ENTERS]->(t)
OPTIONAL MATCH (dd)-[:DEPICTS]->(dsys:System)
OPTIONAL MATCH (dd)-[:DEPICTS]->(dcon:Container)
WITH st, dd, dsys, dcon, [s, t] AS ends
// C4-12 lifting to the diagram's level:
// a component stays when the diagram depicts its container, otherwise it lifts to its container;
// a container stays when the diagram depicts its system or any container, otherwise it lifts to its system.
WITH st, dd, [e IN ends |
  CASE WHEN e:Component AND dcon IS NOT NULL AND EXISTS { MATCH (e)-[:IN]->(dcon) } THEN e
       WHEN e:Component THEN head([(e)-[:IN]->(c) | c])
       ELSE e END] AS step1, dsys, dcon
WITH st, dd, [e IN step1 |
  CASE WHEN e:Container AND (dcon IS NOT NULL OR (dsys IS NOT NULL AND EXISTS { MATCH (e)-[:IN]->(dsys) })) THEN e
       WHEN e:Container THEN head([(e)-[:IN]->(x) | x])
       ELSE e END] AS drawn
WHERE drawn[0] IS NOT NULL AND drawn[0] = drawn[1]
RETURN '/dynamicSteps/' + st.id AS pointer,
       'both ends are drawn as ' + coalesce(drawn[0].id, drawn[0].ref) + ' in ' + dd.id AS detail
