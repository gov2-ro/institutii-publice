"""Fixtures for the status of a legal body: scripts/lookup_status.py and the status part of scripts/consolidate.py.

Run from the repo root:  python3 -m unittest discover -s tests
The tests need no input file, no network and no openpyxl.
"""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import consolidate as c  # noqa: E402
import lookup_status as ls  # noqa: E402

COUNTIES = {"alba": "Alba", "bucuresti": "Bucuresti", "salaj": "Salaj"}
county_of = lambda text: COUNTIES.get(c.fold("bucuresti" if c.fold(text) == "municipiul bucuresti" else text))
UAT = {("alba", "alba iulia"): "Municipiul Alba Iulia"}
uat_of = lambda county, locality: UAT.get((c.fold(county), c.fold(locality)))


def record(rid, cif, source="seap", county="", uat="", name="Corp"):
    return {"id": rid, "name": name, "county": county, "uat": uat, "cif": cif, "cif_source": source, "parents": [],
            "category": "Altele", "family": None, "sources": ["seap"], "link": {}, "possible_duplicate_of": None}


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def row(cui, status="listat", date="2020-05-01", county="ALBA", locality="Alba Iulia"):
    return {"cui": cui, "name": "x", "status": status, "status_label": "", "status_date": date, "county": county,
            "locality": locality, "source": "mf", "checked_at": "2026-06-11"}


class StatusRule(unittest.TestCase):
    def test_status_rule(self):
        expect = {"RADIERE": "radiat", "LICHIDAT": "radiat",
                  "DIZOLVARE FARA LICHIDARE(FUZIUNE)": "fuzionat", "DIZOLVARE FARA LICHIDARE(DIVIZARE)": "fuzionat",
                  "DIZOLVARE CU LICHIDARE(INCEPUT LICHIDARE)": "in_lichidare",
                  "INREGISTRAT": "listat", "MODIFICARE PUBLICI": "listat", "TRANSFER(SOSIRE)": "listat",
                  "RELUARE ACTIVITATE": "listat", "SUSPENDARE ACTIVITATE": "listat"}
        for label, status in expect.items():
            self.assertEqual(ls.status_of(label), status, label)
        self.assertEqual(ls.status_of(" RADIERE "), "radiat")                     # the label is trimmed
        self.assertEqual(set(ls.STATUS_RULE), set(expect))                        # no label outside the rule

    def test_unknown_or_empty_label_stops_the_script(self):
        for label in ("DIZOLVARE", "radiere", "", "   ", None, "DIZOLVARE FARA LICHIDARE"):
            with self.assertRaises(SystemExit, msg=repr(label)):
                ls.status_of(label)

    def test_date_format(self):
        self.assertEqual(ls.iso_date("30.11.1992"), "1992-11-30")
        self.assertEqual(ls.iso_date("02.09.2013 8:46:57"), "2013-09-02")
        self.assertEqual(ls.iso_date(""), "")
        with self.assertRaises(SystemExit):
            ls.iso_date("1992-11-30")

    def test_absent_cui_is_not_found(self):
        rows = ls.build_rows([{"cif": "5", "name": "A"}, {"cif": "7", "name": "B"}],
                             {"7": {"status_label": "RADIERE", "status_date": "2019-01-02", "county": "ALBA", "locality": "Blaj"}},
                             "2026-06-11")
        by = {r["cui"]: r for r in rows}
        self.assertEqual(by["5"]["status"], "not_found")                          # never `radiat`
        self.assertEqual((by["5"]["status_label"], by["5"]["county"]), ("", ""))
        self.assertEqual(by["7"]["status"], "radiat")
        self.assertEqual([r["cui"] for r in rows], ["5", "7"])

    def test_natural_person_row_is_skipped(self):
        header = "COD_FISCAL^DENUMIRE^COD_FISCAL_PARINTE^TIP_UNITATE^TIP_CONTRIB^LOCALITATE^STRADA^NR^DATA_INREGISTRARE^DATA_PRELUCRARE^FAX^SECTOR^TELEFON^JUDET^DATA_STARE^STARE^"
        pj = "11^FIRMA SRL^^Sediu^PJ^Alba Iulia^S^1^01.01.2000^11.06.2026 8:00:00^^^0258^ALBA^01.01.2001^RADIERE^"
        pf = "22^PERSOANA^^Sediu^PF^Alba Iulia^S^1^01.01.2000^11.06.2026 8:00:00^^^0258^ALBA^01.01.2001^INREGISTRAT^"
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.txt").write_bytes("\r\n".join(["﻿" + header, pj, pf, ""]).encode("utf-8"))
            found, latest, stats = ls.read_mf(d, {"11", "22"}, files=("a.txt",))
        self.assertEqual(set(found), {"11"})                                     # the PF row is not kept
        self.assertEqual(found["11"]["status_label"], "RADIERE")
        self.assertNotIn("0258", json.dumps(found))                              # no TELEFON in the result
        self.assertEqual((stats["pj"], stats["pf"], latest), (1, 1, "2026-06-11"))


class ApplyStatus(unittest.TestCase):
    def test_empty_status_is_not_active(self):
        recs = [record("S1", "1"), record("A2", "2", source="anaf"), record("S3", "3")]
        stats, review = c.apply_status(recs, [row("1", status="not_found", date="", county="", locality="")], {}, county_of, uat_of)
        self.assertEqual(recs[0]["status"], "not_found")
        self.assertNotIn("status", recs[1])                                       # an ANAF record stays empty
        self.assertNotIn("status", recs[2])                                       # no row: not checked, not `listat`
        self.assertEqual(c.STATUS_CODE.get(recs[2].get("status")), None)
        out = Path(tempfile.mkdtemp()) / "institutii.csv"
        c.write_csv(out, recs)
        got = {r["id"]: r for r in read_csv(out)}
        self.assertEqual((got["S3"]["status"], got["A2"]["status"]), ("", ""))
        self.assertEqual(got["S1"]["status"], "not_found")

    def test_status_conflict_with_seap(self):
        # CUI 4515077: RADIERE in 2017, and SEAP lists it up to 2026
        recs = [record("S4515077", "4515077")]
        stats, review = c.apply_status(recs, [row("4515077", status="radiat", date="2017-03-01")], {"4515077": 2026}, county_of, uat_of)
        self.assertNotIn("status", recs[0])                                       # the status stays empty
        self.assertEqual([(x["kind"], x["cif"], x["seap_last_seen"]) for x in review], [("seap_conflict", "4515077", 2026)])
        self.assertEqual(stats["conflict"], 1)
        # SEAP lists the CUI one year after the status year: no conflict
        recs = [record("S1", "1")]
        c.apply_status(recs, [row("1", status="fuzionat", date="2017-03-01")], {"1": 2018}, county_of, uat_of)
        self.assertEqual(recs[0]["status"], "fuzionat")
        # `in_lichidare` is not a defunct status: no conflict test
        recs = [record("S2", "2")]
        c.apply_status(recs, [row("2", status="in_lichidare", date="2017-03-01")], {"2": 2026}, county_of, uat_of)
        self.assertEqual(recs[0]["status"], "in_lichidare")

    def test_county_fill_only_when_empty(self):
        empty, has, other = record("S1", "1"), record("S2", "2", county="Salaj", uat="Orasul Zalau"), record("S3", "3")
        stats, review = c.apply_status([empty, has, other],
                                       [row("1"), row("2", county="ALBA"), row("3", county="MUNICIPIUL BUCUREŞTI", locality="Sectorul 3")],
                                       {}, county_of, uat_of)
        self.assertEqual((empty["county"], empty["county_source"], empty["uat"], empty["uat_source"]),
                         ("Alba", "mf", "Municipiul Alba Iulia", "mf"))
        self.assertEqual((has["county"], has["uat"]), ("Salaj", "Orasul Zalau"))  # never replaced
        self.assertNotIn("county_source", has)
        self.assertEqual([(x["kind"], x["id"]) for x in review], [("county_differs", "S2")])
        self.assertEqual(other["county"], "Bucuresti")                           # MUNICIPIUL BUCUREŞTI -> Bucuresti
        self.assertEqual(stats["county_filled"], 2)

    def test_unknown_county_is_listed_not_filled(self):
        rec = record("S1", "1")
        stats, review = c.apply_status([rec], [row("1", county="ATLANTIS")], {}, county_of, uat_of)
        self.assertEqual(rec["county"], "")
        self.assertEqual([x["kind"] for x in review], ["county_unknown"])

    def test_defunct_record_keeps_id(self):
        recs = [record("S9", "9", name="Corp radiat")]
        c.apply_status(recs, [row("9", status="radiat", date="2019-01-02")], {}, county_of, uat_of)
        tmp = Path(tempfile.mkdtemp())
        c.write_csv(tmp / "institutii.csv", recs)
        got = read_csv(tmp / "institutii.csv")
        self.assertEqual([(g["id"], g["cif"], g["status"], g["status_date"], g["status_source"]) for g in got],
                         [("S9", "9", "radiat", "2019-01-02", "mf")])
        # the explorer row keeps the record and marks it: st 1 = radiat, sd = status date
        c.write_explorer_data(tmp, [{**recs[0], "category": "Altele", "family": None, "address": None, "cif_tva": None}])
        rows = json.loads((tmp / "rows.json").read_text(encoding="utf-8"))
        self.assertEqual([(r["i"], r["f"], r["st"], r["sd"]) for r in rows], [("S9", "9", 1, "2019-01-02")])

    def test_explorer_codes(self):
        self.assertEqual(c.STATUS_CODE, {"radiat": 1, "fuzionat": 2, "in_lichidare": 3})
        tmp = Path(tempfile.mkdtemp())
        base = {"category": "Altele", "family": None, "address": None, "cif_tva": None}
        recs = [{**record("S1", "1"), **base, "status": "listat", "status_date": "2020-01-01"},
                {**record("S2", "2"), **base, "status": "in_lichidare", "status_date": "2021-02-03"},
                {**record("S3", "3"), **base, "county": "Alba", "county_source": "mf"}]
        c.write_explorer_data(tmp, recs)
        rows = {r["i"]: r for r in json.loads((tmp / "rows.json").read_text(encoding="utf-8"))}
        self.assertNotIn("st", rows["S1"])                                        # `listat` is never shown
        self.assertNotIn("sd", rows["S1"])
        self.assertEqual((rows["S2"]["st"], rows["S2"]["sd"]), (3, "2021-02-03"))
        self.assertEqual(rows["S3"]["us"], 2)


if __name__ == "__main__":
    unittest.main()
