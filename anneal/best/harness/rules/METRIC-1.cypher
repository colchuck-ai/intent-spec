// id: METRIC-1
// severity: error
// hint: add a measures link to a control or outcome
MATCH (m:Metric {doc: $doc})
WHERE NOT EXISTS { (m)-[:MEASURES]->() }
RETURN '/metrics/' + m.id AS pointer, 'measures nothing' AS detail
