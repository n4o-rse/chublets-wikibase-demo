#!/usr/bin/env python3
"""One-off import of the chublets.software Wikibase Starter Pack into data/csv/ (PRIMER.md of wikibase-static, S7b).

    python tools/import_pack.py PACK_DIR
    python tools/import_pack.py PACK_DIR --check        write nothing; exit 1 when the files would change

PACK_DIR is the unzipped ``chublets-wikibase-starter-pack``. The script reads

    data/wikibase-property-set.csv     one row per property (153): label, datatype, Wikidata twin, CodeMeta terms
    data/wikidata-entities.csv         the Wikidata classes the model needs (labels and Q-ids)
    data/sources.csv, docs/05-open-points.md      copied to background/ as they are

and writes

    data/csv/entities.csv, statements.csv, references.csv, qualifiers.csv     the model, canonical form
    data/csv/idmap.csv                 source, key, id: which pack row became which local id (versioned, never reused)
    background/property-set.csv        the pack's rows with their local id and what became of them
    background/classes.csv             the same for the classes
    background/sources.csv, background/starter-pack-open-points.md

What becomes what
-----------------
* Every property row becomes a local property P100, P101, ... (the kernel owns P1 to P99), with the datatype of the
  pack, except the rows that already are kernel properties: "equivalent Wikidata property" is P4, "instance of" is P2,
  "subclass of" is P1 and "retrieved" is P7. Those get no new number; ``background/property-set.csv`` says so.
* ``wikidata_pid`` becomes a statement ``P4`` ("Wikidata equivalent") with a reference (``P6`` reference URL: the page
  of the twin on Wikidata). More than one twin is possible (the property can repeat), the pack has at most one.
* ``codemeta_terms`` (separated by ``;``) become one "equivalent CodeMeta term" statement each, and the Wikidata
  properties named in ``candidate_wikidata_pids`` become "close match Wikidata property" statements.
* The classes of the pack's class tree (diagrams/06-class-hierarchy.mmd) become local classes Q100 to Q106 with the
  Wikidata class as their twin; the tree ends in the kernel's root Q3.
* Nothing is looked up on Wikidata. The pack says what it verified (``confidence``); that column stays in
  ``background/``. A reference on a twin therefore says "documented at this page", not "retrieved on".

Every row written here carries ``origin = starter-pack``. The ids are the next free number from 100 (PRIMER.md, A4
"IDs der Importer"); a second run reads ``idmap.csv`` first and writes the same files.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

from wikibase_static import csvbuild, csvio
from wikibase_static.model import id_sort_key

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = "starter-pack"
SOURCE = "starter-pack"

# The kernel properties that the pack lists as properties of its own (label in the pack -> kernel id).
KERNEL_ALIASES = {
    "equivalent Wikidata property": "P4",
    "instance of": "P2",
    "subclass of": "P1",
    "retrieved": "P7",
}
# Properties that carry the twin and the metadata (labels in the pack).
LABEL_CODEMETA = "equivalent CodeMeta term"
LABEL_SCHEMA = "equivalent schema.org term"
LABEL_CLOSE = "close match Wikidata property"

# Formatter URLs ($1 is replaced by the value) of the metadata properties. The CodeMeta one is in the note of the pack
# row; the other two are standard addresses.
FORMATTERS = {
    LABEL_CODEMETA: "https://codemeta.github.io/terms/$1",
    LABEL_SCHEMA: "https://schema.org/$1",
    LABEL_CLOSE: "https://www.wikidata.org/entity/$1",
}

# The class tree: (Wikidata id, [Wikidata ids of the superclasses]); an empty list means "directly below Q3".
# Source: diagrams/06-class-hierarchy.mmd of the pack. "chublet subclass of Little Minion" is the one evidenced edge;
# the others are the pack's expectations from Wikidata (unverified). application software is below software here,
# not below "computer program" as in the diagram, so that the model needs one class less.
CLASSES = [
    ("Q7397", []),                               # software
    ("Q95001953", ["Q7397"]),                    # research software
    ("Q166142", ["Q7397"]),                      # application software
    ("Q188860", ["Q7397"]),                      # software library
    ("Q1070421", ["Q7397"]),                     # script file
    ("Q73899440", []),                           # Little Minion (label disputed, pack open point 5)
    ("Q141115627", ["Q73899440", "Q95001953"]),  # chublet
]

PID = re.compile(r"^P[1-9][0-9]*$")
QID = re.compile(r"^Q[1-9][0-9]*$")
FIRST_FREE = 100


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


class IdMap:
    """``data/csv/idmap.csv``: (source, key) -> id. Ids are never reused, even for a key that is gone."""

    COLUMNS = ["source", "key", "id"]

    def __init__(self, path: Path) -> None:
        self.path = path
        self.ids: dict[tuple[str, str], str] = {}
        if path.is_file():
            for row in read_csv(path):
                self.ids[(row["source"], row["key"])] = row["id"]

    def get(self, key: str, kind: str) -> str:
        """The id of ``key`` (``kind`` is "P" or "Q"); a new key gets the next number after the highest one ever given."""
        found = self.ids.get((SOURCE, key))
        if found:
            return found
        used = [int(i[1:]) for i in self.ids.values() if i[0] == kind]
        new = f"{kind}{max([FIRST_FREE - 1] + used) + 1}"
        self.ids[(SOURCE, key)] = new
        return new

    def fix(self, key: str, entity_id: str) -> str:
        """A key that is bound to an id by the kernel."""
        previous = self.ids.setdefault((SOURCE, key), entity_id)
        if previous != entity_id:
            raise SystemExit(f"idmap.csv binds {key!r} to {previous}, but the kernel says {entity_id}")
        return entity_id

    def text(self) -> str:
        rows = [{"source": s, "key": k, "id": i} for (s, k), i in self.ids.items()]
        rows.sort(key=lambda r: (r["source"], id_sort_key(r["id"])))
        return csvio.render_table(self.COLUMNS, rows)


def split(text: str) -> list[str]:
    return [part.strip() for part in text.split(";") if part.strip()]


Rows = list[dict[str, str]]


def build(pack: Path, csv_dir: Path) -> tuple[dict[str, Rows], Rows, Rows, Rows, IdMap]:
    """(background rows, entity rows, statement rows, reference rows, idmap)"""
    properties = read_csv(pack / "data" / "wikibase-property-set.csv")
    entities = {row["qid"]: row for row in read_csv(pack / "data" / "wikidata-entities.csv")}
    idmap = IdMap(csv_dir / "idmap.csv")

    labels = [row["wb_label"] for row in properties]
    if len(set(labels)) != len(labels):
        raise SystemExit("the pack lists a label twice; the label is the key of idmap.csv")
    for label, kernel_id in KERNEL_ALIASES.items():
        if label not in labels:
            raise SystemExit(f"the pack has no row {label!r}; the mapping to {kernel_id} needs it")
    for label in (LABEL_CODEMETA, LABEL_CLOSE):
        if label not in labels:
            raise SystemExit(f"the pack has no row {label!r}")

    for row in properties:
        if row["wb_label"] in KERNEL_ALIASES:
            _kind, kernel_type = csvbuild.KERNEL[KERNEL_ALIASES[row["wb_label"]]]
            if (row["datatype"] or None) != kernel_type:
                raise SystemExit(f"{row['wb_label']}: the pack says {row['datatype']}, the kernel {kernel_type}")

    # ---- ids: the kernel ones are fixed, the rest in the order phase, label (only for keys not yet in idmap.csv)
    local: dict[str, str] = {}
    for row in sorted(properties, key=lambda r: (int(r["phase"]), r["wb_label"].lower(), r["wb_label"])):
        label = row["wb_label"]
        key = f"property:{label}"
        local[label] = idmap.fix(key, KERNEL_ALIASES[label]) if label in KERNEL_ALIASES else idmap.get(key, "P")
    class_ids: dict[str, str] = {}
    for qid, _parents in CLASSES:
        if qid not in entities:
            raise SystemExit(f"{qid} is not in wikidata-entities.csv")
        class_ids[qid] = idmap.get(f"class:{qid}", "Q")

    entity_rows: list[dict[str, str]] = []
    statements: list[dict[str, str]] = []
    references: list[dict[str, str]] = []

    def twin(subject: str, value: str, page: str) -> None:
        sid = f"{subject}-P4-{value}"
        statements.append({"sid": sid, "subject": subject, "property": "P4", "value": value, "rank": "", "origin": ORIGIN})
        references.append({"sid": sid, "group": "1", "property": "P6", "value": page})

    for row in properties:
        label = row["wb_label"]
        pid = local[label]
        if label in KERNEL_ALIASES:
            continue                                    # a kernel property: nothing is written for it
        entity_rows.append({"id": pid, "kind": "property", "datatype": row["datatype"], "origin": ORIGIN, "label_en": label})
        if row["wikidata_pid"]:
            if not PID.match(row["wikidata_pid"]):
                raise SystemExit(f"{label}: {row['wikidata_pid']!r} is not a property id")
            twin(pid, row["wikidata_pid"], f"https://www.wikidata.org/wiki/Property:{row['wikidata_pid']}")
        for term in split(row["codemeta_terms"]):
            statements.append({"sid": "", "subject": pid, "property": local[LABEL_CODEMETA], "value": term, "rank": "", "origin": ORIGIN})
        if row["candidate_wikidata_pids"]:
            if row["wikidata_pid"]:
                raise SystemExit(f"{label}: has a twin and candidates; the pack says candidates only for rows without a twin")
            for candidate in split(row["candidate_wikidata_pids"].replace(",", ";")):
                if PID.match(candidate):               # the pack mixes in prose such as "(native Wikibase description field)"
                    statements.append({"sid": "", "subject": pid, "property": local[LABEL_CLOSE], "value": candidate, "rank": "", "origin": ORIGIN})
        if label in FORMATTERS:
            statements.append({"sid": "", "subject": pid, "property": "P5", "value": FORMATTERS[label], "rank": "", "origin": ORIGIN})

    for qid, parents in CLASSES:
        cid = class_ids[qid]
        entity_rows.append({"id": cid, "kind": "class", "datatype": "", "origin": ORIGIN, "label_en": entities[qid]["label_en"]})
        for parent in parents or ["Q3"]:
            statements.append({"sid": "", "subject": cid, "property": "P1", "value": class_ids.get(parent, parent), "rank": "", "origin": ORIGIN})
        twin(cid, qid, f"https://www.wikidata.org/wiki/{qid}")

    background = {
        "properties": [dict(row, local_id=local[row["wb_label"]],
                            kernel="yes" if row["wb_label"] in KERNEL_ALIASES else "")
                       for row in sorted(properties, key=lambda r: id_sort_key(local[r["wb_label"]]))],
        "classes": [dict(entities[qid], local_id=class_ids[qid]) for qid, _p in CLASSES],
    }
    return background, entity_rows, statements, references, idmap


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import the Starter Pack into data/csv/ (one-off).")
    parser.add_argument("pack", type=Path, help="the unzipped chublets-wikibase-starter-pack")
    parser.add_argument("--csv", type=Path, default=ROOT / "data" / "csv")
    parser.add_argument("--background", type=Path, default=ROOT / "background")
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a file would change")
    args = parser.parse_args(argv)

    if not (args.pack / "data" / "wikibase-property-set.csv").is_file():
        print(f"{args.pack} is not the Starter Pack (data/wikibase-property-set.csv is missing)", file=sys.stderr)
        return 2
    background, entity_rows, statements, references, idmap = build(args.pack, args.csv)

    def table(name: str, columns: list[str], rows: list[dict[str, str]]) -> csvio.Table:
        return csvio.Table(name=name, columns=columns, rows=rows, lines=list(range(2, len(rows) + 2)))

    tables = {
        "entities.csv": table("entities.csv", csvio.ENTITY_COLUMNS + ["label_en"], entity_rows),
        "statements.csv": table("statements.csv", csvio.STATEMENT_COLUMNS, statements),
        "references.csv": table("references.csv", csvio.REFERENCE_COLUMNS, references),
        "qualifiers.csv": table("qualifiers.csv", csvio.QUALIFIER_COLUMNS, []),
    }
    texts = csvio.canonical_texts(tables)
    texts["idmap.csv"] = idmap.text()
    out: dict[Path, str] = {args.csv / name: text for name, text in texts.items()}

    property_columns = ["local_id", "kernel"] + [c for c in read_csv(args.pack / "data" / "wikibase-property-set.csv")[0].keys()]
    out[args.background / "property-set.csv"] = csvio.render_table(property_columns, background["properties"])
    class_columns = ["local_id"] + list(read_csv(args.pack / "data" / "wikidata-entities.csv")[0].keys())
    out[args.background / "classes.csv"] = csvio.render_table(class_columns, background["classes"])
    out[args.background / "sources.csv"] = (args.pack / "data" / "sources.csv").read_text(encoding="utf-8").replace("\r\n", "\n")
    out[args.background / "starter-pack-open-points.md"] = (args.pack / "docs" / "05-open-points.md").read_text(encoding="utf-8").replace("\r\n", "\n")

    changed = [path for path, text in out.items() if not path.is_file() or path.read_bytes() != text.encode("utf-8")]
    if args.check:
        for path in changed:
            print(f"{path.relative_to(ROOT).as_posix()} would change")
        return 1 if changed else 0
    for path, text in out.items():
        if path in changed:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(text.encode("utf-8"))
    new = sum(1 for r in entity_rows if r["kind"] == "property")
    print(f"[import-pack] {new} properties (P{FIRST_FREE}...) and {len(CLASSES)} classes; {len(statements)} statements, "
          f"{len(references)} reference rows; {len(KERNEL_ALIASES)} pack rows are kernel properties; "
          f"{len(changed)} of {len(out)} file(s) written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
