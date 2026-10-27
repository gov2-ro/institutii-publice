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


def source_rec(id_, name, county="Alba", **extra):
    """A source-only record in the shape main() builds (only the fields merge_same_name and infer_sectors read)."""
    src = {"R": "roepas", "G": "registrul", "D": "declaratii"}[id_[0]]
    return {"id": id_, "name": name, "county": county, "uat": None, "cif": None, "category": c.OTHER,
            "sources": [src], "link": {}, "possible_duplicate_of": None, "_cands": [],
            **({"registrul_nums": [id_[1:]]} if src == "registrul" else {}),
            **({"declaratii_count": 7, "declaratii_group": None, "declaratii_by_county": None}
               if src == "declaratii" else {}), **extra}


class Sectors(unittest.TestCase):
    def test_labels_are_unified(self):
        want = "Sectorul 3 al Municipiului Bucuresti"
        for raw in ("Sector 3", "Sectorul 3", "SECTORUL 3 AL MUNICIPIULUI BUCURESTI", "sector3"):
            self.assertEqual(c.sector_label(raw), want, raw)
        for raw in ("Sector 7", "Comuna Test", None):
            self.assertEqual(c.sector_label(raw), raw)

    def test_sector_from_name(self):
        f = c.sector_in_name
        self.assertEqual(f("ADMINISTRATIA DOMENIULUI PUBLIC SECTOR 1"), "Sectorul 1 al Municipiului Bucuresti")
        self.assertEqual(f("Primaria Sectorului 6"), "Sectorul 6 al Municipiului Bucuresti")
        self.assertEqual(f("Directia X sect. 4"), "Sectorul 4 al Municipiului Bucuresti")
        self.assertEqual(f("Directia sector 2 si sector 2"), "Sectorul 2 al Municipiului Bucuresti")
        self.assertIsNone(f("Directia sector 1 si sector 2"))      # two sectors: no guess
        self.assertIsNone(f("Directia sector 7"))                  # not a Bucuresti sector
        self.assertIsNone(f("Directia Generala"))

    def test_infer_only_for_bucuresti_without_uat(self):
        recs = [source_rec("G1", "ADMINISTRATIA PIETELOR SECTOR 2", "Bucuresti"),
                source_rec("G2", "ADMINISTRATIA PIETELOR SECTOR 2", "Alba"),
                source_rec("G3", "ADMINISTRATIA PIETELOR SECTOR 1 SI SECTOR 2", "Bucuresti"),
                source_rec("G4", "ADMINISTRATIA PIETELOR SECTOR 3", "Bucuresti", uat="Sector 1")]
        stats = c.infer_sectors(recs)
        self.assertEqual([r["uat"] for r in recs], ["Sectorul 2 al Municipiului Bucuresti", None, None,
                                                    "Sectorul 1 al Municipiului Bucuresti"])
        self.assertEqual(recs[0]["uat_source"], "name")
        self.assertNotIn("uat_source", recs[3])
        self.assertEqual((stats["inferred"], stats["unified"], stats["ambiguous"]), (1, 1, 1))


class SameName(unittest.TestCase):
    def test_priority_union_and_provenance(self):
        recs = [source_rec("D9", "Judecatoria Filiasi"), source_rec("G5", "JUDECATORIA FILIASI"),
                source_rec("R2", "Judecatoria Filiasi", website="x.ro", sources=["roepas"])]
        stats = c.merge_same_name(recs)
        self.assertEqual([r["id"] for r in recs], ["R2"])
        r = recs[0]
        self.assertEqual(r["sources"], ["roepas", "registrul", "declaratii"])
        self.assertEqual(r["link"], {"registrul": "same_name", "declaratii": "same_name"})
        self.assertEqual((r["merged_ids"], r["registrul_nums"], r["declaratii_count"]), (["G5", "D9"], ["5"], 7))
        self.assertEqual(stats["ids"], 2)

    def test_candidates_union_and_single_multiple_rule(self):
        one = lambda cif: [{"cif": cif, "tier": "weak", "score": 0.6}]
        same = [source_rec("G5", "Judecatoria Filiasi", possible_duplicate_of="1", _cands=one("1")),
                source_rec("D9", "Judecatoria Filiasi", possible_duplicate_of="1", _cands=one("1"))]
        c.merge_same_name(same)
        self.assertEqual((same[0]["possible_duplicate_of"], "match_candidates" in same[0]), ("1", False))
        diff = [source_rec("G5", "Judecatoria Filiasi", possible_duplicate_of="1", _cands=one("1")),
                source_rec("D9", "Judecatoria Filiasi", possible_duplicate_of="2", _cands=one("2"))]
        c.merge_same_name(diff)
        self.assertIsNone(diff[0]["possible_duplicate_of"])
        self.assertEqual([x["cif"] for x in diff[0]["match_candidates"]], ["1", "2"])

    def test_stays_separate(self):
        cases = {
            "same source twice": [source_rec("G1", "Judecatoria Filiasi"), source_rec("G2", "Judecatoria Filiasi")],
            "other county": [source_rec("G1", "Judecatoria Filiasi"), source_rec("D1", "Judecatoria Filiasi", "Dolj")],
            "generic name": [source_rec("G1", "PRIMARIA"), source_rec("D1", "PRIMARIA")],
            "generic family head": [source_rec("G1", "SCOALA GIMNAZIALA"), source_rec("D1", "SCOALA GIMNAZIALA")],
            "village school": [source_rec("G1", "Scoala Gimnaziala Ion Creanga"),
                               source_rec("D1", "Scoala Gimnaziala Ion Creanga")],
            "different sectors": [source_rec("G1", "Directia Venituri - Sector 1", "Bucuresti"),
                                  source_rec("D1", "Directia Venituri - Sector 2", "Bucuresti")],
        }
        for label, recs in cases.items():
            n = len(recs)
            c.merge_same_name(recs)
            self.assertEqual(len(recs), n, label)
            self.assertTrue(all("merged_ids" not in r for r in recs), label)

    def test_anaf_records_are_never_touched(self):
        anaf = {**source_rec("G1", "Judecatoria Filiasi"), "id": "A1", "cif": "1", "sources": ["anaf"]}
        recs = [anaf, source_rec("D1", "Judecatoria Filiasi")]
        c.merge_same_name(recs)
        self.assertEqual(len(recs), 2)


class SectorAndNationwide(unittest.TestCase):

    def test_sector_suffix_matches_name_without_sector(self):
        recs = [source_rec("R1", "Banca Nationala - Sector 3", "Bucuresti"), source_rec("G1", "Banca Nationala", "Bucuresti")]
        c.merge_same_name(recs)
        self.assertEqual([(r["id"], r["merged_ids"]) for r in recs], [("R1", ["G1"])])

    def test_nationwide_needs_bucuresti_and_unique_name(self):
        recs = [source_rec("R1", "Registrul Auto Roman", "Bucuresti"), source_rec("G1", "Registrul Auto Roman", "Alba")]
        c.merge_same_name(recs, nationwide=True)
        self.assertEqual([(r["id"], r["merged_ids"]) for r in recs], [("R1", ["G1"])])
        recs = [source_rec("G1", "Biroul X", "Alba"), source_rec("D1", "Biroul X", "Dolj")]
        c.merge_same_name(recs, nationwide=True)
        self.assertEqual(len(recs), 2)

    def test_strip_sector_suffix_keeps_collisions(self):
        recs = [source_rec("R1", "Banca - Sector 3", "Bucuresti"), source_rec("R2", "Directia - Sector 1", "Bucuresti"),
                source_rec("R3", "Directia - Sector 2", "Bucuresti")]
        c.strip_sector_suffix(recs)
        self.assertEqual([r["name"] for r in recs], ["Banca", "Directia - Sector 1", "Directia - Sector 2"])
        self.assertEqual(recs[0]["aliases"], ["Banca - Sector 3"])

    def test_curated_merge_and_parent(self):
        anaf = {**source_rec("R9", "MINISTERUL X"), "id": "A1", "cif": "1", "sources": ["anaf"], "parents": []}
        gone, sub = source_rec("R1", "Ministerul Y"), source_rec("R2", "Directia Z")
        recs = [anaf, gone, sub]
        stats = c.apply_curated_merges(recs, [
            {"id": "R1", "kind": "merge", "target_id": "A1"}, {"id": "R2", "kind": "parent", "target_id": "A1"}])
        self.assertEqual([r["id"] for r in recs], ["A1", "R2"])
        self.assertEqual((anaf["merged_ids"], anaf["sources"], anaf["aliases"]), (["R1"], ["anaf", "roepas"], ["Ministerul Y"]))
        self.assertEqual(sub["parents"][0]["cif"], "1")
        self.assertEqual(dict(stats), {"merge": 1, "parent": 1})


class SameBody(unittest.TestCase):

    def test_link_set_and_bad_ids_stop(self):
        import tempfile, pathlib
        recs = [{"id": "A1"}, {"id": "A2"}]
        with tempfile.TemporaryDirectory() as d:
            ok = pathlib.Path(d) / "ok.csv"
            ok.write_text("id,same_body_as\nA2,A1\n", encoding="utf-8")
            self.assertEqual(c.apply_same_body(recs, ok), 1)
            self.assertEqual((recs[1]["same_body_as"], "same_body_as" in recs[0]), ("A1", False))
            bad = pathlib.Path(d) / "bad.csv"
            bad.write_text("id,same_body_as\nA2,A9\n", encoding="utf-8")
            with self.assertRaises(SystemExit):
                c.apply_same_body(recs, bad)


class PrefixTier(unittest.TestCase):
    ANAF = "AGENTIA NATIONALA A MEDICAMENTULUI SI A DISPOZITIVELOR MEDICALE DIN ROMANIA"

    def test_cut_off_ani_name_links_to_the_one_anaf_row(self):
        L = linker([row(1, self.ANAF)])
        tier, idx, score, cands = L.link("Valcea", "AGENTIA NATIONALA A MEDICAMENTULUI SI A DISPOZITIVELOR MEDIC",
                                         prefix=True)
        self.assertEqual((tier, L.anaf[idx[0]]["cif"]), ("prefix", "1"))
        self.assertNotEqual(L.link("Valcea", "AGENTIA NATIONALA A MEDICAMENTULUI SI A DISPOZITIVELOR MEDIC")[0],
                            "prefix")                              # only ANI asks for it

    def test_two_anaf_rows_with_a_mid_word_cut_are_ambiguous(self):
        L = linker([row(1, self.ANAF + " BUCURESTI"), row(2, self.ANAF + " FILIALA")])
        tier, idx, score, cands = L.link("Valcea", "AGENTIA NATIONALA A MEDICAMENTULUI SI A DISPOZITIVELOR MEDIC",
                                         prefix=True)
        self.assertEqual((tier, [x["cif"] for x in cands], {x["tier"] for x in cands}),
                         ("ambiguous", ["1", "2"], {"prefix"}))

    def test_generic_head_cut_on_a_word_boundary_does_not_link(self):
        # one row in this county, but the head continues into other names elsewhere: not a cut-off name
        L = linker([row(1, "Serviciul de Utilitati Publice Buftea"),
                    row(2, "Serviciul de Utilitati Publice Otopeni", county="Alba")])
        self.assertNotEqual(L.link("Valcea", "Serviciul de Utilitati Publice", prefix=True)[0], "prefix")

    def test_guards(self):
        L = linker([row(1, "Agentia Nationala Pentru Plati Unitare Centrala"),
                    row(2, "Scoala Gimnaziala Ion Creanga Satu Nou"), row(3, "Directia Generala Venituri Nr 12")])
        link = lambda n: L.link("Valcea", n, prefix=True)[0]
        self.assertNotEqual(link("Agentia Nationala"), "prefix")                       # fewer than 3 content tokens
        self.assertNotEqual(link("Scoala Gimnaziala Ion Creanga"), "prefix")           # local kind
        self.assertNotEqual(link("Directia Generala Venituri Nr 1"), "prefix")         # cut would split a number
        self.assertEqual(L.link("Alba", "Agentia Nationala Pentru Plati", prefix=True)[0], None)   # other county


class CuratedWebsites(unittest.TestCase):
    def rec(self, cif, url=None):
        return {"cif": cif, "website": url, "website_url": url}

    def test_fill_replace_same_and_provenance(self):
        recs = [self.rec("1"), self.rec("2", "https://old.ro"), self.rec("3", "https://same.ro"),
                self.rec("4", "https://keep.ro"), self.rec(None, "https://roepas-only.ro")]
        curated = {"1": "https://new.ro", "2": "https://fixed.ro", "3": "https://same.ro", "9": "https://x.ro"}
        stats, unknown = c.apply_curated_websites(recs, curated)
        self.assertEqual(dict(stats), {"filled": 1, "replaced": 1, "same": 1})
        self.assertEqual(unknown, ["9"])
        self.assertEqual([r["website_url"] for r in recs],
                         ["https://new.ro", "https://fixed.ro", "https://same.ro", "https://keep.ro",
                          "https://roepas-only.ro"])
        self.assertEqual([r.get("website_source") for r in recs],
                         ["curation", "curation", "curation", "roepas", "roepas"])

    def test_file_is_validated(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "websites.csv"
            self.assertEqual(c.load_curated_websites(path), {})            # no file, no curation
            path.write_text("cif,website,checked_at,evidence\n5,https://www.Ex.ro/,2026-10-26,title\n")
            root, c.ROOT = c.ROOT, Path(d)                                  # record_input wants a path under ROOT
            try:
                self.assertEqual(c.load_curated_websites(path), {"5": "https://www.ex.ro"})
                path.write_text("cif,website\n5,https://a.ro\n5,https://b.ro\n")
                with self.assertRaises(SystemExit):
                    c.load_curated_websites(path)
                path.write_text("cif,website\n6,not a site\n")
                with self.assertRaises(SystemExit):
                    c.load_curated_websites(path)
            finally:
                c.ROOT = root
                c.PROVENANCE.clear()


class Provenance(unittest.TestCase):
    def test_kibana_export_time(self):
        name = "Lens Visualization [2026-10-19T20_26_13.348+03_00] 3.csv"
        self.assertEqual(c.kibana_export_time(name), "2026-10-19T20:26:13.348+03:00")
        self.assertIsNone(c.kibana_export_time("other.csv"))


if __name__ == "__main__":
    unittest.main()
