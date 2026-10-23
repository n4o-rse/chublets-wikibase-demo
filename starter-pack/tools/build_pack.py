#!/usr/bin/env python3
"""Build every CSV in data/ from sources/ plus the curated tables in tools/curated.py.

    python tools/build_pack.py            # from the pack root

Standard library plus openpyxl (only for the workbook parse). Deterministic: no
timestamps, sorted where order is not meaningful. Prints a short consistency report;
non-zero exit if a hard check fails.
"""
from __future__ import annotations

import csv
import io
import re
import sys
from collections import Counter, OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import curated  # noqa: E402
import parse_crosswalk  # noqa: E402

DATA = ROOT / "data"
SRC = ROOT / "sources"
DATA.mkdir(exist_ok=True)
problems: list[str] = []


def rows_of(block: str, n: int):
    out = []
    for line in block.splitlines():
        parts = line.split("|")
        if len(parts) != n:
            problems.append(f"bad row ({len(parts)} fields, want {n}): {line[:80]}")
            continue
        out.append([p.strip() for p in parts])
    return out


def write_csv(name: str, fields: list[str], rows: list[dict]):
    path = DATA / name
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    print(f"  {name}: {len(rows)} rows")


# --------------------------------------------------------------------------
# 0. inputs
# --------------------------------------------------------------------------
xw = parse_crosswalk.parse(SRC / "codemeta-wikidata-crosswalk.xlsx")
write_csv("codemeta-wikidata-crosswalk.csv", list(xw[0].keys()), xw)
cm_rows = [r for r in xw if r["codemeta_property"]]
other_rows = [r for r in xw if r["section"] == "wikidata-only"]

s2 = list(csv.DictReader((SRC / "wikidata-software-properties.csv").open(encoding="utf-8")))
s2_pids = {r["pid"] for r in s2 if re.fullmatch(r"P\d+", r["pid"])}

PIPELINE_DATATYPES = {  # py/wikidata/model.py EXPECTED_DATATYPES (n4o-rse/open-archaeo, 51d23b1)
    "P31": "wikibase-item", "P6104": "wikibase-item", "P361": "wikibase-item",
    "P195": "wikibase-item", "P217": "string", "P1324": "url", "P8423": "wikibase-item",
    "P1065": "url", "P2960": "time", "P856": "url", "P5565": "external-id",
    "P5568": "external-id", "P356": "external-id", "P277": "wikibase-item",
    "P1547": "wikibase-item", "P2561": "monolingualtext", "P973": "url",
    "P2888": "url", "P921": "wikibase-item",
}

# --------------------------------------------------------------------------
# 1. wikidata-properties.csv
# --------------------------------------------------------------------------
prop_rows = rows_of(curated.PROPERTIES, 7)
props = OrderedDict()
for pid, label, dt, group, role, prov, conf in prop_rows:
    if pid in props:
        problems.append(f"duplicate property {pid}")
    props[pid] = dict(pid=pid, label_en=label, datatype=dt, group=group, role=role,
                      provenance=prov, confidence=conf)

# crosswalk-derived columns
final_terms: dict[str, list[str]] = {}
reviewer_terms: dict[str, list[str]] = {}
xw_range: dict[str, str] = {}
for r in cm_rows:
    if r["wikidata_final"]:
        final_terms.setdefault(r["wikidata_final"], []).append(r["codemeta_property"])
        xw_range.setdefault(r["wikidata_final"], r["wikidata_range"])
    for p in filter(None, r["reviewer_pids"].split("|")):
        reviewer_terms.setdefault(p, []).append(r["codemeta_property"])
# S9 (ConnOSS v1.2.0) publishes a Wikidata-only block of 10 PIDs; the earlier workbook (S1) listed more (P734, P735, P968, P973, P178 ...)
S9_BLOCK = {r["wikidata_pid"] for r in csv.DictReader((DATA / "connoss-wikidata-only-block.csv").open(encoding="utf-8"))}
S9_MATRIX = list(csv.DictReader((DATA / "connoss-summary-matrix.csv").open(encoding="utf-8")))
S9_TERMS = {r["term"] for r in S9_MATRIX}
S9_BRIDGE = {r["codemeta_term"]: r for r in csv.DictReader((DATA / "datacite-wikidata-bridge.csv").open(encoding="utf-8"))}
other_pids = S9_BLOCK

# tiers from the decision tables (best = lowest number)
decisions = []
for cm, label, dt, tier, strat, src, note in rows_of(curated.CODEMETA_DECISIONS, 7):
    decisions.append(dict(codemeta_property=cm, chublets_property=label, chublets_datatype=dt,
                          tier=tier, strategy=strat, source_field=src, note=note))
non_cm = []
for pid, label, dt, tier, strat, src, note in rows_of(curated.NON_CODEMETA_DECISIONS, 7):
    non_cm.append(dict(pid=pid, chublets_property=label, chublets_datatype=dt, tier=tier,
                       strategy=strat, source_field=src, note=note))

label_to_pid = {v["label_en"]: k for k, v in props.items()}
ALIAS = {"instance of (second class)": "P31", "DOI": "P356", "image": "P18",
         "contributor to the creative work or subject": "P767", "(item description)": "",
         "SoftWare Hash IDentifier (SWHID)": "P6138"}


def pid_for(label: str) -> str:
    if label in ALIAS:
        return ALIAS[label]
    return label_to_pid.get(label, "")


tier_of: dict[str, str] = {}
for d in decisions:
    p = pid_for(d["chublets_property"])
    if p and d["strategy"] != "not-planned":
        tier_of[p] = min(tier_of.get(p, "T9"), d["tier"])
for d in non_cm:
    if d["strategy"] != "not-planned":
        tier_of[d["pid"]] = min(tier_of.get(d["pid"], "T9"), d["tier"])

for pid, p in props.items():
    p["in_wikiproject_software_list"] = "yes" if pid in s2_pids else ""
    p["codemeta_terms_final"] = ";".join(final_terms.get(pid, []))
    p["codemeta_terms_reviewer_suggested"] = ";".join(reviewer_terms.get(pid, []))
    p["in_workbook_wikidata_only_block"] = "yes" if pid in other_pids else ""
    p["crosswalk_range"] = xw_range.get(pid, "")
    p["pipeline_expected_datatype"] = PIPELINE_DATATYPES.get(pid, "")
    p["used_by_open_archaeo_pipeline"] = "yes" if pid in PIPELINE_DATATYPES else ""
    if p["pipeline_expected_datatype"] and p["datatype"] and p["pipeline_expected_datatype"] != p["datatype"]:
        problems.append(f"datatype clash {pid}: table {p['datatype']} vs pipeline {p['pipeline_expected_datatype']}")

# every PID that any source mentions must be in the table
mentioned = set(s2_pids) | set(final_terms) | set(reviewer_terms) | other_pids | set(PIPELINE_DATATYPES)
mentioned |= {d["pid"] for d in non_cm}
missing = sorted(p for p in mentioned if p not in props)
missing_real = list(missing)
if missing_real:
    problems.append("PIDs mentioned in sources but absent from the properties table: " + ", ".join(missing_real))

PROP_FIELDS = ["pid", "label_en", "datatype", "group", "role", "in_wikiproject_software_list",
               "codemeta_terms_final", "codemeta_terms_reviewer_suggested",
               "in_workbook_wikidata_only_block", "crosswalk_range", "pipeline_expected_datatype",
               "used_by_open_archaeo_pipeline", "chublets_tier", "provenance", "confidence"]
write_csv("wikidata-properties.csv", PROP_FIELDS,
          sorted(props.values(), key=lambda r: int(r["pid"][1:])))

# --------------------------------------------------------------------------
# 2. wikidata-entities.csv
# --------------------------------------------------------------------------
ents = [dict(qid=a, label_en=b, kind=c, used_for=d, provenance=e, confidence=f)
        for a, b, c, d, e, f in rows_of(curated.ENTITIES, 6)]
write_csv("wikidata-entities.csv", ["qid", "label_en", "kind", "used_for", "provenance", "confidence"], ents)

# --------------------------------------------------------------------------
# 3. master set: the UNION of (a) all CodeMeta terms, (b) the WikiProject Software list,
#    (c) the workbook's Wikidata-only block, (d) what the chublets pipeline needs.
#    Nothing is excluded; `phase` only says when a property is first populated.
# --------------------------------------------------------------------------
PHASE_OF_TIER = {"T1": 1, "T2": 1, "T3": 2, "T4": 3, "T5": 3}
dec_by_term = {d["codemeta_property"]: d for d in decisions}
for t in {r["codemeta_property"] for r in cm_rows}:
    if t not in dec_by_term:
        problems.append(f"CodeMeta term without decision row: {t}")

WIKIPROJECT = set(s2_pids) | set(curated.WIKIPROJECT_LIST_S7_EXTRA)


def humanise(term: str) -> str:
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", term).lower()
    t = t.replace(" url", " URL").replace("(person)", "").strip()
    return "person " + t if term.endswith("(Person)") else t


def dt_from_range(rng: str) -> str:
    alts = [a.strip().lower() for a in re.split(r"\s+or\s+", rng) if a.strip()]
    if not alts:
        return "string"
    if all(a.startswith("date") for a in alts):
        return "time"
    if all(a in ("number", "integer") for a in alts):
        return "quantity"
    if all(a == "url" for a in alts):
        return "url"
    if all(a in ("text", "url", "integer", "number", "boolean", "postaladdress") for a in alts):
        return "string"
    return "wikibase-item"


terms = []  # one dict per CodeMeta term row (84)
for r in cm_rows:
    d = dec_by_term[r["codemeta_property"]]
    final, src = r["wikidata_final"], ("S1" if r["wikidata_final"] else "")
    if not final and r["resolution"] != "corrected-to-none" and curated.S5_CROSSWALK.get(r["codemeta_property"]):
        final, src = curated.S5_CROSSWALK[r["codemeta_property"]], "S5"
    terms.append(dict(term=r["codemeta_property"], group=SECTION_LABEL if False else r["section"],
                      rng=r["codemeta_range"], final=final, src=src, wb_resolution=r["resolution"],
                      mapping_type=r["mapping_type"], reviewer=r["reviewer_pids"],
                      phase=PHASE_OF_TIER[d["tier"]], oa=d["source_field"], note=d["note"], in_workbook=True,
                      cand=curated.CANDIDATES.get(r["codemeta_property"], "")))
for term, group, rng, s5pid, phase, oa, cand, note in rows_of(curated.EXTRA_CODEMETA, 8):
    terms.append(dict(term=term, group=group, rng=rng, final=s5pid, src="S5" if s5pid else "",
                      wb_resolution="not-in-workbook", mapping_type="", reviewer="", phase=int(phase), oa=oa,
                      note=note, in_workbook=False, cand=cand))
    if term in S9_TERMS:                       # e.g. releaseNotes: in the published crosswalk (S9) but without a row in the workbook (S1)
        terms[-1].update(in_workbook=True, s9_only=True, wb_resolution="s9-only")
GROUP_LABEL = {"Thing": "Thing", "outside-hierarchy": "Thing (outside hierarchy)",
               "codemeta-additional": "CodeMeta additional", "CreativeWork": "CreativeWork",
               "SoftwareSourceCode": "SoftwareSourceCode", "SoftwareApplication": "SoftwareApplication"}
for t in terms:
    t["group"] = GROUP_LABEL.get(t["group"], t["group"])
    t["org_pid"] = curated.S5_CROSSWALK.get(t["term"].replace(" (Person)", ""), "")

master: "OrderedDict[str, dict]" = OrderedDict()


def row_for(key, label, dt, status):
    return master.setdefault(key, dict(
        key=key, wb_label=label, datatype=dt, status=status, pid=key if re.fullmatch(r"P\d+", key) else "",
        terms=[], org=[], msrc=[], origin=[], phases=[], oa=[], cand=[], notes=[], prov=[], conf=[]))


def push(lst, v):
    if v and v not in lst:
        lst.append(v)


for t in terms:
    if t["final"]:
        if t["final"] not in props:
            problems.append(f"crosswalk PID {t['final']} ({t['term']}) not in properties table")
            continue
        pr = props[t["final"]]
        g = row_for(t["final"], pr["label_en"], pr["datatype"], "crosswalked")
        push(g["prov"], ("S9" if t.get("s9_only") else "S1") if t["in_workbook"] else "")
        push(g["prov"], pr["provenance"])
        push(g["conf"], pr["confidence"])
    else:
        g = row_for("cm:" + t["term"], humanise(t["term"]), dt_from_range(t["rng"]), "codemeta-only")
        push(g["prov"], ("S9" if t.get("s9_only") else "S1") if t["in_workbook"] else "S8")
        push(g["conf"], "checked" if t["in_workbook"] else "source-claimed")
        for pid in filter(None, re.split(r"[;|]", t["cand"] + ";" + t["reviewer"])):
            push(g["cand"], pid)
    push(g["terms"], t["term"] if not t["in_workbook"] else t["term"])
    push(g["org"], t["org_pid"])
    push(g["msrc"], t["src"])
    g["phases"].append(t["phase"])
    push(g["oa"], t["oa"])
    push(g["notes"], t["note"])

# (b) WikiProject Software list, (c) workbook Wikidata-only block
for pid in sorted(WIKIPROJECT, key=lambda x: int(x[1:])):
    if pid not in props:
        problems.append(f"WikiProject PID {pid} not in properties table")
        continue
    pr = props[pid]
    g = row_for(pid, pr["label_en"], pr["datatype"], "wikidata-only")
    push(g["origin"], "WikiProject list")
    push(g["prov"], pr["provenance"]); push(g["conf"], pr["confidence"])
for pid in sorted(other_pids, key=lambda x: int(x[1:])):
    if pid in props:
        pr = props[pid]
        g = row_for(pid, pr["label_en"], pr["datatype"], "wikidata-only")
        push(g["origin"], "published crosswalk block")
        push(g["prov"], "S9"); push(g["conf"], pr["confidence"])
# (d) what the chublets pipeline / WikiProject chublets page need
for d in non_cm:
    pid = d["pid"]
    if pid not in props:
        problems.append(f"chublets PID {pid} not in properties table")
        continue
    pr = props[pid]
    g = row_for(pid, pr["label_en"], pr["datatype"], "chublets-addition")
    if pid in PIPELINE_DATATYPES:
        push(g["origin"], "chublets pipeline")
    g["phases"].append(PHASE_OF_TIER[d["tier"]])
    push(g["oa"], d["source_field"]); push(g["notes"], d["note"])
    push(g["prov"], pr["provenance"]); push(g["conf"], pr["confidence"])
for pid in PIPELINE_DATATYPES:
    if pid in master:
        push(master[pid]["origin"], "chublets pipeline")
        master[pid]["phases"].append(1)
    else:
        problems.append(f"pipeline PID {pid} missing from master")
# new properties that exist in no vocabulary
EXTRA = [
    (0, "equivalent Wikidata property", "external-id", "Property metadata. Formatter URL https://www.wikidata.org/entity/$1 so each local property points at its Wikidata twin."),
    (0, "equivalent CodeMeta term", "string", "Property metadata. Formatter URL https://codemeta.github.io/terms/$1 ; stores the CodeMeta term name."),
    (0, "equivalent schema.org term", "string", "Property metadata. Needed for the RDF export (owl:equivalentProperty / schema:sameAs)."),
    (0, "close match Wikidata property", "external-id", "Property metadata for CodeMeta-only properties: records a candidate Wikidata property without claiming equivalence (skos:closeMatch)."),
    (1, "Wikidata item", "external-id", "Link from a chublets item to its Wikidata twin. Formatter URL https://www.wikidata.org/entity/$1. Alternative to a URL-valued exact match; decide once."),
    (1, "open-archaeo ID", "external-id", "Dedicated identifier instead of P217+P195 (P6830 swMATH precedent). Formatter URL https://open-archaeo.info/post/$1/ . The minted 6-hex id is NOT a candidate: it is a function of the slug."),
]
for ph, lab, dt, note in EXTRA:
    g = row_for("new:" + lab, lab, dt, "chublets-addition")
    push(g["origin"], "new"); g["phases"].append(ph); push(g["notes"], note); push(g["prov"], "S3;S4"); push(g["conf"], "proposal")

set_rows = []
for key, g in master.items():
    phase = min(g["phases"]) if g["phases"] else (1 if g["pid"] in PIPELINE_DATATYPES else 3)
    in_wp = ("yes" if g["pid"] in WIKIPROJECT else "no") if g["pid"] else ""
    set_rows.append(dict(
        phase=phase, status=g["status"], wb_label=g["wb_label"], datatype=g["datatype"], wikidata_pid=g["pid"],
        codemeta_terms=";".join(g["terms"]), codemeta_org_pid=";".join(g["org"]),
        mapping_source=";".join(g["msrc"]), in_wikiproject_software=in_wp,
        wikidata_origin=";".join(g["origin"]), open_archaeo_source=" / ".join(g["oa"]),
        candidate_wikidata_pids=";".join(g["cand"]), note=" ".join(g["notes"])[:420],
        provenance=";".join(x for x in g["prov"] if x), confidence=";".join(dict.fromkeys(g["conf"])),
        datacite_elements=" || ".join(dict.fromkeys(S9_BRIDGE[x]["datacite_cell"] for x in g["terms"] if x in S9_BRIDGE and S9_BRIDGE[x]["datacite_cell"]))))
ORDER = {"crosswalked": 0, "codemeta-only": 1, "wikidata-only": 2, "chublets-addition": 3}
set_rows.sort(key=lambda r: (ORDER[r["status"]], r["phase"], r["wb_label"].lower()))
SET_FIELDS = ["status", "phase", "wb_label", "datatype", "wikidata_pid", "codemeta_terms", "codemeta_org_pid",
              "mapping_source", "in_wikiproject_software", "wikidata_origin", "open_archaeo_source",
              "candidate_wikidata_pids", "note", "provenance", "confidence", "datacite_elements"]
write_csv("wikibase-property-set.csv", SET_FIELDS, set_rows)
status_of = {r["wikidata_pid"]: r for r in set_rows if r["wikidata_pid"]}
label_of_key = {k: g["wb_label"] for k, g in master.items()}

# view A: every CodeMeta term -> its Wikibase property (84 rows)
term_rows = []
for i, t in enumerate(terms, 1):
    key = t["final"] if t["final"] else "cm:" + t["term"]
    g = master.get(key)
    differs = ""
    if t["org_pid"] and t["final"] and t["org_pid"] != t["final"]:
        differs = f"workbook {t['final']} vs codemeta.org {t['org_pid']}"
    elif t["org_pid"] and not t["final"]:
        differs = f"workbook: none, codemeta.org {t['org_pid']}"
    term_rows.append(dict(
        row_id=f"C{i:03d}", codemeta_term=t["term"], codemeta_group=t["group"], codemeta_range=t["rng"],
        in_reviewed_workbook="yes" if t["in_workbook"] else "no",
        status="crosswalked" if t["final"] else "codemeta-only", wikidata_pid=t["final"],
        wikidata_label=props[t["final"]]["label_en"] if t["final"] in props else "",
        mapping_source=t["src"], workbook_resolution=t["wb_resolution"], workbook_mapping_type=t["mapping_type"],
        codemeta_org_pid=t["org_pid"], differs_from_codemeta_org=differs,
        wikibase_property=g["wb_label"] if g else "", wikibase_datatype=g["datatype"] if g else "",
        candidate_wikidata_pids=";".join(g["cand"]) if g and not t["final"] else "",
        in_wikiproject_software=("yes" if t["final"] in WIKIPROJECT else "no") if t["final"] else "",
        phase=t["phase"], open_archaeo_source=t["oa"], note=t["note"],
        s9_wikidata_pids=S9_BRIDGE.get(t["term"], {}).get("wikidata_pids", ""),
        s9_datacite=S9_BRIDGE.get(t["term"], {}).get("datacite_cell", ""),
        s9_bridge=S9_BRIDGE.get(t["term"], {}).get("bridge", "not in S9")))
write_csv("codemeta-terms-to-wikibase.csv",
          ["row_id", "codemeta_term", "codemeta_group", "codemeta_range", "in_reviewed_workbook", "status",
           "wikidata_pid", "wikidata_label", "mapping_source", "workbook_resolution", "workbook_mapping_type",
           "codemeta_org_pid", "differs_from_codemeta_org", "wikibase_property", "wikibase_datatype",
           "candidate_wikidata_pids", "in_wikiproject_software", "phase", "open_archaeo_source", "note", "s9_wikidata_pids", "s9_datacite", "s9_bridge"], term_rows)

# view B: every property of the WikiProject Software list -> its Wikibase property
s2_cat = {r["pid"]: r["category"] for r in s2 if re.fullmatch(r"P\d+", r["pid"])}
wp_rows = []
for pid in sorted(WIKIPROJECT, key=lambda x: int(x[1:])):
    g = master[pid]
    cmt = [t["term"] for t in terms if t["final"] == pid]
    wp_rows.append(dict(
        wikidata_pid=pid, wikidata_label=props[pid]["label_en"], wikiproject_category=s2_cat.get(pid, "(page excerpt in earlier chat; not in CSV)"),
        in_csv_transcription="yes" if pid in s2_pids else "no", wikibase_property=g["wb_label"],
        status=g["status"] if g["status"] in ("crosswalked", "wikidata-only") else ("crosswalked" if cmt else "wikidata-only"),
        codemeta_terms=";".join(cmt), phase=next(r["phase"] for r in set_rows if r["wikidata_pid"] == pid),
        label_confidence=props[pid]["confidence"]))
wp_rows.append(dict(wikidata_pid="(unidentified)", wikidata_label="further package-registry ID properties",
                    wikiproject_category="Links & registries", in_csv_transcription="yes (as one row)",
                    wikibase_property="", status="GAP",
                    codemeta_terms="", phase="", label_confidence="not enumerated: the CSV row reads '12 more package-registry IDs'; run tools/check_completeness.py against the page"))
write_csv("wikidata-software-to-wikibase.csv",
          ["wikidata_pid", "wikidata_label", "wikiproject_category", "in_csv_transcription", "wikibase_property",
           "status", "codemeta_terms", "phase", "label_confidence"], wp_rows)

# summary for the paper
cm_distinct = sorted({t["term"] for t in terms})
cw_terms = sorted({t["term"] for t in terms if t["final"]})
co_terms = sorted({t["term"] for t in terms if not t["final"]})
wb_terms = sorted({t["term"] for t in terms if t["in_workbook"]})
wb_cw = sorted({t["term"] for t in terms if t["in_workbook"] and t["src"] == "S1"})
s5_only = sorted({t["term"] for t in terms if t["src"] == "S5"})
cw_pids = sorted({t["final"] for t in terms if t["final"]}, key=lambda x: int(x[1:]))
cw_in_wp = [p for p in cw_pids if p in WIKIPROJECT]
cw_not_wp = [p for p in cw_pids if p not in WIKIPROJECT]
wp_only = [p for p in WIKIPROJECT if p not in cw_pids]
st = Counter(r["status"] for r in set_rows)
SUMMARY = [
    ("codemeta_terms_total", len(cm_distinct), f"distinct term names over {len(terms)} rows (relatedLink has two rows; `identifier (Person)` is separate)"),
    ("codemeta_terms_in_reviewed_workbook", len(wb_terms), f"68 properties of the published ConnOSS crosswalk (S9) = {sum(1 for t in terms if t['in_workbook'] and not t.get('s9_only'))} rows of the earlier workbook S1 = 67 distinct terms (relatedLink twice) + releaseNotes, which only S9 has"),
    ("codemeta_terms_not_in_workbook", len(cm_distinct) - len(wb_terms), "listed on codemeta.github.io/terms (S8) but not in the ConnOSS crosswalk: " + ", ".join(sorted(set(cm_distinct) - set(wb_terms)))),
    ("codemeta_terms_crosswalked_to_wikidata", len(cw_terms), f"{len(wb_cw)} via the reviewed workbook (S1), {len(s5_only)} only via codemeta.org crosswalk (S5): " + ", ".join(s5_only)),
    ("codemeta_terms_without_wikidata_property", len(co_terms), "these become new CodeMeta-only properties in the Wikibase"),
    ("wikidata_pids_used_by_crosswalk", len(cw_pids), "distinct Wikidata properties that have a CodeMeta term"),
    ("  of which in the WikiProject Software list", len(cw_in_wp), ", ".join(cw_in_wp)),
    ("  of which NOT in the WikiProject Software list", len(cw_not_wp), ", ".join(cw_not_wp)),
    ("wikiproject_software_pids_known", len(WIKIPROJECT), f"{len(s2_pids)} in the CSV transcription + {len(curated.WIKIPROJECT_LIST_S7_EXTRA)} only in the earlier page excerpt; PLUS an unknown number of registry IDs (see GAP row)"),
    ("  of which with a CodeMeta term", len([p for p in WIKIPROJECT if p in cw_pids]), ""),
    ("  of which Wikidata-only (no CodeMeta term)", len(wp_only), ""),
    ("published_wikidata_only_block_not_in_wikiproject_list", len([p for p in other_pids if p not in WIKIPROJECT and p in props]), ", ".join(p for p in sorted(other_pids, key=lambda x: int(x[1:])) if p not in WIKIPROJECT and p in props)),
    ("s9_bridge_both_wikidata_and_datacite", sum(1 for b in S9_BRIDGE.values() if b["bridge"] == "both"), "CodeMeta terms with a Wikidata property AND a DataCite element in S9 (DataCite<->Wikidata is derived via CodeMeta, not published)"),
    ("s9_bridge_wikidata_only", sum(1 for b in S9_BRIDGE.values() if b["bridge"] == "wikidata-only"), "term has a Wikidata property but no DataCite element"),
    ("s9_bridge_datacite_only", sum(1 for b in S9_BRIDGE.values() if b["bridge"] == "datacite-only"), "term has a DataCite element but no Wikidata property (CodeMeta-only property in the Wikibase)"),
    ("s9_bridge_neither", sum(1 for b in S9_BRIDGE.values() if b["bridge"] == "neither"), "term in neither"),
    ("wikibase_properties_total", len(set_rows), "the union; nothing excluded"),
] + [(f"  status {k}", st.get(k, 0), v) for k, v in
     [("crosswalked", "CodeMeta term and Wikidata property, one Wikibase property"),
      ("codemeta-only", "CodeMeta term without Wikidata twin: new property"),
      ("wikidata-only", "Wikidata property without CodeMeta term"),
      ("chublets-addition", "needed by the chublets pipeline or the Wikibase itself; in neither vocabulary")]]
write_csv("mapping-summary.csv", ["metric", "value", "note"], [dict(metric=a, value=b, note=c) for a, b, c in SUMMARY])
for a, b, c in SUMMARY:
    print(f"    {a}: {b}")

# enrich wikidata-properties.csv with the Wikibase status
cand_pids = set()
for g in master.values():
    cand_pids.update(g["cand"])
for t in terms:
    cand_pids.update(x for x in re.split(r"[;|]", t["reviewer"] + ";" + t["cand"] + ";" + t["org_pid"]) if re.fullmatch(r"P\d+", x))
for pid, p in props.items():
    if pid in status_of:
        p["wikibase_status"] = status_of[pid]["status"]
    elif pid in cand_pids:
        p["wikibase_status"] = "candidate only (not in set)"
    else:
        p["wikibase_status"] = "NOT ACCOUNTED FOR"
    p["in_wikiproject_software_list"] = "yes" if pid in WIKIPROJECT else ""
PROP_FIELDS.insert(PROP_FIELDS.index("chublets_tier"), "wikibase_status")
PROP_FIELDS.remove("chublets_tier")
write_csv("wikidata-properties.csv", PROP_FIELDS, sorted(props.values(), key=lambda r: int(r["pid"][1:])))
lost = [p["pid"] for p in props.values() if p["wikibase_status"] == "NOT ACCOUNTED FOR"]
if lost:
    problems.append("properties neither in the Wikibase set nor a documented candidate: " + ", ".join(lost))
print("  candidate-only PIDs:", sorted((p["pid"] for p in props.values() if p["wikibase_status"].startswith("candidate")), key=lambda x: int(x[1:])))

# --------------------------------------------------------------------------
# 5. open-archaeo-columns.csv (measured against the shipped CSV)
# --------------------------------------------------------------------------
oa = list(csv.DictReader((SRC / "open-archaeo-software.csv").open(encoding="utf-8")))
fill = {k: sum(1 for r in oa if r[k].strip()) for k in oa[0].keys()}
roles = Counter(r["platform_role"] for r in oa if r["platform"].strip())
regs = Counter(r["registry_name"] for r in oa if r["registry_name"].strip())
# MAPPING.md claims (docs/MAPPING.md, "Column by column")
OA_MAP = [
    ("id", "(minted)", "", "", "function of slug; not an identifier candidate", None),
    ("slug", "open-archaeo ID (proposed) / P217 inventory number", "P217", "P195 collection", "key of the register", None),
    ("url", "P2888 exact match", "P2888", "", "entry page, 416", 416),
    ("name", "label + P2561 name", "P2561", "", "", 416),
    ("description", "item description", "", "", "needs rewriting: sentences, not Wikidata-style descriptions", 416),
    ("category", "P31 instance of (second value)", "P31", "", "resolved through vocabulary.json item_class", 416),
    ("platform", "P277 / P1547 / P31 refinement by platform_role", "P277|P1547|P31", "", "column conflates three concepts", None),
    ("platform_role", "(selector for platform)", "", "", "language 301, host application 34, deployment 8 per MAPPING.md", None),
    ("tags", "P921 main subject", "P921", "", "56 tags need reconciliation", 416),
    ("authors", "P178 developer", "P178", "P1545 series ordinal", "pipe-separated; order is meaningful", 416),
    ("repository", "P1324 source code repository URL", "P1324", "P8423 (required), P1065, P2960", "390 per MAPPING.md", 390),
    ("repository_host", "(derives P8423 and optionally P10627)", "P8423", "", "385 Git, 1 Bitbucket ambiguous", None),
    ("registry", "P5565 / P5568 identifier value", "P5565|P5568", "", "package name parsed from URL", None),
    ("registry_name", "(selector for registry)", "", "", "CRAN 39, PyPI 1 per MAPPING.md", None),
    ("doi", "P356 DOI (qualifier on P348 if a Zenodo release DOI)", "P356", "", "34 per MAPPING.md; 24 are 10.5281 (Zenodo)", 34),
    ("publication", "P1343 described by source (as item)", "P1343", "", "25 per MAPPING.md; 20 are doi.org URLs", 25),
    ("website", "P856 official website", "P856", "", "121 per MAPPING.md", 121),
    ("blogpost", "P973 described at URL", "P973", "", "with youtube: 4 per MAPPING.md", None),
    ("youtube", "P973 described at URL", "P973", "", "", None),
    ("twitter", "-", "", "", "not import material", None),
    ("internetarchive", "P1065 archive URL (qualifier on P1324)", "P1065", "P2960 from path", "222 per MAPPING.md; 221 parse", 222),
    ("notes", "-", "", "", "not import material", None),
]
oa_rows = []
for col, target, pids, qual, note, claim in OA_MAP:
    if col not in fill:
        problems.append(f"open-archaeo column missing in CSV: {col}")
        continue
    first = next((r[col] for r in oa if r[col].strip()), "")
    flag = ""
    if claim is not None and fill[col] != claim:
        flag = f"MAPPING.md says {claim}, measured {fill[col]}"
    oa_rows.append(dict(column=col, filled=fill[col], of=len(oa), example=first[:70],
                        wikidata_target=target, wikidata_pids=pids, qualifiers=qual,
                        note=note, mapping_md_check=flag))
extra_check = []
if fill["blogpost"] + fill["youtube"] != 4:
    extra_check.append(f"blogpost+youtube measured {fill['blogpost']}+{fill['youtube']} (MAPPING.md: 4)")
print("  platform_role:", dict(roles), "| registry_name:", dict(regs), "|", "; ".join(extra_check) or "blog/youtube ok")
write_csv("open-archaeo-columns.csv",
          ["column", "filled", "of", "example", "wikidata_target", "wikidata_pids", "qualifiers", "note", "mapping_md_check"],
          oa_rows)

# --------------------------------------------------------------------------
# 6. identity-block-variants.csv
# --------------------------------------------------------------------------
IDENT = [
    # statement, value, V1 MAPPING.md, V2 model.py, V3 WikiProject page, V4 stated in memory
    ("P31 instance of", "Q141115627 chublet", "Y", "Y", "Y (open-archaeo section)", "Y"),
    ("P6104 maintained by WikiProject", "Q141169143", "Y", "Y", "Y (general section)", "Y"),
    ("P361 part of", "Q141115774 chublets.software", "", "Y", "Y (both sections)", ""),
    ("P361 part of", "Q141190255 open-archaeo (Repository)", "", "Y", "Y (open-archaeo section)", ""),
    ("P195 collection", "Q141190255", "", "Y", "", ""),
    ("P217 inventory number", "slug, qualified by P195", "", "Y", "", ""),
    ("P2888 exact match", "https://open-archaeo.info/post/{slug}/", "Y (column table)", "Y", "Y (open-archaeo section)", ""),
]
write_csv("identity-block-variants.csv",
          ["statement", "value", "V1_MAPPING_md", "V2_model_py_HEAD", "V3_WikiProject_page", "V4_stated_by_Flo"],
          [dict(statement=a, value=b, V1_MAPPING_md=c, V2_model_py_HEAD=d, V3_WikiProject_page=e, V4_stated_by_Flo=f)
           for a, b, c, d, e, f in IDENT])

# --------------------------------------------------------------------------
# 7. wikibase-bootstrap-order.csv
# --------------------------------------------------------------------------
BOOT = [
    (1, "Create the Wikibase instance", "Decide host (wikibase.cloud or self-hosted) and the item/property prefix; the paper draft shows chublets.wikibase.cloud as illustrative only.", "decision"),
    (2, "Create the property-metadata properties", "The four rows with origin 'new' and phase 0 in wikibase-property-set.csv: equivalent Wikidata property, equivalent CodeMeta term, equivalent schema.org term, close match Wikidata property. Everything created afterwards can document itself.", "properties"),
    (3, "Create ALL properties of the set in one go", "Every row of wikibase-property-set.csv: crosswalked, codemeta-only, wikidata-only and chublets-addition. `phase` says when a property is first populated, not whether it exists. Keep a table Wikidata PID -> local PID.", "properties"),
    (4, "Fill the property metadata", "For every property: equivalent Wikidata property (the twin PID), equivalent CodeMeta term, close match Wikidata property for CodeMeta-only rows, formatter URL for external-ids, constraints copied from Wikidata where useful (P1324 requires P8423).", "property metadata"),
    (5, "Create the class items", "chublet (local twin of Q141115627), Little Minion, research software, software library, application software, script file; link each to its Wikidata twin.", "items"),
    (6, "Create the controlled-vocabulary items", "Git, the programming languages and host applications from vocabulary.json (currently all unresolved), the 56 open-archaeo tags after reconciliation, version types, licences.", "items"),
    (7, "Create person and organisation items", "Developers: reconcile through GitHub username (P2037) first, name string second. Q66606154 and Q88865971 already exist in Wikidata.", "items"),
    (8, "Import the example chublets", "Start with the examples in examples/ and check them in the UI before any batch.", "items"),
    (9, "Batch-import open-archaeo (phase 1)", "Use the 208+208 split from n4o-rse/open-archaeo; QuickStatements syntax with local property IDs.", "import"),
    (10, "Populate phases 2 and 3", "Phase 2 from repository metadata (CFF, CodeMeta, GitHub API); phase 3 properties exist but are filled manually or by later sources.", "import"),
    (11, "Export check", "Run the SPARQL queries in sparql/ against the new instance and compare with the CodeMeta projection.", "verification"),
]
write_csv("wikibase-bootstrap-order.csv", ["step", "title", "detail", "kind"],
          [dict(step=a, title=b, detail=c, kind=d) for a, b, c, d in BOOT])

# --------------------------------------------------------------------------
# 8. sources.csv
# --------------------------------------------------------------------------
SOURCES = [
    ("S1", "sources/codemeta-wikidata-crosswalk.xlsx", "CodeMeta <-> Wikidata crosswalk workbook (template Leyla Jael Castro; review Stephan Ferenz; filled by Florian Thiery; reviewers Maryam, Lu, Aida)", "chublets-software/chublets-visuals data/raw/ (HEAD 0a9c5a7)", "2026-10-21", "primary, read in full"),
    ("S2", "sources/wikidata-software-properties.csv", "47-row transcription of the WikiProject Informatics/Software/Properties PDF, five categories", "chublets-software/chublets-visuals data/raw/", "2026-10-21", "hand-transcribed by Flo (2026-09-10); the PDF itself was not available"),
    ("S3", "sources/open-archaeo-MAPPING.md, sources/open-archaeo-software.csv, sources/vocabulary.json", "n4o-rse/open-archaeo: target model, 416-entry software subset, controlled vocabulary; model.py read for constants", "n4o-rse/open-archaeo (HEAD 51d23b1)", "2026-10-21", "primary; MAPPING.md is older than model.py (see identity-block-variants.csv)"),
    ("S4", "-", "Wikidata:WikiProject chublets-software", "https://www.wikidata.org/wiki/Wikidata:WikiProject_chublets-software", "2026-10-21", "search snippet only; direct fetch blocked"),
    ("S5", "-", "CodeMeta crosswalk for Wikidata properties (30 rows)", "https://codemeta.github.io/crosswalk/wikidata/", "2026-10-21", "fetched in full; differs from S1 in places (S1 contains the reviewers' corrections)"),
    ("S6", "-", "Various Wikidata pages and tutorials seen as search snippets", "see docs/05-open-points.md", "2026-10-21", "snippets only"),
    ("S9", "sources/connoss/ (25 files from Zenodo)", "Official ConnOSS crosswalk 'Crosswalks of Research Software Metadata Schemas to CodeMeta', v1.2.0 (2026-08-14), CC BY 4.0; 21 schemas incl. Wikidata and DataCite 4.6; 68 properties", "https://doi.org/10.5281/zenodo.21935688", "2026-10-21", "supplied by Flo as ZIP; read in full; supersedes S1 as the citable source (Wikidata column identical to S1 for all 67 shared terms)"),
    ("S8", "-", "CodeMeta terms page (all terms with ranges, v2 and v3)", "https://codemeta.github.io/terms/", "2026-10-21", "fetched in full; source of the 16 terms that have no workbook row"),
    ("S7", "-", "Earlier chats with Flo (Wikidata Properties fuer Software, 2026-08-25; chublets-visuals talk chat, 2026-09-10)", "claude.ai chat history", "2026-10-21", "summaries and excerpts; the files produced there are not available"),
    ("R", "-", "Assistant recall", "-", "2026-10-21", "unchecked; run tools/verify_wikidata.py"),
]
write_csv("sources.csv", ["code", "local_file", "description", "origin", "retrieved", "reliability"],
          [dict(code=a, local_file=b, description=c, origin=d, retrieved=e, reliability=f) for a, b, c, d, e, f in SOURCES])

# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
print("\nstatus counts:", dict(Counter(r["status"] for r in set_rows)), "| total", len(set_rows))
print("phases:", dict(sorted(Counter(r["phase"] for r in set_rows).items())))
if oa_rows:
    print("MAPPING.md mismatches:", [r["column"] + ": " + r["mapping_md_check"] for r in oa_rows if r["mapping_md_check"]])
_labs = Counter(r["wb_label"].lower() for r in set_rows)
problems += [f"duplicate wb_label: {k}" for k, n in _labs.items() if n > 1]
if problems:
    print("\nPROBLEMS:")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("\nOK")
