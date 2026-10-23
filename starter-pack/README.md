> **In the demo repository.** This folder is the pack as delivered (v1.1), kept unchanged except for this note and `examples-local/`: the
> three QuickStatements examples with the ids of `chublets-wikibase-demo` (`python tools/qs_to_local.py`). The model that the demo
> maintains lies in `../data/csv/`; the paths in the text below are relative to this folder. It can be moved into a repository of its own
> with its history (`git subtree split --prefix=starter-pack`).

# chublets.software -- Wikibase starter pack

Info package to bootstrap a *new Wikibase* for chublets.software (a concept/prototype: everything here is written in the conditional) and to serve as the base for another Claude project. Built 2026-10-21 from the sources listed in `data/sources.csv`; see `CHANGELOG.md` for updates (current: update 1, ConnOSS crosswalk S9).

## Core message (for the paper)
The Wikibase property set (`data/wikibase-property-set.csv`, one row per property) is the **union** of
- **all** CodeMeta terms (83 distinct), and
- **all** properties of the WikiProject Software list that could be identified (63; see open point on the registry IDs),
plus what the chublets pipeline needs on top. Nothing is excluded; `phase` says only when a property is first populated. Every row says whether it is **crosswalked** (CodeMeta term = Wikidata property), **codemeta-only**, **wikidata-only** or a **chublets-addition**. Numbers: `data/mapping-summary.csv`; figure: `diagrams/fig-property-set-composition.*`.

## Reading order
1. `docs/01-wikidata-software-modelling.md`
2. `docs/02-codemeta-crosswalk.md`
3. `docs/03-paper-tables.md` (generated; LaTeX in `paper/`); `docs/06-datacite-wikidata.md` (DataCite <-> Wikidata via CodeMeta)
4. `docs/04-examples.md`, `examples/`
5. `docs/05-open-points.md` -- **read before trusting any Q-ID or label**

## Folders
`data/` CSVs (master: `wikibase-property-set.csv`) · `diagrams/` Mermaid sources + SVG/PNG, paper figure SVG/PDF/PNG · `examples/` QuickStatements, Turtle, CodeMeta · `sparql/` · `sources/` copies of inputs · `tools/` scripts that regenerate everything · `paper/` LaTeX longtables.

## Provenance and confidence
Codes S1--S8, R in `data/sources.csv`. Confidence: checked / source-claimed / recalled / pid-only / proposal. **Nothing was verified against live Wikidata** (the build sandbox could not reach it): run `python tools/verify_wikidata.py` locally.

## Rebuild
`python tools/build_connoss.py && python tools/build_pack.py && python tools/build_paper_tables.py && python tools/build_diagrams.py && python tools/build_figures.py`
Licence: undecided (see open points).
