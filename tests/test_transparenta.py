"""Fixtures for the transparenta.eu source: the rule for new records and the rule for parents (scripts/consolidate.py).

Run from the repo root:  python3 -m unittest discover -s tests
The tests need no input file, no network and no openpyxl.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import consolidate as c  # noqa: E402

MS_2026 = "1782777600000"      # 2026-06-30
MS_2020 = "1593475200000"      # 2020-06-30
county_of = lambda text: c.squash(text).title()
uat_known = lambda county, place: {"alexandria": "Municipiul Alexandria"}.get(place)


def rec(rid, cif, name="Ministerul X", source="anaf", parents=(), category="Altele", sources=None, cif_tva=None):
    return {"id": rid, "name": name, "county": "Alba", "uat": None, "address": None, "cif": cif, "cif_tva": cif_tva,
            "cif_source": source, "parents": [{"cif": p, "name": "P" + p} for p in parents], "category": category,
            "family": None, "sources": sources or ["anaf"], "link": {}, "possible_duplicate_of": None}


def node(cui, name, parents=(), county="TR", address="Teleorman, Municipiul Alexandria, STRADA A, Numar 1"):
    return {"cui": cui, "name": name, "entity_type": "x", "parents": [{"cui": p} for p in parents],
            "uat": {"county_code": county}, "address": address}


def anaf(name, county="TR", stare="INREGISTRAT din data 01.01.2000", address="JUD. TELEORMAN, MUN. ALEXANDRIA, STR. A, NR.1"):
    return {"denumire": name, "adresa": address, "county": county, "county_name": "TELEORMAN", "stare_inregistrare": stare,
            "inactive": False, "data_radiere": ""}


class NewRecords(unittest.TestCase):
    def setUp(self):
        self.records = [rec("A100", "100", "MINISTERUL SANATATII"), rec("A5", "5", "Altul", cif_tva="RO7")]
        ents = {"11": node("11", "CENTRUL JUDETEAN DE APARATURA MEDICALA TELEORMAN", ["100"]),
                "12": node("12", "Corp vechi", ["100"]),
                "13": node("13", "Corp fara parinte nostru", ["999"]),
                "14": node("14", "Corp radiat ANAF", ["100"]),
                "15": node("15", "Corp radiat MF", ["100"]),
                "5": node("5", "Altul", ["100"]),
                "7": node("7", "Are cif tva", ["100"])}
        self.tp = {"entities": ents,
                   "last": {k: {"last_report_ms": MS_2020 if k == "12" else MS_2026} for k in ents},
                   "anaf": {"11": anaf("CENTRUL JUDETEAN DE APARATURA MEDICALA TELEORMAN"), "12": anaf("Corp vechi"),
                            "13": anaf("Corp fara parinte nostru"), "14": anaf("Corp radiat ANAF", stare="RADIERE din data 01.01.2020"),
                            "15": anaf("Corp radiat MF"), "7": anaf("Are cif tva")}}
        self.mf = [{"cui": "15", "status": "radiat"}]

    def run_rule(self):
        return c.transparenta_records(self.tp, self.records, self.mf, 2026, county_of, uat_known)

    def test_only_the_entity_that_meets_every_condition_becomes_a_record(self):
        new = self.run_rule()
        self.assertEqual([r["id"] for r in new], ["T11"])
        r = new[0]
        self.assertEqual((r["cif"], r["cif_source"], r["sources"], r["parent_source"]), ("11", "transparenta", ["transparenta"], "transparenta"))
        self.assertEqual(r["parents"], [{"cif": "100", "name": "MINISTERUL SANATATII"}])
        self.assertEqual((r["county"], r["uat"]), ("Teleorman", "Municipiul Alexandria"))

    def test_no_address_takes_the_county_of_a_local_parent(self):
        self.records.append(rec("A200", "200", "COMUNA BOLBOSI"))
        self.records[-1]["county"] = "Gorj"
        self.tp["entities"]["11"] = node("11", "CLUBUL SPORTIV VIITORUL BOLBOSI", ["200"], address=None)
        self.tp["anaf"]["11"] = anaf("CLUBUL SPORTIV VIITORUL BOLBOSI")
        r = self.run_rule()[0]
        self.assertEqual((r["county"], r["address"]), ("Gorj", None))

    def test_a_cif_tva_counts_as_a_known_cui(self):
        self.assertNotIn("T7", [r["id"] for r in self.run_rule()])
        self.records[1]["cif_tva"] = None
        self.assertIn("T7", [r["id"] for r in self.run_rule()])

    def test_a_report_of_the_year_before_counts(self):
        self.tp["last"]["12"]["last_report_ms"] = "1751241600000"      # 2025-06-30
        self.assertIn("T12", [r["id"] for r in self.run_rule()])

    def test_mf_in_lichidare_blocks(self):
        self.mf = [{"cui": "11", "status": "in_lichidare"}, {"cui": "15", "status": "radiat"}]
        self.assertEqual(self.run_rule(), [])

    def test_address_places(self):
        f = lambda a: c.transparenta_uat(a, "Gorj", lambda county, place: place)
        self.assertEqual(f("JUD. GORJ, SAT BOLBOŞI COM. BOLBOŞI, NR.31"), "bolbosi")
        self.assertEqual(f("JUD. GORJ, MUN. MOTRU, STR. T"), "motru")
        self.assertEqual(f("MUN. BUCUREŞTI, SECTOR 3, STR. T"), "Sectorul 3 al Municipiului Bucuresti")
        self.assertIsNone(f("JUD. GORJ, STR. T"))


class ParentRule(unittest.TestCase):
    def tp(self, **parents):
        return {"entities": {k: node(k, "n", v) for k, v in parents.items()}}

    def test_record_without_parent_takes_the_parents_of_the_entity(self):
        recs = [rec("A100", "100", "MINISTERUL CULTURII"), rec("S9", "9", "Studioul", "seap", sources=["seap"])]
        changed = c.transparenta_parents(self.tp(**{"9": ["100", "404"]}), recs)
        s = recs[1]
        self.assertEqual(changed, [s])
        self.assertEqual(s["parents"], [{"cif": "100", "name": "MINISTERUL CULTURII"}])     # 404 is not a record of ours
        self.assertEqual((s["parent_source"], s["sources"]), ("transparenta", ["seap", "transparenta"]))
        self.assertEqual(s["category"], "Cultură, sport și tineret")                         # ancestors feed categorize

    def test_a_set_parent_and_anaf_records_stay(self):
        recs = [rec("A100", "100"), rec("A200", "200"), rec("S9", "9", source="seap", parents=["200"], sources=["seap"]),
                rec("A8", "8")]
        changed = c.transparenta_parents(self.tp(**{"9": ["100"], "8": ["100"]}), recs)
        self.assertEqual(changed, [])
        self.assertEqual([p["cif"] for p in recs[2]["parents"]], ["200"])
        self.assertEqual(recs[3]["parents"], [])                                              # an ANAF root stays a root
        self.assertEqual(recs[3]["sources"], ["anaf"])

    def test_a_category_that_a_name_set_stays(self):
        recs = [rec("A100", "100", "MINISTERUL SANATATII"), rec("S9", "9", "Scoala gimnaziala X", "seap", category="Educație")]
        c.transparenta_parents(self.tp(**{"9": ["100"]}), recs)
        self.assertEqual(recs[1]["category"], "Educație")

    def test_a_self_parent_is_ignored_and_a_cycle_stops(self):
        recs = [rec("S1", "1", source="seap"), rec("S2", "2", source="seap")]
        self.assertEqual(c.transparenta_parents(self.tp(**{"1": ["1"]}), recs), [])
        with self.assertRaises(SystemExit):
            c.transparenta_parents(self.tp(**{"1": ["2"], "2": ["1"]}), recs)

    def test_explorer_bit_and_key(self):
        self.assertEqual(c.SRC_BIT["transparenta"], 64)
        recs = [{**rec("S1", "1", source="seap", sources=["seap", "transparenta"]), "parent_source": "transparenta"},
                {**rec("S2", "2", source="seap", sources=["seap"])}]
        tmp = Path(tempfile.mkdtemp())
        c.write_explorer_data(tmp, recs)
        rows = {r["i"]: r for r in json.loads((tmp / "rows.json").read_text(encoding="utf-8"))}
        self.assertEqual((rows["S1"]["s"], rows["S1"]["pt"]), (96, 1))
        self.assertNotIn("pt", rows["S2"])


if __name__ == "__main__":
    unittest.main()
