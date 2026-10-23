# Local ids for this repository, made by tools/qs_to_local.py from starter-pack/examples/alligator.qs.
# A template for apply-qs: the item may exist already, then this would create a second one. Check the ids in data/csv/ first.
# QuickStatements v1 (tab-separated) -- ILLUSTRATIVE, untested.
# Target: Wikidata property IDs. For the new Wikibase replace Pxxx by the local property IDs
# (see data/wikibase-property-set.csv, column wikidata_pid -> local ID after creation).
# Evidence: open-archaeo row 2f00c7 (sources/open-archaeo-software.csv). Nothing here is live-verified.
# Before running: search Wikidata for an existing "Alligator" item and reconcile by P1324 (repository URL) first.
CREATE
LAST	Len	"Alligator"
LAST	Den	"chublet: statistical analysis and ontology tool"
LAST	P2	Q106
LAST	P2	Q102
LAST	P118	Q108
LAST	P122	Q109
LAST	P122	Q110
LAST	P106	Q110
LAST	P116	"alligator"	P106	Q110
LAST	P115	"https://open-archaeo.info/post/alligator/"
LAST	P125	"https://github.com/leiza-rse/alligator"	P126	Q114
LAST	P120	"https://tools.leiza.de/alligator/"
# archive URL and date (Internet Archive item, 2021-06-04); P1065 qualified by P2960
LAST	P105	"https://archive.org/details/github.com-RGZM-alligator_-_2021-06-04_01-29-28"	P104	+2021-06-04T00:00:00Z/11
# developers: Q66606154 (Florian Thiery), Q88865971 (Allard W. Mees) -- verify both Q-IDs before use
LAST	P113	Q365	P146	"1"
LAST	P113	Q374	P146	"2"
# TODO main subject (P921): "Statistical analysis", "Schemas and ontologies" -- items unresolved
