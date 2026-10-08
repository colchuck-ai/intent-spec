// id: DFD-6
// severity: error
// hint: list exactly two different ends in connects, at least one of them a process
MATCH (f:DataFlow {doc: $doc})
OPTIONAL MATCH (f)-[r:CONNECTS]->(t)
WITH f, count(r) AS n, count(DISTINCT t) AS nd,
     sum(CASE WHEN t:Process THEN 1 ELSE 0 END) AS np,
     // REF-2/REF-5: an imported or external end may be a process; don't judge it
     sum(CASE WHEN t:Ref OR t:ExternalReference THEN 1 ELSE 0 END) AS nx
WHERE n <> 2 OR nd <> 2 OR (np = 0 AND nx = 0)
RETURN '/dataFlows/' + f.id AS pointer,
       CASE WHEN n <> 2 THEN 'connects ' + n + ' ends, not 2'
            WHEN nd <> 2 THEN 'connects the same end twice'
            ELSE 'neither end is a process' END AS detail
