# Rubric: rule-query

For each rule under the element that has a query in `harness/rules/<ID>.cypher`, read the statement and the query. Fail if any answer is no.

1. Does the query report a row for every case the statement forbids?
2. Does it report no row for any case the statement allows?
3. Does the query apply the derivations the statement cites ([ID]) the way the derivation states them?
4. Does the rule's invalid example break the rule in the way the statement describes, not by an accident of the query?

Quote the statement and the query lines that disagree.
