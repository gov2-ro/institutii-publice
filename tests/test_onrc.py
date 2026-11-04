"""Fixtures for scripts/onrc_candidates.py: name key, tiers and the reader. No inputs, no network.

Run from the repo root:  python3 -m unittest discover -s tests
"""
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import onrc_candidates as o  # noqa: E402


def onrc(name, cui, county="Alba", cod="J1/1/2000", form="SA"):
    return {"DENUMIRE": name, "CUI": cui, "COD_INMATRICULARE": cod, "FORMA_JURIDICA": form, "ADR_JUDET": county,
            "ADR_LOCALITATE": "Loc", "DATA_INMATRICULARE": "01/01/2000"}


def record(rid, name, county, cif=""):
    return {"id": rid, "name": name, "county": county, "category": "Companii de stat", "cif": cif}


def queue(records, onrc_rows, states=None):
    by_key = defaultdict(list)
    for r in onrc_rows:
        by_key[o.name_key(r["DENUMIRE"])].append(r)
    return o.build_queue(records, by_key, states or {}, {"1048": "funcțiune", "1084": "radiată"})


class NameKey(unittest.TestCase):
    def test_onrc_name_key(self):
        for name in ("TETAROM SA", "TETAROM S.A.", "S.C. TETAROM S.A.", "SC TETAROM SA", "S C TETAROM S A",
                     "Tetarom - S.A.", "SC TETAROM"):
            self.assertEqual(o.name_key(name), "tetarom", name)
        self.assertEqual(o.name_key("ECOSERV SIG S R L SIGHISOARA"), "ecoserv sig sighisoara")
        self.assertEqual(o.name_key("DRUMURI MUNICIPALE S.R.L."), o.name_key("S C DRUMURI MUNICIPALE S A"))
        self.assertEqual(o.name_key("TRANSURBAN RA"), o.name_key("TRANSURBAN SA"))
        self.assertEqual(o.name_key("Băile Sărate"), "baile sarate")                  # diacritics fold
        self.assertEqual(o.name_key("SC SA"), "")                                      # only form words: empty key
        self.assertEqual(o.name_key("SCOALA GIMNAZIALA NR 1"), "scoala gimnaziala nr 1")  # SCOALA is not SC

    def test_company_form_flag(self):
        self.assertTrue(o.has_company_form("SC TETAROM"))
        self.assertTrue(o.has_company_form("ELECTRICA FURNIZARE S A SFEE"))
        self.assertFalse(o.has_company_form("SCOALA GIMNAZIALA NR 1"))
        self.assertFalse(o.has_company_form("PRIMARIA SASAR"))


class Tiers(unittest.TestCase):
    def setUp(self):
        self.rows = [
            onrc("ALFA SA", "100", "Alba"),
            onrc("BETA SA", "200", "Cluj"),
            onrc("GAMA SA", "300", "Alba", "J1/3/2000"), onrc("GAMA SRL", "301", "Alba", "J1/4/2000", "SRL"),
            onrc("DELTA SA", "400", "Alba"), onrc("DELTA SA", "401", "Cluj", "J12/1/2000"),
            onrc("ZERO SA", "0", "Alba"),
            onrc("HELD SA", "500", "Alba"),
        ]
        self.records = [record("D1", "SC ALFA SA", "Alba"), record("D2", "BETA SA", "Alba"),
                        record("D3", "GAMA", "Alba"), record("D4", "DELTA SA", "Alba"),
                        record("D5", "ZERO SA", "Alba"), record("D6", "OMEGA SA", "Alba"),
                        record("D7", "HELD SA", "Alba"), record("S500", "OTHER", "Alba", cif="500"),
                        record("D8", "ALFA", "Cluj", cif="9")]

    def by_id(self):
        return {q["id"]: q for q in queue(self.records, [r for r in self.rows if r["CUI"] != "0"])}

    def test_onrc_tiers(self):
        q = self.by_id()
        self.assertEqual((q["D1"]["tier"], q["D1"]["cui"], q["D1"]["status"]), ("exact_county", "100", "identity_candidate"))
        self.assertEqual((q["D2"]["tier"], q["D2"]["onrc_rows_same_county"]), ("exact_elsewhere", 0))
        self.assertEqual((q["D3"]["tier"], q["D3"]["onrc_rows_total"], q["D3"]["onrc_rows_same_county"]), ("ambiguous", 2, 2))
        self.assertEqual(q["D3"]["status"], "ambiguous")
        self.assertEqual((q["D4"]["tier"], q["D4"]["cui"]), ("exact_county", "400"))      # one row in the county, two in all
        self.assertEqual(q["D4"]["onrc_rows_total"], 2)
        self.assertEqual(q["D5"]["tier"], "none")                                          # rows with CUI 0 are dropped
        self.assertEqual(q["D6"]["tier"], "none")
        self.assertEqual((q["D7"]["tier"], q["D7"]["status"], q["D7"]["cui_other_record"]),
                         ("exact_county", "merge_candidate", "S500"))
        self.assertNotIn("D8", q)                                                          # a record with a CIF is not queued
        self.assertNotIn("S500", q)                                                        # only D records are queued

    def test_ambiguous_lists_five_rows(self):
        rows = [onrc("MANY SA", str(900 + k), "Cluj", f"J1/{k}/2000") for k in range(8)]
        q = queue([record("D1", "MANY", "Alba")], rows)
        self.assertEqual(len(q), 5)
        self.assertEqual({r["onrc_rows_total"] for r in q}, {8})

    def test_in_function(self):
        self.assertEqual(o.in_function(["1048"]), "yes")
        self.assertEqual(o.in_function(["1048", "1084"]), "no")
        self.assertEqual(o.in_function(["1070", "1139"]), "no")
        self.assertEqual(o.in_function(["1057"]), "unknown")
        self.assertEqual(o.in_function([]), "unknown")


class IdentityRule(unittest.TestCase):
    def row(self, **kw):
        base = {"tier": "exact_county", "record_name": "TETAROM SA", "legal_form": "SA", "onrc_rows_same_county": 1,
                "cui_other_record": "", "cui": "100", "in_function": "yes"}
        return {**base, **kw}

    def test_onrc_rule_passes(self):
        self.assertEqual(o.identity_rejects(self.row(), {"100": 1}), "")
        self.assertEqual(o.identity_rejects(self.row(record_name="S C ECOSERV SIG S R L", legal_form="SRL"), {}), "")
        self.assertEqual(o.identity_rejects(self.row(record_name="ROMATSA R A", legal_form="RA"), {}), "")
        self.assertEqual(o.identity_rejects(self.row(record_name="R A T SRL", legal_form="SRL"), {}), "")

    def test_onrc_rule_rejects(self):
        rejects = o.identity_rejects
        self.assertIn("form conflict", rejects(self.row(record_name="ROMGAZ SA", legal_form="RA"), {}))
        self.assertIn("form conflict", rejects(self.row(record_name="CALORGAL SA", legal_form="SRL"), {}))
        self.assertIn("second ONRC row", rejects(self.row(onrc_rows_same_county=2), {}))
        self.assertIn("another record", rejects(self.row(cui_other_record="S100"), {}))
        self.assertIn("another D record", rejects(self.row(), {"100": 2}))
        self.assertIn("not in function: no", rejects(self.row(in_function="no"), {}))
        self.assertIn("not in function: unknown", rejects(self.row(in_function="unknown"), {}))
        self.assertIn("tier exact_elsewhere", rejects(self.row(tier="exact_elsewhere"), {}))
        self.assertIn("no company form", rejects(self.row(record_name="SCOALA NR 1", legal_form="SA"), {}))
        self.assertIn("only SC", rejects(self.row(record_name="SC OIL TERMINAL", legal_form="SA"), {}))


class Reader(unittest.TestCase):
    def test_onrc_quote_none(self):
        header = "DENUMIRE^CUI^COD_INMATRICULARE^ADR_JUDET"
        lines = [header,
                 'CRISTEA R. DUMITRU "DEPANAREA RADIO-TV." PF^0^F40/22/1991^Bucureşti',
                 'ALFA "SA^123^J1/1/2000^Alba',
                 'TOO^FEW']
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "OD_FIRME.csv"
            p.write_bytes(("﻿" + "\r\n".join(lines) + "\r\n").encode("utf-8"))
            rows = list(o.read_firme(p))
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0]["DENUMIRE"], 'CRISTEA R. DUMITRU "DEPANAREA RADIO-TV." PF')
        self.assertEqual(rows[0]["ADR_JUDET"], "Bucureşti")
        self.assertEqual((rows[1]["DENUMIRE"], rows[1]["CUI"]), ('ALFA "SA', "123"))   # an odd quote keeps the next columns
        self.assertIsNone(rows[2])                                                      # a wrong column count is flagged
        self.assertEqual(list(rows[0])[0], "DENUMIRE")                                  # the BOM is gone

    def test_read_rows_state_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "OD_STARE_FIRMA.csv"
            p.write_bytes("﻿COD_INMATRICULARE^COD\r\nJ1/1/2000^1048\r\n".encode("utf-8"))
            self.assertEqual(list(o.read_rows(p)), [["J1/1/2000", "1048"]])


if __name__ == "__main__":
    unittest.main()
