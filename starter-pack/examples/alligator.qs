# QuickStatements v1 (tab-separated) -- ILLUSTRATIVE, untested.
# Target: Wikidata property IDs. For the new Wikibase replace Pxxx by the local property IDs
# (see data/wikibase-property-set.csv, column wikidata_pid -> local ID after creation).
# Evidence: open-archaeo row 2f00c7 (sources/open-archaeo-software.csv). Nothing here is live-verified.
# Before running: search Wikidata for an existing "Alligator" item and reconcile by P1324 (repository URL) first.
CREATE
LAST	Len	"Alligator"
LAST	Den	"chublet: statistical analysis and ontology tool"
LAST	P31	Q141115627
LAST	P31	Q166142
LAST	P6104	Q141169143
LAST	P361	Q141115774
LAST	P361	Q141190255
LAST	P195	Q141190255
LAST	P217	"alligator"	P195	Q141190255
LAST	P2888	"https://open-archaeo.info/post/alligator/"
LAST	P1324	"https://github.com/leiza-rse/alligator"	P8423	Q186055
LAST	P856	"https://tools.leiza.de/alligator/"
# archive URL and date (Internet Archive item, 2021-06-04); P1065 qualified by P2960
LAST	P1065	"https://archive.org/details/github.com-RGZM-alligator_-_2021-06-04_01-29-28"	P2960	+2021-06-04T00:00:00Z/11
# developers: Q66606154 (Florian Thiery), Q88865971 (Allard W. Mees) -- verify both Q-IDs before use
LAST	P178	Q66606154	P1545	"1"
LAST	P178	Q88865971	P1545	"2"
# TODO main subject (P921): "Statistical analysis", "Schemas and ontologies" -- items unresolved
