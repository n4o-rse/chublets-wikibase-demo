# Changelog

## 2026-10-21 (evening), update 1 -- ConnOSS crosswalk (S9) added

Trigger: the official ConnOSS crosswalk (https://doi.org/10.5281/zenodo.21935688, v1.2.0, CC BY 4.0) was supplied as ZIP and compared with the sources of the first pack. **The counts in the first pack stay valid** (153 properties = 37 crosswalked + 46 CodeMeta-only + 52 Wikidata-only + 18 chublets additions; 83 CodeMeta terms; 37 crosswalked terms). What changes are the *provenance*, three labels, two lists and the additions below.

### What to carry over (checklist for the files already in use)
| # | Change | Where | Action for you |
|---|---|---|---|
| 1 | New source **S9** = published ConnOSS crosswalk. It is the citable version of S1 (the working workbook). | `data/sources.csv`, README, `docs/02`, `docs/06` | Cite S9 (DOI) instead of the workbook in the paper. |
| 2 | Wikidata column of S9 equals S1 for all 67 shared terms (checked row by row). **No Wikidata mapping changed**, including the corrections P50->P178, editor->none, funder->P8324, sponsor->P859, screenshot->P18, softwareHelp->P2078, identifier->P356, name->P2561, relatedLink->P973 / P11201. | `data/connoss-vs-s1-diff.csv` (new) | none |
| 3 | **releaseNotes** is part of the 68 properties of S9 (no row in S1). Still without Wikidata property. In the first pack it counted as "not in the workbook". | `codemeta-terms-to-wikibase.csv`: `in_reviewed_workbook` yes, `workbook_resolution` s9-only; `mapping-summary.csv` | Numbers: terms in the reviewed crosswalk **67 -> 68** (now equals S9's "68 properties"); terms outside it **16 -> 15**; total 83 unchanged. Fix any sentence quoting 67/16. |
| 4 | S9 publishes a Wikidata-only block of **10** PIDs (P1072, P1073, P144, P1343, P101, P800, P166, P463, P485, P154); S1 contained more (P734, P735, P968, P973, P178 ...). | `mapping-summary.csv`: metric renamed `workbook_wikidata_only_block_not_in_wikiproject_list` -> `published_wikidata_only_block_not_in_wikiproject_list`, value **11 -> 7** (P101, P154, P166, P463, P485, P800, P1343); `wikibase-property-set.csv` column `wikidata_origin`: "workbook block" -> "published crosswalk block" | The "52 Wikidata-only = 46 on the list + 6 from the crosswalk block" in the figure stays correct (the six are P101, P154, P166, P463, P485, P800). P1343 is crosswalked (referencePublication, S5). |
| 5 | P1343 *described by source*, P101 and P463 carry the reviewer note "doesn't seem to be related" in S9. referencePublication -> P1343 exists **only** in the codemeta.org crosswalk (S5), not in S9. | `codemeta-terms-to-wikibase.csv` (`differs_from_codemeta_org`) | Decide whether to keep referencePublication as crosswalked (current) or CodeMeta-only. Affects 37/46 -> 36/47 if changed. |
| 6 | Five terms crosswalked only via S5 (email, familyName, fileFormat, givenName, referencePublication) are **not** in S9 at all (S9 = 68 properties, no Person terms). | `mapping-summary.csv` | Say in the paper that these five come from codemeta.org, not from the ConnOSS crosswalk. |
| 7 | **New data files:** `connoss-summary-matrix.csv` (68 terms x 21 schemas), `datacite-wikidata-bridge.csv`, `connoss-vs-s1-diff.csv`, `connoss-wikidata-only-block.csv`. | `data/` | Add to your copy. |
| 8 | New columns: `codemeta-terms-to-wikibase.csv` += `s9_wikidata_pids`, `s9_datacite`, `s9_bridge`; `wikibase-property-set.csv` += `datacite_elements` (last column). | `data/` | Tools reading columns by position must be adapted (new columns are appended at the end). |
| 9 | `mapping-summary.csv` += 4 rows `s9_bridge_*` (24 both / 8 Wikidata-only / 9 DataCite-only / 27 neither). | `data/` | -- |
| 10 | New docs: `docs/06-datacite-wikidata.md`, this file. `docs/03-paper-tables.md` += Table E (hub table). `docs/05-open-points.md` updated. | docs | -- |
| 11 | Originals copied to `sources/connoss/` (25 files). | sources | Licence CC BY 4.0: attribution required. |
| 12 | New tool `tools/build_connoss.py` (run **before** `build_pack.py`). Rebuild order: build_connoss -> build_pack -> build_paper_tables -> build_diagrams -> build_figures. | tools | -- |

### Unchanged
All Wikibase property labels/IDs, the figure `fig-property-set-composition`, diagrams 00-08 (regenerated, content identical), examples, SPARQL.

### Open after this update
- The registry-ID gap of the WikiProject list (12 IDs) is **not** closed by S9.
- Nothing was verified against live Wikidata.
- DataCite elements are not yet a property of the Wikibase (proposal in `docs/06`).
- Other schemas in S9 that may matter for the planned exports: DCAT 3 (30 terms mapped), schema.org SDO (30), maSMP (33), CFF (17). `connoss-summary-matrix.csv` has them; no further use made yet.

## 2026-10-21 (midday) -- first release
Initial pack (153 properties, 28 entities, examples, SPARQL, diagrams 00-05).

## 2026-10-21 (afternoon)
Added class diagrams 06-08.
