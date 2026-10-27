#!/usr/bin/env python3
# /// script
# dependencies = ["openpyxl"]
# ///
"""Consolidate the public-institution sources into one list (data/consolidated/).

Backbone is the ANAF list of public entities (CIF, UAT, address, parent authorities). Three other
sources are linked onto it by county + name:
  - ROePAS scrape (data/roepas/institutii.json): website, email, phone, coordinates, procedures
  - National Register of Public Institutions (docs/reference/*.csv, a damaged PDF extraction):
    register number
  - ANI integrity declarations (data/declaratii-integritate/, Kibana exports): number of declarations
    filed per institution, a rough proxy for its size, and names missing from ANAF (state-owned
    companies especially). Umbrella entries of the ANI form are left out, unless a specific name
    was typed after them.

Link tiers: exact name / canonical (local authorities collapse to their locality name) / unit (same
military unit number, anywhere) / tokens (IDF-weighted overlap >= 0.75, numbers must agree) / prefix (ANI
only: the name is a cut-off form of exactly one ANAF name). Only those merge into an ANAF record. A weaker
candidate (overlap 0.5-0.75) is NOT merged: the source row stays its own record and points at the
possible ANAF match in `possible_duplicate_of`. Source rows with no candidate are kept as-is, so
the output is a union with provenance in `sources` and `link`.

Ambiguity: when several eligible ANAF rows tie (same name, equal token score) and neither a locality
hint nor a county name in the source name singles one out, nothing merges; the source row stays its own
record and lists the tied rows in `match_candidates` ({cif, tier, score}, sorted by -score, cif).
`possible_duplicate_of` is kept for a single weak candidate only.

Source-only records (ROePAS, Registrul, ANI with no ANAF match) that share a name and county across
different sources are combined into one record (link `same_name`, absorbed ids in `merged_ids`). In Bucuresti,
a record with no UAT gets its sector from the name (`uat_source` = "name"); sector labels are unified.

Curated websites (curation/websites.csv, keyed by CIF) fill or replace the ROePAS website of an ANAF record;
`website_source` is "curation" or "roepas".

Outputs (data/consolidated/): institutii.json (`match_candidates` is omitted when empty), institutii.csv
(`match_candidate_cifs`, " | " joined), and metadata.json + rows.json, the compact copy that
explorer/index.html loads. metadata.json carries `dataset`: generation time plus path, size, SHA-256,
mtime and row count of every input file read (ANI exports also `exported_at`, and `capped` at 10,000 rows).

Usage: uv run scripts/consolidate.py   (or python3 with openpyxl installed)
"""
import csv
import datetime
import hashlib
import json
import math
import re
import sys
import unicodedata
from bisect import bisect_left
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANAF_XLSX = ROOT / "docs/reference/Lista_EP_portal_01102026.xlsx"
REGISTRUL_CSV = ROOT / "docs/reference/Registrul-National-al-Institutiilor-Publice-din-Romania.pdf.csv"
ROEPAS_JSON = ROOT / "data/roepas/institutii.json"
DECLARATII_DIR = ROOT / "data/declaratii-integritate"
DECLARATII_MERGED = DECLARATII_DIR / "declaratii.csv"
OUT_DIR = ROOT / "data/consolidated"
CURATED_WEBSITES = ROOT / "curation/websites.csv"
CURATED_MERGES = ROOT / "curation/merges.csv"
CURATED_ALIASES = ROOT / "curation/aliases.csv"
CURATED_SAME_BODY = ROOT / "curation/same_body.csv"

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

PROVENANCE = []         # one entry per input file read; written to metadata.json as `dataset.inputs`
KIBANA_TS = re.compile(r"\[(\d{4}-\d\d-\d\dT\d\d)_(\d\d)_(\d\d(?:\.\d+)?)([+-]\d\d)_(\d\d)\]")


def iso_utc(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).isoformat(timespec="seconds")


def record_input(source, path, rows, **extra):
    """Remember an input file for the `dataset` block: path, size, SHA-256, mtime, data-row count."""
    data = path.read_bytes()
    PROVENANCE.append({"source": source, "path": path.relative_to(ROOT).as_posix(), "bytes": len(data),
                       "sha256": hashlib.sha256(data).hexdigest(), "modified_at": iso_utc(path.stat().st_mtime),
                       "rows": rows, **extra})


def kibana_export_time(filename):
    """'Lens Visualization [2026-10-19T20_26_13.348+03_00] 3.csv' -> '2026-10-19T20:26:13.348+03:00' or None."""
    m = KIBANA_TS.search(filename)
    return f"{m.group(1)}:{m.group(2)}:{m.group(3)}{m.group(4)}:{m.group(5)}" if m else None



def load_anaf():
    import openpyxl                                 # lazy: the tests import this module without openpyxl
    ws = openpyxl.load_workbook(ANAF_XLSX, read_only=True, data_only=True).worksheets[0]
    rows = []
    for r in list(ws.iter_rows(values_only=True))[1:]:
        v = [squash(x) or None for x in (list(r) + [None] * 10)[:10]]
        if not v[1]:
            continue
        rows.append({"county": v[0], "cif": v[1], "cif_tva": v[2], "name": v[3], "uat": v[4],
                     "address": v[5], "parent_cifs": [c for c in dict.fromkeys([v[6], v[8]]) if c]})
    record_input("anaf", ANAF_XLSX, len(rows))
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
    record_input("registrul", REGISTRUL_CSV, len(out))
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
    record_input("roepas", ROEPAS_JSON, len(rows))
    return rows


def load_curated_websites(path=None):
    """Hand-checked websites keyed by CIF (curation/websites.csv: cif, website, checked_at, evidence).
    They fill or correct the ROePAS website of an ANAF record. A missing file means no curation."""
    path = path or CURATED_WEBSITES
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if (r.get("cif") or "").strip()]
    out = {}
    for r in rows:
        cif, url = r["cif"].strip(), clean_website(r["website"])
        if not url:
            raise SystemExit(f"{path}: CIF {cif}: not a website: {r['website']!r}")
        if cif in out:
            raise SystemExit(f"{path}: CIF {cif} is listed twice")
        out[cif] = url
    record_input("curation", path, len(rows))
    return out


def apply_curated_websites(records, curated):
    """A curated website replaces the ROePAS one of the record with that CIF. `website_source` says where
    each website comes from. Returns the counts and the curated CIFs that match no record."""
    stats, used = Counter(), set()
    for rec in records:
        if rec.get("website_url"):
            rec["website_source"] = "roepas"
        url = curated.get(rec["cif"]) if rec["cif"] else None
        if not url:
            continue
        used.add(rec["cif"])
        prev = rec.get("website_url")
        stats["same" if prev == url else "replaced" if prev else "filled"] += 1
        rec.update({"website": url, "website_url": url, "website_source": "curation"})
    return stats, sorted(set(curated) - used)


def load_curated_merges(path=None):
    """Hand-checked record links (curation/merges.csv: id, kind, target_id, checked_at, evidence).
    kind `merge`: record `id` is the same body as `target_id` and is absorbed into it.
    kind `parent`: record `id` is a sub-unit of ANAF record `target_id`.
    kind `rename`: record `id` gets the display name `new_name`; the old name goes to `aliases`.
    A missing file means no curation."""
    path = path or CURATED_MERGES
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        rows = [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(fh) if (r.get("id") or "").strip()]
    seen = set()
    for r in rows:
        if r["kind"] not in ("merge", "parent", "rename") or not (r["new_name"] if r["kind"] == "rename" else r["target_id"]):
            raise SystemExit(f"{path}: {r['id']}: kind must be merge or parent (with a target_id) or rename (with a new_name)")
        if r["id"] in seen:
            raise SystemExit(f"{path}: id {r['id']} is listed twice")
        seen.add(r["id"])
    return rows


def absorb(keep, rec, how):
    """Fold the source data of `rec` into `keep`. The id of `rec` goes to `keep["merged_ids"]`."""
    for src in rec["sources"]:
        if src not in keep["sources"]:
            keep["sources"].append(src)
        keep["link"].setdefault(src, how)
    if "roepas" in rec["sources"]:
        for k in ("website", "website_url", "email", "phone", "fax", "lat", "lon", "roepas_url",
                  "procedures_count", "online_procedures_count", "org_units"):
            if keep.get(k) in (None, "", []):
                keep[k] = rec.get(k)
        keep["roepas_ids"] = sorted({*keep.get("roepas_ids", []), *rec.get("roepas_ids", [])})
    if "registrul" in rec["sources"]:
        keep["registrul_nums"] = sorted({*keep.get("registrul_nums", []), *rec.get("registrul_nums", [])})
    if "declaratii" in rec["sources"]:
        for k in ("declaratii_count", "declaratii_group", "declaratii_by_county"):
            if keep.get(k) in (None, "", []):
                keep[k] = rec.get(k)
    if keep["category"] == OTHER and rec["category"] != OTHER:
        keep["category"] = rec["category"]
    if fold(rec["name"]) != fold(keep["name"]):
        keep["aliases"] = sorted({*keep.get("aliases", []), squash(rec["name"])})
    keep["sources"].sort(key=SRC_ORDER.index)
    keep["merged_ids"] = list(dict.fromkeys([*keep.get("merged_ids", []), rec["id"], *rec.get("merged_ids", [])]))


def apply_curated_merges(records, curated):
    """Apply curation/merges.csv. Stops on an unknown id. -> stats."""
    by_id = {r["id"]: r for r in records}
    stats, drop = Counter(), set()
    for c in sorted(curated, key=lambda c: c["kind"] == "rename"):         # renames last: merged records may be renamed
        rec, target = by_id.get(c["id"]), by_id.get(c["target_id"])
        if c["kind"] == "rename":
            if not rec:
                raise SystemExit(f"{CURATED_MERGES}: {c['id']} matches no record")
            rec["aliases"] = sorted({*rec.get("aliases", []), squash(rec["name"])})
            rec["name"] = squash(c["new_name"])
            stats["rename"] += 1
            continue
        if not rec or not target:
            raise SystemExit(f"{CURATED_MERGES}: {c['id']} or {c['target_id']} matches no record")
        if c["kind"] == "merge":
            absorb(target, rec, "curation")
            drop.add(rec["id"])
        else:
            if not target["cif"]:
                raise SystemExit(f"{CURATED_MERGES}: parent {c['target_id']} has no CIF")
            rec["parents"] = [{"cif": target["cif"], "name": target["name"]}]
            rec["possible_duplicate_of"] = None
            rec.pop("match_candidates", None)
        stats[c["kind"]] += 1
    records[:] = [r for r in records if r["id"] not in drop]
    return stats


def apply_same_body(records, path=None):
    """curation/same_body.csv (id, same_body_as, name, decided_at, evidence): two records, two tax IDs, one body
    (a court with a second CIF). Neither record is merged. `same_body_as` is set on `id`; the partner is the
    canonical record. The build stops on an unknown id or a chain. -> number of links."""
    path = path or CURATED_SAME_BODY
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as fh:
        links = {r["id"]: r["same_body_as"] for r in csv.DictReader(fh) if (r.get("id") or "").strip()}
    by_id = {r["id"]: r for r in records}
    bad = sorted(i for i, t in links.items() if i not in by_id or t not in by_id or t in links)
    if bad:
        raise SystemExit(f"{path}: unknown id or chained link: {bad}")
    for i, t in links.items():
        by_id[i]["same_body_as"] = t
    return len(links)


def check_aliases(records, path=None):
    """curation/aliases.csv (institution_id, alias, kind, basis, status) is a master for other projects.
    Every institution_id must be a record id of this build, or the build stops: an id that a merge absorbed
    must be replaced by its survivor (see `merged_ids`)."""
    path = path or CURATED_ALIASES
    if not path.exists():
        return
    ids = {r["id"] for r in records}
    with path.open(encoding="utf-8", newline="") as fh:
        missing = sorted({r["institution_id"] for r in csv.DictReader(fh)} - ids)
    if missing:
        raise SystemExit(f"{path}: ids match no record: {missing}")


SECTOR_SUFFIX_RE = re.compile(r"\s*-\s*sector(?:ul)?\s*\d$", re.I)


def strip_sector_suffix(records):
    """ROePAS adds " - Sector N" to Bucuresti names. Drop it from the display name of a source-only record,
    unless another record would then share its county and name (two sector bodies). The old name stays
    in `aliases`. -> number of names changed."""
    key = lambda r, name: (fold(r["county"]), fold(name))
    stripped = {r["id"]: SECTOR_SUFFIX_RE.sub("", squash(r["name"])) for r in records
                if not r["cif"] and SECTOR_SUFFIX_RE.search(squash(r["name"]))}
    taken = Counter(key(r, stripped.get(r["id"], r["name"])) for r in records)
    n = 0
    for r in records:
        new = stripped.get(r["id"])
        if new and fold(new) and taken[key(r, new)] == 1:
            r["aliases"] = sorted({*r.get("aliases", []), squash(r["name"])})
            r["name"] = new
            n += 1
    return n


def load_declaratii():
    """ANI 'Declaratii integritate' Kibana exports, one per group of counties: 'NAME|COUNTY' (the
    institutie_id.keyword value) and the number of declarations filed under it. The exports are
    capped at the top 10,000 values: a file with 10,000 rows has lost its rarest names (warned about).
    Exports may overlap (a county group re-exported in parts): a value seen in several files is
    counted once. Some names carry a dropdown code ("323 0 PRIMARIA"); it is dropped and the counts
    are added up. Writes the merged list to DECLARATII_MERGED."""
    raw = {}
    for path in sorted(DECLARATII_DIR.glob("Lens Visualization*.csv")):
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.reader(fh))[1:]
        capped = len(rows) >= 10000
        record_input("declaratii", path, len(rows), exported_at=kibana_export_time(path.name),
                     **({"capped": True} if capped else {}))
        if capped:
            print(f"warning: {path.name} hit the 10,000-value cap, its rarest names are missing", file=sys.stderr)
        for key, count in rows:
            raw[key] = max(raw.get(key, 0), int(count.replace(",", "")))
    totals = Counter()
    for key, count in raw.items():
        name, _, county = key.rpartition("|")
        name = re.sub(r"^\d+ 0\b", "", squash(name)).strip()
        totals[(name, squash(county))] += count
    rows = [{"name": n, "county": c, "count": v} for (n, c), v in sorted(totals.items(), key=lambda kv: -kv[1])]
    with DECLARATII_MERGED.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "county", "count"])
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- linking

UAT_RE = re.compile(
    r"^(?:primaria|primarie|consiliul local|consiliul judetean|comuna|orasul|oras|municipiul|municipiu|"
    r"sectorul|judetul|municipiului|comunei|orasului)(?:\s+al)?(?:\s+(?:comunei|orasului|municipiului|sectorului|judetului|comuna|orasul|"
    r"municipiul))?\s+")
SECTOR_LABEL = "Sectorul {} al Municipiului Bucuresti"
SECTOR_UAT_RE = re.compile(r"^sector(?:ul)? ?([1-6])(?: al municipiului bucuresti)?$")
SECTOR_NAME_RE = re.compile(r"\bsect(?:or|orul|orului)?\.? ?([1-9])\b")


def sector_label(uat):
    """'Sector 3' / 'Sectorul 3' -> 'Sectorul 3 al Municipiului Bucuresti'; any other value is returned as is."""
    m = SECTOR_UAT_RE.match(fold(uat or ""))
    return SECTOR_LABEL.format(m.group(1)) if m else uat


def sector_in_name(name):
    """The one sector (1-6) that a name states, as a UAT label; None for none, two different, or an invalid one."""
    found = set(SECTOR_NAME_RE.findall(fold(name)))
    return SECTOR_LABEL.format(found.pop()) if len(found) == 1 and next(iter(found), "1") in "123456" else None


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


UNIT_RE = re.compile(r"\b(?:unitatea militara|u ?m)\s*(?:nr\s*)?(\d{3,5})\b")


TIE_EPS = 1e-9          # token scores closer than this are equal: float sums must not decide a match


class Linker:
    """Link (county, name) to an ANAF row.

    link() -> (tier, [anaf indexes], score, candidates). Tiers that merge: exact, canonical, unit, tokens.
    `weak` is a possible duplicate (not merged). `ambiguous` means several eligible rows tie and nothing
    singles one out (no merge). `candidates` lists {"cif", "tier", "score"} of every tied eligible row
    (and of a single weak row), sorted by -score, cif. A locality `hint` breaks a tie only when exactly
    one tied row's UAT ends with it. In the canonical tier a second tie-break applies: `prep` collapses
    "Consiliul Local X - Serviciul apa" onto the locality of "Comuna X", so the candidate whose name has the
    same " - suffix" structure as the source name (plain or with suffix) wins when it is the only one. A county name in the source name that differs from every county
    name in a candidate's name makes that candidate ineligible (DSP Ilfov is not DSP Bucuresti)."""

    def __init__(self, anaf):
        self.anaf = anaf
        self.county_tokens = {t for a in anaf for t in fold(a["county"]).split()}
        names = sorted({fold(a["county"]) for a in anaf if fold(a["county"])}, key=lambda c: (-len(c), c))
        self.county_re = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b") if names else None
        self.exact, self.canon = defaultdict(list), defaultdict(list)
        self.tokidx = defaultdict(lambda: defaultdict(set))
        df = Counter()
        for i, a in enumerate(anaf):
            a["_ck"] = fold(a["county"])
            a["_f"] = fold(a["name"])
            a["_kind"], a["_canon"] = prep(a["name"])
            a["_toks"] = self.tokens(a["_canon"])
            a["_nums"] = set(re.findall(r"\d+", a["_canon"]))
            a["_geo"] = self.geo(a["_f"])
            a["_plain"] = " - " not in squash(a["name"])
            self.exact[(a["_ck"], a["_f"])].append(i)
            self.canon[(a["_ck"], a["_canon"])].append(i)
            df.update(a["_toks"])
            for t in a["_toks"]:
                self.tokidx[a["_ck"]][t].add(i)
        self.idf = {t: math.log(len(anaf) / (1 + n)) for t, n in df.items()}
        self.units = defaultdict(list)              # military unit numbers are unique nationwide
        for i, a in enumerate(anaf):
            m = UNIT_RE.search(a["_f"])
            if m:
                self.units[m.group(1).zfill(5)].append(i)
        self.sorted_f = defaultdict(list)           # per county: sorted (folded name, index), for the prefix tier
        for i, a in enumerate(anaf):
            self.sorted_f[a["_ck"]].append((a["_f"], i))
        for lst in self.sorted_f.values():
            lst.sort()
        self.all_f = sorted(a["_f"] for a in anaf)  # nationwide, to tell a generic head from a cut-off name
        self.nat_exact, self.nat_canon = defaultdict(list), defaultdict(list)
        for i, a in enumerate(anaf):
            self.nat_exact[a["_f"]].append(i)
            self.nat_canon[a["_canon"]].append(i)

    def geo(self, folded):
        """The county names written in a folded name (frozenset)."""
        return frozenset(self.county_re.findall(folded)) if self.county_re else frozenset()

    def tokens(self, canon):
        ts = {t for t in canon.replace("uat:", "").split() if t not in STOP and len(t) > 1 and not t.isdigit()}
        return (ts - self.county_tokens) or ts

    def score(self, t1, t2):
        w = lambda t: self.idf.get(t, 4.0)
        union = sum(w(t) for t in sorted(t1 | t2))   # sorted: float sums must not depend on the hash seed
        return sum(w(t) for t in sorted(t1 & t2)) / union if union else 0.0

    def by_hint(self, idx, hint):
        """The one row of `idx` whose UAT ends with the locality hint, or None when none or several do."""
        h = fold(hint)
        if not h:
            return None
        hit = [i for i in idx if fold(self.anaf[i]["uat"]).endswith(h)]
        return hit[0] if len(hit) == 1 else None

    def cands(self, scored, tier):
        """[(index, score)] -> sorted candidate dicts."""
        out = [{"cif": self.anaf[i]["cif"], "tier": tier, "score": round(s, 4)} for i, s in scored]
        return sorted(out, key=lambda c: (-c["score"], c["cif"]))

    def prefix_rows(self, ck, f, kind, src_geo):
        """Eligible ANAF rows of the county whose folded name continues the folded source name `f` (a cut-off
        form, ANI cut names at 60 characters). Needs 3+ content tokens, the same numbers, and a cut that does not
        split a number (nr 1 / nr 12)."""
        if kind != "other" or DECL_LOCAL_KIND.search(f) or len([t for t in f.split() if t not in STOP and len(t) > 1
                                                                 and not t.isdigit()]) < 3:
            return []
        nums, lst, out = set(re.findall(r"\d+", f)), self.sorted_f.get(ck, []), []
        k = bisect_left(lst, (f, -1))
        while k < len(lst) and lst[k][0].startswith(f):
            af, i = lst[k]
            a, k = self.anaf[i], k + 1
            if len(af) == len(f) or a["_kind"] != "other" or set(re.findall(r"\d+", af)) != nums:
                continue
            if f[-1].isdigit() and af[len(f)].isdigit():
                continue
            if src_geo and a["_geo"] and src_geo.isdisjoint(a["_geo"]):
                continue
            # a cut on a word boundary may be a generic head ("SERVICIUL DE UTILITATI PUBLICE" -> "... BUFTEA"):
            # accept it only when one ANAF name in the whole country continues it. A mid-word cut is a truncation.
            if af[len(f)] == " " and self.nationwide_prefix(f + " ") > 1:
                continue
            out.append(i)
        return out

    def nationwide_prefix(self, p):
        k, n = bisect_left(self.all_f, p), 0
        while k + n < len(self.all_f) and self.all_f[k + n].startswith(p) and n < 2:
            n += 1
        return n

    def link(self, county, name, hint=None, prefix=False):
        src_geo = self.geo(fold(name))               # before strip_suffix drops "- Judetul Ilfov"
        name = strip_suffix(name)
        ck, f = fold(county), fold(name)
        kind, canon = prep(name)
        for tier, idx in (("exact", self.exact.get((ck, f))), ("canonical", self.canon.get((ck, canon)))):
            if idx:
                pick = idx[0] if len(idx) == 1 else self.by_hint(idx, hint)
                if pick is None and tier == "canonical":
                    same = [i for i in idx if self.anaf[i]["_plain"] == (" - " not in name)]
                    pick = same[0] if len(same) == 1 else None
                if pick is not None:
                    return tier, [pick], 1.0, []
                return "ambiguous", sorted(idx), 1.0, self.cands([(i, 1.0) for i in idx], tier)
        m = UNIT_RE.search(f)
        if m and self.units.get(m.group(1).zfill(5)):
            idx = self.units[m.group(1).zfill(5)]
            same = [i for i in idx if self.anaf[i]["_ck"] == ck]
            pool = same if len(idx) > 1 and same else idx
            pick = pool[0] if len(pool) == 1 else self.by_hint(pool, hint)
            if pick is not None:
                return "unit", [pick], 1.0, []
            return "ambiguous", sorted(pool), 1.0, self.cands([(i, 1.0) for i in pool], "unit")
        toks = self.tokens(canon)
        nums = set(re.findall(r"\d+", canon))
        cand = set()
        for t in toks:
            if self.idf.get(t, 4.0) > 2.0:           # skip very common words when generating candidates
                cand |= self.tokidx[ck].get(t, set())
        strong, weak = [], []
        for i in sorted(cand):                       # eligibility first, then the best of the eligible rows
            a = self.anaf[i]
            if a["_kind"] != kind:
                continue
            if src_geo and a["_geo"] and src_geo.isdisjoint(a["_geo"]):
                continue                             # names another county: "DSP Ilfov" is not "DSP Bucuresti"
            if nums and a["_nums"] and nums != a["_nums"]:
                continue                             # "Scoala nr 1" is not "Scoala nr 2"
            s = self.score(toks, a["_toks"])
            if s >= 0.75 and nums == a["_nums"]:
                strong.append((i, s))
            elif s >= 0.5:
                weak.append((i, s))
        for pool, tier in ((strong, "tokens"), (weak, "weak")):
            if tier == "weak" and prefix:               # a cut-off name beats a weak overlap
                rows = self.prefix_rows(ck, f, kind, src_geo)
                if len(rows) == 1:
                    return "prefix", rows, 1.0, []
                if rows:
                    return "ambiguous", rows, 1.0, self.cands([(i, 1.0) for i in rows], "prefix")
            if not pool:
                continue
            best = max(s for _, s in pool)
            tied = [(i, s) for i, s in pool if best - s <= TIE_EPS]
            pick = tied[0][0] if len(tied) == 1 else self.by_hint([i for i, _ in tied], hint)
            if pick is not None:
                s = dict(tied)[pick]
                return tier, [pick], s, ([] if tier == "tokens" else self.cands([(pick, s)], "weak"))
            return ("ambiguous" if tier == "tokens" else "weak"), sorted(i for i, _ in tied), best, \
                self.cands(tied, tier)
        return None, [], 0.0, []

    def anywhere(self, name):
        """The one ANAF row with this exact/canonical name in any county, or None."""
        for index, key in ((self.nat_exact, fold(name)), (self.nat_canon, prep(name)[1])):
            if len(index.get(key, [])) == 1:
                return index[key][0]
        return None


# ANI's institution field comes from a form dropdown: besides real institutions it has umbrella entries
# ("PRIMARIA", "ALTE INSTITUTII DIN SUBORDINEA ...", "... AUTORITATI SUBORDONATE") pooling many employers
# of a county. Those are counted in the report but are not institutions.
DECL_AGGREGATE = re.compile(
    r"^(alte institutii|institutii publice|autoritati publice|companii nationale|societati|unitati militare|"
    r"instante|procurori|consilii|birou(l|ri) electoral|ministerul public parchete|regii|autoritati|federatii|"
    r"sindicate)\b"
    r"|^[\d ]*$"
    r"|\b(autoritati subordonate|aparat central|institutiile prefectului)\b"
    r"|^(primaria|primarii|primarie|consiliul local|judecatoria|judecatorie|scoala gimnaziala|politia romana|jandarmeria romana|"
    r"parchetul de pe langa (judecatoria|judecatorii|tribunale)|"
    r"consiliul superior al magistraturii (judecatorii|tribunale))$")
DECL_SPREAD = 10        # a name filed under this many counties is a dropdown label (see link_declaratii) or umbrella
DECL_MIN_COUNT = 2      # an unlinked name needs this many declarations to become a record (singletons are mostly typos)
DECL_ABBREV = [(re.compile(p), r) for p, r in (
    (r"\btg\b", "targu"), (r"\brm\b", "ramnicu"), (r"\bmun\b", "municipiul"), (r"\bjud\b", "judetul"),
    (r"\bu ?m\b", "unitatea militara"), (r"\bmutat din judetul \d+$", ""), (r"\bcod caen( \d+)*", ""))]


DECL_LOCAL_KIND = re.compile(
    r"^(scoala|gradinita|liceul|colegiul|grup scolar|club|clubul|biblioteca|caminul|casa de cultura|spital\w*|"
    r"centrul|muzeul|teatrul|politia locala|serviciul public|administratia (strazilor|domeniului|pietelor)|"
    r"directia (de|pentru) (asistenta|evidenta)|directia de sanatate publica|parohia)\b")


def umbrella_labels(rows):
    """The umbrella entries as filed bare, i.e. the ones seen under DECL_SPREAD+ counties, longest first.
    A widespread entry that is itself label + institution ("ALTE INSTITUTII DIN SUBORDINEA MINISTERULUI
    AGRICULTURII ... AGENTIA DE PLATI ...", one per county) is not a label, and neither is a name the
    old form cut at 60 characters ("... MINISTERULUI AGRICULTURII SI"), which would split mid-label."""
    seen = defaultdict(set)
    for r in rows:
        f = fold(r["name"])
        cut = len(r["name"]) == 60 or re.search(r"\b(si|a|al|de|din|pentru|la|cu|in)$", f)
        if DECL_AGGREGATE.search(f) and not cut:
            seen[f].add(fold(r["county"]))
    labels = []
    for f in sorted((f for f, c in seen.items() if len(c) >= DECL_SPREAD), key=len):
        if split_umbrella(f, labels[::-1])[0] is None:
            labels.append(f)
    return labels[::-1]


def split_umbrella(name, labels):
    """'SOCIETATI COMERCIALE LA CARE STATUL ESTE ACTIONAR ... IOR S A' -> ('IOR S A', label): the form
    let people type the institution after picking an umbrella entry. -> (None, None) for a bare one."""
    f = fold(name)
    for label in labels:
        if f.startswith(label + " "):
            rest = f[len(label):].strip()
            if (re.search(r"[a-z]{3}", rest) and not DECL_AGGREGATE.search(rest)
                    and not re.match(r"(din subordinea|sau|la care|si)\b", rest)):
                return rest.upper(), label
            break
    return None, None


def link_declaratii(linker, name, county, county_re, widespread):
    """-> (tier, idx, score, folded county, candidates). The ANI county is not always where the institution sits (a
    ministry shows up under all 42), so a county named in the institution name is tried first, and a name
    that does not link in its county is looked up among the Bucharest bodies (exact/canonical only, tier
    'national'), then among all counties when exactly one row has that name (tier 'elsewhere': a commune
    filed under the wrong county). Local kinds (schools, clubs, street administrations...) skip both
    fallbacks: a "Scoala gimnaziala Ion Creanga" elsewhere is another school. A `widespread` name
    (DECL_SPREAD+ counties) is a stale dropdown label ("INSPECTORATUL TERITORIAL DE MUNCA BOTOSANI"
    filed in 36 counties): its own county goes first. When a county has several eligible rows and nothing
    singles one out (tier 'ambiguous'), the fallbacks are skipped: the name stays unresolved and keeps
    its candidates."""
    ck, f = fold(county), fold(name)
    for pat, rep in DECL_ABBREV:
        f = pat.sub(rep, f).strip()
    name = f
    if f == "consiliul judetean":                   # the council of the row's county
        name = f"consiliul judetean {ck}"
    named = set(county_re.findall(f))
    order = [named.pop()] if len(named) == 1 and ck not in named else []
    order = [ck] + order if widespread else order + [ck]
    weak = amb = None
    for c in order:
        tier, idx, score, cands = linker.link(c, name, prefix=True)
        if tier in ("exact", "canonical", "unit", "tokens", "prefix"):
            return tier, idx, score, c, []
        if tier == "ambiguous" and not amb:
            amb = (tier, idx, score, c, cands)
        if tier == "weak" and not weak:
            weak = (tier, idx, score, c, cands)
    if amb:
        return amb
    if not DECL_LOCAL_KIND.search(f):
        tier, idx, score, _ = linker.link("bucuresti", name)
        if tier in ("exact", "canonical"):
            return "national", idx, score, "bucuresti", []
        i = linker.anywhere(name)
        if i is not None:
            return "elsewhere", [i], 1.0, linker.anaf[i]["_ck"], []
    return weak or (None, [], 0.0, order[0], [])


# ---------------------------------------------------------------- categories

LOCAL, EDU, HEALTH, SOCIAL = "Administrație locală", "Educație", "Sănătate", "Asistență socială și muncă"
ORDER, DEF, JUST = "Ordine publică și urgențe", "Apărare", "Justiție"
CULT, AGRI = "Cultură, sport și tineret", "Agricultură, mediu și păduri"
UTIL, FIN, TRANS = "Servicii publice locale și regii", "Finanțe publice", "Transport și infrastructură"
RES, CENT = "Cercetare", "Autorități centrale și deconcentrate"
ORG, OTHER = "Asociații și organizații profesionale", "Altele"
COMPANY = "Companii de stat"
# A legal form (S A, SA, S R L, SRL) makes a company, with one exception: right after a single-letter word it can
# be the tail of an initialism ("D S V S A ALBA LABORATOR SANITAR VETERINAR" = D.S.V.S.A.). Then the name is a
# company only if no institutional noun follows ("C N A I R S A SECTIA DRUMURI" stays a company).
_FORM = r"\b(?:s a|sa|s r l|srl)\b"
_INSTITUTIONAL = r"\b(?:laborator\w*|sanitar\w*|veterinar\w*|directia|serviciul|inspectoratul|scoala|spital\w*)\b"
COMPANY_RE = re.compile(rf"(?<!\b[a-z] ){_FORM}|(?<=\b[a-z] ){_FORM}(?!.*{_INSTITUTIONAL})|"
                        r"\b(?:compania nationala|societatea nationala|societatea comerciala|cn|sn)\b")

RULES = [  # first match wins; patterns run on fold()ed names
    (ORG, r"^(colegiul (medicilor|farmacistilor|dentistilor|veterinar)|ordinul|oamgmamr|uniunea|federatia|asociatia|"
          r"fundatia|camera (de comert|notarilor|auditorilor|consultantilor)|sindicat|patronat|cooperativa)\b"),
    (LOCAL, r"^(primaria|primarie|consiliul? local|consiliul? judetean|consiliul general|comuna|orasul|oras|"
            r"municipiul|municipiului|comunei|orasului|sectorul|judetul|uat|unitatea administrativ)\b(?!.*\b(scoala|liceul|spital|spitalul|directia|serviciul|centrul|"
            r"clubul|biblioteca|gradinita|colegiul|casa|caminul|administratia|regia|politia)\b)"),
    (COMPANY, COMPANY_RE.pattern),
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
    (AGRI, r"\b(sanitar veterinar\w*|sanitara veterinara|veterinar\w* si pentru siguranta)\b"),   # before HEALTH: "laborator"
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
# word boundaries: `culturii` must not match inside `agriculturii`
ANCESTOR_HINTS = [(label, re.compile(r"\b(?:" + p + r")\b")) for label, p in ANCESTOR_HINTS]


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

# ---------------------------------------------------------------- state tree
# "Structura statului" view (docs/specs/structura-statului.md). The top layer follows the Constitution and is
# curated by hand, keyed by CIF (stable across ANAF releases). Virtual nodes: (id, label, parent id or None, note).
# Members: (cif, node id, note); a node lists its members in this order. Local administration (county -> UAT)
# is built by the page from the ANAF roots, so it has no entry here.
STATE_NODES = [
    ("parlament", "Parlamentul", None, "Titlul III, cap. I"),
    ("presedinte", "Președintele României", None, "Titlul III, cap. II"),
    ("guvern", "Guvernul", None, "Titlul III, cap. III; cap. V secț. 1"),
    ("ministere", "Ministere", "guvern", None),
    ("specialitate", "Organe de specialitate ale administrației centrale", "guvern", None),
    ("justitie", "Autoritatea judecătorească", None, "Titlul III, cap. VI"),
    ("ccr", "Curtea Constituțională", None, "Titlul V"),
    ("curtea-conturi", "Curtea de Conturi", None, "Titlul IV, art. 140"),
    ("avp", "Avocatul Poporului", None, "Titlul II, cap. IV"),
    ("ces", "Consiliul Economic și Social", None, "Titlul IV, art. 141"),
    ("autonome", "Autorități administrative autonome", None, "art. 117 alin. 3; sub control parlamentar"),
    ("aparare", "Apărare și siguranță națională", None,
     "art. 118-119; CSAT coordonează. MApN și MAI rămân la Guvern / Ministere"),
    ("servicii", "Servicii publice autonome", None, "sub control parlamentar"),
    ("academii", "Academii și instituții publice autonome", None, None),
]
STATE_MEMBERS = [
    ("4265795", "parlament", None), ("4284070", "parlament", None), ("7901650", "parlament", "art. 79"),
    ("4283732", "presedinte", None),
    ("4283422", "guvern", None),
    ("4266863", "ministere", None), ("4267095", "ministere", None), ("4221187", "ministere", None),
    ("11424532", "ministere", None), ("4192812", "ministere", None), ("26369185", "ministere", None),
    ("24931499", "ministere", None), ("13729380", "ministere", None), ("43507695", "ministere", None),
    ("4221306", "ministere", None), ("38918422", "ministere", None), ("4265841", "ministere", None),
    ("16335444", "ministere", None), ("4266669", "ministere", None), ("4266456", "ministere", None),
    ("13633330", "ministere", None),
    ("26288978", "specialitate", None), ("16277408", "specialitate", None), ("11795573", "specialitate", None),
    ("22464311", "specialitate", None), ("49199357", "specialitate", None),
    ("10792013", "specialitate", "disputat: Guvern sau autoritate autonomă"),
    ("11795581", "specialitate", "disputat: coordonare MDLPA"),
    ("26429279", "specialitate", None), ("4266499", "specialitate", None),
    ("4340587", "justitie", None), ("4364748", "justitie", None), ("16973795", "justitie", None),
    ("4265850", "ccr", None), ("4265922", "curtea-conturi", None), ("9766550", "avp", None),
    ("10464660", "ces", None),
    ("16460641", "autonome", None), ("4266189", "autonome", None), ("12932750", "autonome", None),
    ("22838777", "autonome", None), ("8844560", "autonome", None), ("11514848", "autonome", None),
    ("14751237", "autonome", None), ("31588130", "autonome", None), ("18073706", "autonome", None),
    ("14818035", "autonome", None), ("50306805", "autonome", None), ("20329980", "autonome", None),
    ("36401992", "autonome", None),
    ("4204291", "aparare", None), ("10668016", "aparare", None), ("4267230", "aparare", None),
    ("4283635", "aparare", None), ("15085226", "aparare", None),
    ("8296093", "servicii", None), ("8468440", "servicii", None), ("4266448", "servicii", None),
    ("15726657", "servicii", "disputat: control parlamentar sau MAE"),
    ("4192472", "academii", None), ("5091859", "academii", None), ("33354101", "academii", None),
    ("18476245", "academii", "disputat"), ("11697800", "academii", "disputat: autonom sau sub MS"),
]
STATE_ATTACH = [("8609468", "4221306"), ("26246549", "4267117")]   # (child root, root it hangs under)
LOCAL_ROOT_RE = re.compile(r"^(municipiul|oras|orasul|comuna|judetul|sectorul|primaria|municipiului)\b")


def state_tree(records):
    """The `state` block of metadata.json: virtual nodes, CIF -> node mapping, attach rules, and the roots
    the page cannot place (UATs go to the local-administration branch, the rest to "Neclasificate")."""
    roots = {r["cif"]: r for r in records if r["cif"] and not r["parents"]}
    mapped = {c for c, _, _ in STATE_MEMBERS} | {c for c, _ in STATE_ATTACH}
    is_uat = lambda r: r["category"] == LOCAL or LOCAL_ROOT_RE.match(fold(r["name"]))
    uat = sorted(c for c, r in roots.items() if c not in mapped and is_uat(r))
    other = sorted((c for c, r in roots.items() if c not in mapped and not is_uat(r)), key=lambda c: roots[c]["name"])
    lost = [c for c, _, _ in STATE_MEMBERS if c not in roots] + [c for p in STATE_ATTACH for c in p if c not in roots]
    if lost:
        print(f"warning: STATE_TREE CIFs that are not ANAF roots: {lost}", file=sys.stderr)
    return {"nodes": [{"id": i, "label": l, "parent": p, **({"note": n} if n else {})} for i, l, p, n in STATE_NODES],
            "members": [[c, n] + ([note] if note else []) for c, n, note in STATE_MEMBERS],
            "attach": [list(a) for a in STATE_ATTACH], "uat": uat, "unclassified": other}, [roots[c] for c in other]


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

def union_candidates(lists):
    """Candidate dicts of several rows -> one list, one entry per CIF (best score), sorted by -score, cif."""
    best = {}
    for c in (c for cs in lists for c in cs):
        if c["cif"] not in best or c["score"] > best[c["cif"]]["score"]:
            best[c["cif"]] = c
    return sorted(best.values(), key=lambda c: (-c["score"], c["cif"]))


def candidate_fields(cands):
    """-> (possible_duplicate_of, match_candidates). One weak candidate is a possible duplicate; several
    are an unresolved match and name no single target."""
    if len(cands) == 1:
        return cands[0]["cif"], []
    return None, list(cands)


def declaratii_standalone(rows, aggregate):
    """Unlinked ANI names become records of their own. The same name filed under several counties is one
    institution (its staff live or work elsewhere, or the county was misfiled): one record in the county
    with most declarations, keeping the per-county split. Local kinds are the exception ("Scoala
    gimnaziala nr 1" in two counties is two schools). A name spread over DECL_SPREAD+ counties with no
    county holding most declarations is an umbrella entry and goes to `aggregate`."""
    by_name = defaultdict(lambda: defaultdict(list))
    for t in rows:
        by_name[fold(t[3]["name"])][t[3]["county"]].append(t)
    out = []
    for f, by_county in by_name.items():
        per_county = []
        for ts in by_county.values():                 # rows that resolved to the same county add up
            top = max(ts, key=lambda t: t[3]["count"])
            per_county.append((top[0], top[1], top[2], {**top[3], "count": sum(t[3]["count"] for t in ts)},
                               union_candidates(t[4] for t in ts)))
        per_county.sort(key=lambda t: -t[3]["count"])
        total = sum(t[3]["count"] for t in per_county)
        if DECL_LOCAL_KIND.search(f):
            out.extend(t for t in per_county if t[3]["count"] >= DECL_MIN_COUNT)
        elif len(per_county) >= DECL_SPREAD and per_county[0][3]["count"] * 2 < total:
            aggregate.extend(t[3] for t in per_county)
        elif total >= DECL_MIN_COUNT:
            top = per_county[0]
            split = [[t[3]["county"], t[3]["count"]] for t in per_county] if len(per_county) > 1 else None
            out.append((top[0], top[1], top[2], {**top[3], "count": total, "by_county": split},
                        union_candidates(t[4] for t in per_county)))
    return out


# Kinds with many same-named bodies per county (village schools, kindergartens, libraries): never combined by name.
# The other DECL_LOCAL_KIND kinds (hospitals, colleges, street administrations...) are unique per locality, so
# a name with a proper noun combines (the brief's own example is "Administratia domeniului public sector 1").
SAME_NAME_NEVER = re.compile(r"^(scoala|gradinita|grup scolar|biblioteca|caminul|parohia|casa de cultura)\b")
SRC_ORDER = ["anaf", "roepas", "registrul", "declaratii"]
SRC_PRIORITY = {"roepas": 0, "registrul": 1, "declaratii": 2}       # the surviving id of a same-name group


def generic_name(f):
    """A name with a family head but no proper noun after it ("scoala gimnaziala", "primaria"): many bodies share it."""
    for _, pat, _cat in FAMILY_HEADS:
        m = pat.search(f)
        if m:
            return not [t for t in f[m.end():].split() if t not in STOP and not t.isdigit()]
    return False


def same_name_key(rec):
    return (fold(rec["county"]), fold(strip_suffix(rec["name"])))


def explicit_sectors(rec):
    return set(SECTOR_NAME_RE.findall(fold(rec["name"])))


def merge_same_name(records, nationwide=False):
    """Combine source-only records (ROePAS, Registrul, ANI) with the same folded name and county across
    different sources. Skipped: village-level kinds (SAME_NAME_NEVER), generic names, a group where any source holds the name more than once,
    a group whose names state different sectors, and a county-less record. A name with a sector ("- Sector 2") matches the
    same name without one. The surviving id follows ROePAS > Registrul > ANI.
    `nationwide`: second pass, the county is ignored but one record must be in Bucuresti (the sources file
    a national body under its seat or under a wrong county). Mutates `records`; -> stats."""
    groups = defaultdict(list)
    for rec in records:
        if rec["sources"] in (["roepas"], ["registrul"], ["declaratii"]) and rec["county"]:
            k = same_name_key(rec)
            groups[k[1] if nationwide else k].append(rec)
    stats = {"groups": Counter(), "ids": 0, "dup_source": 0, "generic": 0, "sectors": 0}
    drop = set()
    for key, grp in sorted(groups.items()):
        if len({r["sources"][0] for r in grp}) < 2:
            continue
        name = key if nationwide else key[1]
        if SAME_NAME_NEVER.search(name) or generic_name(name):
            stats["generic"] += 1
            continue
        if any(n > 1 for n in Counter(r["sources"][0] for r in grp).values()):
            stats["dup_source"] += 1
            continue
        if len(set().union(*map(explicit_sectors, grp))) > 1:
            stats["sectors"] += 1
            continue
        if nationwide and not any(fold(r["county"]) == "bucuresti" for r in grp):
            continue
        grp.sort(key=lambda r: (fold(r["county"]) != "bucuresti", SRC_PRIORITY[r["sources"][0]])
                 if nationwide else SRC_PRIORITY[r["sources"][0]])
        keep, rest = grp[0], grp[1:]
        cands = union_candidates(r["_cands"] for r in grp)
        for r in rest:
            absorb(keep, r, "same_name")
            drop.add(r["id"])
        keep["possible_duplicate_of"], multi = candidate_fields(cands)
        keep["_cands"] = cands
        keep.pop("match_candidates", None)
        if multi:
            keep["match_candidates"] = multi
        stats["groups"]["+".join(keep["sources"])] += 1
        stats["ids"] += len(rest)
    records[:] = [r for r in records if r["id"] not in drop]
    return stats


LOCAL_KIND_RE = re.compile(
    r"\b(scoala|gradinita|liceul|colegiul|grup scolar|biblioteca|caminul|parohia|casa de cultura|primaria|consiliul local|"
    r"club|scolar|palatul copiilor|cantina|tribunal|tribunalul|curtea de apel|judecatoria)\b|\bsc |\bnr\.? ?\d")
KEY_SMALL = {"de", "al", "a", "si", "pentru", "la", "din", "cu", "in"}


def loose_key(rec):
    """County + the folded name with punctuation, word order and small words ignored."""
    toks = [t for t in fold_words(rec["name"]) if t not in KEY_SMALL]
    return (fold(rec["county"]), " ".join(sorted(toks)))


def fold_words(name):
    return re.sub(r"[^a-z0-9 ]", " ", unicodedata.normalize("NFD", name.lower()).encode("ascii", "ignore").decode()).split()


def merge_loose_names(records):
    """Owner rule (2026-10-27): same county + same normalised name + not a local body = one body.
    Local bodies: LOCAL_KIND_RE, SAME_NAME_NEVER, generic names. A group with two ANAF CIFs stays apart (ANAF
    says they differ). The survivor is the ANAF record, else ROePAS > Registrul > ANI, then the lowest id.
    The group may hold the same source twice. Mutates `records`; -> stats."""
    groups = defaultdict(list)
    for rec in records:
        if rec["county"]:
            groups[loose_key(rec)].append(rec)
    stats = {"groups": 0, "ids": 0, "anaf": 0, "local": 0}
    drop = set()
    for key, grp in sorted(groups.items()):
        if len(grp) < 2:
            continue
        f = fold(grp[0]["name"])
        if LOCAL_KIND_RE.search(f) or SAME_NAME_NEVER.search(f) or generic_name(f):
            stats["local"] += 1
            continue
        if sum(1 for r in grp if r["cif"]) >= 2:
            stats["anaf"] += 1
            continue
        if len(set().union(*map(explicit_sectors, grp))) > 1 or any(r.get("same_body_as") for r in grp):
            continue
        order = lambda r: (not r["cif"], SRC_PRIORITY.get(r["sources"][0], -1) if not r["cif"] else -1, r["id"])
        grp.sort(key=order)
        keep, rest = grp[0], grp[1:]
        cands = union_candidates(r.get("_cands", []) for r in grp)
        for r in rest:
            absorb(keep, r, "same_name")
            drop.add(r["id"])
        if not keep["cif"]:
            keep["possible_duplicate_of"], multi = candidate_fields(cands)
            keep["_cands"] = cands
            keep.pop("match_candidates", None)
            if multi:
                keep["match_candidates"] = multi
        stats["groups"] += 1
        stats["ids"] += len(rest)
    records[:] = [r for r in records if r["id"] not in drop]
    return stats


def infer_sectors(records):
    """Unify sector labels on non-ANAF records, then set the sector of a Bucuresti record without UAT when its
    name states exactly one sector (`uat_source` = "name"). -> stats."""
    stats = {"unified": 0, "inferred": 0, "ambiguous": 0}
    for rec in records:
        if rec["cif"]:
            continue
        label = sector_label(rec["uat"])
        if label != rec["uat"]:
            rec["uat"] = label
            stats["unified"] += 1
        if fold(rec["county"]) == "bucuresti" and not rec["uat"]:
            found = sector_in_name(rec["name"])
            if found:
                rec["uat"], rec["uat_source"] = found, "name"
                stats["inferred"] += 1
            elif len(set(SECTOR_NAME_RE.findall(fold(rec["name"])))) > 1:
                stats["ambiguous"] += 1
    return stats


TIER_RANK = {"exact": 0, "canonical": 1, "unit": 1, "tokens": 2, "prefix": 2, "national": 3, "elsewhere": 3}


def main():
    PROVENANCE.clear()
    anaf, registrul, roepas, declaratii = load_anaf(), load_registrul(), load_roepas(), load_declaratii()
    curated = load_curated_websites()
    print(f"sources: anaf={len(anaf)} registrul={len(registrul)} roepas={len(roepas)} "
          f"declaratii={len(declaratii)}", file=sys.stderr)
    linker = Linker(anaf)
    county_display = {fold(a["county"]): a["county"] for a in anaf}
    county_of = lambda c: county_display.get(fold(c)) or squash(c).title()
    by_cif = {a["cif"]: a for a in anaf}
    # ROePAS says "Alba Iulia", ANAF says "Municipiul Alba Iulia": map the former onto the latter
    uat_label = {}
    for a in anaf:
        uat_label.setdefault((fold(a["county"]), UAT_RE.sub("", fold(a["uat"]), count=1)), a["uat"])
    unified = Counter()

    def uat_of(county, city):
        raw = uat_label.get((fold(county), fold(city)), city)
        label = sector_label(raw)
        unified[label != raw] += 1
        return label

    links = {"roepas": defaultdict(list), "registrul": defaultdict(list), "declaratii": defaultdict(list)}
    standalone = {"roepas": [], "registrul": [], "declaratii": []}
    for src, rows in (("roepas", roepas), ("registrul", registrul)):
        for row in rows:
            tier, idx, score, cands = linker.link(row["county"], row["name"], row.get("city"))
            if tier in TIER_RANK:
                links[src][idx[0]].append((tier, row))
            else:
                standalone[src].append((tier, idx, score, row, cands))
    county_re = re.compile(r"\b(" + "|".join(sorted(county_display, key=len, reverse=True)) + r")\b")
    aggregate, labels = [], umbrella_labels(declaratii)
    spread = Counter(fold(r["name"]) for r in declaratii)
    for row in declaratii:
        if DECL_AGGREGATE.search(fold(row["name"])):
            specific, group = split_umbrella(row["name"], labels)
            if not specific:
                aggregate.append(row)
                continue
            row = {**row, "name": specific, "group": group}
        tier, idx, score, ck, cands = link_declaratii(linker, row["name"], row["county"], county_re,
                                                spread[fold(row["name"])] >= DECL_SPREAD)
        row = {**row, "county": county_of(ck)}
        if tier in TIER_RANK:
            links["declaratii"][idx[0]].append((tier, row))
        else:
            standalone["declaratii"].append((tier, idx, score, row, cands))

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
        dec = links["declaratii"].get(i, [])
        others = [r["name"] for _, r in roe] + [r["name"] for _, r in reg] + [r["name"] for _, r in dec]
        rec["aliases"] = sorted({squash(n) for n in others if fold(n) != fold(a["name"])})
        if reg:
            rec["sources"].append("registrul")
            rec["link"]["registrul"] = sorted(reg, key=lambda t: TIER_RANK[t[0]])[0][0]
            rec["registrul_nums"] = sorted(r["num"] for _, r in reg)
        if dec:
            rec["sources"].append("declaratii")
            rec["link"]["declaratii"] = sorted(dec, key=lambda t: TIER_RANK[t[0]])[0][0]
            rec["declaratii_count"] = sum(r["count"] for _, r in dec)
        records.append(rec)

    def standalone_link(cands):
        """The link fields of a source row with no merge: `possible_duplicate_of` and `match_candidates`."""
        possible, multi = candidate_fields(cands)
        return {"possible_duplicate_of": possible, **({"match_candidates": multi} if multi else {}), "_cands": cands}

    for tier, idx, score, r, cands in standalone["roepas"]:
        records.append({
            "id": "R" + r["id"], "name": r["name"], "county": county_of(r["county"]),
            "uat": uat_of(r["county"], r["city"]), "address": r["address"], "cif": None, "cif_tva": None, "parents": [],
            "category": categorize(r["name"]), "sources": ["roepas"], "link": {}, **standalone_link(cands),
            "website": r["website"], "website_url": r["website_url"], "email": r["email"],
            "phone": r["phone"], "fax": r["fax"], "lat": r["lat"], "lon": r["lon"],
            "roepas_ids": [r["id"]], "roepas_url": r["detail_url"],
            "procedures_count": r["procedures_count"], "online_procedures_count": r["online_procedures_count"],
            "org_units": r["org_units"]})
    for tier, idx, score, r, cands in standalone["registrul"]:
        records.append({
            "id": "G" + r["num"], "name": r["name"], "county": county_of(r["county"]), "uat": None,
            "address": None, "cif": None, "cif_tva": None, "parents": [],
            "category": categorize(r["name"]), "sources": ["registrul"], "link": {},
            **standalone_link(cands),
            "registrul_nums": [r["num"]]})
    for tier, idx, score, r, cands in declaratii_standalone(standalone["declaratii"], aggregate):
        group = r.get("group")
        records.append({
            "id": "D" + hashlib.sha1(f"{fold(r['name'])}|{fold(r['county'])}".encode()).hexdigest()[:8],
            "name": r["name"], "county": r["county"], "uat": None, "address": None, "cif": None,
            "cif_tva": None, "parents": [],
            "category": COMPANY if group and re.match(r"(societati|companii|regii)", group)
            else categorize(r["name"], [group] if group else []),
            "sources": ["declaratii"], "link": {}, **standalone_link(cands),
            "declaratii_count": r["count"], "declaratii_group": group and group.upper(),
            "declaratii_by_county": r.get("by_county")})

    curation_stats = apply_curated_websites(records, curated)
    merge_stats = merge_same_name(records)
    national_stats = merge_same_name(records, nationwide=True)
    for k in ("ids", "dup_source", "generic", "sectors"):
        merge_stats[k] += national_stats[k]
    merge_stats["groups"].update(national_stats["groups"])
    merge_stats["national"] = sum(national_stats["groups"].values())
    merge_stats["curated"] = apply_curated_merges(records, load_curated_merges())
    merge_stats["loose"] = merge_loose_names(records)
    merge_stats["sector_names"] = strip_sector_suffix(records)
    check_aliases(records)
    merge_stats["same_body"] = apply_same_body(records)
    sector_stats = infer_sectors(records)
    sector_stats["unified"] += unified[True]
    for rec in records:
        rec.pop("_cands", None)
    assign_families(records)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "institutii.json").write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    write_csv(OUT_DIR / "institutii.csv", records)
    write_explorer_data(OUT_DIR, records)
    report(records, anaf, links, standalone, declaratii, aggregate, merge_stats, sector_stats, curation_stats)


CSV_COLS = ["id", "name", "category", "family", "county", "uat", "address", "cif", "cif_tva", "parent_cifs",
            "parent_names", "website", "website_url", "email", "phone", "fax", "lat", "lon", "sources",
            "link_roepas", "link_registrul", "possible_duplicate_of", "match_candidate_cifs", "roepas_ids", "roepas_url",
            "registrul_nums", "procedures_count", "online_procedures_count", "org_units", "link_declaratii",
            "declaratii_count", "declaratii_group", "uat_source", "merged_ids", "website_source", "same_body_as", "aliases"]


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
            row["link_declaratii"] = r["link"].get("declaratii")
            row["match_candidate_cifs"] = flat([c["cif"] for c in r.get("match_candidates", [])])
            w.writerow(row)


SRC_BIT = {"anaf": 1, "roepas": 2, "registrul": 4, "declaratii": 8}


def dataset_block():
    """`dataset` in metadata.json: when the output was built and from which input files (see record_input).
    Only the ANI exports carry `exported_at` (from the Kibana file name); `modified_at` is the file mtime."""
    return {"generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "inputs": sorted(PROVENANCE, key=lambda e: (e["source"], e["path"]))}


def write_explorer_data(out_dir, records):
    """Compact rows for the static explorer: short keys, empty values omitted, categories/counties by index.
    metadata.json holds the lookup lists, rows.json the rows; explorer/ links to both."""
    counts = Counter(r["category"] for r in records)
    cats = sorted(counts, key=lambda c: (c == OTHER, -counts[c]))
    counties = sorted({r["county"] for r in records if r["county"]})
    ci, ki = {c: i for i, c in enumerate(cats)}, {c: i for i, c in enumerate(counties)}
    families = [f for f, _ in Counter(r["family"] for r in records if r["family"]).most_common()]
    fi = {f: i for i, f in enumerate(families)}
    rows = []
    for r in records:
        row = {"i": r["id"], "n": r["name"], "c": ci[r["category"]], "s": sum(SRC_BIT[x] for x in r["sources"])}
        optional = {
            "k": ki.get(r["county"]), "u": r["uat"], "a": r["address"], "f": r["cif"], "t": r["cif_tva"],
            "p": [p["cif"] for p in r["parents"]], "w": r.get("website_url"), "e": r.get("email"),
            "ph": r.get("phone"), "fx": r.get("fax"), "la": r.get("lat"), "lo": r.get("lon"),
            "ru": r.get("roepas_url"), "pc": r.get("procedures_count"), "po": r.get("online_procedures_count"),
            "ou": r.get("org_units"), "rn": r.get("registrul_nums"), "d": r["possible_duplicate_of"],
            "lr": r["link"].get("roepas"), "lg": r["link"].get("registrul"), "al": r.get("aliases"),
            "m": fi.get(r["family"]), "dc": r.get("declaratii_count"), "ld": r["link"].get("declaratii"),
            "dg": r.get("declaratii_group"), "dk": r.get("declaratii_by_county"),
            "mc": [c["cif"] for c in r.get("match_candidates", [])],
            "us": 1 if r.get("uat_source") else None, "mi": r.get("merged_ids"),
        }
        for k, v in optional.items():
            if v is None or v == "" or v == []:           # a known 0 (pc, po) stays: it differs from unknown
                continue
            row[k] = v
        rows.append(row)
    state, _ = state_tree(records)
    meta = {"categories": cats, "counties": counties, "families": families, "state": state,
            "dataset": dataset_block()}
    (out_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    (out_dir / "rows.json").write_text(json.dumps(rows, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def report(records, anaf, links, standalone, declaratii, aggregate, merge_stats, sector_stats, curation_stats):
    n = Counter(tuple(r["sources"]) for r in records)
    print(f"\nconsolidated records: {len(records)}", file=sys.stderr)
    for k, v in sorted(n.items(), key=lambda kv: -kv[1]):
        print(f"  {'+'.join(k):28s} {v}", file=sys.stderr)
    for src in ("roepas", "registrul"):
        linked = sum(len(v) for v in links[src].values())
        weak = sum(1 for t, *_ in standalone[src] if t == "weak")
        amb = sum(1 for t, *_ in standalone[src] if t == "ambiguous")
        print(f"{src}: {linked} rows merged into ANAF, {weak} weak candidates kept separate, "
              f"{len(standalone[src]) - weak - amb} with no candidate, {amb} ambiguous (several candidates)",
              file=sys.stderr)
    total = sum(r["count"] for r in declaratii)
    linked = [r for v in links["declaratii"].values() for _, r in v]
    print(f"declaratii: {len(declaratii)} names, {total} declarations", file=sys.stderr)
    tiers = Counter(t for v in links["declaratii"].values() for t, _ in v)
    print(f"  merged into ANAF: {len(linked)} names ({sum(r['count'] for r in linked)} declarations) "
          f"onto {len(links['declaratii'])} records; by tier {dict(tiers)}", file=sys.stderr)
    named = sum(1 for v in links["declaratii"].values() for _, r in v if r.get("group"))
    print(f"  names typed after an umbrella entry: {named} merged into ANAF, "
          f"{sum(1 for r in records if r.get('declaratii_group'))} records of their own", file=sys.stderr)
    print(f"  umbrella entries: {len(aggregate)} names ({sum(r['count'] for r in aggregate)} declarations)",
          file=sys.stderr)
    own = [r for r in records if r["sources"] == ["declaratii"]]
    print(f"  records of their own: {len(own)} ({sum(1 for r in own if r['possible_duplicate_of'])} weak, "
          f"{sum(1 for r in own if r.get('match_candidates'))} ambiguous), "
          f"{sum(r['declaratii_count'] for r in own)} declarations", file=sys.stderr)
    mg = merge_stats
    print(f"\nsame-name merges (source-only records of different sources): {sum(mg['groups'].values())} groups, "
          f"{mg['ids']} ids absorbed; skipped: {mg['generic']} generic or village-level names, "
          f"{mg['dup_source']} groups with a repeated name inside one source, {mg['sectors']} with different sectors",
          file=sys.stderr)
    print(f"  of which nationwide (county ignored): {mg['national']} groups; curated: {dict(mg['curated'])}; "
          f"sector suffix removed from {mg['sector_names']} names; same_body_as links: {mg['same_body']}", file=sys.stderr)
    print(f"  loose-name merges: {mg['loose']['groups']} groups, {mg['loose']['ids']} ids absorbed; skipped: "
          f"{mg['loose']['anaf']} with two ANAF CIFs, {mg['loose']['local']} local or generic names", file=sys.stderr)
    for k, v in sorted(mg["groups"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:28s} {v}", file=sys.stderr)
    prefix = sum(1 for v in links["declaratii"].values() for t, _ in v if t == "prefix")
    pamb = sum(1 for r in records if any(c["tier"] == "prefix" for c in r.get("match_candidates", [])))
    print(f"prefix tier: {prefix} ANI names merged into ANAF; {pamb} records with ambiguous prefix candidates",
          file=sys.stderr)
    print(f"sectors: {sector_stats['unified']} labels unified, {sector_stats['inferred']} inferred from the name, "
          f"{sector_stats['ambiguous']} names state several sectors (left blank)", file=sys.stderr)
    cs, unknown = curation_stats
    print(f"curated websites: {cs['filled']} filled, {cs['replaced']} replaced, {cs['same']} same as ROePAS; "
          f"{len(unknown)} CIFs match no record {unknown}", file=sys.stderr)
    _, loose = state_tree(records)
    print(f"\nneclasificate (central roots with no STATE_TREE entry): {len(loose)}", file=sys.stderr)
    for r in loose:
        print(f"  {r['cif']} {r['name']}", file=sys.stderr)
    print("\ncategories:", file=sys.stderr)
    for k, v in Counter(r["category"] for r in records).most_common():
        print(f"  {k:40s} {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
