// id: C4-23
// severity: warning
// hint: add a container instance on a node in the diagram's environment, or list the container in notDeployed with the reason
MATCH (dg:DeploymentDiagram {doc: $doc})-[:DEPICTS]->(s:System)<-[:IN]-(c:Container {doc: $doc})
MATCH (dg)-[:COVERS]->(env)
// notDeployed is stored as a JSON string map; its keys are every 4th token when split on unescaped quotes
WITH dg, s, c, env,
     CASE WHEN dg.notDeployed IS NULL THEN []
          ELSE split(replace(replace(dg.notDeployed, '\\\\', ''), '\\"', ''), '"') END AS toks
WITH dg, s, c, env, [i IN range(0, size(toks) - 1) WHERE i % 4 = 1 | toks[i]] AS notDeployed
WHERE NOT c.id IN notDeployed
  // C4-22: a node's environment is that of the outermost node containing it
  AND NOT EXISTS {
    MATCH (ci:ContainerInstance {doc: $doc})-[:INSTANTIATES]->(c),
          (ci)-[:IN]->(:DeploymentNode)-[:IN*0..]->(root:DeploymentNode)-[:BELONGS]->(env)
    WHERE NOT EXISTS { MATCH (root)-[:IN]->() }
  }
RETURN '/deploymentDiagrams/' + dg.id AS pointer,
       'container ' + c.id + ' of ' + s.id + ' has no instance in ' + coalesce(env.id, env.ref) + ' and is not in notDeployed' AS detail
