#!/usr/bin/env python3
"""Close the registry-ID gap: report PIDs of the WikiProject Software page that are missing from the Wikibase set.

    python tools/check_completeness.py wikiproject-wikitext.txt

Give it the wikitext (Edit -> copy) or the rendered text of
https://www.wikidata.org/wiki/Wikidata:WikiProject_Informatics/Software/Properties .
Every P-number found there must appear in data/wikibase-property-set.csv (column wikidata_pid).
"""
import csv, re, sys
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
have = {r["wikidata_pid"] for r in csv.DictReader((D / "wikibase-property-set.csv").open(encoding="utf-8")) if r["wikidata_pid"]}
found = set(re.findall(r"\bP\d+\b", Path(sys.argv[1]).read_text(encoding="utf-8")))
missing = sorted(found - have, key=lambda p: int(p[1:]))
print(f"{len(found)} PIDs on page, {len(found & have)} in set, {len(missing)} missing")
for p in missing:
    print(p)
sys.exit(1 if missing else 0)
