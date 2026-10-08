// id: PRODUCT-3
// severity: warning
// hint: add a job whose motivates link names this executor, or remove the executor
MATCH (e:JobExecutor {doc: $doc})
WHERE NOT EXISTS { MATCH (:Job {doc: $doc})-[:MOTIVATES]->(e) }
RETURN '/jobExecutors/' + e.id AS pointer, 'no job motivates this executor' AS detail
