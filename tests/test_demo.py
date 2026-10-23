"""Tests of the model in this repository (S7b).

    python -m unittest discover -s tests

They read the committed tables (`data/csv/`), the Wikibase JSON made from them (`data/derived/`, after
`python main.py`) and the RDF file in `dist/`. The pack itself is not needed: `background/property-set.csv` is its
property table with the local ids added.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import re
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import wikibase_static  # noqa: E402
from wikibase_static import csvbuild, csvio, loader, rdf, step_import_open_archaeo as importer, step_import_wikidata as wikidata  # noqa: E402

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


def quietly(step, args: list[str]) -> int:
    """Run an importer's ``main`` without its report on the terminal (the test looks at the files, not at the text)."""
    with contextlib.redirect_stdout(io.StringIO()):
        return step.main(args)


def table(name: str) -> list[dict[str, str]]:
    with (CSV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def table_at(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def background() -> list[dict[str, str]]:
    with (ROOT / "background" / "property-set.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def version() -> tuple[int, ...]:
    return tuple(int(part) for part in wikibase_static.__version__.split("."))


class Package(unittest.TestCase):
    def test_the_installed_package_is_new_enough(self) -> None:
        self.assertGreaterEqual(version(), (0, 15, 0), "pip install --upgrade --force-reinstall --no-deps -r requirements.txt")


# The tables are hand-maintained since the review of 2026-10-22; these are the places where they differ from the pack snapshot
# in background/ (labels as Wikidata has them, verification-report.csv; datatypes from the same report and from the review).
LIVE_LABELS = {"distribution package ID P3112 (label to be filled)": "DistroWatch ID",
               "distribution package ID P3418 (label to be filled)": "Google Play Store app ID",
               "distribution package ID P3442 (label to be filled)": "Debian stable package",
               "distribution package ID P3454 (label to be filled)": "Arch Linux package",
               "distribution package ID P3463 (label to be filled)": "Fedora package",
               "distribution package ID P3473 (label to be filled)": "Ubuntu package",
               "distribution package ID P3499 (label to be filled)": "Gentoo package",
               "distribution package ID P3597 (label to be filled)": "F-Droid package",
               "edition or translation of": "version, edition or translation of", "GitHub username": "GitHub account",
               "download link": "download URL", "SoftWare Hash IDentifier (SWHID)": "SoftWare Hash IDentifier"}
CHANGED_DATATYPES = {"equivalent CodeMeta term": "external-id", "equivalent schema.org term": "external-id", "port": "quantity"}
NEW_PROPERTIES = {"digital rights management system": ("P1032", "wikibase-item"), "ISO standard": ("P503", "external-id"),
                  "language of work or name": ("P407", "wikibase-item"), "movement": ("P135", "wikibase-item"),
                  "removed feature": ("P756", "wikibase-item"), "RfC ID": ("P892", "external-id"),
                  "Stack Exchange tag": ("P1482", "url"), "TeX string": ("P1993", "string"), "Unicode character": ("P487", "string")}


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
            expected = (CHANGED_DATATYPES.get(row["wb_label"], row["datatype"]), LIVE_LABELS.get(row["wb_label"], row["wb_label"]))
            self.assertEqual((entity["kind"], entity["datatype"], entity["label_en"]), ("property", *expected))

    def test_the_numbers_from_100_are_the_next_free_ones_and_in_idmap(self) -> None:
        mapped = {r["key"]: r["id"] for r in table("idmap.csv")}
        ids = sorted((int(i[1:]) for i in mapped.values() if i[0] == "P" and int(i[1:]) >= 100))
        self.assertEqual(ids, list(range(100, 100 + len(ids))))
        self.assertEqual(len(ids), 149 + len(NEW_PROPERTIES))
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
        # plus one hand row (2026-10-23, S7d): "creator" (P171) is also the twin of Wikidata P50 (author), see TestWikidata
        self.assertEqual(len([s for s in statements if s["property"] == "P4" and s["subject"].startswith("P")]), 98 + len(NEW_PROPERTIES) + 1)

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
        self.assertEqual(sum(1 for r in table("entities.csv") if r["kind"] == "class" and r["origin"] == "starter-pack"), 7)
        self.assertEqual(len(classes), 7 + 3)                       # plus the three class stubs of the Wikidata import (S7d)
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

    def test_it_holds_the_model_and_what_the_importer_added(self) -> None:
        imported = sum(1 for r in table("entities.csv") if r["origin"] in ("open-archaeo", "wikidata", "wikidata-stub"))
        merged = len(table_at(CSV / "merges.csv"))              # a merged item is a redirect, no entity
        self.assertEqual(len(self.site.entities), 3 + 10 + 149 + len(NEW_PROPERTIES) + 7 + imported - merged)
        self.assertEqual(len(self.site.properties), 10 + 149 + len(NEW_PROPERTIES))

    def test_the_kernel_properties_carry_their_wikidata_twins(self) -> None:
        twins = {"P1": "P279", "P2": "P31", "P3": "P1647", "P5": "P1630", "P6": "P854", "P7": "P813", "P8": "P248"}
        for entity_id, wikidata in twins.items():
            raw = json.loads((ROOT / "data" / "derived" / "entities" / f"{entity_id}.json").read_text(encoding="utf-8"))
            values = [c["mainsnak"]["datavalue"]["value"] for c in raw["claims"].get("P4", [])]
            self.assertEqual(values, [wikidata], entity_id)

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


class Review(unittest.TestCase):
    """The decisions of 2026-10-22: domain and range, schema.org terms, live labels, nine properties of the WikiProject page."""

    def setUp(self) -> None:
        self.entities = {r["id"]: r for r in table("entities.csv")}
        self.statements = table("statements.csv")

    def values(self, prop: str) -> dict[str, list[str]]:
        found: dict[str, list[str]] = {}
        for s in self.statements:
            if s["property"] == prop:
                found.setdefault(s["subject"], []).append(s["value"])
        return found

    def test_every_item_property_has_the_range_instance_and_no_other_property_has_a_range(self) -> None:
        ranges = self.values("P10")
        for entity_id, row in self.entities.items():
            if row["kind"] == "property" and row["datatype"] == "wikibase-item":
                self.assertEqual(ranges.get(entity_id), ["Q3"], entity_id)
            elif row["kind"] == "property":
                self.assertNotIn(entity_id, ranges, f"{entity_id} ({row['datatype']}) has no entity values, so no range")

    def test_the_domain_is_software_or_property_and_the_person_only_properties_have_none(self) -> None:
        domains = self.values("P9")
        self.assertEqual({v for vs in domains.values() for v in vs}, {"Q100", "Q2"})
        self.assertEqual(sorted(i for i, v in domains.items() if v == ["Q2"]), ["P100", "P101", "P102"])
        by_label = {r["label_en"]: r["id"] for r in self.entities.values()}
        for label in ("family name", "given name", "affiliation", "editor", "email address", "notable work"):
            self.assertNotIn(by_label[label], domains, label)

    def test_the_schema_org_terms_are_bare_names_and_the_eight_unsuitable_ones_are_left_out(self) -> None:
        terms = self.values("P102")
        self.assertEqual(sum(len(v) for v in terms.values()), 71)
        for entity_id, values in terms.items():
            for value in values:
                self.assertRegex(value, r"^[a-z][A-Za-z]+$", f"{entity_id}: a bare property name, formatter https://schema.org/$1")
        label = {r["id"]: r["label_en"] for r in self.entities.values()}
        for term in ("availableOnDevice", "countriesNotSupported"):
            self.assertIn(term, [v for vs in terms.values() for v in vs], term)
        for term in ("device", "source", "status", "code", "documentation", "legislationDate", "HowTo"):
            self.assertNotIn(term, [v for vs in terms.values() for v in vs], term)
        self.assertEqual(terms["P194"], ["encodingFormat"], label["P194"])

    def test_the_nine_properties_of_the_wikiproject_page_have_their_twins(self) -> None:
        twins = self.values("P4")
        by_label = {r["label_en"]: r for r in self.entities.values()}
        for label, (pid, datatype) in NEW_PROPERTIES.items():
            row = by_label[label]
            self.assertEqual((row["kind"], row["datatype"]), ("property", datatype), label)
            self.assertEqual(twins[row["id"]], [pid], label)
        self.assertEqual(sorted(by_label[l]["id"] for l in NEW_PROPERTIES), [f"P{n}" for n in range(249, 258)])

    def test_port_is_a_quantity_and_has_no_range(self) -> None:
        port = next(r for r in self.entities.values() if r["label_en"] == "port")
        self.assertEqual(port["datatype"], "quantity")
        self.assertNotIn(port["id"], self.values("P10"))

    def test_the_verification_report_has_no_failure_and_every_difference_is_resolved(self) -> None:
        with (ROOT / "background" / "verification-report.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([r["id"] for r in rows if r["verdict"] == "FAIL"], [])
        self.assertEqual(sum(1 for r in rows if r["verdict"] == "DIFF"), 14)
        labels = {r["label_en"] for r in self.entities.values()}
        for live in LIVE_LABELS.values():
            self.assertIn(live, labels)


class Attribution(unittest.TestCase):
    """The CC-BY crosswalk the mapping builds on is credited with its DOI (2026-10-21)."""

    DOI = "https://doi.org/10.5281/zenodo.21935688"

    def test_the_source_table_names_the_crosswalk_with_its_doi(self) -> None:
        with (ROOT / "background" / "sources.csv").open(encoding="utf-8", newline="") as handle:
            rows = {r["code"]: r for r in csv.DictReader(handle)}
        self.assertIn("S9", rows)
        self.assertIn(self.DOI, rows["S9"]["origin"])

    def test_the_readme_credits_it_and_the_licence_section_no_longer_asks(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## Attribution", text)
        self.assertIn(self.DOI, text)
        self.assertNotIn("**Open:** whether the CodeMeta crosswalk", text)

    def test_every_source_code_used_in_the_property_set_is_defined(self) -> None:
        with (ROOT / "background" / "sources.csv").open(encoding="utf-8", newline="") as handle:
            codes = {r["code"] for r in csv.DictReader(handle)}
        used = {c for row in background() for c in row["provenance"].split(";") if c}
        self.assertLessEqual(used, codes)



class OpenArchaeo(unittest.TestCase):
    """S7c: the 416 software entries of open-archaeo, imported into the tables (identity block V2); since 2026-10-23 all of them."""

    RAW = ROOT / "data" / "raw" / "open-archaeo-software.csv"
    MAPPING = CSV / "mapping" / "open-archaeo.csv"
    VOCABULARY = CSV / "mapping" / "open-archaeo-vocabulary.csv"

    @classmethod
    def setUpClass(cls) -> None:
        with cls.RAW.open(encoding="utf-8", newline="") as handle:
            cls.entries = list(csv.DictReader(handle))
        cls.entities = {r["id"]: r for r in table("entities.csv")}
        cls.statements = table("statements.csv")
        cls.idmap = {r["key"]: r["id"] for r in table("idmap.csv") if r["source"] == "open-archaeo"}
        cls.items = {cls.idmap[f"entry:{e['id']}"]: e for e in cls.entries if f"entry:{e['id']}" in cls.idmap}

    def values(self, subject: str, prop: str) -> list[str]:
        return [s["value"] for s in self.statements if s["subject"] == subject and s["property"] == prop]

    def test_the_source_is_the_whole_list_and_the_import_is_all_of_it(self) -> None:
        self.assertEqual(len(self.entries), 416)
        self.assertEqual(sorted(e["id"] for e in importer.select(self.entries, None)), sorted(e["id"] for e in self.items.values()))
        self.assertEqual(len(self.items), 416)
        counts = {c: sum(1 for e in self.items.values() if e["category"] == c)
                  for c in ("Packages and libraries", "Scripts", "Standalone software")}
        self.assertEqual(counts, {"Packages and libraries": 248, "Scripts": 74, "Standalone software": 94})

    def test_every_item_is_a_chublet_of_its_category_with_the_identity_block(self) -> None:
        by_label = {r["label_en"]: r["id"] for r in self.entities.values()}
        wikiproject, platform, collection = (by_label[x] for x in
                                             ("WikiProject chublets.software", "chublets.software", "open-archaeo (Repository)"))
        classes = {"Packages and libraries": "Q103", "Scripts": "Q104", "Standalone software": "Q102"}
        for item, entry in self.items.items():
            self.assertEqual(self.values(item, "P2"), ["Q106", classes[entry["category"]]], item)
            self.assertEqual(self.values(item, "P118"), [wikiproject], item)
            self.assertEqual(self.values(item, "P122"), [platform, collection], item)
            self.assertEqual(self.values(item, "P106"), [collection], item)
            self.assertEqual(self.values(item, "P116"), [entry["slug"]], item)
            self.assertEqual(self.values(item, "P115"), [entry["url"]], item)

    def test_the_twins_of_the_identity_items_are_the_ones_of_the_pack(self) -> None:
        by_label = {r["label_en"]: r["id"] for r in self.entities.values() if r["origin"] == "open-archaeo"}
        for label, wikidata in (("WikiProject chublets.software", "Q141169143"), ("chublets.software", "Q141115774"),
                                ("open-archaeo (Repository)", "Q141190255"), ("Git", "Q186055")):
            self.assertEqual(self.values(by_label[label], "P4"), [wikidata], label)

    def test_every_importer_statement_has_one_reference_and_no_item_value_is_a_foreign_id(self) -> None:
        references = table("references.csv")
        own = [s for s in self.statements if s["origin"] == "open-archaeo"]
        self.assertGreater(len(own), 1000)
        for s in own:
            refs = [r for r in references if r["sid"] == s["sid"]]
            self.assertEqual([(r["property"], r["group"]) for r in refs], [("P6", "1")], s["sid"])
            self.assertTrue(refs[0]["value"].startswith("https://open-archaeo.info/post/"), s["sid"])
            if re.fullmatch(r"Q[1-9][0-9]*", s["value"]) and s["property"] != "P4":
                self.assertTrue(s["value"] in self.entities or s["value"] in csvbuild.KERNEL, s)

    def test_the_importer_rows_all_belong_to_an_item_it_made(self) -> None:
        made = {i for i, r in self.entities.items() if r["origin"] == "open-archaeo"}
        for s in self.statements:
            if s["origin"] == "open-archaeo":
                self.assertIn(s["subject"], made, s)
        self.assertTrue(set(self.items) <= made)

    def test_authors_and_tags_are_items_and_the_deployment_role_is_not_imported(self) -> None:
        for item, entry in self.items.items():
            self.assertEqual(len(self.values(item, "P113")), len([a for a in entry["authors"].split("|") if a]), item)
            self.assertEqual(len(self.values(item, "P117")), len([t for t in entry["tags"].split("|") if t]), item)
            if entry["platform_role"] == "deployment":
                self.assertEqual(self.values(item, "P123") + self.values(item, "P109"), [], item)

    def test_a_reimport_changes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "csv"
            target.mkdir()
            for path in CSV.glob("*.csv"):
                (target / path.name).write_bytes(path.read_bytes())
            args = ["--csv", str(target), "--input", str(self.RAW), "--mapping", str(self.MAPPING), "--vocabulary", str(self.VOCABULARY), "--all"]
            self.assertEqual(quietly(importer, args), 0)
            for path in CSV.glob("*.csv"):
                self.assertEqual((target / path.name).read_bytes(), path.read_bytes(), path.name)


class EveryItemIsAChublet(unittest.TestCase):
    """Florian, 2026-10-23: every software item of chublets is an instance of chublet (Q106)."""

    def test_all_software_items_are_chublets(self) -> None:
        statements = table("statements.csv")
        classes = defaultdict(set)
        for s in statements:
            if s["property"] == "P2":
                classes[s["subject"]].add(s["value"])
        entities = {r["id"]: r for r in table("entities.csv")}
        software = {i for i, c in classes.items() if "Q100" in c or "Q105" in c or entities[i]["origin"] in ("open-archaeo", "wikidata") and "Q106" in c}
        seeds = {r["id"] for r in entities.values() if r["origin"] == "wikidata"}
        self.assertGreaterEqual(len(software), 421)
        self.assertTrue(seeds <= software)
        self.assertEqual(sorted(i for i in software if "Q106" not in classes[i]), [])
        self.assertEqual(sum(1 for i in software if entities[i]["origin"] == "open-archaeo"), 416)


class Merges(unittest.TestCase):
    """S7h: the two items that came from Wikidata and from open-archaeo are merged (Florian, 2026-10-23: Wikidata stays)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = table_at(CSV / "merges.csv")
        cls.site = loader.load_site(ROOT / "data" / "raw", ROOT / "data" / "derived")
        cls.idmap = {r["key"]: r["id"] for r in table("idmap.csv") if r["source"] == "wikidata"}

    def test_alligator_and_profileaar_are_merged_into_their_wikidata_items(self) -> None:
        pairs = {(r["from"], r["to"]) for r in self.rows}
        self.assertLessEqual({("Q381", self.idmap["Q74004218"]), ("Q846", self.idmap["Q74823867"])}, pairs)
        self.assertEqual(self.site.redirects, {r["from"]: r["to"] for r in self.rows})

    def test_three_people_are_merged_into_their_wikidata_items(self) -> None:
        pairs = {(r["from"], r["to"]) for r in self.rows}
        self.assertLessEqual({("Q382", "Q365"), ("Q279", "Q380"), ("Q383", "Q374")}, pairs)       # florianthiery, RonaldVisser, Allard Mees
        for target, name in (("Q365", "Florian Thiery"), ("Q380", "Ronald Visser"), ("Q374", "Allard Wijnand Mees")):
            entity = self.site.entities[target]
            self.assertEqual(entity.labels["en"], name)
            self.assertTrue(any(s.mainsnak.property == "P4" for s in entity.statements), target)
        alligator = self.site.entities[self.idmap["Q74004218"]]
        plain = [s.mainsnak.entity_id for s in alligator.statements if s.mainsnak.property == "P113" and not s.qualifiers]
        self.assertEqual(len(plain), len(set(plain)))                         # nobody twice (the two with a role qualifier are a statement of their own)
        self.assertLessEqual({"Q365", "Q374"}, set(plain) | {s.mainsnak.entity_id for s in alligator.statements if s.mainsnak.property == "P113"})

    def test_the_suggestions_have_nothing_left_to_name(self) -> None:
        with (ROOT / "dist" / "merge-suggestions.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        merged = {r["from"] for r in self.rows} | {r["to"] for r in self.rows}
        self.assertFalse([r for r in rows if r["from"] in merged or r["to"] in merged])         # a merged pair is not suggested again
        self.assertEqual(rows, [])                                                              # nothing else looks like a duplicate

    def test_the_languages_python_and_javascript_are_merged_into_their_wikidata_stubs(self) -> None:
        pairs = {(r["from"], r["to"]) for r in self.rows}
        self.assertLessEqual({("Q139", "Q370"), ("Q406", "Q371")}, pairs)
        self.assertEqual(self.site.entities["Q370"].labels["en"], "Python")
        self.assertEqual(self.site.entities["Q371"].labels["en"], "JavaScript")

    def test_there_is_one_item_with_both_sources_in_it(self) -> None:
        for row in self.rows:
            self.assertNotIn(row["from"], self.site.entities)
            if row["from"] not in ("Q381", "Q846"):
                continue
            target = self.site.entities[row["to"]]
            props = {s.mainsnak.property for s in target.statements}
            self.assertTrue({"P4", "P115", "P116", "P118"} <= props, (row, props))      # twin from Wikidata, identity block from open-archaeo
            self.assertEqual([s.mainsnak.entity_id for s in target.statements if s.mainsnak.property == "P2"].count("Q106"), 1)

    def test_nothing_points_at_a_merged_id_any_more(self) -> None:
        merged = set(self.site.redirects)
        for entity in self.site.entities.values():
            self.assertFalse(merged & set(entity.referenced_ids()), entity.id)

    def test_the_merged_ids_forward_and_are_same_as_in_the_rdf(self) -> None:
        ttl = next((ROOT / "dist").glob("*.ttl")).read_text(encoding="utf-8")
        for row in self.rows:
            page = (ROOT / "docs" / f"{row['from']}.html").read_text(encoding="utf-8")
            self.assertIn(f'url={row["to"]}.html', page)
            self.assertIn(f"wd:{row['to']}", ttl)
            self.assertRegex(ttl, rf"wd:{row['from']}\s+owl:sameAs wd:{row['to']}")

    def test_the_wikidata_report_knows_that_they_are_merged(self) -> None:
        report = (ROOT / "dist" / "wikidata-import.txt").read_text(encoding="utf-8")
        self.assertIn("2 of them merged already", report)


class StarterPack(unittest.TestCase):
    """The pack lies in ``starter-pack/`` and its QuickStatements examples have local versions that ``apply-qs`` accepts."""

    PACK = ROOT / "starter-pack"

    def test_the_pack_is_there_as_delivered(self) -> None:
        for name in ("README.md", "CHANGELOG.md", "data/wikibase-property-set.csv", "data/wikidata-entities.csv", "examples/alligator.qs",
                     "examples/quantaar.qs", "examples/amt-sketch.qs", "docs/05-open-points.md", "tools/verify_wikidata.py"):
            self.assertTrue((self.PACK / name).is_file(), name)

    def test_the_local_examples_are_what_the_script_makes(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        try:
            import qs_to_local
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(qs_to_local.main(["--check"]), 0)
        finally:
            sys.path.remove(str(ROOT / "tools"))
        self.assertEqual(sorted(p.name for p in (self.PACK / "examples-local").glob("*.qs")), ["alligator.qs", "amt-sketch.qs", "quantaar.qs"])

    def test_no_local_example_names_a_wikidata_id_for_a_property(self) -> None:
        for path in (self.PACK / "examples-local").glob("*.qs"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line and not line.startswith("#"):
                    fields = line.split("\t")
                    if len(fields) > 1:
                        self.assertNotRegex(fields[1], r"^P[0-9]{4,}$", f"{path.name}: {line}")

    def test_each_local_example_can_be_applied_to_a_copy_of_the_tables(self) -> None:
        import shutil
        from wikibase_static import step_apply_qs
        with tempfile.TemporaryDirectory() as scratch:
            copy = Path(scratch) / "csv"
            shutil.copytree(CSV, copy)
            for path in sorted((self.PACK / "examples-local").glob("*.qs")):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = step_apply_qs.main([str(path), "--csv", str(copy), "--applied", str(Path(scratch) / "applied.csv")])
                self.assertEqual(code, 0, f"{path.name}: {out.getvalue()}")
                self.assertIn("item(s) created", out.getvalue())


class Edits(unittest.TestCase):
    """S7e: the first QuickStatements file was applied and is remembered."""

    FILE = ROOT / "data" / "edits" / "2026-10-23-amt-inception.qs"

    def test_the_file_is_listed_with_its_hash(self) -> None:
        import hashlib
        rows = table_at(ROOT / "data" / "edits" / "applied.csv")
        digest = hashlib.sha256(self.FILE.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        self.assertEqual([(r["sha256"], r["file"]) for r in rows], [(digest, "data/edits/2026-10-23-amt-inception.qs")])

    def test_amt_has_its_inception_with_a_reference_and_no_origin(self) -> None:
        (statement,) = [r for r in table("statements.csv") if r["subject"] == "Q358" and r["property"] == "P137"]
        self.assertEqual((statement["value"], statement["origin"]), ("2017", ""))
        refs = [(r["property"], r["value"]) for r in table("references.csv") if r["sid"] == statement["sid"]]
        self.assertEqual(refs, [("P6", "https://www.nfdi4objects.net/en/services/academic-meta-tool-amt/")])

    def test_applying_it_again_changes_nothing(self) -> None:
        from wikibase_static import step_apply_qs
        before = {p.name: p.read_bytes() for p in CSV.glob("*.csv")}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = step_apply_qs.main([str(self.FILE), "--csv", str(CSV), "--applied", str(ROOT / "data" / "edits" / "applied.csv")])
        self.assertEqual(code, 0)
        self.assertIn("applied already", out.getvalue())
        self.assertEqual({p.name: p.read_bytes() for p in CSV.glob("*.csv")}, before)

    def test_the_published_page_of_amt_shows_the_year(self) -> None:
        page = (ROOT / "docs" / "Q358.html").read_text(encoding="utf-8")
        self.assertIn("2017", page)


class Wikidata(unittest.TestCase):
    """S7d: the Wikidata items listed in seeds-wikidata.csv, imported with local ids, twins and stubs."""

    SEEDS = CSV / "seeds-wikidata.csv"
    RAW = ROOT / "data" / "raw" / "wikidata"

    @classmethod
    def setUpClass(cls) -> None:
        cls.seeds = table("seeds-wikidata.csv")
        cls.entities = {r["id"]: r for r in table("entities.csv")}
        cls.statements = table("statements.csv")
        cls.idmap = {r["key"]: r["id"] for r in table("idmap.csv") if r["source"] == "wikidata"}

    def values(self, subject: str, prop: str) -> list[str]:
        return [s["value"] for s in self.statements if s["subject"] == subject and s["property"] == prop]

    def test_the_report_finds_two_seeds_that_open_archaeo_has_as_well(self) -> None:
        report = (ROOT / "dist" / "wikidata-import.txt").read_text(encoding="utf-8")
        self.assertIn("share the repository URL https://github.com/ISAAKiel/profileAAR", report)
        self.assertIn("share the exact match URL https://open-archaeo.info/post/alligator/", report)

    def test_the_five_seeds_are_research_software_and_each_is_an_item_with_its_twin(self) -> None:
        self.assertEqual([s["qid"] for s in self.seeds], ["Q74003194", "Q74004218", "Q74005133", "Q74823867", "Q74824570"])
        self.assertEqual({s["kind"] for s in self.seeds}, {"research software"})
        for seed in self.seeds:
            item = self.idmap[seed["qid"]]
            self.assertEqual(self.entities[item]["origin"], "wikidata", seed["qid"])
            self.assertEqual(self.values(item, "P4"), [seed["qid"]], seed["qid"])
            self.assertIn("Q100", self.values(item, "P2"), seed["qid"])          # Wikidata says software, the twin translates it

    def test_the_raw_data_is_kept_with_its_revisions(self) -> None:
        manifest = json.loads((self.RAW / "manifest.json").read_text(encoding="utf-8"))
        for seed in self.seeds:
            self.assertIsNotNone(manifest["entities"][seed["qid"]]["lastrevid"], seed["qid"])
            self.assertTrue((self.RAW / "entities" / f"{seed['qid']}.json").is_file())

    def test_creator_is_the_twin_of_author_and_of_creator(self) -> None:
        self.assertEqual(sorted(self.values("P171", "P4")), ["P170", "P50"])
        self.assertEqual(self.values(self.idmap["Q74824570"], "P171"), [self.idmap["Q58529575"]])

    def test_no_value_of_an_importer_row_is_a_wikidata_id(self) -> None:
        datatypes = {i: r["datatype"] for i, r in self.entities.items() if r["kind"] == "property"}
        own = [s for s in self.statements if s["origin"] in ("wikidata", "wikidata-stub")]
        self.assertGreater(len(own), 100)
        for s in own:
            if s["property"] != "P4" and datatypes.get(s["property"], "wikibase-item") == "wikibase-item":
                self.assertTrue(s["value"] in self.entities or s["value"] in csvbuild.KERNEL, s)
            self.assertNotIn("wd:", s["value"], s)

    def test_a_stub_has_label_description_and_twin_and_nothing_else_a_class_stub_also_its_parent(self) -> None:
        stubs = [i for i, r in self.entities.items() if r["origin"] == "wikidata-stub"]
        self.assertGreaterEqual(len(stubs), 15)
        for item in stubs:
            wanted = ["P1", "P4"] if self.entities[item]["kind"] == "class" else ["P4"]
            self.assertEqual(sorted(s["property"] for s in self.statements if s["subject"] == item), wanted, item)
            self.assertTrue(self.entities[item]["label_en"], item)

    def test_the_types_without_a_twin_are_classes_below_software(self) -> None:
        classes = {r["label_en"]: i for i, r in self.entities.items() if r["origin"] == "wikidata-stub" and r["kind"] == "class"}
        self.assertEqual(sorted(classes), ["QGIS plugin", "plug-in", "utility software"])
        for item in classes.values():
            self.assertEqual(self.values(item, "P1"), ["Q100"], item)

    def test_the_gap_report_names_the_three_properties_the_model_does_not_know(self) -> None:
        report = table_at(ROOT / "dist" / "wikidata-gaps.csv")
        self.assertEqual([(r["wikidata_property"], r["snaks"]) for r in report], [("P136", "7"), ("P1535", "6"), ("P2283", "5")])

    def test_a_reimport_changes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "data" / "csv"
            target.mkdir(parents=True)
            for path in CSV.glob("*.csv"):
                (target / path.name).write_bytes(path.read_bytes())
            args = ["--csv", str(target), "--seeds", str(self.SEEDS), "--raw", str(self.RAW), "--offline"]
            self.assertEqual(quietly(wikidata, args), 0)
            for path in CSV.glob("*.csv"):
                self.assertEqual((target / path.name).read_bytes(), path.read_bytes(), path.name)
            for name in ("wikidata-gaps.csv", "wikidata-import.txt"):
                self.assertEqual((Path(tmp) / "dist" / name).read_bytes(), (ROOT / "dist" / name).read_bytes(), name)


if __name__ == "__main__":
    unittest.main()

class Crm(unittest.TestCase):
    """The CIDOC CRM overlay (S11): one row at the root class `software`, the rest of the class tree inherits it."""

    D14 = "http://www.cidoc-crm.org/extensions/crmdig/D14_Software"
    E73 = "http://www.cidoc-crm.org/cidoc-crm/E73_Information_Object"

    @classmethod
    def setUpClass(cls) -> None:
        cls.site = loader.load_site(ROOT / "data" / "raw", ROOT / "data" / "derived")
        cls.result = rdf.build(cls.site, rdf.Namespaces(BASE))

    def test_the_overlay_has_two_rows_the_root_class_and_little_minion_each_with_a_reason(self) -> None:
        rows = table("../crm.csv")
        self.assertEqual([(r["class"], r["crm_class"]) for r in rows], [("Q100", "crmdig:D14"), ("Q105", "crmdig:D14")])
        self.assertTrue(all(r["note"] for r in rows))
        self.assertEqual(self.site.crm, {"Q100": ["crmdig:D14_Software"], "Q105": ["crmdig:D14_Software"]})

    def test_every_class_of_the_model_is_anchored_in_d14(self) -> None:
        classes = self.site.crm_classes()
        edges = self.site.crm_edges()
        without = sorted(c for c in classes if not self.site.crm_anchors(c, edges))
        self.assertEqual(without, [])
        for class_id in ("Q100", "Q101", "Q102", "Q103", "Q104", "Q105", "Q106"):
            self.assertEqual([a.curie for a in self.site.crm_anchors(class_id, edges)], ["crmdig:D14_Software"], class_id)

    def test_the_export_anchors_software_in_d14_and_the_chain_reaches_e73(self) -> None:
        triples = {(s.value, p.value, o.value) for s, p, o in self.result.triples if all(isinstance(x, rdf.Iri) for x in (s, p, o))}
        subclass = RDFS + "subClassOf"
        self.assertIn((BASE + "/entity/Q100", subclass, self.D14), triples)
        self.assertIn((self.D14, subclass, "http://www.cidoc-crm.org/extensions/crmdig/D1_Digital_Object"), triples)
        self.assertIn(("http://www.cidoc-crm.org/extensions/crmdig/D1_Digital_Object", subclass, self.E73), triples)
        self.assertIn((BASE + "/entity/Q105", subclass, self.D14), triples)

    def test_the_published_file_has_the_crm_section_and_the_page_shows_the_class(self) -> None:
        text = next((ROOT / "dist").glob("*.ttl")).read_text(encoding="utf-8")
        self.assertIn("# CIDOC CRM anchoring (wikibase-static)", text)
        page = (ROOT / "docs" / "Q106.html").read_text(encoding="utf-8")
        self.assertIn("crmdig:D14_Software", page)
        self.assertIn('class="crm"', page)

    def test_the_shacl_check_finds_no_violation_and_one_mutation_finds_exactly_one(self) -> None:
        from wikibase_static import step_check_crm
        text = next((ROOT / "dist").glob("*.ttl")).read_text(encoding="utf-8")
        self.assertEqual([r for r in step_check_crm.validate(text, BASE) if r[0] == "Violation"], [])
        # Little Minion loses its row: take away the triple that anchors it (and nothing else)
        import rdflib
        graph = rdflib.Graph()
        graph.parse(data=text, format="turtle")
        cut = (rdflib.URIRef(f"{BASE}/entity/Q105"), rdflib.RDFS.subClassOf, rdflib.URIRef("http://www.cidoc-crm.org/extensions/crmdig/D14_Software"))
        self.assertIn(cut, graph)
        graph.remove(cut)
        rows = [r for r in step_check_crm.validate(graph.serialize(format="turtle"), BASE) if r[0] == "Violation"]
        self.assertEqual([r[1] for r in rows], [f"{BASE}/entity/Q105"])

    def test_the_dcat_classes_of_the_published_file_reach_the_crm(self) -> None:
        import rdflib
        graph = rdflib.Graph()
        graph.parse(next((ROOT / "dist").glob("*.ttl")), format="turtle")
        for name, expected in (("Dataset", self.E73), ("Catalog", "http://www.cidoc-crm.org/cidoc-crm/E31_Document"),
                               ("Distribution", "http://www.cidoc-crm.org/extensions/crmdig/D1_Digital_Object")):
            self.assertIn((rdflib.URIRef("http://www.w3.org/ns/dcat#" + name), rdflib.RDFS.subClassOf, rdflib.URIRef(expected)), graph)
