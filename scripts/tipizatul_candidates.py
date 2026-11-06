# /// script
# dependencies = ["openpyxl"]
# ///
"""Candidates for the tipizatul.eu map. Reads the bundle data/tipizatul/procedures.json (data only), links each
institution name that has procedures with documents to an ANAF row with consolidate.Linker, and writes the ignored
queue data/tipizatul/review.csv (name, county, tier, cif, record_id, anaf_name, procedures).
It prints the institutions of curation/tipizatul.csv that the bundle no longer holds. It changes no data.

    uv run scripts/tipizatul_candidates.py [--bundle FILE]
"""
import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import consolidate as C

ROOT = C.ROOT
KEEP_TIERS = ("exact", "canonical", "tokens")


def bundle_institutions(bundle):
    """-> {institution name: (county, number of procedures with documents)}. The county is the most common one."""
    procedures = json.loads(Path(bundle).read_text(encoding="utf-8"))["procedures"].values()
    counties = collections.defaultdict(collections.Counter)
    for p in procedures:
        if not p.get("documents"):          # the site hides procedures with no documents
            continue
        m = re.search(r"Jude[tț]\s+(.+)$", (p["fields"].get("institutiaResponsabila") or "").strip())
        counties[p["institution"]][(m.group(1).strip() if m else (p.get("county") or ""))] += 1
    return {n: (c.most_common(1)[0][0], sum(c.values())) for n, c in counties.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=str(ROOT / "data/tipizatul/procedures.json"))
    args = ap.parse_args()
    inst = bundle_institutions(args.bundle)
    anaf = C.load_anaf()
    linker = C.Linker(anaf, C.load_curated_aliases())
    county_of = {C.fold(a["county"]): a["county"] for a in anaf if a["county"]}
    bucuresti = next(v for k, v in county_of.items() if "bucuresti" in k)
    rec_of = {}
    json_path = ROOT / "data/consolidated/institutii.json"
    if json_path.exists():
        rec_of = {r["cif"]: r["id"] for r in json.loads(json_path.read_text(encoding="utf-8")) if r["cif"]}
    rows = []
    for name, (county, n) in sorted(inst.items()):
        f = C.fold(county)
        cty = county_of.get(f) or (bucuresti if "bucuresti" in f else None)
        if cty is None:
            rows.append({"institution": name, "county": county, "tier": "nocounty", "cif": "", "record_id": "",
                         "anaf_name": "", "procedures": n})
            continue
        tier, idx = linker.link(cty, name)[:2]
        a = anaf[idx[0]] if idx and tier not in ("weak", "ambiguous") else None
        rows.append({"institution": name, "county": county, "tier": tier, "cif": a["cif"] if a else "",
                     "record_id": rec_of.get(a["cif"], "") if a else "", "anaf_name": a["name"] if a else "",
                     "procedures": n})
    out = ROOT / "data/tipizatul/review.csv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    tiers = collections.Counter(r["tier"] for r in rows)
    print(f"names: {len(rows)}; by tier: {dict(tiers)}", file=sys.stderr)
    linked = [r for r in rows if r["cif"]]
    print(f"linked names: {len(linked)}; distinct CIFs: {len({r['cif'] for r in linked})}; "
          f"queue: {out}", file=sys.stderr)
    cur = ROOT / "curation/tipizatul.csv"
    if cur.exists():
        with cur.open(encoding="utf-8", newline="") as fh:
            gone = [r["institution"] for r in csv.DictReader(fh) if r["institution"] not in inst]
        for g in gone:
            print(f"not in the bundle any more: {g}")
        print(f"curation/tipizatul.csv: {len(gone)} institutions not in the bundle", file=sys.stderr)


if __name__ == "__main__":
    main()
