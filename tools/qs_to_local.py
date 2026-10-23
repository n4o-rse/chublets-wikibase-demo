#!/usr/bin/env python3
"""The QuickStatements examples of the Starter Pack with local ids, ready for ``python main.py apply-qs``.

    python tools/qs_to_local.py              reads starter-pack/examples/*.qs, writes starter-pack/examples-local/*.qs
    python tools/qs_to_local.py --check      write nothing; exit 1 when the files would change

The pack's files use Wikidata ids. Here every property ``Pxxx`` becomes its local id (``background/property-set.csv``, columns
``wikidata_pid`` and ``local_id``) and every item ``Qxxx`` becomes its local twin (the P4 statements in ``data/csv/statements.csv``).
Text between quotes, ``LAST``, ``CREATE``, label commands and comments stay as they are. An id without a local twin stops the script.
The files are templates: the item they describe may exist already (Alligator is Q359); ``apply-qs`` would create a second one.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "starter-pack" / "examples"
OUT = ROOT / "starter-pack" / "examples-local"
HEADER = ("# Local ids for this repository, made by tools/qs_to_local.py from starter-pack/examples/{name}.\n"
          "# A template for apply-qs: the item may exist already, then this would create a second one. Check the ids in data/csv/ first.\n")


def twins() -> tuple[dict[str, str], dict[str, str]]:
    items: dict[str, str] = {}
    with (ROOT / "data" / "csv" / "statements.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["property"] == "P4" and row["subject"].startswith("Q") and row["value"].startswith("Q"):
                items.setdefault(row["value"], row["subject"])
    with (ROOT / "background" / "property-set.csv").open(encoding="utf-8", newline="") as handle:
        props = {r["wikidata_pid"]: r["local_id"] for r in csv.DictReader(handle) if r["wikidata_pid"] and r["local_id"]}
    return items, props


def convert(text: str, items: dict[str, str], props: dict[str, str], where: str) -> str:
    out = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            out.append(line)
            continue
        fields = line.split("\t")
        for i, field in enumerate(fields):
            if re.fullmatch(r"-?[PQ]\d+", field.strip()) is None:
                continue
            minus = "-" if field.startswith("-") else ""
            token = field.lstrip("-")
            table = props if token.startswith("P") else items
            if token not in table:
                raise SystemExit(f"{where}:{number}: {token} has no local id")
            fields[i] = minus + table[token]
        out.append("\t".join(fields))
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    items, props = twins()
    changed = 0
    for source in sorted(PACK.glob("*.qs")):
        text = HEADER.format(name=source.name) + convert(source.read_text(encoding="utf-8"), items, props, source.name)
        target = OUT / source.name
        if target.is_file() and target.read_text(encoding="utf-8") == text:
            continue
        changed += 1
        if not args.check:
            OUT.mkdir(parents=True, exist_ok=True)
            with target.open("w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
    print(f"[qs_to_local] {changed} file(s) {'would change' if args.check else 'written'}")
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
