# GRC: governance, risk and compliance rules (spike: GRC-31, GRC-10).
package intent.rules.grc

import data.intent.graph as g
import data.intent.report.finding
import rego.v1

# The controls a profile's own selections include or exclude (choice).
selected(p, choice) := {c |
	some s in g.of("selections")
	g.items[s].item.choice == choice
	p in g.out(s, "in")
	some c in g.out(s, "names")
}

excluders(c) := {p | some p in g.of("profiles"); c in selected(p, "exclude")}

# Each profile's imports, minus the profiles that exclude control c.
imports_keeping(c) := {p: (g.out(p, "imports") - excluders(c)) | some p in g.of("profiles")}

# derived GRC-31: a profile includes a control when it, or a profile it imports, includes it,
# and it does not exclude it. Rego has no recursive rules, so the closure is reachability:
# from profile p, follow imports only through profiles that do not exclude c, and look
# for a profile that includes c. graph.reachable terminates on cycles (GRC-32).
includes(p) := {c |
	some q in g.of("profiles")
	some c in selected(q, "include")
	not p in excluders(c)
	some r in graph.reachable(imports_keeping(c), {p})
	c in selected(r, "include")
}

adopted[product] contains control if {
	some a in g.of("adoptions")
	some product in g.out(a, "governs")
	some control in g.out(a, "adopts")
}

# METADATA
# title: GRC-10
# description: A product has an adoption for every control that a profile it selects includes [GRC-31] (coverage).
# custom:
#   severity: error
#   hint: add an adoption (any mode) that governs the product and adopts the control, or exclude the control in a profile
violation contains finding(rego.metadata.rule(), g.pointer(product), detail) if {
	some product in g.local_of("products")
	some p in g.out(product, "selects")
	some c in includes(p)
	not c in object.get(adopted, product, set())
	detail := sprintf("no adoption of %s, which selected profile %s includes", [g.items[c].id, g.items[p].id])
}
