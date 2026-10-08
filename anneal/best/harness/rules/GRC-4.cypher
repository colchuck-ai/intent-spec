// id: GRC-4
// severity: error
// hint: examine only procedures that operationalize the assessed control; fix examines or the procedure's operationalizes
MATCH (a:AssessmentObjective {doc: $doc})-[:ASSESSES]->(c)
MATCH (a)-[:EXAMINES]->(p:Procedure)   // an imported procedure (a :Ref) is skipped [REF-2]
WHERE NOT (p)-[:OPERATIONALIZES]->(c)
RETURN '/assessmentObjectives/' + a.id AS pointer,
       'examines ' + p.id + ', which does not operationalize ' + coalesce(c.id, c.ref) AS detail
