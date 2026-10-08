// id: C4-24
// severity: error
// hint: list in notDeployed only containers of a depicted system that have no instance in the diagram's environment
MATCH (dg:DeploymentDiagram {doc: $doc})-[:COVERS]->(env)
WHERE dg.notDeployed IS NOT NULL
// notDeployed is stored as a JSON string map; its keys are every 4th token when split on unescaped quotes
WITH dg, env, split(replace(replace(dg.notDeployed, '\\\\', ''), '\\"', ''), '"') AS toks
UNWIND [i IN range(0, size(toks) - 1) WHERE i % 4 = 1 | toks[i]] AS key
WITH dg, env, key
WHERE NOT key CONTAINS ':'   // REF-2, REF-5: imported targets are not inspected
OPTIONAL MATCH (c:Container {doc: $doc, id: key})
WITH dg, env, key, c,
     c IS NOT NULL AND EXISTS { MATCH (dg)-[:DEPICTS]->(:System)<-[:IN]-(c) } AS depicted,
     c IS NOT NULL AND EXISTS {
       // C4-22: a node's environment is that of the outermost node containing it
       MATCH (ci:ContainerInstance {doc: $doc})-[:INSTANTIATES]->(c),
             (ci)-[:IN]->(:DeploymentNode)-[:IN*0..]->(root:DeploymentNode)-[:BELONGS]->(env)
       WHERE NOT EXISTS { MATCH (root)-[:IN]->() }
     } AS deployed
WHERE NOT depicted OR deployed
RETURN '/deploymentDiagrams/' + dg.id AS pointer,
       'notDeployed key ' + key + CASE
         WHEN c IS NULL THEN ' is not a container'
         WHEN NOT depicted THEN ' is not a container of a depicted system'
         ELSE ' has an instance in ' + coalesce(env.id, env.ref) END AS detail
