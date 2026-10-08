// id: GRC-24
// severity: error
// hint: only a contractual influencer binds, and only an external system or an external reference with a party (the counterparty)
MATCH (i:Influencer {doc: $doc})-[:BINDS]->(t)
WHERE NOT t:Imported   // an imported system is external [REF-5]; its fields are not visible here
WITH i, t,
     CASE
       WHEN NOT 'contractual' IN coalesce(i.kinds, []) THEN 'binds ' + coalesce(t.id, t.ref) + ' but is not contractual'
       WHEN t:System AND NOT coalesce(t.external, false) THEN 'binds internal system ' + t.id
       WHEN t:ExternalReference AND coalesce(t.party, '') = '' THEN 'binds external reference ' + t.id + ', which has no party'
     END AS problem
WHERE problem IS NOT NULL
RETURN '/influencers/' + i.id AS pointer, problem AS detail
