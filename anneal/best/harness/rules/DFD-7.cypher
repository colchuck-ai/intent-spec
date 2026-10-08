// id: DFD-7
// severity: error
// hint: set leaves to one of the flow's connects ends, or omit it when the origin is unknown
MATCH (f:DataFlow {doc: $doc})-[:LEAVES]->(x)
WITH f, collect(x) AS xs
WITH f, xs, [x IN xs WHERE NOT EXISTS { MATCH (f)-[:CONNECTS]->(x) } | coalesce(x.id, x.ref)] AS strays
WHERE size(xs) > 1 OR size(strays) > 0
RETURN '/dataFlows/' + f.id AS pointer,
       CASE WHEN size(xs) > 1 THEN 'leaves ' + size(xs) + ' ends'
            ELSE 'leaves ' + strays[0] + ', which it does not connect' END AS detail
