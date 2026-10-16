# Resolving references across a document and the documents it imports.
#
# Input: {document, imports: {alias: doc}}. The caller fetches each imported document;
# there is no lockfile. A scope names the document an id is read in: "" for the
# document being checked, or an import alias.
#
# data.model (generated from erd.md for the spike; from the JSON Schema later) gives
# the item types (keys) and which fields of each type are links.
package intent.lib.ref

import rego.v1

doc(scope) := input.document if scope == ""

doc(scope) := input.imports[scope] if scope != ""

scopes := {""} | {alias | some alias, _ in input.imports}

# index[scope][id] = {"key": "controls", "item": {...}}. Ids are document-unique (INV-3),
# so one id names one item in its document.
index[scope][id] := {"key": key, "item": item} if {
	some scope in scopes
	some key, _ in data.model.types
	some id, item in doc(scope)[key]
}

pointer(key, id) := sprintf("/%s/%s", [key, id])

# Resolve a reference read in a scope to {scope, id, key, item}. An alias:id read in the
# checked document resolves into that import. An alias:id read inside an imported document
# names one of *its* imports, which the flat input shape does not carry, so it stays
# unresolved (spike gap: transitive imports).
resolve(scope, ref) := {"scope": scope, "id": ref, "key": e.key, "item": e.item} if {
	not contains(ref, ":")
	e := index[scope][ref]
}

resolve("", ref) := {"scope": alias, "id": id, "key": e.key, "item": e.item} if {
	[alias, id] := split(ref, ":")
	e := index[alias][id]
}

# A stable key for a resolved item, usable as a set member or graph node.
key(t) := sprintf("%s|%s", [t.scope, t.id])

# The references a link field holds, as a list, whether the link is to-one or to-many.
refs(item, field) := v if {
	is_array(item[field])
	v := item[field]
}

refs(item, field) := [item[field]] if is_string(item[field])

# DOC-2: an item's stage is its own stage, or else its document's stage.
stage(_, item) := item.stage

stage(scope, item) := doc(scope).stage if not item.stage

# Every link in the checked document: {key, id, item, verb, ref}.
links contains {"key": key, "id": id, "item": item, "verb": verb, "ref": ref} if {
	some key, verbs in data.model.links
	some id, item in input.document[key]
	some verb in verbs
	some ref in refs(item, verb)
}
