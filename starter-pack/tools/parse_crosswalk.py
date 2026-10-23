#!/usr/bin/env python3
"""Parse the CodeMeta <-> Wikidata crosswalk workbook into data/codemeta-wikidata-crosswalk.csv.

Source: sources/codemeta-wikidata-crosswalk.xlsx, sheet "Crosswalk CodeMeta"
(template by Leyla Jael Castro, reviewed by Stephan Ferenz, filled by Florian Thiery;
reviewers: Maryam, Lu, Aida). Columns, by header row 4:
  A property, B range, C description, D comment      -> CodeMeta side
  F property, G range, H description                 -> Wikidata side (free text)
  M, N, O reviews; P mapping type

Resolution rule for the final Wikidata property:
  1. text containing "corrected:" -> the part after it wins ("no mapping" -> none)
  2. otherwise the first P-number in the cell ("wd:856" is a typo for P856)
The first-pass value is kept in its own column so nothing is lost.
"""
from __future__ import annotations
import csv, re, sys
from pathlib import Path
import openpyxl

PID = re.compile(r"\bP\d+\b")
TYPES = ["Thing", "CreativeWork", "SoftwareSourceCode", "SoftwareApplication"]


def clean(v):
    return re.sub(r"\s+", " ", str(v)).strip() if v is not None else ""


def resolve(raw: str):
    """-> (first_pass_pid, final_pid, status)"""
    raw = raw.strip()
    if not raw:
        return "", "", "unmapped"
    low = raw.lower()
    first = ""
    head = raw.split("corrected:")[0]
    m = PID.search(head)
    if m:
        first = m.group(0)
    elif re.search(r"wd:\s*(\d+)\b", head):          # typo "wd:856"
        first = "P" + re.search(r"wd:\s*(\d+)\b", head).group(1)
    if "corrected:" in low:
        tail = raw[low.index("corrected:") + len("corrected:"):]
        if "no mapping" in tail.lower():
            return first, "", "corrected-to-none"
        m2 = PID.search(tail)
        if m2:
            return first, m2.group(0), "corrected"
        # corrected text holds a label only, e.g. "official demo URL (P11201)" is caught above
        return first, "", "corrected-unparsed"
    if first:
        return first, first, "as-proposed"
    m3 = PID.search(raw)
    if m3:
        return "", m3.group(0), "suggested-in-text"   # e.g. "(P361 - part of) could be a match."
    return "", "", "unmapped"


def parse(xlsx: Path):
    ws = openpyxl.load_workbook(xlsx, data_only=True)["Crosswalk CodeMeta"]
    rows, section, in_other = [], "", False
    for r in range(5, ws.max_row + 1):
        g = lambda col: clean(ws[f"{col}{r}"].value)
        a, b = g("A"), g("B")
        if not any(g(c) for c in "ABCDFGHMNOP"):
            continue
        if a.startswith(("Properties from", "Properties outside", "Additional properties")) and not b:
            tail = a.split("->")[-1].strip()
            if "->" not in a and a.strip() == "Properties from Thing":
                tail = "Thing"
            if tail in TYPES:
                section = tail
            elif a.startswith("Properties outside"):
                section = "outside-hierarchy"
            elif a.startswith("Additional properties"):
                section = "codemeta-additional"
            else:
                section = section  # sub-divider (e.g. "-> WebPage"): does not change the section
            continue
        if not a and g("F"):
            in_other = True
            rows.append(dict(section="wikidata-only", codemeta_property="", codemeta_range="",
                             codemeta_description="", codemeta_note="",
                             wikidata_raw=g("F"), wikidata_first_pass="", wikidata_final=(PID.search(g("F")) or [""])[0] if PID.search(g("F")) else "",
                             resolution="wikidata-only", wikidata_range=g("G"), wikidata_description=g("H"),
                             mapping_type=g("P"), reviewer_pids="", review_1=g("M"), review_2=g("N"), review_3=g("O"), xlsx_row=r))
            continue
        if not a:
            if g("M") or g("N") or g("O"):
                rows.append(dict(section="wikidata-only", codemeta_property="", codemeta_range="",
                                 codemeta_description="", codemeta_note="", wikidata_raw=g("F"),
                                 wikidata_first_pass="", wikidata_final="", resolution="wikidata-only-note",
                                 wikidata_range=g("G"), wikidata_description=g("H"), mapping_type=g("P"),
                                 reviewer_pids="", review_1=g("M"), review_2=g("N"), review_3=g("O"), xlsx_row=r))
            continue
        first, final, status = resolve(g("F"))
        found = []
        for col in "MNO":                                # PIDs that reviewers mention, in order
            for pid in PID.findall(g(col)):
                if pid not in found and pid != final:
                    found.append(pid)
        suggestion = "|".join(found)
        rows.append(dict(section=section, codemeta_property=a, codemeta_range=b,
                         codemeta_description=g("C"), codemeta_note=g("D"),
                         wikidata_raw=g("F"), wikidata_first_pass=first, wikidata_final=final,
                         resolution=status, wikidata_range=g("G"), wikidata_description=g("H"),
                         reviewer_pids=suggestion,
                         mapping_type=g("P"), review_1=g("M"), review_2=g("N"), review_3=g("O"),
                         xlsx_row=r))
    return rows


if __name__ == "__main__":
    src = Path(sys.argv[1]); out = Path(sys.argv[2])
    rows = parse(src)
    fields = list(rows[0].keys())
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(len(rows), "rows ->", out)
