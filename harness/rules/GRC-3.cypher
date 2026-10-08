// id: GRC-3
// severity: error
// hint: verify only standards the assessed control enforces; add the standard to the control's enforces or drop it from verifies
MATCH (a:AssessmentObjective {doc: $doc})-[:ASSESSES]->(c:Control)   // an imported control (a :Ref) is skipped [REF-2]
MATCH (a)-[:VERIFIES]->(s)
WHERE NOT (c)-[:ENFORCES]->(s)
RETURN '/assessmentObjectives/' + a.id AS pointer,
       'verifies ' + coalesce(s.id, s.ref) + ', which control ' + c.id + ' does not enforce' AS detail
