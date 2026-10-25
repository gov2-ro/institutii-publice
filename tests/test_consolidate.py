"""Regression fixtures for scripts/consolidate.py: matching ambiguity and category rules.

Run from the repo root:  python3 -m unittest discover -s tests
The tests use tiny synthetic ANAF lists and need neither openpyxl nor the ignored source inputs.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import consolidate as c  # noqa: E402


def row(cif, name, county="Valcea", uat="Comuna Test"):
    return {"county": county, "cif": str(cif), "cif_tva": None, "name": name, "uat": uat, "address": None,
            "parent_cifs": []}


def linker(rows, fillers=400):
    """Fillers keep token IDF high (the linker ignores very common words when it looks for candidates).
    The 'Ilfov' filler makes 'ilfov' a known county name."""
    base = [row(900000 + k, f"Zzfiller{k} Qqfiller{k}", county="Ilfov" if k == 0 else "Alba", uat="Comuna F")
            for k in range(fillers)]
    return c.Linker(rows + base)


class ExactCanonical(unittest.TestCase):
    def test_exact_tie_is_not_merged_and_lists_candidates(self):
        L = linker([row(30, "Tribunalul Valcea", uat="Municipiul Ramnicu Valcea"),
                    row(10, "Tribunalul Valcea", uat="Municipiul Ramnicu Valcea")])
        tier, idx, score, cands = L.link("Valcea", "TRIBUNALUL VALCEA")
        self.assertEqual(tier, "ambiguous")
        self.assertEqual([x["cif"] for x in cands], ["10", "30"])      # sorted by -score, cif
        self.assertEqual({x["tier"] for x in cands}, {"exact"})

    def test_hint_resolves_a_tie_when_it_singles_out_one_row(self):
        L = linker([row(1, "Scoala Gimnaziala", uat="Comuna Alfa"), row(2, "Scoala Gimnaziala", uat="Orasul Horezu")])
        tier, idx, score, cands = L.link("Valcea", "Scoala Gimnaziala", "Horezu")
        self.assertEqual((tier, [L.anaf[i]["cif"] for i in idx], cands), ("exact", ["2"], []))

    def test_hint_that_does_not_distinguish_leaves_the_tie(self):
        L = linker([row(1, "Scoala Gimnaziala", uat="Comuna Alfa"), row(2, "Scoala Gimnaziala", uat="Orasul Beta")])
        for hint in (None, "Nowhere", "a"):                     # none, no match, or several matches
            tier, idx, score, cands = L.link("Valcea", "Scoala Gimnaziala", hint)
            self.assertEqual(tier, "ambiguous", hint)
            self.assertEqual([x["cif"] for x in cands], ["1", "2"])

    def test_generic_school_names_in_two_uats_stay_distinct(self):
        L = linker([row(1, "SCOALA GIMNAZIALA", uat="Comuna Alfa"), row(2, "SCOALA GIMNAZIALA", uat="Comuna Beta")])
        self.assertEqual(L.link("Valcea", "Scoala Gimnaziala")[0], "ambiguous")
        got = {h: L.anaf[L.link("Valcea", "Scoala Gimnaziala", h)[1][0]]["cif"] for h in ("Alfa", "Beta")}
        self.assertEqual(got, {"Alfa": "1", "Beta": "2"})

    def test_commune_wins_over_its_service_with_the_same_canonical_key(self):
        L = linker([row(1, "CONSILIUL LOCAL STOENESTI - SERVICIUL APA"), row(2, "COMUNA STOENESTI")])
        tier, idx, score, cands = L.link("Valcea", "Primaria Comunei Stoenesti")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("canonical", "2"))

    def test_genitive_municipality_name_is_a_local_authority(self):
        self.assertEqual(c.prep("MUNICIPIULUI MANGALIA"), ("uat", "uat:mangalia"))
        self.assertEqual(c.prep("MUNICIPIUL MANGALIA"), ("uat", "uat:mangalia"))
        self.assertEqual(c.prep("CONSILIUL JUDETEAN CONSTANTA")[1], "uat:judet:constanta")
        L = linker([row(1, "MUNICIPIUL MANGALIA", county="Constanta")])
        self.assertEqual(L.link("Constanta", "MUNICIPIULUI MANGALIA")[0], "canonical")


class UnitTier(unittest.TestCase):
    def test_same_county_singles_out_one_unit(self):
        L = linker([row(1, "Unitatea Militara 02512 Alfa", county="Bucuresti"),
                    row(2, "Unitatea Militara 02512 Beta", county="Constanta")])
        tier, idx, score, cands = L.link("Constanta", "UM 02512 M Constanta")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("unit", "2"))

    def test_units_in_one_county_are_ambiguous(self):
        L = linker([row(1, "Unitatea Militara 02512 Alfa", county="Bucuresti"),
                    row(2, "Unitatea Militara 02512 Beta", county="Bucuresti")])
        tier, idx, score, cands = L.link("Constanta", "UM 02512 M Constanta")
        self.assertEqual((tier, [x["cif"] for x in cands]), ("ambiguous", ["1", "2"]))


class Tokens(unittest.TestCase):
    def test_dsp_ilfov_is_not_dsp_bucuresti(self):
        rows = [row(4400956, "DIRECTIA DE SANATATE PUBLICA A MUNICIPIULUI BUCURESTI", county="Bucuresti"),
                row(11445640, "DIRECTIA DE SANATATE PUBLICA A JUDETULUI ILFOV", county="Bucuresti")]
        L = linker(rows)
        tier, idx, score, cands = L.link("Bucuresti", "Directia de Sanatate Publica Ilfov - Sector 1", "Sector 1")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("tokens", "11445640"))
        tier, idx, score, cands = L.link("Bucuresti", "Directia de Sanatate Publica a Municipiului Bucuresti")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("exact", "4400956"))

    def test_without_geographic_evidence_the_dsp_pair_stays_ambiguous(self):
        rows = [row(4400956, "DIRECTIA DE SANATATE PUBLICA A MUNICIPIULUI BUCURESTI", county="Bucuresti"),
                row(11445640, "DIRECTIA DE SANATATE PUBLICA A JUDETULUI ILFOV", county="Bucuresti")]
        tier, idx, score, cands = linker(rows).link("Bucuresti", "Directia de Sanatate Publica")
        self.assertEqual((tier, [x["cif"] for x in cands]), ("ambiguous", ["11445640", "4400956"]))

    def test_das_dorohoi_is_not_das_botosani(self):
        rows = [row(4392462, "DIRECTIA ASISTENTA SOCIALA", county="Botosani", uat="Municipiul Dorohoi"),
                row(15305089, "DIRECTIA DE ASISTENTA SOCIALA", county="Botosani", uat="Municipiul Botosani")]
        L = linker(rows)
        tier, idx, score, cands = L.link("Botosani", "Directia de Asistenta Sociala Botosani", "Botosani")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("tokens", "15305089"))
        tier, idx, score, cands = L.link("Botosani", "Directia de Asistenta Sociala Botosani")   # no hint
        self.assertEqual(tier, "ambiguous")
        self.assertEqual([x["cif"] for x in cands], ["15305089", "4392462"])      # equal scores: by CIF text

    def test_incompatible_number_does_not_shadow_an_eligible_row(self):
        rows = [row(1, "Scoala Gimnaziala Nr 2 Mihai Viteazul"), row(2, "Scoala Gimnaziala nr. 1 Mihai Viteazul")]
        L = linker(rows)
        tier, idx, score, cands = L.link("Valcea", "Scoala Gimnaziala Mihai Viteazul nr 1")
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("tokens", "2"))

    def test_other_number_alone_is_not_a_match(self):
        L = linker([row(1, "Scoala Gimnaziala Nr 2 Mihai Viteazul")])
        self.assertIsNone(L.link("Valcea", "Scoala Gimnaziala Mihai Viteazul nr 1")[0])

    def test_token_tie_lists_sorted_candidates_and_no_merge(self):
        rows = [row(7, "Liceul Teoretic Mihai Eminescu"), row(5, "Liceul Teoretic Eminescu Mihai")]
        tier, idx, score, cands = linker(rows).link("Valcea", "Eminescu Mihai Liceul Teoretic")
        self.assertEqual(tier, "ambiguous")
        self.assertEqual([(x["cif"], x["tier"]) for x in cands], [("5", "tokens"), ("7", "tokens")])

    def test_candidate_fields(self):
        one = [{"cif": "1", "tier": "weak", "score": 0.6}]
        two = one + [{"cif": "2", "tier": "weak", "score": 0.6}]
        self.assertEqual(c.candidate_fields(one), ("1", []))
        self.assertEqual(c.candidate_fields(two), (None, two))
        self.assertEqual(c.candidate_fields([]), (None, []))
        merged = c.union_candidates([two, [{"cif": "2", "tier": "tokens", "score": 0.9}]])
        self.assertEqual([(x["cif"], x["score"]) for x in merged], [("2", 0.9), ("1", 0.6)])


class Categories(unittest.TestCase):
    def test_agriculture_umbrella_does_not_make_culture(self):
        self.assertEqual(c.categorize("OPAQUE NAME", ["MINISTERUL AGRICULTURII SI DEZVOLTARII RURALE"]), c.AGRI)
        self.assertEqual(c.categorize("OPAQUE NAME", ["MINISTERUL CULTURII"]), c.CULT)

    def test_abbreviation_fragment_is_not_a_company(self):
        self.assertEqual(c.categorize("D S V S A ALBA LABORATOR SANITAR VETERINAR"), c.AGRI)

    def test_real_companies_stay_companies(self):
        for name in ("ELECTRICA S A", "CONPET SA", "X S.R.L.", "C N A I R S A SECTIA DRUMURI NATIONALE TARGU MURES",
                     "TELECOMUNICATII C F R SA", "COMPANIA NATIONALA DE ADMINISTRARE A INFRASTRUCTURII RUTIERE"):
            self.assertEqual(c.categorize(name), c.COMPANY, name)

    def test_mangalia_municipality_is_local_authority(self):
        self.assertEqual(c.categorize("MUNICIPIULUI MANGALIA"), c.LOCAL)


class Provenance(unittest.TestCase):
    def test_kibana_export_time(self):
        name = "Lens Visualization [2026-10-19T20_26_13.348+03_00] 3.csv"
        self.assertEqual(c.kibana_export_time(name), "2026-10-19T20:26:13.348+03:00")
        self.assertIsNone(c.kibana_export_time("other.csv"))


if __name__ == "__main__":
    unittest.main()
