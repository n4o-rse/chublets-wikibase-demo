# 01 How software is modelled in Wikidata

Basis: WikiProject Informatics/Software/Properties (S2, transcription of 47 rows in five categories, plus 17 PIDs from an earlier page excerpt) and the Wikidata pages seen as snippets (S6). Machine-readable: `data/wikidata-properties.csv` (109 properties with datatype, group, role) and `data/wikidata-entities.csv` (28 items).

## Core pattern
- Item class: `instance of` (P31) software (Q7397) or a narrower class (application software Q166142, software library Q188860, ...). chublets use the local class chublet (Q141115627), subclass of Little Minion (Q73899440).
- Name statement: P2561 is mandatory on the WikiProject page.
- Repository: P1324 (source code repository URL) requires the qualifier P8423 (version control system), e.g. Git Q186055.
- Versions: one P348 (software version identifier) statement per release, qualifiers P548 (version type), P577 (publication date), P4945 (download URL), P356/P1476 as needed; preferred rank for the newest.
- Abandoned software: Q281039 with P580/P582/P585.
- Archive evidence: P1065 (archive URL) with P2960 (archive date).

## Groups
Identity and people, Relations, Technical, Distribution, Identifiers/registries -- see column `group` in `data/wikidata-properties.csv`. The registry-ID family (package indices, distro packages) is **not fully enumerated**: 12 IDs are missing from the transcription (GAP row), 8 distro-package labels unknown.

## Entities
`data/wikidata-entities.csv`: classes (software, library, application), version-control items (Git), the chublets platform items (Q141115627, Q141115774, Q141169143, Q141190255) and people.
