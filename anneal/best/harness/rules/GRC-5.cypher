// id: GRC-5
// severity: warning
// hint: add an assessment objective that assesses this control
MATCH (c:Control {doc: $doc})
WHERE NOT EXISTS { MATCH (:AssessmentObjective {doc: $doc})-[:ASSESSES]->(c) }
RETURN '/controls/' + c.id AS pointer, 'control is assessed by no assessment objective' AS detail
