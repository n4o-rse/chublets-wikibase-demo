# 02 CodeMeta <-> Wikidata crosswalk

## Sources
- **S1** reviewed workbook (template Leyla Jael Castro, review Stephan Ferenz, filled by Florian Thiery, reviewers Maryam, Lu, Aida): 68 rows, 33 with a final Wikidata property, 35 without.
- **S9** the published ConnOSS crosswalk (Zenodo 10.5281/zenodo.21935688, v1.2.0, CC BY 4.0, 21 schemas, 68 properties): the citable version of S1; its Wikidata column is identical to S1 for all 67 shared terms; adds the row releaseNotes. Use S9 as the reference in the paper; S1 stays in the pack for the review trail (reviewer comments).
- **S5** official codemeta.org crosswalk (30 rows) as secondary source.
- **S8** official CodeMeta terms page: source of 16 terms with no workbook row.

## How the final mapping was derived (`tools/parse_crosswalk.py`)
A "corrected:" text in the review columns wins ("no mapping" means none); otherwise the first P-number; typo `wd:856` read as P856. Full trace per row in `data/codemeta-wikidata-crosswalk.csv` (columns wikidata_raw, wikidata_first_pass, wikidata_final, resolution).

## Notable corrections
P50 (author) -> P178 (developer) as proposed in the workbook; `editor` -> none; `funder` -> P8324; `wd:856` -> P856; `relatedLink` appears twice.

## Result (`data/mapping-summary.csv`)
83 distinct CodeMeta terms: 37 crosswalked (32 via S1, 5 only via S5: email, familyName, fileFormat, givenName, referencePublication), 46 without Wikidata property. The 37 crosswalk PIDs: 17 are on the WikiProject Software list, 20 are not (P18, P123, P126, P162, P734, P735, P767, P859, P921, P968, P973, P1343, P2561, P2701, P2860, P2888, P3575, P5017, P8324, P11201). Differences between S1 and S5 are flagged in `differs_from_codemeta_org`.

## Wikibase consequence
Each crosswalked pair becomes **one** Wikibase property carrying the metadata properties *equivalent Wikidata property* and *equivalent CodeMeta term*; CodeMeta-only terms become new properties (optionally with *close match Wikidata property* candidates); Wikidata-only properties are created as they are.
