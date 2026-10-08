// id: RISK-1
// severity: warning
// hint: keep appliesTo within the STRIDE-per-element set for the category (external-entity S,R; process S,T,R,I,D,E; data-store T,R,I,D; data-flow T,I,D), or give the threat a rationale
WITH {
  spoofing: ['external-entity', 'process'],
  tampering: ['process', 'data-store', 'data-flow'],
  repudiation: ['external-entity', 'process', 'data-store'],
  `information-disclosure`: ['process', 'data-store', 'data-flow'],
  `denial-of-service`: ['process', 'data-store', 'data-flow'],
  `elevation-of-privilege`: ['process']
} AS stride
MATCH (t:Threat {doc: $doc})
WHERE t.category <> 'other'   // category other allows any appliesTo
  AND coalesce(trim(t.rationale), '') = ''
UNWIND coalesce(t.appliesTo, []) AS kind
WITH t, kind, stride[t.category] AS allowed
WHERE allowed IS NOT NULL AND NOT kind IN allowed
RETURN '/threats/' + t.id AS pointer,
       t.category + ' does not apply to ' + kind + ' in STRIDE-per-element, and the threat gives no rationale' AS detail
