// id: RISK-13
// severity: error
// hint: link a control or requirement to the treatment with executes, or change its strategy
MATCH (t:Treatment {doc: $doc, strategy: 'reduce'})
WHERE NOT EXISTS { MATCH (x)-[:EXECUTES]->(t) WHERE x:Control OR x:Requirement }
RETURN '/treatments/' + t.id AS pointer, 'reduce treatment executed by no control or requirement' AS detail
