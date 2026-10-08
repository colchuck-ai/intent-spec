// id: C4-21
// severity: error
// hint: an outermost deployment node belongs to exactly one environment; a node inside another takes its environment from the outermost node, so drop its belongs
MATCH (n:DeploymentNode {doc: $doc})
WITH n, EXISTS { MATCH (n)-[:IN]->() } AS contained, COUNT { (n)-[:BELONGS]->() } AS envs
WHERE (contained AND envs > 0) OR (NOT contained AND envs <> 1)
RETURN '/deploymentNodes/' + n.id AS pointer,
       CASE WHEN contained THEN 'contained node belongs to an environment'
            ELSE 'outermost node belongs to ' + toString(envs) + ' environments' END AS detail
