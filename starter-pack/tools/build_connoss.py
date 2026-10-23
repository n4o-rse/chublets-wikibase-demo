#!/usr/bin/env python3
"""Read the official ConnOSS crosswalk (S9, Zenodo 10.5281/zenodo.21935688, v1.2.0, CC BY 4.0) and write

  data/connoss-summary-matrix.csv   one row per CodeMeta/schema.org term (68), one column per schema (21), cleaned
  data/datacite-wikidata-bridge.csv one row per term: Wikidata property and DataCite element side by side (CodeMeta as hub)
  data/connoss-vs-s1-diff.csv       comparison of the Wikidata column with the earlier workbook (S1) used in the first pack

DataCite <-> Wikidata is NOT a published pair: both are mapped to CodeMeta, so the bridge is derived via the term.
Input: sources/connoss/CodeMeta Crosswalk Summary.xlsx
"""
import csv, re
from pathlib import Path
import openpyxl
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import parse_crosswalk

R = Path(__file__).resolve().parent.parent
PID = re.compile(r"P\d+")
flat = lambda v: re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""

ws = openpyxl.load_workbook(R / "sources/connoss/CodeMeta Crosswalk Summary.xlsx", data_only=True).worksheets[0]
hdr = [flat(c.value) for c in ws[1]]
cols = [(i, h) for i, h in enumerate(hdr) if i >= 6 and h]
rows = []
for r in ws.iter_rows(min_row=2, values_only=True):
    dom, prop = flat(r[0]), flat(r[1])
    if not dom or not prop or prop.startswith("Properties"):
        continue
    rows.append(dict(domain=dom, term=prop, range=flat(r[2]), comment=flat(r[4]), cells={h: flat(r[i]) for i, h in cols}))

with (R / "data/connoss-summary-matrix.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["domain", "term", "range", "comment"] + [h for _, h in cols])
    for x in rows:
        w.writerow([x["domain"], x["term"], x["range"], x["comment"]] + [x["cells"][h] for _, h in cols])

dc_h = next(h for _, h in cols if h.startswith("DataCite"))
old = {}
for r in parse_crosswalk.parse(R / "sources/codemeta-wikidata-crosswalk.xlsx"):
    if r["codemeta_property"]:
        old.setdefault(r["codemeta_property"], set()).update([r["wikidata_final"]] if r["wikidata_final"] else [])

bridge, diff = [], []
for x in rows:
    wd, dc = x["cells"]["Wikidata"], x["cells"][dc_h]
    pids = sorted(set(PID.findall(wd)), key=lambda p: int(p[1:]))
    cat = "both" if (pids and dc) else "wikidata-only" if pids else "datacite-only" if dc else "neither"
    bridge.append([x["term"], x["domain"], ";".join(pids), wd, dc, cat])
    o = sorted(old.get(x["term"], []), key=lambda p: int(p[1:]))
    diff.append([x["term"], ";".join(o) if x["term"] in old else "(no row in S1)", ";".join(pids),
                 "same" if x["term"] in old and o == pids else "NEW in S9" if x["term"] not in old else "DIFFERENT"])
with (R / "data/datacite-wikidata-bridge.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["codemeta_term", "domain", "wikidata_pids", "wikidata_cell", "datacite_cell", "bridge"]); w.writerows(bridge)
with (R / "data/connoss-vs-s1-diff.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["codemeta_term", "s1_wikidata_final", "s9_wikidata", "verdict"]); w.writerows(diff)
# Wikidata-only block of the published Wikidata crosswalk (rows after the CodeMeta rows: PIDs with no CodeMeta term)
wrows = list(csv.reader((R / "sources/connoss/Wikidata - Crosswalk CodeMeta.csv").open(encoding="utf-8")))
block = [(r[5].strip(), flat(r[7])) for r in wrows[1:] if not r[0].strip() and PID.fullmatch(r[5].strip())]
with (R / "data/connoss-wikidata-only-block.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["wikidata_pid", "label_or_reviewer_note"]); w.writerows(block)
from collections import Counter
print("wikidata-only block:", [b[0] for b in block])
print(len(rows), "terms;", dict(Counter(b[5] for b in bridge)), dict(Counter(d[3] for d in diff)))
