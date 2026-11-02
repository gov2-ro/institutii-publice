"""Fixtures for the SEAP source: scripts/extract_seap.py and the SEAP and identity parts of scripts/consolidate.py.

Run from the repo root:  python3 -m unittest discover -s tests
The tests need neither openpyxl, xlrd nor the dump.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import consolidate as c  # noqa: E402
import extract_seap as x  # noqa: E402


class NormalizeCui(unittest.TestCase):
    def test_plain_and_leading_zeros(self):
        self.assertEqual(x.normalize_cui("4266928"), "4266928")
        self.assertEqual(x.normalize_cui("0004266928"), "4266928")
        self.assertEqual(x.normalize_cui(" 42 669 28 "), "4266928")
        self.assertEqual(x.normalize_cui("4266928.0"), "4266928")

    def test_ro_prefix_is_removed(self):
        self.assertEqual(x.normalize_cui("RO4266928"), "4266928")
        self.assertEqual(x.normalize_cui("ro 4266928"), "4266928")
        self.assertEqual(x.normalize_cui("R 8468440"), "8468440")                 # a typo seen in the data
        self.assertEqual(x.normalize_cui("RO1883902 / J13/60/1"), "1883902")      # trade register number appended

    def test_scientific_notation_only_when_exact(self):
        self.assertEqual(x.normalize_cui("1.2345E+4"), "12345")
        self.assertEqual(x.normalize_cui("1,2345E+4"), "12345")
        self.assertIsNone(x.normalize_cui("1.8839E+14"))        # a rounded 15-digit value
        self.assertIsNone(x.normalize_cui("1.2E+6"))            # zeros would be invented
        self.assertIsNone(x.normalize_cui("1.5E-3"))

    def test_fifteen_digit_and_short_values_are_rejected(self):
        self.assertIsNone(x.normalize_cui("188390000000000"))
        self.assertIsNone(x.normalize_cui("12345678901"))
        self.assertIsNone(x.normalize_cui("7"))
        self.assertIsNone(x.normalize_cui("0000"))

    def test_blank_and_text_are_rejected(self):
        for raw in ("", "   ", None, "CUI", "CUI autoritate contractanta", "n/a", "12-34"):
            self.assertIsNone(x.normalize_cui(raw), raw)


class ReadAuthorities(unittest.TestCase):
    def test_header_after_a_title_row_and_repeated_header_rows(self):
        rows = [["Raport Contracte T1 2023"], ["Autoritate contractanta", "CUI autoritate contractanta", "Tip autoritate",
                                              "Tip activitate", "Localitate", "Judet"],
                ["Primaria Alfa", "0004266928", "Autoritate locala", "Servicii", "Alfa", "ALBA"],
                ["Primaria Alfa", "4266928", "Autoritate locala", "Servicii", "Alfa", "ALBA"],
                ["Autoritate contractanta", "CUI autoritate contractanta", "", "", "", ""],     # header repeated in the data
                ["", ""],                                                                        # blank: skipped
                ["Fara CUI", ""],
                ["Spital Beta", "1.8839E+14", "", "", "", ""]]
        counts, n, rejects, found = x.read_authorities(rows)
        self.assertTrue(found)
        self.assertEqual((n, rejects), (4, 2))
        self.assertEqual(counts[("4266928", "Primaria Alfa", "Autoritate locala", "Servicii", "Alfa", "ALBA")], 2)

    def test_two_columns_named_cui_only_use_the_first_two_cells(self):
        counts, n, rejects, _ = x.read_authorities([["Autoritate contractanta", "CUI", "CUI"], ["Scoala 1", "123456", "999"]])
        self.assertEqual(list(counts), [("123456", "Scoala 1", "", "", "", "")])

    def test_older_reports_have_the_bidder_first_and_the_authority_later(self):
        head = ["CASTIGATOR", "CASTIGATOR_CUI", "TIP_ANUNT", "AUTORITATE_CONTRACTANTA", "AUTORITATE_CONTRACTANTA_C",
                "TIP_AUTORITATE", "TIP__ACTIVITATE_AUTORITAT"]
        counts, n, rejects, found = x.read_authorities([head, ["Furnizor SRL", "RO 1", "Anunt", "Spital Alfa", "5002142",
                                                               "Institutii", "Sanatate"]])
        self.assertEqual(list(counts), [("5002142", "Spital Alfa", "Institutii", "Sanatate", "", "")])

    def test_a_cui_column_after_a_bidder_name_is_not_a_header(self):
        self.assertFalse(x.read_authorities([["CASTIGATOR", "CASTIGATOR_CUI"], ["Furnizor SRL", "123456"]])[3])
        self.assertFalse(x.read_authorities([["Obiect", "CUI"], ["Ceva", "123456"]])[3])

    def test_a_second_report_inside_the_file_has_its_own_layout(self):
        rows = [["NR", "DENUMIRE_AC", "CUI_AC"], ["1", "Alfa", "111"],
                ["DENUMIRE_AC", "CUI_AC", "COD_NUTS"], ["Beta", "222", "RO1"]]
        counts, n, rejects, _ = x.read_authorities(rows)
        self.assertEqual(sorted(k[:2] for k in counts), [("111", "Alfa"), ("222", "Beta")])
        self.assertEqual((n, rejects), (2, 0))

    def test_a_file_without_header_is_reported(self):
        self.assertFalse(x.read_authorities([["a", "b"], ["c", "d"]])[3])

    def test_report_type_and_period(self):
        self.assertEqual(x.report_type("12603603-datagov-raport-anunturi-de-atribuire-la-proceduri-fara-anunt-de-initiere-t-iii-2023.csv"),
                         "atribuire_fara_anunt")
        self.assertEqual(x.report_type("94f1fc6f-anunturi-de-atribuire-la-proceduri-fr-anun-de-initiere-t_iv_2025.xlsx"),
                         "atribuire_fara_anunt")
        self.assertEqual(x.report_type("6df70e9f-raport-date-din-modificare-contract-ti-2026.xlsx"), "modificare_contract")
        self.assertEqual(x.report_type("728c1bb4-raport-notificari-de-atribuire-la-cumpararea-directa-ti-2026.xlsx"),
                         "notificari_directa")
        self.assertEqual(x.report_type("5bcff70e-raport-achizitii-directe-ti-2026.xlsx"), "achizitii_directe")
        self.assertEqual(x.period("a-t-iv-2023.csv", "Achiziții publice 2023"), "2023-Q4")
        self.assertEqual(x.period("raport-contracte-tiii.xlsx", "Achiziții publice 2026"), "2026-Q3")
        self.assertEqual(x.period("raport-t1-2023.xls", "Achiziții publice 2023"), "2023-Q1")
        self.assertEqual(x.period("raport-contracte.xls", "Achizitii publice 2019"), "2019")

    def test_aggregate_name_is_the_most_frequent_then_the_newest(self):
        files = [{"period": "2025-Q1", "report_type": "contracte",
                  "counts": {("55", "A SA", "", "", "", ""): 2, ("55", "B SA", "", "", "", ""): 2}},
                 {"period": "2026-Q1", "report_type": "achizitii_directe",
                  "counts": {("55", "B SA", "", "", "Alfa", "ALBA"): 1, ("9", "Z", "", "", "", ""): 1}}]
        a = {r["cui"]: r for r in x.aggregate(files)}
        self.assertEqual(a["55"]["name"], "B SA")
        self.assertEqual(a["55"]["names"], "A SA")
        self.assertEqual((a["55"]["first_seen"], a["55"]["last_seen"], a["55"]["rows"]), ("2025-Q1", "2026-Q1", 5))
        self.assertEqual(a["55"]["report_types"], "achizitii_directe|contracte")
        self.assertEqual((a["55"]["locality"], a["55"]["county"]), ("Alfa", "ALBA"))
        self.assertEqual(list(a), ["9", "55"])                  # numeric order


class CachedWithoutDump(unittest.TestCase):
    def test_authorities_are_rebuilt_from_the_cache_when_the_file_is_gone(self):
        with tempfile.TemporaryDirectory() as d:
            dump, out = Path(d) / "dump", Path(d) / "out"
            (dump / "y").mkdir(parents=True)
            res = {"id": "abcdef12-0000-0000-0000-000000000000", "name": "Contracte TII 2023", "size": 99,
                   "url": "https://x/abcdef12-contracte-tii-2023.csv"}
            (dump / "packages.json").write_text(x.json.dumps([{"id": "p", "title": "Achizitii publice 2023",
                                                               "resources": [res]}]), encoding="utf-8")
            counts = {("55", "Alfa", "Autoritate locala", "Servicii", "Alfa", "ALBA"): 3}
            x.write_cache(out / "cache" / f"{res['id']}.csv", counts, 3, 1, size=99, sha256="ab", file="y/abcdef12-contracte-tii-2023.csv",
                          period="2023-Q2", report_type="contracte")
            sys.argv = ["extract_seap", "--dump", str(dump), "--out", str(out)]
            x.main()
            manifest = x.json.loads((out / "manifest.json").read_text(encoding="utf-8"))["files"]
            self.assertEqual([(e["status"], e["rows"], e["authorities"], e["period"]) for e in manifest], [("cached", 3, 1, "2023-Q2")])
            line = (out / "authorities.csv").read_text(encoding="utf-8").splitlines()[1]
            self.assertEqual(line, "55,Alfa,,2023-Q2,2023-Q2,3,contracte,Autoritate locala,Servicii,Alfa,ALBA")

    def test_a_cache_of_another_size_is_not_used(self):
        with tempfile.TemporaryDirectory() as d:
            dump, out = Path(d) / "dump", Path(d) / "out"
            dump.mkdir()
            res = {"id": "abcdef12-0000", "name": "n", "size": 100, "url": "https://x/abcdef12-n.csv"}
            (dump / "packages.json").write_text(x.json.dumps([{"id": "p", "title": "2023", "resources": [res]}]), encoding="utf-8")
            x.write_cache(out / "cache" / "abcdef12-0000.csv", {}, 0, 0, size=99, sha256="ab", file="", period="2023", report_type="x")
            sys.argv = ["extract_seap", "--dump", str(dump), "--out", str(out)]
            x.main()
            self.assertEqual(x.json.loads((out / "manifest.json").read_text())["files"][0]["status"], "missing")


class PrivateNames(unittest.TestCase):
    def rule(self, name, tip=""):
        return c.seap_private(name, tip)

    def test_each_kind_is_excluded(self):
        self.assertEqual(self.rule("PAROHIA ORTODOXA SF. NICOLAE"), "church")
        self.assertEqual(self.rule("MANASTIREA HUREZI"), "church")
        self.assertEqual(self.rule("Arhiepiscopia Sibiului"), "church")
        self.assertEqual(self.rule("FUNDATIA PENTRU COPII"), "foundation")
        self.assertEqual(self.rule("ASOCIATIA DE PROPRIETARI BLOC 5"), "association")
        self.assertEqual(self.rule("CLUBUL SPORTIV FC ALFA"), "sports club")
        self.assertEqual(self.rule("Asociatia Fotbal Club Beta"), "association")
        self.assertEqual(self.rule("CENTRUL DE FORMARE ALFA", "Operatorii economici care beneficiază de finanțare din instrumente structurale"), "tip")

    def test_the_exceptions_are_kept(self):
        self.assertIsNone(self.rule("ASOCIATIA DE DEZVOLTARE INTERCOMUNITARA APA ALFA"))
        self.assertIsNone(self.rule("Asociatia Municipiilor din Romania"))
        self.assertIsNone(self.rule("UNIUNEA NATIONALA A CONSILIILOR JUDETENE DIN ROMANIA",
                                    "Operatorii economici care beneficiază de finanțare din instrumente structurale"))
        self.assertIsNone(self.rule("SC SEPSI REKREATIV SA", "Operatorii economici care beneficiază de finanțare din instrumente structurale"))
        self.assertIsNone(self.rule("CLUBUL SPORTIV MUNICIPAL ALFA"))
        self.assertIsNone(self.rule("CLUBUL SPORTIV SCOLAR BETA"))
        self.assertIsNone(self.rule("CLUBUL SPORTIV UNIVERSITAR GAMMA"))
        self.assertIsNone(self.rule("CLUBUL SPORTIV AL ARMATEI STEAUA"))

    def test_companies_and_public_bodies_are_kept(self):
        for name in ("SERVICIUL PUBLIC DE ALIMENTARE CU APA ALFA SRL", "TERMOENERGETICA ALFA SA", "SCOALA GIMNAZIALA NR 1",
                     "SPITALUL SF. SPIRIDON", "COMPANIA NATIONALA DE ADMINISTRARE A INFRASTRUCTURII RUTIERE SA",
                     "UNIUNEA NATIONALA A CONSILIILOR JUDETENE DIN ROMANIA", "CLUBUL COPIILOR ALFA"):
            self.assertIsNone(self.rule(name), name)


def rec(id_, name, cif=None, **extra):
    return {"id": id_, "name": name, "cif": cif, "cif_tva": extra.pop("cif_tva", None), "sources": ["anaf"], "link": {},
            "merged_ids": extra.pop("merged_ids", []), **extra}


def identities(rows, records):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "identities.csv"
        path.write_text("id,cif,checked_at,evidence\n" + "".join(f"{i},{k},2026-11-02,test\n" for i, k in rows),
                        encoding="utf-8")
        return c.apply_curated_identities(records, c.load_curated_identities(path)) if records is not None \
            else c.load_curated_identities(path)


class Identities(unittest.TestCase):
    def test_a_row_sets_the_cif_and_the_source(self):
        records = [rec("A1", "Alfa", "1"), rec("R2", "Beta")]
        self.assertEqual(identities([("R2", "361684")], records), 1)
        self.assertEqual((records[1]["cif"], records[1]["cif_source"], records[0]["cif_source"]), ("361684", "curation", "anaf"))

    def test_an_absorbed_id_goes_to_the_survivor(self):
        records = [rec("G2", "Beta", merged_ids=["R7"])]
        identities([("R7", "361684")], records)
        self.assertEqual(records[0]["cif"], "361684")

    def test_unknown_id_stops(self):
        with self.assertRaisesRegex(SystemExit, "matches no record"):
            identities([("R9", "361684")], [rec("R2", "Beta")])

    def test_duplicate_id_and_duplicate_cif_stop(self):
        with self.assertRaisesRegex(SystemExit, "id listed twice"):
            identities([("R2", "361684"), ("R2", "361685")], None)
        with self.assertRaisesRegex(SystemExit, "cif listed twice"):
            identities([("R2", "361684"), ("R3", "361684")], None)

    def test_cif_that_is_not_digits_stops(self):
        with self.assertRaisesRegex(SystemExit, "not digits"):
            identities([("R2", "RO361684")], None)

    def test_a_record_with_a_cif_stops(self):
        with self.assertRaisesRegex(SystemExit, "already has the CIF"):
            identities([("A1", "361684")], [rec("A1", "Alfa", "1")])

    def test_a_cif_of_an_anaf_record_points_to_merges(self):
        with self.assertRaisesRegex(SystemExit, "curation/merges.csv"):
            identities([("R2", "1")], [rec("A1", "Alfa", "1"), rec("R2", "Beta")])

    def test_two_rows_for_one_survivor_stop(self):
        with self.assertRaisesRegex(SystemExit, "are one record"):
            identities([("R2", "361684"), ("R7", "361685")], [rec("R2", "Beta", merged_ids=["R7"])])


class LinkSeap(unittest.TestCase):
    row = lambda self, cui: {"cui": cui, "name": "N", "rows": 1}

    def test_cif_then_cif_tva(self):
        records = [rec("A1", "Alfa", "10"), rec("A2", "Beta", "20", cif_tva="30")]
        linked, rest = c.link_seap(records, [self.row("10"), self.row("30"), self.row("40")])
        self.assertEqual(sorted(linked), ["10", "30"])
        self.assertEqual([r["cui"] for r in rest], ["40"])
        self.assertEqual(records[1]["sources"], ["anaf", "seap"])
        self.assertEqual((records[0]["link"]["seap"], records[1]["link"]["seap"]), ("cif", "cif_tva"))

    def test_cif_wins_over_cif_tva(self):
        linked, _ = c.link_seap([rec("A1", "Alfa", "10"), rec("A2", "Beta", "20", cif_tva="10")], [self.row("10")])
        self.assertEqual(linked["10"]["id"], "A1")

    def test_a_cui_with_two_records_stops(self):
        with self.assertRaisesRegex(SystemExit, "more than one record"):
            c.link_seap([rec("A1", "Alfa", "10", cif_tva="5"), rec("A2", "Beta", "20", cif_tva="5")], [self.row("5")])


if __name__ == "__main__":
    unittest.main()
