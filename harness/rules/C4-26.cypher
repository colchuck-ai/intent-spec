// id: C4-26
// severity: error
// hint: give each step in a dynamic diagram a different order
MATCH (st:DynamicStep {doc: $doc})-[:IN]->(dd:DynamicDiagram)
WITH dd, st.order AS ord, collect(st) AS steps
WHERE ord IS NOT NULL AND size(steps) > 1
UNWIND steps AS st
RETURN '/dynamicSteps/' + st.id AS pointer,
       'order ' + toString(ord) + ' is shared by ' + toString(size(steps)) + ' steps in ' + dd.id AS detail
