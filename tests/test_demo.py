"""Tests of the model in this repository (S7b).

    python -m unittest discover -s tests

They read the committed tables (`data/csv/`), the Wikibase JSON made from them (`data/derived/`, after
`python main.py`) and the RDF file in `dist/`. The pack itself is not needed: `background/property-set.csv` is its
property table with the local ids added.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import wikibase_static  # noqa: E402
from wikibase_static import csvbuild, csvio, loader, rdf  # noqa: E402

CSV = ROOT / "data" / "csv"
RDFS, OWL, RDF = rdf.RDFS, rdf.OWL, rdf.RDF
BASE = "https://n4o-rse.github.io/chublets-wikibase-demo"
BRIDGE = {
    (BASE + "/prop/direct/P1", RDFS + "subPropertyOf", RDFS + "subClassOf"),
    (BASE + "/prop/direct/P2", RDFS + "subPropertyOf", RDF + "type"),
    (BASE + "/prop/direct/P3", RDFS + "subPropertyOf", RDFS + "subPropertyOf"),
    (BASE + "/entity/Q1", OWL + "equivalentClass", RDFS + "Class"),
    (BASE + "/entity/Q2", OWL + "equivalentClass", RDF + "Property"),
    (BASE + "/entity/Q3", OWL + "equivalentClass", OWL + "Thing"),
}


def table(name: str) -> list[dict[str, str]]:
    with (CSV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def background() -> list[dict[str, str]]:
    with (ROOT / "background" / "property-set.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def version() -> tuple[int, ...]:
    return tuple(int(part) for part in wikibase_static.__version__.split("."))


class Package(unittest.TestCase):
    def test_the_installed_package_is_new_enough(self) -> None:
        self.assertGreaterEqual(version(), (0, 6, 0), "pip install --upgrade --force-reinstall --no-deps -r requirements.txt")


class Pack(unittest.TestCase):
    """Every row of the Starter Pack is accounted for."""

    def test_the_pack_has_153_property_rows_and_each_has_an_id(self) -> None:
        rows = background()
        self.assertEqual(len(rows), 153)
        self.assertTrue(all(re.fullmatch(r"P[1-9][0-9]*", r["local_id"]) for r in rows))
        self.assertEqual(len({r["local_id"] for r in rows}), 153)

    def test_four_rows_are_kernel_properties_and_the_rest_are_in_entities_csv(self) -> None:
        rows = background()
        kernel = {r["wb_label"]: r["local_id"] for r in rows if r["kernel"]}
        self.assertEqual(kernel, {"equivalent Wikidata property": "P4", "instance of": "P2", "subclass of": "P1", "retrieved": "P7"})
        entities = {r["id"]: r for r in table("entities.csv")}
        for row in rows:
            if row["kernel"]:
                self.assertNotIn(row["local_id"], entities, row["wb_label"])
                continue
            entity = entities[row["local_id"]]
            self.assertEqual((entity["kind"], entity["datatype"], entity["label_en"]), ("property", row["datatype"], row["wb_label"]))

    def test_the_numbers_from_100_are_the_next_free_ones_and_in_idmap(self) -> None:
        mapped = {r["key"]: r["id"] for r in table("idmap.csv")}
        ids = sorted((int(i[1:]) for i in mapped.values() if i[0] == "P" and int(i[1:]) >= 100))
        self.assertEqual(ids, list(range(100, 100 + len(ids))))
        self.assertEqual(len(ids), 149)
        for row in background():
            self.assertEqual(mapped[f"property:{row['wb_label']}"], row["local_id"])

    def test_every_twin_is_a_p4_statement_with_a_reference_to_its_wikidata_page(self) -> None:
        statements = table("statements.csv")
        references = {r["sid"]: r for r in table("references.csv")}
        twins = {(s["subject"], s["value"]): s for s in statements if s["property"] == "P4"}
        for row in background():
            if row["wikidata_pid"] and not row["kernel"]:
                statement = twins[(row["local_id"], row["wikidata_pid"])]
                self.assertEqual(references[statement["sid"]]["value"], f"https://www.wikidata.org/wiki/Property:{row['wikidata_pid']}")
        self.assertEqual(sum(1 for r in background() if r["wikidata_pid"] and not r["kernel"]), 98)
        self.assertEqual(len([s for s in statements if s["property"] == "P4" and s["subject"].startswith("P")]), 98)

    def test_the_codemeta_terms_and_the_close_matches_are_statements(self) -> None:
        by_label = {r["wb_label"]: r["local_id"] for r in background()}
        codemeta, close = by_label["equivalent CodeMeta term"], by_label["close match Wikidata property"]
        statements = table("statements.csv")
        have_terms = {(s["subject"], s["value"]) for s in statements if s["property"] == codemeta}
        have_close = {(s["subject"], s["value"]) for s in statements if s["property"] == close}
        for row in background():
            if row["kernel"] and not row["codemeta_terms"]:
                continue
            for term in [t.strip() for t in row["codemeta_terms"].split(";") if t.strip()]:
                if not row["kernel"]:
                    self.assertIn((row["local_id"], term), have_terms, row["wb_label"])
            for candidate in re.findall(r"\bP[1-9][0-9]*\b", row["candidate_wikidata_pids"]):
                self.assertIn((row["local_id"], candidate), have_close, row["wb_label"])

    def test_the_class_tree_ends_in_the_root(self) -> None:
        parents: dict[str, list[str]] = {}
        for s in table("statements.csv"):
            if s["property"] == "P1":
                parents.setdefault(s["subject"], []).append(s["value"])
        classes = [r["id"] for r in table("entities.csv") if r["kind"] == "class"]
        self.assertEqual(len(classes), 7)
        for class_id in classes:
            seen, todo = set(), [class_id]
            while todo:
                current = todo.pop()
                if current not in seen:
                    seen.add(current)
                    todo.extend(parents.get(current, []))
            self.assertIn("Q3", seen, class_id)
        self.assertEqual(sorted(parents["Q106"]), ["Q101", "Q105"])         # chublet: research software and Little Minion

    def test_the_tables_are_in_canonical_form(self) -> None:
        problems: list[str] = []
        tables = {name: csvio.read_table(CSV / name, csvio.REQUIRED[name], problems, name) for name in csvio.TABLES}
        self.assertEqual(problems, [])
        for name, text in csvio.canonical_texts(tables).items():
            self.assertEqual((CSV / name).read_text(encoding="utf-8"), text, f"{name}: run python main.py csv-fmt")


class Site(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = loader.load_site(ROOT / "data" / "raw", ROOT / "data" / "derived")

    def test_it_loads_without_a_problem_and_has_the_kernel(self) -> None:
        self.assertEqual(self.site.problems, [])
        self.assertTrue(self.site.has_kernel())
        for entity_id in list(csvbuild.KERNEL):
            self.assertIn(entity_id, self.site.entities)

    def test_it_holds_exactly_the_model(self) -> None:
        self.assertEqual(len(self.site.entities), 3 + 10 + 149 + 7)
        self.assertEqual(len(self.site.properties), 10 + 149)

    def test_the_derived_json_is_what_from_csv_makes_of_the_tables(self) -> None:
        problems: list[str] = []
        built = csvbuild.build(csvbuild.read_set(CSV, problems, "csv"), csvbuild.kernel_set(), BASE)
        self.assertEqual(sorted(set(problems) | set(built.problems)), [])
        for entity_id, obj in built.entities.items():
            on_disk = json.loads((ROOT / "data" / "derived" / "entities" / f"{entity_id}.json").read_text(encoding="utf-8"))
            self.assertEqual(on_disk, json.loads(json.dumps(obj)), entity_id)


class Export(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.site = loader.load_site(ROOT / "data" / "raw", ROOT / "data" / "derived")
        cls.result = rdf.build(cls.site, rdf.Namespaces(BASE))

    def test_the_export_carries_the_bridge(self) -> None:
        triples = {(s.value, p.value, o.value) for s, p, o in self.result.triples if all(isinstance(x, rdf.Iri) for x in (s, p, o))}
        self.assertTrue(BRIDGE <= triples)

    def test_the_published_file_has_the_bridge_in_a_section_of_its_own(self) -> None:
        files = sorted((ROOT / "dist").glob("*.ttl"))
        self.assertEqual(len(files), 1, "run python main.py first")
        text = files[0].read_text(encoding="utf-8")
        self.assertIn("# RDFS bridge of the kernel", text)
        import rdflib
        graph = rdflib.Graph()
        graph.parse(data=text, format="turtle")
        for s, p, o in BRIDGE:
            self.assertIn((rdflib.URIRef(s), rdflib.URIRef(p), rdflib.URIRef(o)), graph)

    def test_without_the_kernel_there_is_no_bridge(self) -> None:
        stripped = loader.Site(entities={k: v for k, v in self.site.entities.items() if k != "Q1"})
        self.assertFalse(stripped.has_kernel())
        self.assertEqual(rdf.build(stripped, rdf.Namespaces(BASE)).bridge, set())


if __name__ == "__main__":
    unittest.main()
