# Resolve: turn the fetched documents into one graph that rules read.
#
# Input: {document: <id>, documents: {<id>: doc}, aliases: {<id>: {<alias>: <id>}}}
#   document   the id of the document being checked
#   documents  it and every document it imports, transitively, one version each
#   aliases    per document, which fetched document each of its import aliases names
#
# Output, for rules:
#   items[gid]  {doc, type, id, stage, item, links: [{verb, to, ref}]}
#               gid is "<doc>:<id>"; type is the item type key (e.g. "controls");
#               stage is resolved (DOC-2) and absent on external references;
#               every link's `to` is the gid of a resolved item
#   unresolved  every reference in the checked document that names nothing (REF-1)
#
# Only this package reads aliases, raw link fields or data.model. Rules never do.
package intent.graph

import data.intent.report.finding
import rego.v1

gid(doc, id) := sprintf("%s:%s", [doc, id])

pointer(gid) := sprintf("/%s/%s", [items[gid].type, items[gid].id])

local(gid) if items[gid].doc == input.document

# The gids a link of an item points to, as a set.
out(gid, verb) := {l.to | some l in items[gid].links; l.verb == verb}

# Items of one type: in any fetched document, or in the checked document only (REF-5).
of(type) := object.get(by_type, type, set())

local_of(type) := {g | some g in of(type); local(g)}

by_type[x.type] contains g if some g, x in items

# ---- resolution

raw[gid(doc, id)] := {"doc": doc, "type": type, "id": id, "item": item} if {
	some doc, d in input.documents
	some type, _ in data.model.types
	some id, item in d[type]
}

# A reference read in a document: an id in the same document, or alias:id in an import.
target(doc, ref) := gid(doc, ref) if {
	not contains(ref, ":")
	raw[gid(doc, ref)]
}

target(doc, ref) := gid(input.aliases[doc][alias], id) if {
	[alias, id] := split(ref, ":")
	raw[gid(input.aliases[doc][alias], id)]
}

refs(item, field) := item[field] if is_array(item[field])

refs(item, field) := [item[field]] if is_string(item[field])

link_refs(x) := [{"verb": verb, "ref": ref} |
	some verb in data.model.links[x.type]
	some ref in refs(x.item, verb)
]

# DOC-2: an item's stage is its own stage, or else its document's stage.
stage(x) := x.item.stage

stage(x) := input.documents[x.doc].stage if not x.item.stage

items[g] := object.union(
	{"doc": x.doc, "type": x.type, "id": x.id, "item": x.item, "links": links},
	{"stage": stage(x) | x.type != "externalReferences"},
) if {
	some g, x in raw
	links := [object.union(l, {"to": target(x.doc, l.ref)}) | some l in link_refs(x); target(x.doc, l.ref)]
}

# An alias:id is unresolved when its alias is not declared in imports, or its document
# was fetched and declares no such id. An import the caller could not fetch is not
# reported here (as in the harness).
unresolved contains {"gid": g, "verb": l.verb, "ref": l.ref, "in": where} if {
	some g, x in raw
	x.doc == input.document
	some l in link_refs(x)
	not target(x.doc, l.ref)
	where := missing(x.doc, l.ref)
}

missing(_, ref) := "" if not contains(ref, ":")

missing(doc, ref) := "" if {
	[alias, _] := split(ref, ":")
	not input.documents[doc].imports[alias]
}

missing(doc, ref) := sprintf(" in %s", [input.aliases[doc][alias]]) if {
	[alias, _] := split(ref, ":")
	input.aliases[doc][alias]
}

# METADATA
# title: REF-1
# description: A link not drawn to EXTERNAL_REFERENCE resolves to a local or imported item.
# custom:
#   severity: error
#   hint: point the link at an item declared in this document, or at alias:id for an alias in imports whose document declares that id
violation contains finding(rego.metadata.rule(), pointer(u.gid), detail) if {
	some u in unresolved
	detail := sprintf("%s -> %s does not resolve%s", [u.verb, u.ref, u["in"]])
}
