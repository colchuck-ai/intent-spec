// id: GRC-30
// severity: warning
// hint: the environment's operator is downstream; make the adoption delegated (delegatedTo that operator) instead of inherited
MATCH (a:Adoption {doc: $doc})-[:INHERITS]->(x:ExternalReference)
MATCH (a)-[:GOVERNS]->(prod)
MATCH (env:Environment {doc: $doc})-[:SERVES]->(prod)
WHERE x.party IS NOT NULL AND env.operator IS NOT NULL
  AND toLower(trim(x.party)) = toLower(trim(env.operator))
RETURN '/adoptions/' + a.id AS pointer,
       'inherits ' + x.id + ', whose party ' + x.party + ' operates environment ' + env.id AS detail
