# 06 DataCite <-> Wikidata via CodeMeta (from the ConnOSS crosswalk, S9)

**Source:** *Crosswalks of Research Software Metadata Schemas to CodeMeta*, v1.2.0 (2026-08-14), https://doi.org/10.5281/zenodo.21935688, CC BY 4.0 (authors incl. L. J. Castro, S. Ferenz, F. Thiery and the other data collectors). 21 schemas are mapped to CodeMeta; there is **no published DataCite <-> Wikidata pair**. Both are mapped to the same CodeMeta term, so the table `data/datacite-wikidata-bridge.csv` joins them per term (CodeMeta as hub). Everything below is derived, not published.

## Result (68 terms)
| Bridge | Terms | Meaning for the Wikibase |
|---|---|---|
| both | 24 | CodeMeta term has a Wikidata property **and** a DataCite element: the two can be linked through one Wikibase property |
| Wikidata only | 8 | no DataCite element (e.g. codeRepository, programmingLanguage, operatingSystem, softwareRequirements, issueTracker) |
| DataCite only | 9 | DataCite has an element, Wikidata has no property: CodeMeta-only property in the Wikibase, with a DataCite element as extra evidence (copyrightHolder, copyrightYear, editor, provider, description, embargoDate, embargoEndDate, funding, referencePublication) |
| neither | 27 | only CodeMeta |

## Does it change the Wikidata mappings?
**No.** The Wikidata column of S9 is identical to the earlier workbook (S1) for all 67 terms they share (`data/connoss-vs-s1-diff.csv`: 67 same, 1 new). The crosswalked set (37 terms / 37 PIDs) and every count of the Wikibase property set (153; 37/46/52/18) are unchanged. What did change is listed in `CHANGELOG.md`.

## Caveats
- Several DataCite elements are many-to-one: `date` serves copyrightYear, dateCreated, dateModified and others (distinguished by `dateType`), `contributor` serves contributor, editor, producer, provider, sponsor and maintainer (distinguished by `contributorType`), `relatedItem` serves hasPart, isPartOf, url, referencePublication (distinguished by `relationType`). A DataCite export from the Wikibase therefore needs the qualifier or type, not just the property.
- DataCite mappings in S9 contain reviewer corrections written as free text; `datacite_cell` keeps the cleaned text, nothing is parsed further.
- DataCite elements without a CodeMeta term (alternateIdentifier, resourceType, language, geoLocation) are listed at the end of the DataCite crosswalk file and are not in the bridge.
- Proposal, **not** implemented in the property set: a Wikibase property-metadata property *equivalent DataCite element* next to *equivalent CodeMeta term*. The element text is available in `wikibase-property-set.csv`, column `datacite_elements`.
