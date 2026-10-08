// id: GRC-18
// severity: warning
// hint: set derives to the external reference for the CIS benchmark, DISA STIG or vendor hardening guide it follows
// Whether a reference is such a source is free text, so this checks for a derives link and, for a local
// external reference, a title that names a benchmark, STIG, guide or baseline. Imported targets are skipped (REF-2).
MATCH (b:SecureBaseline {doc: $doc})
OPTIONAL MATCH (b)-[:DERIVES]->(x)
WITH b, x
WHERE x IS NULL
   OR (x:ExternalReference AND NOT coalesce(x.title, '') =~ '(?i).*\\b(CIS|STIG|benchmark|guide|guidance|baseline|hardening)\\b.*')
RETURN '/secureBaselines/' + b.id AS pointer,
       CASE WHEN x IS NULL THEN 'derives from nothing'
            ELSE 'derives from ' + x.id + ', which does not read as a CIS benchmark, DISA STIG or vendor guide' END AS detail
