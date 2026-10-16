# Collects every rule's violations into one report, applying ruleWaivers.
#
# Each rule is a `violation contains finding(rego.metadata.rule(), pointer, detail)` body
# in its area package, annotated with OPA METADATA (title = rule ID, description, and
# custom.severity, custom.hint).
package intent.report

import rego.v1

finding(meta, pointer, detail) := {
	"rule": meta.title,
	"severity": meta.custom.severity,
	"hint": meta.custom.hint,
	"pointer": pointer,
	"detail": detail,
}

# Resolution problems (REF-1) come from the graph; everything else from the rules.
# As in a compiler, rules run only on a document whose references all resolve: a link
# that names nothing is missing from the graph, and rules would report the gap again.
all := data.intent.graph.violation if count(data.intent.graph.violation) > 0

all := {f | some f in data.intent.rules[_].violation} if count(data.intent.graph.violation) == 0

# The rationale an item gives for waiving a rule, found by the finding's pointer.
# Only warnings can be waived; DOC-3 reports a waiver of an error rule.
rationale(f) := r if {
	f.severity == "warning"
	[_, type, id] := split(f.pointer, "/")
	r := input.documents[input.document][type][id].ruleWaivers[f.rule]
}

waived contains object.union(f, {"rationale": rationale(f)}) if some f in all

findings contains f if {
	some f in all
	not rationale(f)
}

errors := count({f | some f in findings; f.severity == "error"})
