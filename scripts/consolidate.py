#!/usr/bin/env python3
"""Consolidate the public-institution sources into one list (data/consolidated/).

Backbone is the ANAF list of public entities (CIF, UAT, address, parent authorities). Two other
sources are linked onto it by county + name:
  - ROePAS scrape (data/roepas/institutii.json): website, email, phone, coordinates, procedures
  - National Register of Public Institutions (docs/reference/*.csv, a damaged PDF extraction):
    register number

Link tiers: exact name / canonical (local authorities collapse to their locality name) / tokens
(IDF-weighted overlap >= 0.75, numbers must agree). Only those merge into an ANAF record. A weaker
candidate (overlap 0.5-0.75) is NOT merged: the source row stays its own record and points at the
possible ANAF match in `possible_duplicate_of`. Source rows with no candidate are kept as-is, so
the output is a union with provenance in `sources` and `link`.

Outputs (data/consolidated/): institutii.json, institutii.csv, and explorer-data.js, the compact
copy that explorer/index.html loads.

Usage: python3 scripts/consolidate.py
"""
import csv
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
ANAF_XLSX = ROOT / "docs/reference/Lista_EP_portal_01102026.xlsx"
REGISTRUL_CSV = ROOT / "docs/reference/Registrul-National-al-Institutiilor-Publice-din-Romania.pdf.csv"
ROEPAS_JSON = ROOT / "data/roepas/institutii.json"
OUT_DIR = ROOT / "data/consolidated"

# ---------------------------------------------------------------- text helpers


def squash(s):
    """Plain whitespace/hyphens: the Registrul export is full of nbsp and U+2010."""
    if s is None:
        return ""
    s = str(s).replace("\xa0", " ").replace("‐", "-").replace("‑", "-").replace("–", "-")
    return " ".join(s.split())


def fold(s):
    """Lowercase ascii alphanumerics separated by single spaces, for matching."""
    s = unicodedata.normalize("NFKD", squash(s)).encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", s).split())


# ---------------------------------------------------------------- loaders


def load_anaf():
    ws = openpyxl.load_workbook(ANAF_XLSX, read_only=True, data_only=True).worksheets[0]
    rows = []
    for r in list(ws.iter_rows(values_only=True))[1:]:
        v = [squash(x) or None for x in (list(r) + [None] * 10)[:10]]
        if not v[1]:
            continue
        rows.append({"county": v[0], "cif": v[1], "cif_tva": v[2], "name": v[3], "uat": v[4],
                     "address": v[5], "parent_cifs": [c for c in dict.fromkeys([v[6], v[8]]) if c]})
    return rows


REG_LINE = re.compile(r'^"?(\d{5})"?,"([^"]*)","?(.*)$')


def load_registrul():
    """Physical-line parser; the csv module merges neighbouring rows on the broken quotes."""
    recs = []
    for line in REGISTRUL_CSV.read_text(encoding="utf-8-sig").split("\n")[1:]:
        if not line.strip() or line.strip() == '""':
            continue
        m = REG_LINE.match(line)
        if m:
            recs.append([m.group(1), m.group(2), m.group(3)])
        elif recs:                                  # name wrapped onto the next line
            recs[-1][2] += " " + line
    out = []
    for num, county, name in recs:
        county, name = squash(county), squash(name)
        if name.endswith('"'):
            name = name[:-1].rstrip()
        name = re.sub(r"^[\s\-,.;:]+", "", name)             # stray "- " / ", " left by the PDF extraction
        # Bistrita-Nasaud block: county text is glued onto the name (or sits in the county cell)
        m = re.match(r"^(BISTRITA-NASAUD)\s*(.*)$", county) or (
            None if county else re.match(r"^(BISTRITA-NASAUD)\s+(.*)$", name))
        if m:
            county, name = m.group(1), (m.group(2) + " " + (name if county else "")).strip()
        out.append({"num": num, "county": county, "name": name})
    return out


TLDS = "ro|com|net|org|eu|info|biz|gov|edu|md|hu|de|it|fr|uk|us|tv|co|io|app|xyz|online|site|ong"
HOST_RE = re.compile(rf"^(?:https?://)?((?:[a-z0-9-]+\.)+(?:{TLDS}))(/\S*)?$", re.I)


def clean_website(raw):
    """ROePAS website field is free text: emails, names, '-', 'www.x y.ro', 'web:x ; e-mail:y'.
    Only the first token is trusted; ambiguous values give None rather than a guessed link."""
    tokens = re.split(r"[\s;,]+", (raw or "").strip())
    tok = re.sub(r"^(web|site):", "", tokens[0], flags=re.I)
    m = HOST_RE.match(tok)
    if not m:
        return None
    scheme = "http://" if tok.lower().startswith("http://") else "https://"
    return scheme + m.group(1).lower() + (m.group(2) or "").rstrip("/")


def load_roepas():
    rows = json.loads(ROEPAS_JSON.read_text(encoding="utf-8"))
    for r in rows:
        raw = r["website"]
        r["website_url"] = clean_website(raw)
        if raw and "@" in raw and not r["email"]:           # an address typed into the website box
            r["email"] = squash(raw)
    return rows


# ---------------------------------------------------------------- linking

UAT_RE = re.compile(
    r"^(?:primaria|primarie|consiliul local|consiliul judetean|comuna|orasul|oras|municipiul|municipiu|"
    r"sectorul|judetul)(?:\s+al)?(?:\s+(?:comunei|orasului|municipiului|sectorului|judetului|comuna|orasul|"
    r"municipiul))?\s+")
COUNTY_RE = re.compile(r"^(?:consiliul? judetean|judetul)\b")
ALIASES = [
    (r"\bscoala cu clasele? (?:i|1) ?(?:viii|8)\b", "scoala gimnaziala"),
    (r"\bscoala cu cls? (?:i|1) ?(?:viii|8)\b", "scoala gimnaziala"),
    (r"\bscoala generala\b", "scoala gimnaziala"),
    (r"\bscoala cu clasele (?:i|1) ?(?:iv|4)\b", "scoala primara"),
    (r"\bgrup(?:ul)? scolar\b", "liceul tehnologic"),          # pre-2012 name of the same school type
    (r"\bgradinita cu program (?:prelungit|normal|saptamanal)\b", "gradinita"),
    (r"\bcentrul? scolar (?:pentru|de) educatie incluziva\b", "centrul scolar educatie incluziva"),
]
STOP = set("de la al a cu si din in pe nr sc sa ra pentru comuna comunei orasul orasului municipiul "
           "municipiului judetean judetul judetului judeteana primaria".split())


def strip_suffix(name):
    """'Directia X Mures - Targu Mures' / '... - Sector 2' -> 'Directia X Mures'. Other suffixes with
    digits (U.M. 0319) are kept: those are distinct units."""
    parts = re.split(r"\s-\s", squash(name), maxsplit=1)
    if len(parts) == 2 and fold(parts[0]) and (
            not re.search(r"\d", parts[1]) or re.fullmatch(r"sector(ul)? ?\d", parts[1].strip().lower())):
        return parts[0]
    return squash(name)


def prep(name):
    """-> (kind, canonical). kind 'uat' = local authority, collapsed to its locality name."""
    base = re.sub(r"\(.*?\)", " ", squash(name))
    f = fold(base)
    if UAT_RE.match(f):
        loc = UAT_RE.sub("", fold(re.split(r"\s-\s", base, maxsplit=1)[0]), count=1)   # drop " - village" suffixes
        loc = re.sub(r" al municipiului bucuresti$", "", loc)
        # a county council and the municipality of the same name are different authorities
        return "uat", ("uat:judet:" if COUNTY_RE.match(f) else "uat:") + loc
    for pat, rep in ALIASES:
        f = re.sub(pat, rep, f)
    return "other", f


class Linker:
    """Link (county, name) to an ANAF row. link() -> (tier, [anaf indexes], score)."""

    def __init__(self, anaf):
        self.anaf = anaf
        self.county_tokens = {t for a in anaf for t in fold(a["county"]).split()}
        self.exact, self.canon = defaultdict(list), defaultdict(list)
        self.tokidx = defaultdict(lambda: defaultdict(set))
        df = Counter()
        for i, a in enumerate(anaf):
            a["_ck"] = fold(a["county"])
            a["_f"] = fold(a["name"])
            a["_kind"], a["_canon"] = prep(a["name"])
            a["_toks"] = self.tokens(a["_canon"])
            self.exact[(a["_ck"], a["_f"])].append(i)
            self.canon[(a["_ck"], a["_canon"])].append(i)
            df.update(a["_toks"])
            for t in a["_toks"]:
                self.tokidx[a["_ck"]][t].add(i)
        self.idf = {t: math.log(len(anaf) / (1 + n)) for t, n in df.items()}

    def tokens(self, canon):
        ts = {t for t in canon.replace("uat:", "").split() if t not in STOP and len(t) > 1 and not t.isdigit()}
        return (ts - self.county_tokens) or ts

    def score(self, t1, t2):
        w = lambda t: self.idf.get(t, 4.0)
        union = sum(w(t) for t in t1 | t2)
        return sum(w(t) for t in t1 & t2) / union if union else 0.0

    def link(self, county, name, hint=None):
        name = strip_suffix(name)
        ck, f = fold(county), fold(name)
        kind, canon = prep(name)
        for tier, idx in (("exact", self.exact.get((ck, f))), ("canonical", self.canon.get((ck, canon)))):
            if idx:
                if len(idx) > 1 and hint:           # same name on several CIFs: prefer the matching UAT
                    idx = sorted(idx, key=lambda i: not fold(self.anaf[i]["uat"]).endswith(fold(hint)))
                return tier, idx[:1], 1.0
        toks = self.tokens(canon)
        cand = set()
        for t in toks:
            if self.idf.get(t, 4.0) > 2.0:           # skip very common words when generating candidates
                cand |= self.tokidx[ck].get(t, set())
        best, best_i = 0.0, None
        for i in cand:
            a = self.anaf[i]
            if a["_kind"] != kind:
                continue
            s = self.score(toks, a["_toks"])
            if s > best:
                best, best_i = s, i
        if best_i is None:
            return None, [], 0.0
        digits_ok = set(re.findall(r"\d+", canon)) == set(re.findall(r"\d+", self.anaf[best_i]["_canon"]))
        if best >= 0.75 and digits_ok:
            return "tokens", [best_i], best
        if best >= 0.5:
            return "weak", [best_i], best
        return None, [], best


# ---------------------------------------------------------------- categories

LOCAL, EDU, HEALTH, SOCIAL = "Administrație locală", "Educație", "Sănătate", "Asistență socială și muncă"
ORDER, DEF, JUST = "Ordine publică și urgențe", "Apărare", "Justiție"
CULT, AGRI = "Cultură, sport și tineret", "Agricultură, mediu și păduri"
UTIL, FIN, TRANS = "Servicii publice locale și regii", "Finanțe publice", "Transport și infrastructură"
RES, CENT = "Cercetare", "Autorități centrale și deconcentrate"
ORG, OTHER = "Asociații și organizații profesionale", "Altele"

RULES = [  # first match wins; patterns run on fold()ed names
    (ORG, r"^(colegiul (medicilor|farmacistilor|dentistilor|veterinar)|ordinul|oamgmamr|uniunea|federatia|asociatia|"
          r"fundatia|camera (de comert|notarilor|auditorilor|consultantilor)|sindicat|patronat|cooperativa)\b"),
    (LOCAL, r"^(primaria|primarie|consiliul? local|consiliul? judetean|consiliul general|comuna|orasul|oras|"
            r"municipiul|sectorul|judetul|uat|unitatea administrativ)\b(?!.*\b(scoala|liceul|spital|spitalul|directia|serviciul|centrul|"
            r"clubul|biblioteca|gradinita|colegiul|casa|caminul|administratia|regia|politia)\b)"),
    (JUST, r"\b(judecatoria|tribunalul|curtea de apel|parchetul|penitenciar\w*|inalta curte|magistraturii|"
           r"executori|oficiul (de cadastru|registrului comertului)|cadastru|probatiune|expertize|reeducare|"
           r"detentie)\b"),
    (DEF, r"\b(unitatea militara|um \d+|u m \d+|garnizoana|batalionul|brigada|regimentul|apararii nationale|"
          r"academia (fortelor|tehnica militara|navala)|centrul militar|cercul militar|statul major|"
          r"fortele (terestre|aeriene|navale)|arhivele militare)\b"),
    (FIN, r"\b(finante|finantelor|trezoreria|administrare fiscala|anaf|garda financiara|curtea de conturi|"
          r"camera de conturi|autoritatea vamala|directia regionala vamala|vamal\w*|impozite si taxe|"
          r"venituri (buget|la bugetul)|buget local)\b"),
    (RES, r"\b(cercetare|statiunea de cercetare|institutul national de|institutul de (cercetare|inginerie))\b"),
    (HEALTH, r"\b(spital\w*|policlinica|dispensar\w*|sanatoriul|ambulanta|centrul (de sanatate|medical)|"
             r"sanatate publica|asigurari de sanatate|laborator\w*|medicina legala|farmacia|transfuzie|"
             r"institutul (de|clinic|oncologic|national de boli|national de sanatate)|crucea rosie|"
             r"cabinet\w*|medicina (familiei|scolara)|stomatolog\w*|asistenta medic\w*|medico sociala)\b"),
    (ORDER, r"\b(politi[ae]\w*|jandarm\w*|pompieri|situatii de urgenta|isu|politia locala|frontiera|"
            r"inspectoratul (judetean|general|de politie|pentru situatii)|pasapoarte|evidenta (a )?persoanelor|"
            r"serviciul public comunitar|garda de coasta|garda de mediu|garda nationala de mediu)\b"),
    (SOCIAL, r"\b(asistenta sociala|protectia (copilului|persoanelor|sociala)|dgaspc|centrul de (zi|plasament|"
             r"ingrijire|recuperare|asistenta|primire)|camin(ul)? (pentru|de batrani)|casa de copii|"
             r"casa (judeteana|nationala|teritoriala) de pensii|ocuparea fortei de munca|inspectia muncii|"
             r"inspectoratul teritorial de munca|plati si inspectie sociala|handicap\w*|dizabilit\w*|"
             r"varstnic\w*|pensionari|incluziune sociala|d g a s p c|reabilitare sociala|cresa|crese|"
             r"cantina de ajutor social|ajutor social|adapost|munca)\b"),
    (EDU, r"\b(scoala|scoli|liceul|liceu|colegiul|colegiu|gradinita|gradinite|universitatea|universitate|"
          r"academia|facultatea|seminarul|centrul scolar|centrul judetean de resurse|casa corpului didactic|"
          r"inspectoratul scolar|palatul copiilor|clubul copiilor|cluburile copiilor|camin scolar|"
          r"grup scolar|grupul scolar|conservatorul|politehnica|invatamant\w*|educatie|cantina scolara|"
          r"gimnaziul|bugetar scolar)\b"),
    (CULT, r"\b(biblioteca|muzeul|muzee|teatrul|filarmonica|opera|ansamblul|casa de cultura|centrul cultural|"
           r"camin cultural|caminul cultural|scoala populara|conservarea|patrimoniu|cultura|culte|"
           r"arhivele|arhiva|clubul sportiv|club sportiv|baza sportiva|stadion\w*|sala polivalenta|"
           r"complexul sportiv|sport|tineret|biserica|manastirea|parohia|cinema\w*|institutul cultural|"
           r"cultural\w*)\b"),
    (AGRI, r"\b(ocolul silvic|ocol silvic|directia silvica|romsilva|agricultur\w*|agricol\w*|consultanta agricola|"
           r"protectia mediului|mediului|garda de mediu|bazinala|apele romane|gospodarire a apelor|anif|apia|"
           r"plati si interventie|"
           r"imbunatatiri funciare|utilizatorilor de apa|parcul national|rezervatia|vanatoare|piscicol\w*|"
           r"sanitar veterinar\w*|veterinar\w*|fitosanitar\w*|zootehnie|silvic\w*|paduri\w*)\b"),
    (TRANS, r"\b(drumuri|drumurilor|cnair|autostrazi|cfr|calea ferata|aeroport\w*|administratia (portului|"
            r"canalelor|fluvial)|aviatia civila|autoritatea rutiera|registrul auto|iscir|metrorex|"
            r"transporturi|infrastructura rutiera|transport public|transport urban)\b"),
    (UTIL, r"\b(regia autonoma|regia|serviciul public (de|local)|serviciul (comunitar )?(de )?(apa|alimentare|"
           r"utilitati|gospodarire|administrare)|serviciu (de )?apa|alimentare cu apa|utilitati publice|gosloc|"
           r"gospodarie comunala|salubri\w*|termoficare|piete|agrement|s c|srl|gaz|trans|"
           r"administratia (dezvoltare|serviciilor|imobilelor)|"
           r"administratia (domeniului public|pietelor|strazilor|cimitirelor|bazelor sportive|patrimoniului)|"
           r"apa canal|energie|gaze|societatea|compania)\b"),
    (CENT, r"\b(ministerul|guvernul|secretariatul general|prefectura|institutia prefectului|presedintia|"
           r"administratia prezidentiala|serviciul roman de informatii|serviciul de telecomunicatii|comisariatul|"
           r"biroul|departamentul|inspectia|organismul intermediar|"
           r"parlamentul|senatul|camera deputatilor|agentia|autoritatea|oficiul|consiliul national|"
           r"consiliul concurentei|institutul national de statistica|directia (judeteana|regionala)|"
           r"casa nationala|inspectoratul|comisia|curtea constitutionala|academia romana)\b"),
]
RULES = [(label, re.compile(p)) for label, p in RULES]
ANCESTOR_HINTS = [
    (EDU, r"educatiei|cercetarii|invatamantului"), (HEALTH, r"sanatatii"), (DEF, r"apararii"),
    (ORDER, r"afacerilor interne"), (JUST, r"justitiei"), (CULT, r"culturii|tineretului|sportului"),
    (SOCIAL, r"muncii|solidaritatii|familiei"), (AGRI, r"agriculturii|mediului|apelor|padurilor"),
    (FIN, r"finantelor"), (TRANS, r"transporturilor|infrastructurii|lucrarilor publice"),
    (CENT, r"secretariatul general al guvernului|guvernul"),
]
ANCESTOR_HINTS = [(label, re.compile(p)) for label, p in ANCESTOR_HINTS]


def categorize(name, ancestor_names=()):
    f = fold(name)
    for label, pat in RULES:
        if pat.search(f):
            return label
    for anc in ancestor_names:                      # opaque name: inherit from a ministry-like parent
        af = fold(anc)
        for label, pat in ANCESTOR_HINTS:
            if pat.search(af):
                return label
    return OTHER


# ---------------------------------------------------------------- families
# A "family" bundles institutions of the same kind: "Casa Corpului Didactic" (one per county),
# "Scoala gimnaziala" (thousands, each with its own proper-noun name). Two ways to get one:
#   1. curated generic heads, for kinds whose members carry a proper noun in the name
#   2. network families: the name minus county/locality words is identical across many counties
FAMILY_HEADS = [  # (label, regex on fold()ed name, only for these categories or None); first match wins
    ("Comună", r"^comuna\b", LOCAL), ("Oraș", r"^(orasul|oras)\b", LOCAL), ("Municipiu", r"^municipiul\b", LOCAL),
    ("Sector", r"^sectorul\b", LOCAL), ("Județ", r"^judetul\b", LOCAL),
    ("Consiliu județean", r"^consiliul? judetean\b", LOCAL), ("Primărie", r"^(primaria|primarie)\b", LOCAL),
    ("Consiliu local", r"^consiliul? local\b", LOCAL), ("UAT", r"^(uat|unitatea administrativ)", LOCAL),
    ("Unitate militară", r"\b(unitatea militara|um \d+|u m \d+)\b", None),
    ("Școală gimnazială", r"^(scoala (gimnaziala|generala|cu clasele?|cu cls)|gimnaziul)\b", None),
    ("Școală de arte", r"^scoala (de arte|populara)", None),
    ("Școală profesională / specială / postliceală",
     r"^scoala (profesionala|postliceala|speciala|sanitara|de meserii|de ucenici)", None),
    ("Școală (alte tipuri)", r"^scoala\b", None),
    ("Liceu tehnologic", r"^(liceul tehnologic|grup(ul)? scolar)\b", None),
    ("Liceu teoretic", r"^liceul teoretic\b", None), ("Liceu (alte tipuri)", r"^liceul\b", None),
    ("Colegiu național", r"^colegiul national\b", None), ("Colegiu tehnic", r"^colegiul tehnic\b", None),
    ("Colegiu (alte tipuri)", r"^colegiul\b(?! (medicilor|farmacistilor|dentistilor|veterinar))", None),
    ("Grădiniță", r"^(gradinita|gradinite)\b", None),
    ("Club sportiv școlar", r"^club(ul)? sportiv scolar", None), ("Club sportiv", r"^(club(ul)? sportiv|sport club)", None),
    ("Centru școlar de educație incluzivă", r"^centrul scolar", None),
    ("Universitate", r"^universitatea\b", None), ("Seminar teologic", r"^seminarul\b", None),
    ("Spital județean", r"^spitalul (clinic )?judetean", None), ("Spital municipal", r"^spitalul municipal", None),
    ("Spital orășenesc", r"^spitalul orasenesc", None), ("Spital clinic", r"^spitalul clinic", None),
    ("Spital (alte tipuri)", r"^spital", None), ("Centru de sănătate", r"^centrul de sanatate", None),
    ("Bibliotecă", r"^biblioteca\b", None), ("Muzeu", r"^muzeul\b", None), ("Teatru", r"^teatrul\b", None),
    ("Casă de cultură", r"^casa de cultura", None), ("Cămin cultural", r"^caminul cultural", None),
    ("Centru cultural", r"^centrul cultural", None), ("Parohie", r"^parohia\b", None),
    ("Centru financiar", r"^centrul financiar", None), ("Serviciu public local", r"^serviciul public|^(consiliul? local\b.*?)?serviciul?\b.*\b(apa|canal\w*|salubri\w*|"
     r"utilitati|gospodarie|gospodarire)\b", None),
    ("Regie autonomă", r"^regia\b", None), ("Institut național", r"^institutul national", None),
    ("Stațiune de cercetare", r"^statiunea de cercetare", None),
]
FAMILY_HEADS = [(label, re.compile(p), cat) for label, p, cat in FAMILY_HEADS]
FAMILY_ADMIN = set("al a ai ale judetului municipiului orasului comunei sectorului".split())


def family_key(rec, county_tokens):
    """Name with county/locality words and numbers removed: 'Casa Corpului Didactic Bihor' -> 'casa corpului didactic'."""
    f = re.sub(r"\bnr\b ?\d*|\b\d+\b", " ", fold(re.sub(r"\(.*?\)", " ", rec["name"])))
    loc = re.sub(r"^(comuna|orasul|oras|municipiul|sectorul)\s+", "", fold(rec["uat"] or ""))
    skip = FAMILY_ADMIN | set(fold(rec["county"] or "").split()) | set(loc.split())
    return " ".join(t for t in f.split() if t not in skip)


CONTENT_STOP = set("de si pentru in cu la pe al a judetean judeteana judetului judetul".split())
ACRONYMS = {"anif": "ANIF", "apia": "APIA", "oamgmamr": "OAMGMAMR", "dgrfp": "DGRFP"}
# name-derived labels come from diacritic-free source names; restore the common ones for display
DIACRITICS = dict(p.split("=") for p in (
    "si=și in=în agricultura=agricultură actiuni=acțiuni adultilor=adulților administratia=administrația agentia=agenția agricola=agricolă "
    "ambulanta=ambulanță aparare=apărare aparatura=aparatură asigurari=asigurări asistenta=asistență "
    "caminul=căminul comert=comerț comertului=comerțului comunala=comunală comunitara=comunitară "
    "constructii=construcții consultanta=consultanță cooperatie=cooperație cresa=creșa cultura=cultură "
    "directia=direcția educationala=educațională evidenta=evidența excelenta=excelență "
    "farmacistilor=farmaciștilor filiala=filială financiara=financiară finantelor=finanțelor "
    "forestiera=forestieră fortei=forței frontiera=frontieră garzii=gărzii generala=generală "
    "gospodarie=gospodărie gospodarire=gospodărire imbunatatiri=îmbunătățiri imobiliara=imobiliară "
    "inspectie=inspecție institutia=instituția interventie=intervenție intreprinderi=întreprinderi "
    "judetean=județean judeteana=județeană judetul=județul langa=lângă legala=legală locala=locală "
    "maxima=maximă medicala=medicală munca=muncă national=național nationala=națională "
    "nationale=naționale operatiuni=operațiuni orasenesc=orășenesc plati=plăți politia=poliția "
    "politie=poliție politiei=poliției posta=poștă pregatirea=pregătirea prestatii=prestații "
    "profesionala=profesională protectia=protecția protectie=protecție publica=publică "
    "regionala=regională reprezentanta=reprezentanță reproductie=reproducție roman=român romana=română "
    "rurala=rurală rutiera=rutieră saditor=săditor sanatate=sănătate sanguina=sanguină sanitara=sanitară "
    "scolar=școlar sectia=secția semintelor=semințelor siguranta=siguranța silvica=silvică "
    "sociala=socială statistica=statistică teritoriala=teritorială traditionale=tradiționale "
    "utilitati=utilități varstnice=vârstnice veterinara=veterinară").split())


def pretty(key):
    words = [ACRONYMS.get(w) or DIACRITICS.get(w, w) for w in key.split()]
    text = " ".join(words)
    return text[0].upper() + text[1:]


def content(key):
    return tuple(t for t in key.split() if t not in CONTENT_STOP)


def merge_variants(groups):
    """Official names drift ('Directia pentru cultura' / '... cultura, culte si patrimoniul national'):
    fold a family into another whose content words are a prefix of its own. -> {key: label key}."""
    by_ct = defaultdict(list)
    for key in groups:
        by_ct[content(key)].append(key)
    root = {}
    for ct in sorted(by_ct, key=len):
        parent = next((ct[:n] for n in range(len(ct) - 1, 1, -1) if ct[:n] in by_ct), None)
        root[ct] = root[parent] if parent else ct
    clusters = defaultdict(list)
    for ct, keys in by_ct.items():
        clusters[root[ct]].extend(keys)
    label = {}
    for root_ct, keys in clusters.items():
        best = max(by_ct[root_ct], key=lambda k: len(groups[k]))   # the shortest name covers the whole cluster
        for k in keys:
            label[k] = best
    return label


def assign_families(records, min_members=5, min_counties=4):
    keys = {}
    for rec in records:
        f = fold(rec["name"])
        rec["family"] = None
        for label, pat, cat in FAMILY_HEADS:
            if (cat is None or rec["category"] == cat) and pat.search(f):
                rec["family"] = label
                break
        if rec["family"] is None:
            keys[rec["id"]] = family_key(rec, None)
    groups = defaultdict(list)
    for rec in records:
        if keys.get(rec["id"]):
            groups[keys[rec["id"]]].append(rec)
    groups = {k: v for k, v in groups.items()
              if len(v) >= min_members and len({m["county"] for m in v}) >= min_counties}
    label = merge_variants(groups)
    for key, members in groups.items():
        for m in members:
            m["family"] = pretty(label[key])


# ---------------------------------------------------------------- build

TIER_RANK = {"exact": 0, "canonical": 1, "tokens": 2}


def main():
    anaf, registrul, roepas = load_anaf(), load_registrul(), load_roepas()
    print(f"sources: anaf={len(anaf)} registrul={len(registrul)} roepas={len(roepas)}", file=sys.stderr)
    linker = Linker(anaf)
    county_display = {fold(a["county"]): a["county"] for a in anaf}
    county_of = lambda c: county_display.get(fold(c)) or squash(c).title()
    by_cif = {a["cif"]: a for a in anaf}
    # ROePAS says "Alba Iulia", ANAF says "Municipiul Alba Iulia": map the former onto the latter
    uat_label = {}
    for a in anaf:
        uat_label.setdefault((fold(a["county"]), UAT_RE.sub("", fold(a["uat"]), count=1)), a["uat"])
    uat_of = lambda county, city: uat_label.get((fold(county), fold(city)), city)

    links = {"roepas": defaultdict(list), "registrul": defaultdict(list)}
    standalone = {"roepas": [], "registrul": []}
    for src, rows in (("roepas", roepas), ("registrul", registrul)):
        for row in rows:
            tier, idx, score = linker.link(row["county"], row["name"], row.get("city"))
            if tier in TIER_RANK:
                links[src][idx[0]].append((tier, row))
            else:
                standalone[src].append((tier, idx, score, row))

    def best_roepas(i):
        cands = links["roepas"].get(i, [])
        # best tier first, then prefer one that has a website, then lowest id
        return sorted(cands, key=lambda t: (TIER_RANK[t[0]], not t[1]["website"], int(t[1]["id"])))

    records = []
    for i, a in enumerate(anaf):
        parents = [{"cif": c, "name": by_cif[c]["name"]} for c in a["parent_cifs"] if c in by_cif]
        rec = {
            "id": "A" + a["cif"], "name": a["name"], "county": a["county"], "uat": a["uat"],
            "address": a["address"], "cif": a["cif"], "cif_tva": a["cif_tva"], "parents": parents,
            "category": categorize(a["name"], [p["name"] for p in parents]),
            "sources": ["anaf"], "link": {}, "possible_duplicate_of": None,
        }
        roe = best_roepas(i)
        if roe:
            tier, r = roe[0]
            rec["sources"].append("roepas")
            rec["link"]["roepas"] = tier
            rec.update({"website": r["website"], "website_url": r["website_url"], "email": r["email"],
                        "phone": r["phone"], "fax": r["fax"], "lat": r["lat"], "lon": r["lon"],
                        "roepas_ids": [x[1]["id"] for x in roe], "roepas_url": r["detail_url"],
                        "procedures_count": r["procedures_count"],
                        "online_procedures_count": r["online_procedures_count"], "org_units": r["org_units"]})
        reg = links["registrul"].get(i, [])
        # names the other sources use for the same entity ("Primaria Comunei X" for "COMUNA X"), for search
        others = [r["name"] for _, r in roe] + [r["name"] for _, r in reg]
        rec["aliases"] = sorted({squash(n) for n in others if fold(n) != fold(a["name"])})
        if reg:
            rec["sources"].append("registrul")
            rec["link"]["registrul"] = sorted(reg, key=lambda t: TIER_RANK[t[0]])[0][0]
            rec["registrul_nums"] = sorted(r["num"] for _, r in reg)
        records.append(rec)

    def possible(idx):
        return anaf[idx[0]]["cif"] if idx else None

    for tier, idx, score, r in standalone["roepas"]:
        records.append({
            "id": "R" + r["id"], "name": r["name"], "county": county_of(r["county"]),
            "uat": uat_of(r["county"], r["city"]), "address": r["address"], "cif": None, "cif_tva": None, "parents": [],
            "category": categorize(r["name"]), "sources": ["roepas"], "link": {},
            "possible_duplicate_of": possible(idx) if tier == "weak" else None,
            "website": r["website"], "website_url": r["website_url"], "email": r["email"],
            "phone": r["phone"], "fax": r["fax"], "lat": r["lat"], "lon": r["lon"],
            "roepas_ids": [r["id"]], "roepas_url": r["detail_url"],
            "procedures_count": r["procedures_count"], "online_procedures_count": r["online_procedures_count"],
            "org_units": r["org_units"]})
    for tier, idx, score, r in standalone["registrul"]:
        records.append({
            "id": "G" + r["num"], "name": r["name"], "county": county_of(r["county"]), "uat": None,
            "address": None, "cif": None, "cif_tva": None, "parents": [],
            "category": categorize(r["name"]), "sources": ["registrul"], "link": {},
            "possible_duplicate_of": possible(idx) if tier == "weak" else None,
            "registrul_nums": [r["num"]]})

    assign_families(records)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "institutii.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    write_csv(OUT_DIR / "institutii.csv", records)
    write_explorer_data(OUT_DIR / "explorer-data.js", records)
    report(records, anaf, links, standalone)


CSV_COLS = ["id", "name", "category", "family", "county", "uat", "address", "cif", "cif_tva", "parent_cifs",
            "parent_names", "website", "website_url", "email", "phone", "fax", "lat", "lon", "sources",
            "link_roepas", "link_registrul", "possible_duplicate_of", "roepas_ids", "roepas_url",
            "registrul_nums", "procedures_count", "online_procedures_count", "org_units"]


def write_csv(path, records):
    flat = lambda v: " | ".join(map(str, v)) if isinstance(v, list) else v
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLS)
        w.writeheader()
        for r in records:
            row = {k: flat(r.get(k)) for k in CSV_COLS}
            row["parent_cifs"] = flat([p["cif"] for p in r["parents"]])
            row["parent_names"] = flat([p["name"] for p in r["parents"]])
            row["link_roepas"], row["link_registrul"] = r["link"].get("roepas"), r["link"].get("registrul")
            w.writerow(row)


SRC_BIT = {"anaf": 1, "roepas": 2, "registrul": 4}


def write_explorer_data(path, records):
    """Compact rows for the static explorer: short keys, empty values omitted, categories/counties by index."""
    counts = Counter(r["category"] for r in records)
    cats = sorted(counts, key=lambda c: (c == OTHER, -counts[c]))
    counties = sorted({r["county"] for r in records if r["county"]})
    ci, ki = {c: i for i, c in enumerate(cats)}, {c: i for i, c in enumerate(counties)}
    families = [f for f, _ in Counter(r["family"] for r in records if r["family"]).most_common()]
    fi = {f: i for i, f in enumerate(families)}
    rows = []
    for r in records:
        row = {"n": r["name"], "c": ci[r["category"]], "s": sum(SRC_BIT[x] for x in r["sources"])}
        optional = {
            "k": ki.get(r["county"]), "u": r["uat"], "a": r["address"], "f": r["cif"], "t": r["cif_tva"],
            "p": [p["cif"] for p in r["parents"]], "w": r.get("website_url"), "e": r.get("email"),
            "ph": r.get("phone"), "fx": r.get("fax"), "la": r.get("lat"), "lo": r.get("lon"),
            "ru": r.get("roepas_url"), "pc": r.get("procedures_count"), "po": r.get("online_procedures_count"),
            "ou": r.get("org_units"), "rn": r.get("registrul_nums"), "d": r["possible_duplicate_of"],
            "lr": r["link"].get("roepas"), "lg": r["link"].get("registrul"), "al": r.get("aliases"),
            "m": fi.get(r["family"]),
        }
        for k, v in optional.items():
            if v is None or v == "" or v == [] or (k in ("pc", "po") and not v):
                continue
            row[k] = v
        rows.append(row)
    data = {"categories": cats, "counties": counties, "families": families, "rows": rows}
    path.write_text("window.EXPLORER_DATA=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n",
                    encoding="utf-8")


def report(records, anaf, links, standalone):
    n = Counter(tuple(r["sources"]) for r in records)
    print(f"\nconsolidated records: {len(records)}", file=sys.stderr)
    for k, v in sorted(n.items(), key=lambda kv: -kv[1]):
        print(f"  {'+'.join(k):28s} {v}", file=sys.stderr)
    for src in ("roepas", "registrul"):
        linked = sum(len(v) for v in links[src].values())
        weak = sum(1 for t, *_ in standalone[src] if t == "weak")
        print(f"{src}: {linked} rows merged into ANAF, {weak} weak candidates kept separate, "
              f"{len(standalone[src]) - weak} with no candidate", file=sys.stderr)
    print("\ncategories:", file=sys.stderr)
    for k, v in Counter(r["category"] for r in records).most_common():
        print(f"  {k:40s} {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
