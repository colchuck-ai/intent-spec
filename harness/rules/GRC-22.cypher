// id: GRC-22
// severity: warning
// hint: add a control that achieves this control objective
MATCH (o:ControlObjective {doc: $doc})
WHERE NOT EXISTS { MATCH (:Control {doc: $doc})-[:ACHIEVES]->(o) }
RETURN '/controlObjectives/' + o.id AS pointer, 'control objective is achieved by no control' AS detail
