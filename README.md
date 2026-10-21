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
* **149 properties** (P100 to P248) from the Starter Pack: the union of all CodeMeta terms and the properties of the
  WikiProject Software list, each with its Wikidata twin (`P4`), its CodeMeta terms and, for the CodeMeta-only ones,
  the Wikidata properties that come close,
* **7 classes** (Q100 to Q106): software, research software, application software, software library, script file,
  Little Minion and chublet, in the class tree the pack drew, each with its Wikidata twin.

The logo (`assets/logo.png`, set in `site.yaml`) is the chublets raven.
Every entity page offers its RDF as Turtle and as JSON for download (`docs/ttl/`, `docs/json/`) and a button that copies the concept URI to the clipboard.

There are no software entries yet. They come from open-archaeo (S7c) and from Wikidata (S7d).
The pages show the model the way a Wikibase does; the RDF export additionally carries the **RDFS bridge**
(`wdt:P1 rdfs:subPropertyOf rdfs:subClassOf` and five more triples, in a section of their own in the Turtle files), so that
a reasoner or a property path reads the class tree.

**What is not verified:** the Starter Pack was built without access to Wikidata. Every twin, every Q-id and every label
carries the reliability the pack gave it (`background/property-set.csv`, column `confidence`; `background/sources.csv`
explains the codes). `tools/verify_wikidata.py` of the pack is the check, and it has not been run. A reference on a twin says
"documented at this Wikidata page", not "retrieved on a date".

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

`tools/import_pack.py` made the tables once from the unzipped Starter Pack:

```cmd
python tools/import_pack.py C:\git\chublets-wikibase-starter-pack
```

It is kept for the record and can be run again: it reads `data/csv/idmap.csv` first, so the same pack row gets the same
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
terms (the chublets-visuals are MIT). **Open:** whether the CodeMeta crosswalk the mapping builds on, which is CC BY, asks for an
attribution (`background/sources.csv` names it; the Starter Pack lists the question, `background/starter-pack-open-points.md`, point 7).
