// id: GRC-2
// severity: warning
// hint: link the policy to the influencer it answers with satisfies, or remove the policy
MATCH (p:Policy {doc: $doc})
WHERE NOT EXISTS { MATCH (p)-[:SATISFIES]->() }
RETURN '/policies/' + p.id AS pointer, 'policy satisfies no influencer' AS detail
