#!/usr/bin/env python3
"""Compare labels and datatypes in data/wikidata-properties.csv and data/wikidata-entities.csv with live Wikidata.

    python tools/verify_wikidata.py            # stdlib only; needs internet access (NOT possible in the sandbox that built the pack)

Writes data/verification-report.csv (id, kind, field, expected, live, verdict).
"""
import csv, json, urllib.parse, urllib.request
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
API = "https://www.wikidata.org/w/api.php"
UA = {"User-Agent": "chublets-pack-verify/0.1 (thiery.florian@googlemail.com)"}


def fetch(ids):
    q = urllib.parse.urlencode({"action": "wbgetentities", "ids": "|".join(ids), "props": "labels|datatype", "languages": "en", "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(f"{API}?{q}", headers=UA), timeout=60) as r:
        return json.load(r)["entities"]


rows = []
for name, idcol, labcol in (("wikidata-properties.csv", "pid", "label_en"), ("wikidata-entities.csv", "qid", "label_en")):
    rows += [(r[idcol], r, labcol) for r in csv.DictReader((D / name).open(encoding="utf-8"))]
out = []
for i in range(0, len(rows), 50):
    batch = rows[i:i + 50]
    ents = fetch([b[0] for b in batch])
    for eid, r, labcol in batch:
        e = ents.get(eid, {})
        if "missing" in e:
            out.append((eid, "entity", "exists", "yes", "missing", "FAIL")); continue
        live = e.get("labels", {}).get("en", {}).get("value", "")
        out.append((eid, "entity", "label", r[labcol], live, "ok" if live.lower() == r[labcol].lower() else "DIFF"))
        if r.get("datatype") and e.get("datatype"):
            out.append((eid, "entity", "datatype", r["datatype"], e["datatype"], "ok" if r["datatype"] == e["datatype"] else "DIFF"))
with (D / "verification-report.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id", "kind", "field", "expected", "live", "verdict"]); w.writerows(out)
print(len(out), "checks;", sum(o[5] != "ok" for o in out), "to review -> data/verification-report.csv")
