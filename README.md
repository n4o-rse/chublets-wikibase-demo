# chublets-wikibase-demo

A static, read-only demonstration of the data model planned for the chublets.software Wikibase
(<https://chublets-wikibase.de>), built with [wikibase-static](https://github.com/n4o-rse/wikibase-static).
Unlike [fuzzy-sl-static](https://github.com/n4o-rse/fuzzy-sl-static), which is a copy of a Wikibase that exists,
the data here starts as **CSV tables** in `data/csv/`; `wikibase-static` turns them into Wikibase JSON and from there into
pages, a search index, RDF and a SPARQL page, with the same code as for a harvested Wikibase.

**State (S7b):** the model only. `data/csv/` holds

* the **kernel** that `wikibase-static` mixes in (Q1 Class, Q2 Property, Q3 Instance; P1 subclass of, P2 instance of,
  P3 subproperty of, P4 Wikidata equivalent, P5 formatter URL, P6 reference URL, P7 retrieved, P8 stated in, P9 domain,
  P10 range; the numbers 1 to 99 are reserved for it),
* **158 properties** (P100 to P257): 149 from the Starter Pack, the union of all CodeMeta terms and the properties of the
  WikiProject Software list, each with its Wikidata twin (`P4`), its CodeMeta terms and, for the CodeMeta-only ones,
  the Wikidata properties that come close, and nine from the WikiProject Software properties page that the pack lacked
  (P249 to P257, review of 2026-10-22),
* **7 classes** (Q100 to Q106): software, research software, application software, software library, script file,
  Little Minion and chublet, in the class tree the pack drew, each with its Wikidata twin.
  Three more classes (Q372 utility software, Q378 QGIS plugin, Q379 plug-in) are stubs taken over from Wikidata because items of the seeds
  are instances of them.

The logo (`assets/logo.png`, set in `site.yaml`) is the chublets raven.
Every entity page offers its RDF as Turtle and as JSON for download (`docs/ttl/`, `docs/json/`) and a button that copies the concept URI to the clipboard.

**All 416 software entries** from open-archaeo (S7c; first a hundred chosen in proportion to the three categories, since 2026-10-23 all of them:
248 packages and libraries, 74 scripts, 94 standalone programs), each a chublet with the identity block (instance of chublet and of its category class,
maintained by the WikiProject, part of chublets.software and of the open-archaeo collection, collection, inventory number = slug),
its authors, tags, languages, repository with archive link, registry package and links.

**Five Wikidata items** (S7d: AMT, Alligator, SPARQLing Unicorn, profileAAR, Text mining minion) as a first test of the Wikidata import, with 18 stubs for the
items they point to (15 items, 3 classes).
The pages show the model the way a Wikibase does; the RDF export additionally carries the **RDFS bridge**
(`wdt:P1 rdfs:subPropertyOf rdfs:subClassOf` and five more triples, in a section of their own in the Turtle files), so that
a reasoner or a property path reads the class tree.

**What was checked, and what was not:** on 2026-10-21 the pack's `tools/verify_wikidata.py` compared the labels and
datatypes of all 137 Wikidata properties, classes and items of the pack with live Wikidata (`background/verification-report.csv`,
source `S11`): all exist, 14 differed. The differences are resolved in the tables (twelve labels now read as on Wikidata, the
datatype of "port" is `quantity`; the report lists one class, Q88865971, that the model does not use). The 15 PIDs of the
WikiProject page that the pack did not carry were looked up (`background/lookup-missing.csv`): nine are properties of the page and are
in the model, six only appear in description texts. **Not checked:** the twins' statements beyond label and datatype, and the
`confidence` values in `background/property-set.csv`, which stay as the pack gave them. A reference on a twin says
"documented at this Wikidata page", not "retrieved on a date". The WikiProject page was last edited on 8 May 2024 and is little
maintained (`background/demo-sources.csv`, `S10`).

**Domain and range (review of 2026-10-22):** the domain (`P9`) is software (`Q100`) for the software properties and
property (`Q2`) for the three metadata properties P100 to P102; 29 properties have none (qualifier-like, or for persons only, or not tied to software).
The range (`P10`) is `Q3` (any item) for each of the 66 properties with item values and absent otherwise, because the datatype
already is the range. The classes for person, organisation, work and the like are not in the model yet; they come with the data
that needs them. P101 (CodeMeta term) and P102 (schema.org term) are `external-id` with a formatter URL, so their values are bare
names (`applicationCategory`). P102 has 71 values; eight CodeMeta terms have no schema.org term of the same meaning
and none is written. The decisions are in `background/decisions/`.

## Use

Python 3.10 or later.

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py --strict
python -m unittest discover -s tests
```

`python main.py` runs `from-csv`, `load`, `build`, `search`, `rdf` and `sparql`. It needs no network. It writes
`data/derived/` (Wikibase JSON made from the CSV), `docs/` (the pages, served by GitHub Pages) and `dist/` (the RDF
file); run it twice and `git status` stays clean. After a new release of `wikibase-static` run
`pip install --upgrade --force-reinstall --no-deps -r requirements.txt` (pip keeps an installed package of the same
version). `python main.py --strict` treats every `WARN` line (a dead internal link, a model rule broken in the CSV)
as an error; each model warning names the file and line.

`python main.py csv-fmt` puts the four tables into their canonical form (fixed column order, rows sorted by id), and
`python main.py csv-fmt --check` only reports. Edit the tables with any editor, then run `python main.py --strict` and
commit `data/`, `docs/` and `dist/` together.

## CIDOC CRM

`data/crm.csv` ties the classes of the model to CIDOC CRM without touching the tables: one row, `software` (Q100) is
`crmdig:D14` (Software, a D1 Digital Object, an E73 Information Object). Research software, application software,
software library, script file and chublet inherit it along `subclass of`; their pages say "from software". The RDF
file carries `software rdfs:subClassOf crmdig:D14_Software` and the chain D14 to D1 to E73 in a section of its own.
**Little Minion** (Q105, the pack's second parent of chublet) has no CRM class yet: its meaning is an open point
(`background/starter-pack-open-points.md`), and `load` names it as unanchored. Needs `wikibase-static` 0.7.0.

## CIDOC CRM

`data/crm.csv` ties the classes of the model to CIDOC CRM without touching the tables. `software` (Q100) is
`crmdig:D14` (Software, a D1 Digital Object, an E73 Information Object); research software, application software,
software library, script file and chublet inherit it along `subclass of`, and their pages say "from software".
**Little Minion** (Q105, the pack's second parent of chublet) hangs under the root class of the kernel, not under
`software`, so it has a row of its own, also D14. The RDF file carries `rdfs:subClassOf crmdig:D14_Software` for both and
the chain D14 to D1 to E73 in a section of its own, together with the DCAT classes of the file (`dcat:Dataset` is an E73,
`dcat:Catalog` an E31 and a D1, `dcat:Distribution` a D1) and `subclass of` / `instance of` spelled out as `rdfs:subClassOf`
and `rdf:type`, so that a reader without inference (the N4O profile) finds every class anchored.

`python main.py --strict check-crm` checks that with SHACL (pySHACL, `data/shapes-crm.ttl` of the package) on the file in
`dist/`: a class that reaches no CRM class over `rdfs:subClassOf` is a violation, one that reaches only E1 is a warning.
Needs `wikibase-static` 0.8.0.

## Where the software entries came from

`data/raw/open-archaeo-software.csv` is a copy of `out/open-archaeo-software.csv` of [open-archaeo](https://github.com/n4o-rse/open-archaeo)
(416 entries, never edited). The package imports it into the tables; without `--all` it takes a hundred in proportion to the three
categories (`--limit N` for another size), the demo keeps all of them:

```cmd
python main.py import-open-archaeo --all
python main.py --strict
```

The mapping (`data/csv/mapping/open-archaeo.csv`: which column becomes which Wikidata property, which qualifiers) and the vocabulary
(`data/csv/mapping/open-archaeo-vocabulary.csv`: tags, languages, host applications, categories and the four identity items, each with
its Wikidata item where the Starter Pack knows one) are plain tables you can edit. Rows written by the importer have `origin=open-archaeo`;
empty that cell in a row you change by hand and the next import leaves it, and the rest of its property, alone. `--limit N` and `--all`
choose the size; ids are never reused (`data/csv/idmap.csv`). Not imported, and listed in the report: the platform role "deployment"
(Mobile app, Web app: it would need classes of its own), a repository host that is not certainly Git (Bitbucket) gets no version control
system, and publications are items that carry only their DOI or URL as label (every property of the model has the domain "software").
Needs `wikibase-static` 0.9.0.

## Where the Wikidata items came from

`data/csv/seeds-wikidata.csv` lists the Wikidata items (`qid, kind, note`); `data/raw/wikidata/` holds the answers of Wikidata as they were
saved (the six items and the labels of the items they point to, 2026-10-23; never edited; the sixth, Q141818802 (QSKOS Plugin), was saved in a browser and stored with `--from-dir`). The package turns them into items:

```cmd
python main.py import-wikidata --offline
python main.py --strict
```

Without `--offline` the importer asks Wikidata which revisions changed and fetches only those (`--from-dir DIR` stores JSON files you saved in a
browser first). A Wikidata property becomes a local one through its Wikidata twin (`P4`); three have none and are listed in
`dist/wikidata-gaps.csv` and `dist/wikidata-import.txt` (genre, used by, uses). Wikidata "author" (P50) is a twin of "creator" (P171) next to P170, a
decision of 2026-10-23. The column `instance_of` of the seed list (here `Q106`, chublet) makes every seed a chublet, also those that Wikidata calls only software or Little Minion. Items the seeds point to become stubs with label, description and their Wikidata twin; three types without a local twin
(utility software, plug-in, QGIS plugin) become classes below software, which is an assumption of the importer. Rows written by the importer have
`origin=wikidata` or `wikidata-stub`; empty that cell in a row you change by hand and the next import leaves it alone. The report also says which
repository and exact-match URLs occur in the open-archaeo items; it merges nothing. With all 416 entries it finds two of the five: profileAAR
by its repository URL and Alligator by the open-archaeo page that Wikidata names as exact match; the two pairs are merged (see below).
Needs `wikibase-static` 0.14.0.

## Merged items

Alligator and profileAAR came twice, once from Wikidata and once from open-archaeo, and so did three people (Florian Thiery, Ronald Visser,
Allard Mees: an open-archaeo account name and a Wikidata stub) and two languages. `data/csv/merges.csv` merges the open-archaeo items into the Wikidata items,
made with `python main.py merge Q381 Q359` (`--dry-run`, `--list`, `--undo Q381`). `python main.py merge --suggest` finds such pairs by
name and writes `dist/merge-suggestions.csv`; the two languages Python and JavaScript (open-archaeo item and Wikidata stub) are merged
as well, so the list is empty now.
The tables are not changed; the merge is applied when the tables are read, so the importers can run again without undoing it.
The merged items keep their ids as redirects (their pages forward, the RDF says `owl:sameAs`). Different values of one property, such
as two repository URLs for Alligator (the project moved from RGZM to leiza-rse) or the authors that exist as items from both sources,
are all kept; the run names the properties. Needs `wikibase-static` 0.14.0.

## Changes with QuickStatements

`python main.py apply-qs data/edits/FILE.qs` changes the tables with a QuickStatements file (a subset of v1, local ids, `wd:Q42` for
Wikidata; all or nothing per file; `--dry-run` says what would happen). `data/edits/applied.csv` remembers the hash of every applied
file, so the same file does not act twice. The first file, `data/edits/2026-10-23-amt-inception.qs`, adds the year 2017 as inception of
the Academic Meta Tool (Q358) with a reference; it comes from `examples/amt-sketch.qs` of the Starter Pack. Rows made this way have no
origin: they count as hand work and the importers never overwrite them. Needs `wikibase-static` 0.15.0.

## Chublets and the class hierarchy

Everything that is software is an instance of chublet (Q106): the 416 open-archaeo entries and the Wikidata seeds from their importers, and
by hand (`data/edits/2026-10-23-chublets-everywhere.qs`, applied with `apply-qs`) the host programs (QGIS, ArcGIS, Blender, ...), the
programming languages (R, Python, ...) and the platforms Git and GitHub. Persons, accounts, organisations, topics, DOIs, licences, the
language English, Wikidata and the three project items are not chublets. A new import brings new host programs and languages without that
line: they need a line in a new `.qs` file (`python main.py apply-qs`).

The overview shows, under every class, the whole hierarchy around it (all paths from the root down to the class, the class in bold, all
subclasses below), and the class pages show it as well. Needs `wikibase-static` 0.17.0.

## Source rows

Every entity page has a tab "Source rows" next to "Read": it opens the rows of `entities.csv`, `statements.csv`, `qualifiers.csv`,
`references.csv` and `merges.csv` that the page is made from, as they stand in the files, with a button that copies them and a link to the
file in the GitHub editor (`edit_url` in `site.yaml`). Nothing can be changed on the page; the link leads to GitHub, and the change comes
with the next build. Needs `wikibase-static` 0.16.0.

## Where the model came from

`tools/import_pack.py` made the tables once from the unzipped Starter Pack (v1.1, which adds the published ConnOSS crosswalk as source `S9`; the model is the same as in v1.0, only `background/` changed):

```cmd
python tools/import_pack.py starter-pack
```

The pack itself lies in `starter-pack/` since 2026-10-23, as it was delivered (v1.1, with its own README; its licence is still undecided,
`background/starter-pack-open-points.md`, point 7). `starter-pack/examples-local/` has its three QuickStatements examples with local ids,
made by `python tools/qs_to_local.py`; they are templates for `apply-qs` (Alligator exists already as Q359, so applying that file would
make a second item) and a test applies them to a copy of the tables.

It is kept for the record. **Since the review of 2026-10-22 the tables are maintained by hand; do not run it again** (it would overwrite the
reviewed rows). It can be run again against a changed pack: it reads `data/csv/idmap.csv` first, so the same pack row gets the same
number, and it writes the same files (`--check` writes nothing and exits 1 when a file would change). Run it against a
changed pack and then look at `git diff` before committing; hand edits to the imported rows are overwritten, so edit
the tables directly from now on and do not run the script again unless the pack changes.

Four rows of the pack are kernel properties and get no new number: "equivalent Wikidata property" is P4,
"instance of" is P2, "subclass of" is P1 and "retrieved" is P7. `background/` keeps the pack's own rows with the local
id (`property-set.csv`, `classes.csv`), the source codes and the pack's open points.

Numbers from 100 on are given once and never reused (`data/csv/idmap.csv`). The real Wikibase will mint its own
numbers for them; only the kernel has the same ones in both places. For that reason the RDF export uses the address of
this demo as base (`rdf_base` in `site.yaml`), not the address of the real Wikibase.

## Publishing

`.github/workflows/site.yml` runs on every push and pull request: `python main.py --strict` twice, with `git status`
required to be clean after each run, and, on `main`, publishes `docs/` to GitHub Pages. Set Settings, Pages, Source to
"GitHub Actions" once.

## Licence

The data of this repository (the tables in `data/csv/`, the pages, the RDF export) is under
[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) (decided 2026-10-21; Wikidata data is CC0 as well). The footer of
the pages and `cc:license` in the RDF say so. **Not covered:** the logo (`assets/logo.png`, the chublets raven), which keeps its own
terms (the chublets-visuals are MIT).

## Attribution

The mapping of the properties to CodeMeta terms and to Wikidata builds on the published crosswalks of research software
metadata schemas to CodeMeta: *Crosswalks of Research Software Metadata Schemas to CodeMeta* (ConnOSS), v1.2.0, licensed
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), <https://doi.org/10.5281/zenodo.21935688>. Please cite it when you reuse
the mapping (`background/sources.csv`, code `S9`). The CodeMeta terms themselves come from <https://codemeta.github.io/terms/>,
the Wikidata columns also from the CodeMeta crosswalk for Wikidata (<https://codemeta.github.io/crosswalk/wikidata/>).
The crosswalk files themselves are not part of this repository; the Starter Pack carries them in `sources/connoss/`.
