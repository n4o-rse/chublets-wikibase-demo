#!/usr/bin/env python3
"""The numbers the paper states about this repository, counted from the tables and from the built files.

    python tools/paper_numbers.py            a Markdown table
    python tools/paper_numbers.py --json     the same as JSON
    python tools/paper_numbers.py --no-rdf   skip the check on the Turtle file in dist/ (it needs rdflib and takes a few seconds)

Reads, never writes. Run it after ``python main.py`` so that ``data/derived/``, ``docs/`` and ``dist/`` match ``data/csv/``.

Definitions (they reproduce the figures the paper gave on 2026-11-02, before the data care of the second round):

* chublets: items with ``P2 -> Q106``, a merged item (``merges.csv``, ``from``) counted once, as a redirect of its target.
* tools per topic: chublets with ``P117 ->`` the topic (Q116 Statistical analysis, Q126 Chronological modelling); "with repository" adds ``P125``
  (source code repository URL). The statements of a merged item count for its target.
* with licence: chublets with ``P107`` (copyright license).
* entries of the static copy: the files of ``data/derived/entities/`` (items, classes and properties, kernel included, merged items are no entity).
* items of those: ``kind = item`` in ``entities.csv`` minus the merged ones.
* rows of ``statements.csv`` without the header line.
* statements of Alligator (Q359): the claims in ``docs/json/Q359.json``, i.e. after the merge.
* the same chublet count asked of the Turtle file with SPARQL (the check query of the data care, rdflib): it must equal the first.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "csv"
BASE = "https://n4o-rse.github.io/chublets-wikibase-demo"
CHUBLET, INSTANCE_OF, MAIN_SUBJECT, REPOSITORY, LICENCE = "Q106", "P2", "P117", "P125", "P107"
TOPICS = {"Q116": "Statistical analysis", "Q126": "Chronological modelling"}
ALLIGATOR = "Q359"


def table(name: str) -> list[dict[str, str]]:
    with (CSV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def count_tables() -> dict[str, object]:
    statements, entities, merges = table("statements.csv"), table("entities.csv"), table("merges.csv")
    redirect = {m["from"]: m["to"] for m in merges}
    where = lambda i: redirect.get(i, i)                                    # noqa: E731
    chublets = {where(s["subject"]) for s in statements if s["property"] == INSTANCE_OF and s["value"] == CHUBLET}
    with_repository = {where(s["subject"]) for s in statements if s["property"] == REPOSITORY}
    out: dict[str, object] = {
        "chublets": len(chublets),
        "chublets_with_licence": len({where(s["subject"]) for s in statements if s["property"] == LICENCE} & chublets),
    }
    for topic in TOPICS:
        tools = {where(s["subject"]) for s in statements if s["property"] == MAIN_SUBJECT and s["value"] == topic} & chublets
        out[f"{topic}_tools"] = len(tools)
        out[f"{topic}_tools_with_repository"] = len(tools & with_repository)
    out["entries_static_copy"] = len(list((ROOT / "data" / "derived" / "entities").glob("*.json")))
    out["items_static_copy"] = sum(1 for r in entities if r["kind"] == "item" and r["id"] not in redirect)
    out["statements_csv_rows"] = len(statements)
    claims = ROOT / "docs" / "json" / f"{ALLIGATOR}.json"
    if claims.exists():
        data = json.loads(claims.read_text(encoding="utf-8"))
        entity = next(iter(data["entities"].values())) if "entities" in data else data
        out["alligator_statements"] = sum(len(v) for v in entity.get("claims", {}).values())
    return out


def count_rdf() -> dict[str, object]:
    try:
        import rdflib
    except ImportError:
        return {"rdf": "rdflib is not installed"}
    files = sorted((ROOT / "dist").glob("*.ttl"))
    if not files:
        return {"rdf": "no Turtle file in dist/, run python main.py first"}
    graph = rdflib.Graph()
    graph.parse(files[0], format="turtle")
    prefixes = f"PREFIX chb: <{BASE}/entity/>\nPREFIX chbt: <{BASE}/prop/direct/>\n"
    query = prefixes + "SELECT (COUNT(DISTINCT ?tool) AS ?n) WHERE { ?tool chbt:P2 chb:Q106 . }"
    return {"chublets_rdf": int(next(iter(graph.query(query)))[0]), "rdf_file": files[0].name}


LABELS = {
    "chublets": "chublets in total",
    "chublets_with_licence": "chublets with a licence",
    "Q116_tools": "tools, Statistical analysis (Q116)",
    "Q116_tools_with_repository": "  of them with a repository",
    "Q126_tools": "tools, Chronological modelling (Q126)",
    "Q126_tools_with_repository": "  of them with a repository",
    "entries_static_copy": "entries of the static copy",
    "items_static_copy": "  of them items",
    "statements_csv_rows": "rows of statements.csv (without header)",
    "alligator_statements": "statements of Alligator (Q359), after the merge",
    "chublets_rdf": "chublets, SPARQL on the Turtle file",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--json", action="store_true", help="print JSON instead of a Markdown table")
    parser.add_argument("--no-rdf", action="store_true", help="do not ask the Turtle file (no rdflib needed)")
    args = parser.parse_args(argv)
    numbers = count_tables()
    if not args.no_rdf:
        numbers.update(count_rdf())
    problems = []
    if "chublets_rdf" in numbers and numbers["chublets_rdf"] != numbers["chublets"]:
        problems.append(f"the Turtle file says {numbers['chublets_rdf']} chublets, the tables {numbers['chublets']}: run python main.py again")
    if args.json:
        print(json.dumps(numbers, indent=2, ensure_ascii=False))
    else:
        print("| What | Value |\n|---|---|")
        for key, value in numbers.items():
            if key in LABELS:
                print(f"| {LABELS[key]} | {value} |")
            elif key == "rdf":
                print(f"| Turtle file | {value} |")
    for problem in problems:
        print(f"WARN: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
