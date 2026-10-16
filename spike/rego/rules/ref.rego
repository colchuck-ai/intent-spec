# References: rules every link obeys, in every layer (spike: REF-3).
package intent.rules.ref

import data.intent.lib.ref
import data.intent.report.finding
import rego.v1

# METADATA
# title: REF-3
# description: >-
#   A ratified item does not link to a proposed item [DOC-2]. Imports are followed: an
#   alias:id target's stage is its own, or else its document's. A target that resolves to
#   no item is skipped (REF-1), and so is an external reference, which has no stage.
# custom:
#   severity: error
#   hint: ratify the target too, or keep the linking item proposed
violation contains finding(rego.metadata.rule(), ref.pointer(l.key, l.id), detail) if {
	some l in ref.links
	ref.stage("", l.item) == "ratified"
	t := ref.resolve("", l.ref)
	t.key != "externalReferences"
	ref.stage(t.scope, t.item) == "proposed"
	detail := sprintf("%s -> %s, which is proposed", [l.verb, l.ref])
}
