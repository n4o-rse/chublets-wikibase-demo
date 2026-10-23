# Diagrams
Colour scheme: items grey, real objects green, classes orange, terms purple, vocabulary terms white, properties amber (`00-legend`). Paper figure: `diagrams/fig-property-set-composition.{svg,pdf,png}`. Regenerate: `tools/build_diagrams.py`, `tools/build_figures.py`.

## Class diagrams
- `06-class-hierarchy`: only where a hierarchy exists. Solid edge = evidenced (chublet P279 Q73899440, from open-archaeo MAPPING.md); dashed edges = expected `subclass of` links in general Wikidata, **unverified** (recalled). The label of Q73899440 is disputed: MAPPING.md and the project notes say Little Minion, a comment in model.py says research software (see `docs/05-open-points.md`).
- `07-item-instance-of`: how an open-archaeo item gets its classes through P31 (chublet, research software for every item, one category class). This is instance-of, not a class hierarchy.
- `08-entities-flat`: all 28 entities grouped by kind, without any hierarchy.
