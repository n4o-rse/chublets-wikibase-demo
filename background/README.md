# background

What the Starter Pack said about the model, kept next to the tables so that a number or a decision can be traced back.
Nothing here is read by the pipeline.

| File | Content |
|---|---|
| `property-set.csv` | The 153 rows of `data/wikibase-property-set.csv` of the Starter Pack, with two columns in front: `local_id` (the property in `data/csv/`) and `kernel` (`yes` for the four rows that are kernel properties and got no new number) |
| `classes.csv` | The Wikidata classes of the model (rows of `data/wikidata-entities.csv`), with `local_id` |
| `sources.csv` | The source codes (S1 to S9, R; S9 is the published ConnOSS crosswalk, <https://doi.org/10.5281/zenodo.21935688>) that `provenance` in `property-set.csv` refers to |
| `starter-pack-open-points.md` | The open points of the pack, copied as they are. Point 7 (licence) is why the footer of the pages says "licence not yet decided" |

`confidence` in `property-set.csv` is the reliability the pack gave each row: `checked`, `source-claimed`, `recalled`,
`pid-only`, `proposal`. Nothing was compared with Wikidata itself (the pack was built without access); the pack's
`tools/verify_wikidata.py` is the check.

The files are written by `tools/import_pack.py`; do not edit them by hand.
