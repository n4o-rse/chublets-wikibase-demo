# 05 Open points

1. **Identity block differs between sources** (`data/identity-block-variants.csv`): MAPPING.md, model.py and the WikiProject page list different statement sets (model.py the most complete, MAPPING.md the smallest). Decide the canonical block.
2. **Registry-ID gap**: 12 registry-ID properties of the WikiProject list are not enumerated and 8 distro-package labels are unknown. Run `python tools/check_completeness.py <wikitext>` with the WikiProject page text and add what it reports -- this is needed before the paper may say "ALL".
3. **No live verification**: Wikidata was unreachable. Labels marked recalled/pid-only, and all Q-IDs, need `tools/verify_wikidata.py`.
4. **Alligator and AMT Q-IDs** unknown: use `sparql/04-find-alligator-amt.rq`.
5. **Q73899440 (Little Minion)**: ambiguity noted in the comments of model.py; confirm it is the intended superclass.
6. **Attribution** of the crosswalk workbook authors (Castro, Ferenz, Thiery, reviewers) must be stated in the paper.
7. **Licence undecided**: Wikidata data is CC0, the CodeMeta crosswalk CC-BY, chublets-visuals MIT.
8. All SPARQL and QuickStatements files are untested.
