// id: DFD-17
// severity: error
// hint: a context-level DFD depicts a system and includes exactly one process representing that system; use level detail otherwise
MATCH (d:DataFlowDiagram {doc: $doc})
WHERE d.level = 'context'
OPTIONAL MATCH (d)-[:DEPICTS]->(t)
WITH d, collect(t) AS ts
OPTIONAL MATCH (d)-[:INCLUDES]->(p:Process)
WITH d, ts, collect(p) AS ps,
     EXISTS { MATCH (d)-[:INCLUDES]->(:Ref) } AS unknown   // REF-2: an imported element may be a process
WITH d, ts, ps, unknown, head(ps) AS p0
WITH d, ps,
  CASE
    WHEN any(t IN ts WHERE t:Container) THEN 'depicts a container, not a system'
    WHEN NOT unknown AND size(ps) <> 1 THEN 'includes ' + size(ps) + ' processes, not exactly one'
    WHEN size(ps) = 1 AND any(t IN ts WHERE t:System)
         AND NOT EXISTS { MATCH (p0)-[:REPRESENTS]->(s) WHERE s IN ts }
      THEN 'process ' + p0.id + ' does not represent the depicted system'
  END AS problem
WHERE problem IS NOT NULL
RETURN '/dataFlowDiagrams/' + d.id AS pointer, problem AS detail
