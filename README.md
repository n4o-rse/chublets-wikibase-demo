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

The logo (`assets/logo.png`, set in `site.yaml`) is the chublets raven.
Every entity page offers its RDF as Turtle and as JSON for download (`docs/ttl/`, `docs/json/`) and a button that copies the concept URI to the clipboard.

There are no software entries yet. They come from open-archaeo (S7c) and from Wikidata (S7d).
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
The range (`P10`) is `Q3` (any item) for each of the 63 properties with item values and absent otherwise, because the datatype
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

## Where the model came from

`tools/import_pack.py` made the tables once from the unzipped Starter Pack (v1.1, which adds the published ConnOSS crosswalk as source `S9`; the model is the same as in v1.0, only `background/` changed):

```cmd
python tools/import_pack.py C:\git\chublets-wikibase-starter-pack
```

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
