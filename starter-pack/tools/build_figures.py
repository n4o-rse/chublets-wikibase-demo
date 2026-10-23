#!/usr/bin/env python3
"""Paper figure: how the Wikibase property set is composed (numbers read from data/*.csv).

    python tools/build_figures.py       # needs matplotlib

Writes diagrams/fig-property-set-composition.{svg,pdf,png}. Three stacked bars share one colour code:
    crosswalked        a CodeMeta term and a Wikidata property meet in one Wikibase property
    CodeMeta-only      a CodeMeta term without a Wikidata property -> new property
    Wikidata-only      a Wikidata property without a CodeMeta term
    chublets addition  needed by the chublets pipeline or the Wikibase itself, in neither vocabulary
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "diagrams"
OUT.mkdir(exist_ok=True)


def read(n):
    return list(csv.DictReader((DATA / n).open(encoding="utf-8")))


summary = {r["metric"].strip(): int(r["value"]) for r in read("mapping-summary.csv") if r["value"].strip().isdigit()}
pset = read("wikibase-property-set.csv")
st = Counter(r["status"] for r in pset)
cm_total = summary["codemeta_terms_total"]
cm_cw = summary["codemeta_terms_crosswalked_to_wikidata"]
cm_only = summary["codemeta_terms_without_wikidata_property"]
wp_total = summary["wikiproject_software_pids_known"]
wp_cw = summary["of which with a CodeMeta term"]
wp_only = summary["of which Wikidata-only (no CodeMeta term)"]
total = summary["wikibase_properties_total"]
cw_not_wp = summary["of which NOT in the WikiProject Software list"]
wd_only_block = st["wikidata-only"] - wp_only
assert cm_cw + cm_only == cm_total and wp_cw + wp_only == wp_total
assert sum(st.values()) == total

COL = {"crosswalked": ("#166534", "#ffffff"), "codemeta-only": ("#9a3412", "#ffffff"),
       "wikidata-only": ("#fbbf24", "#000000"), "chublets-addition": ("#4c1d95", "#ffffff")}
LAB = {"crosswalked": "crosswalked", "codemeta-only": "CodeMeta only", "wikidata-only": "Wikidata only",
       "chublets-addition": "chublets addition"}

bars = [
    (f"CodeMeta terms\n(n = {cm_total})", [("crosswalked", cm_cw), ("codemeta-only", cm_only)]),
    (f"WikiProject Software list\n(n = {wp_total} identified,\nplus registry IDs not enumerated)", [("crosswalked", wp_cw), ("wikidata-only", wp_only)]),
    (f"Wikibase property set\n(n = {total}, nothing excluded)", [("crosswalked", st["crosswalked"]), ("codemeta-only", st["codemeta-only"]),
                                                              ("wikidata-only", st["wikidata-only"]), ("chublets-addition", st["chublets-addition"])]),
]
notes = {
    2: {"crosswalked": f"{wp_cw} on the list\n+ {cw_not_wp} elsewhere in Wikidata",
        "wikidata-only": f"{wp_only} on the list\n+ {wd_only_block} from the\ncrosswalk workbook"},
}

fig, ax = plt.subplots(figsize=(11, 4.6))
H, GAP = 0.62, 1.0
scale = 100.0 / total
for i, (title, segs) in enumerate(bars):
    y = (len(bars) - 1 - i) * GAP
    x = 0.0
    for status, n in segs:
        w = n * scale
        fc, tc = COL[status]
        ax.add_patch(Rectangle((x, y), w, H, facecolor=fc, edgecolor="black", linewidth=0.8))
        ax.text(x + w / 2, y + H / 2, f"{n}", ha="center", va="center", color=tc, fontsize=13, fontweight="bold")
        if i in notes and status in notes[i]:
            ax.text(x + w / 2, y - 0.07, notes[i][status], ha="center", va="top", fontsize=8.3, color="#222222")
        x += w
    ax.text(-1.2, y + H / 2, title, ha="right", va="center", fontsize=10.5)
ax.set_xlim(-34, 101)
ax.set_ylim(-0.75, (len(bars) - 1) * GAP + H + 0.45)
ax.axis("off")
handles = [Rectangle((0, 0), 1, 1, facecolor=COL[k][0], edgecolor="black") for k in COL]
ax.legend(handles, [LAB[k] for k in COL], loc="upper center", bbox_to_anchor=(0.62, 1.04), ncol=4, frameon=False, fontsize=10)
fig.tight_layout()
for ext in ("svg", "pdf", "png"):
    fig.savefig(OUT / f"fig-property-set-composition.{ext}", dpi=200, bbox_inches="tight", facecolor="white")
print("wrote fig-property-set-composition.{svg,pdf,png}")
