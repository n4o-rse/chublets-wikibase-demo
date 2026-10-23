#!/usr/bin/env python3
"""Write diagrams/*.mmd (numbers read from data/*.csv) and render them to SVG + PNG with mmdc.

    python tools/build_diagrams.py            # needs mermaid-cli (mmdc) and a Chromium
    python tools/build_diagrams.py --no-render  # only write the .mmd sources

Colour scheme (Flo's standing Mermaid scheme):
    so      Subject/Object  #e2e8f0 on black text   (pastel grey, oval)  - items, process steps
    ro      RealObject      #166534 white text      (dark green)         - real-world things: repos, websites, people, services
    cls     Class           #9a3412 white text      (dark orange)        - classes
    term    Term            #4c1d95 white text      (dark purple)        - controlled-vocabulary values
    owl     OWL nodes       #ffffff black text      (white)              - vocabulary terms (CodeMeta, schema.org)
    pm      PropMeta        #fbbf24 black text      (amber)              - properties, qualifiers, property metadata
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA, OUT = ROOT / "data", ROOT / "diagrams"
OUT.mkdir(exist_ok=True)

CLASSDEFS = """
  classDef so fill:#e2e8f0,stroke:#000000,color:#000000
  classDef ro fill:#166534,stroke:#000000,color:#ffffff
  classDef cls fill:#9a3412,stroke:#000000,color:#ffffff
  classDef term fill:#4c1d95,stroke:#000000,color:#ffffff
  classDef owl fill:#ffffff,stroke:#000000,color:#000000
  classDef pm fill:#fbbf24,stroke:#000000,color:#000000
"""
LEGEND = """
  subgraph LEG["Legend"]
    direction LR
    l1(["item / step"]):::so
    l2["real object"]:::ro
    l3["class"]:::cls
    l4["term"]:::term
    l5["vocabulary term"]:::owl
    l6["property / qualifier"]:::pm
  end
"""


def read(name):
    return list(csv.DictReader((DATA / name).open(encoding="utf-8")))


def mm(title, body, direction="LR", legend=False):
    return f"---\ntitle: \"{title}\"\n---\nflowchart {direction}\n{CLASSDEFS}{body}{LEGEND if legend else ''}"


summ = {r["metric"].strip(): int(r["value"]) for r in read("mapping-summary.csv") if r["value"].strip().isdigit()}
boot = read("wikibase-bootstrap-order.csv")
pset = read("wikibase-property-set.csv")
st_ = Counter(r["status"] for r in pset)

diagrams = {}

# 0 legend (kept out of the other diagrams so edges never cross it)
diagrams["00-legend"] = mm("Colour legend for all diagrams", """
  a(["item or process step"]):::so
  b["real object: repository, website, person, service"]:::ro
  c["class"]:::cls
  d["term: controlled-vocabulary value"]:::term
  e["vocabulary term: CodeMeta, schema.org"]:::owl
  f["property, qualifier, property metadata"]:::pm
  a ~~~ b ~~~ c ~~~ d ~~~ e ~~~ f
""", direction="TB")

# 1 identity block ---------------------------------------------------------
diagrams["01-identity-block"] = mm("The identity of an open-archaeo chublet (as in pipeline model.py)", """
  item(["chublet item<br/>e.g. Alligator"]):::so
  chub["chublet<br/>Q141115627"]:::cls
  minion["Little Minion<br/>Q73899440"]:::cls
  wp["WikiProject chublets.software<br/>Q141169143"]:::ro
  plat["chublets.software<br/>Q141115774"]:::ro
  oa["open-archaeo (Repository)<br/>Q141190255"]:::ro
  slug["P217 inventory number: 'alligator'<br/>qualifier P195 collection: open-archaeo"]:::pm
  url["https://open-archaeo.info/post/alligator/"]:::ro
  item -->|"P31 instance of"| chub
  chub -->|"subclass of"| minion
  item -->|"P6104 maintained by WikiProject"| wp
  item -->|"P361 part of"| plat
  item -->|"P361 part of"| oa
  item -->|"P195 collection"| oa
  item --> slug
  item -->|"P2888 exact match"| url
""")

# 2 crosswalk flow ---------------------------------------------------------
diagrams["02-crosswalk-flow"] = mm("How the Wikibase property set is composed (all CodeMeta terms and all WikiProject properties)", f"""
  cm["CodeMeta terms<br/>{summ['codemeta_terms_total']}"]:::owl
  wp["WikiProject Software list<br/>{summ['wikiproject_software_pids_known']} identified, plus registry IDs not enumerated"]:::owl
  cw["crosswalked<br/>{st_['crosswalked']} Wikibase properties<br/>CodeMeta term = Wikidata property"]:::ro
  co["CodeMeta only<br/>{st_['codemeta-only']} new properties<br/>no Wikidata twin"]:::cls
  wo["Wikidata only<br/>{st_['wikidata-only']} properties<br/>no CodeMeta term"]:::pm
  ad["chublets additions<br/>{st_['chublets-addition']} properties<br/>pipeline and Wikibase needs"]:::term
  cm -->|"{summ['codemeta_terms_crosswalked_to_wikidata']} terms"| cw
  cm -->|"{summ['codemeta_terms_without_wikidata_property']} terms"| co
  wp -->|"{summ['of which with a CodeMeta term']} properties"| cw
  wp -->|"{summ['of which Wikidata-only (no CodeMeta term)']} properties"| wo
  wb["Wikibase property set<br/>{summ['wikibase_properties_total']} properties, nothing excluded"]:::so
  cw --> wb
  co --> wb
  wo --> wb
  ad --> wb
""", direction="LR")

# 3 example item -----------------------------------------------------------
diagrams["03-example-alligator"] = mm("Example item: Alligator (open-archaeo row 2f00c7)", """
  item(["Alligator"]):::so
  chub["chublet"]:::cls
  app["application software<br/>Q166142"]:::cls
  repo["github.com/leiza-rse/alligator"]:::ro
  q1["P8423 version control system → Git"]:::pm
  q2["P1065 archive URL (Internet Archive)<br/>P2960 archive date 2021-06-04"]:::pm
  web["tools.leiza.de/alligator/"]:::ro
  git["Git<br/>Q186055"]:::term
  tag1["Statistical analysis"]:::term
  tag2["Schemas and ontologies"]:::term
  p1["Florian Thiery<br/>Q66606154"]:::ro
  p2["Allard W. Mees<br/>Q88865971"]:::ro
  item -->|"P31"| chub
  item -->|"P31 (category: Standalone software)"| app
  item -->|"P1324 source code repository URL"| repo
  repo -.-> q1
  q1 -.-> git
  repo -.-> q2
  item -->|"P856 official website"| web
  item -->|"P921 main subject (unresolved)"| tag1
  item -->|"P921 main subject (unresolved)"| tag2
  item -->|"P178 developer, ordinal 1 (to reconcile)"| p1
  item -->|"P178 developer, ordinal 2 (to reconcile)"| p2
""")

# 4 pipeline ---------------------------------------------------------------
diagrams["04-open-archaeo-to-wikibase"] = mm("open-archaeo to Wikidata to a chublets Wikibase", """
  csv["open-archaeo.csv<br/>562 entries"]:::ro
  sw["software subset<br/>416 entries"]:::ro
  split{{"stratified split<br/>208 + 208"}}:::so
  py["Python route<br/>py/wikidata/main.py"]:::so
  orf["OpenRefine route<br/>find.software"]:::so
  wd["Wikidata<br/>P31 chublet · P6104 WikiProject"]:::ro
  rec["reconcile first<br/>P1324 repository, then DOI"]:::so
  wb["chublets Wikibase<br/>waves 0 to 3"]:::ro
  cmj["CodeMeta"]:::owl
  dcat["DCAT"]:::owl
  dc["DataCite"]:::owl
  nfdi["nfdi.software"]:::ro
  csv -->|"filter 3 categories"| sw
  sw --> split
  split --> py
  split --> orf
  py --> rec
  orf --> rec
  rec --> wd
  wd -->|"Wikidata item property"| wb
  wb --> cmj
  wb --> dcat
  wb --> dc
  dcat --> nfdi
""")

# 5 bootstrap --------------------------------------------------------------
steps = "\n".join(f'  s{r["step"]}(["{r["step"]}. {r["title"]}"]):::so' for r in boot)
chain = "\n".join(f"  s{boot[i]['step']} --> s{boot[i + 1]['step']}" for i in range(len(boot) - 1))
diagrams["05-wikibase-bootstrap-order"] = mm("Bootstrapping a new chublets Wikibase", steps + "\n" + chain, direction="TB", legend=False)


# 6 class hierarchy (only where a hierarchy is evidenced; dashed = expected from general Wikidata, unverified) ------
diagrams["06-class-hierarchy"] = mm("Class hierarchy: solid = evidenced in open-archaeo sources, dashed = expected in Wikidata (unverified)", """
  chub["chublet<br/>Q141115627"]:::cls
  lm["Q73899440<br/>Little Minion (label disputed, see open points)"]:::cls
  rs["research software<br/>Q95001953"]:::cls
  sw["software<br/>Q7397"]:::cls
  cp["computer program<br/>Q40056"]:::cls
  app["application software<br/>Q166142"]:::cls
  lib["software library<br/>Q188860"]:::cls
  scr["script file<br/>Q1070421"]:::cls
  foss["free and open-source software<br/>Q506883"]:::cls
  aw["abandonware<br/>Q281039"]:::cls
  chub -->|"P279 subclass of"| lm
  chub -.->|"P279, only if the superclass is not applied via P31"| rs
  rs -.->|"P279"| sw
  cp -.->|"P279"| sw
  app -.->|"P279"| cp
  lib -.->|"P279"| sw
  scr -.->|"P279"| sw
  foss -.->|"P279"| sw
  aw -.->|"P279"| sw
""", direction="BT")

# 7 how an item gets its classes (P31, no hierarchy) ------------------------------
diagrams["07-item-instance-of"] = mm("How an open-archaeo item receives its classes (P31, not P279)", """
  item(["chublet item<br/>e.g. Alligator"]):::so
  chub["chublet<br/>Q141115627"]:::cls
  rs["research software<br/>Q95001953<br/>vocabulary.json superclass"]:::cls
  app["application software<br/>Q166142<br/>Standalone software"]:::cls
  lib["software library<br/>Q188860<br/>Packages and libraries"]:::cls
  scr["script file<br/>Q1070421<br/>Scripts"]:::cls
  item -->|"P31 always"| chub
  item -->|"P31 applied to every item"| rs
  item -->|"P31 by open-archaeo category"| app
  item -->|"P31 by open-archaeo category"| lib
  item -->|"P31 by open-archaeo category"| scr
""", direction="LR")

# 8 all entities, no hierarchy -------------------------------------------------
ents = read("wikidata-entities.csv")
KIND = {"class": ("Classes", "cls"), "version-type": ("Version types (P548 values)", "term"), "vcs": ("Version control", "term"),
        "topic": ("Topic", "term"), "forge": ("Forge", "ro"), "platform": ("chublets platform items", "ro"),
        "wikiproject": ("chublets platform items", "ro"), "collection": ("chublets platform items", "ro"),
        "person": ("People and organisations", "ro"), "organisation": ("People and organisations", "ro"),
        "software-example": ("Native Wikidata examples", "so")}
groups = {}
for e in ents:
    g, c = KIND[e["kind"]]
    groups.setdefault(g, []).append((e, c))
body = []
gi = 0
for g, es in groups.items():
    for k in range(0, len(es), 5):
        title = g if k == 0 else f"{g} (cont.)"
        body.append(f'  subgraph G{gi}["{title}"]')
        body.append("    direction LR")
        for e, c in es[k:k + 5]:
            body.append(f'    {e["qid"]}["{e["label_en"]}<br/>{e["qid"]}"]:::{c}')
        body.append("  end")
        gi += 1
diagrams["08-entities-flat"] = mm(f"All {len(ents)} entities of the model, grouped by kind (no hierarchy)", "\n".join(body), direction="TB")

CFG = {"theme": "base", "themeVariables": {"fontFamily": "Arial, Helvetica, sans-serif", "fontSize": "14px"},
       "flowchart": {"htmlLabels": False, "curve": "basis", "useMaxWidth": False}}

for name, src in diagrams.items():
    (OUT / f"{name}.mmd").write_text(src + "\n", encoding="utf-8")
print(f"wrote {len(diagrams)} .mmd")

if "--no-render" in sys.argv:
    sys.exit(0)
mmdc = shutil.which("mmdc")
chrome = next((p for p in (os.environ.get("CHROME_PATH"), "/opt/pw-browsers/chromium-1194/chrome-linux/chrome") if p and Path(p).exists()), None)
if not mmdc or not chrome:
    sys.exit("mmdc or chromium not found: sources written, rendering skipped")
tmp = ROOT / ".mmdc"
tmp.mkdir(exist_ok=True)
(tmp / "config.json").write_text(json.dumps(CFG), encoding="utf-8")
(tmp / "puppeteer.json").write_text(json.dumps({"executablePath": chrome, "args": ["--no-sandbox", "--disable-gpu"]}), encoding="utf-8")
for name in diagrams:
    for ext, extra in (("svg", []), ("png", ["-s", "2", "-b", "white"])):
        cmd = [mmdc, "-i", str(OUT / f"{name}.mmd"), "-o", str(OUT / f"{name}.{ext}"), "-c", str(tmp / "config.json"),
               "-p", str(tmp / "puppeteer.json"), "-q", *extra]
        r = subprocess.run(cmd, capture_output=True, text=True)
        print(("ok  " if r.returncode == 0 else "FAIL"), f"{name}.{ext}", (r.stderr.strip()[:200] if r.returncode else ""))
shutil.rmtree(tmp, ignore_errors=True)
