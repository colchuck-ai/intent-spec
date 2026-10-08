// id: RISK-15
// severity: error
// hint: only an accept treatment waives standards or procedures; remove waives or change the strategy to accept
// The second clause (a waiver applies only within the products the treatment applies to [RISK-17]) bounds what a
// waiver means; it constrains no stored link, so rules that read waivers (GRC-16, GRC-21) apply RISK-17 themselves.
MATCH (t:Treatment {doc: $doc})-[:WAIVES]->(x)
WHERE coalesce(t.strategy, '') <> 'accept'
RETURN '/treatments/' + t.id AS pointer,
       coalesce(t.strategy, '(no strategy)') + ' treatment waives ' + coalesce(x.id, x.ref) AS detail
