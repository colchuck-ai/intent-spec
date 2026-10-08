// id: GRC-1
// severity: error
// hint: a statutory, regulatory or contractual influencer cites its one source (the law, regulation or contract); set cites
MATCH (i:Influencer {doc: $doc})
WHERE any(k IN coalesce(i.kinds, []) WHERE k IN ['statutory', 'regulatory', 'contractual'])
WITH i, COUNT { (i)-[:CITES]->() } AS n
WHERE n <> 1
RETURN '/influencers/' + i.id AS pointer, 'cites ' + n + ' sources, needs exactly one' AS detail
