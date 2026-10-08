// id: GRC-25
// severity: warning
// hint: bind this external system with a contractual influencer (e.g. a BAA or DPA) since it receives data a statutory or regulatory influencer covers
MATCH (s:System {doc: $doc})
WHERE coalesce(s.external, false)
MATCH (s)<-[:REPRESENTS]-(:ExternalEntity)<-[:CONNECTS]-(f:DataFlow)-[:CARRIES]->(e:DataElement)-[:TRIGGERS]->(i:Influencer)
WHERE any(k IN coalesce(i.kinds, []) WHERE k IN ['statutory', 'regulatory'])   // an imported influencer (a :Ref) is skipped [REF-2]
  AND NOT EXISTS { MATCH (b:Influencer)-[:BINDS]->(s) WHERE 'contractual' IN coalesce(b.kinds, []) }
WITH s, collect(DISTINCT i.id) AS triggered, collect(DISTINCT f.id) AS flows
RETURN '/systems/' + s.id AS pointer,
       'no contractual influencer binds it; flows ' + reduce(x = '', y IN flows | x + CASE x WHEN '' THEN '' ELSE ', ' END + y)
       + ' carry data triggering ' + reduce(x = '', y IN triggered | x + CASE x WHEN '' THEN '' ELSE ', ' END + y) AS detail
