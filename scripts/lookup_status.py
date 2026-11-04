#!/usr/bin/env python3
"""Look up the status of every record with a CUI that is not from ANAF, in the Finance Ministry (MF) files.

Input (not in git): the two UTF-8 July files of the MF dataset "Date de identificare plătitori"
(data.gov.ro, CC-BY-4.0): delimiter `^`, CRLF, no quoting, a trailing `^`.
  - data/consolidated/institutii.csv (output of consolidate.py): the CUIs to look up
    (`cif_source` `seap` or `curation`).
Output (ignored by git): data/lookup/status.csv with the columns
  cui, name, status, status_label, status_date, county, locality, source, checked_at

Rules:
  - A row with `TIP_CONTRIB` PF is a natural person. The script skips it and never keeps it. A CUI that only such a
    row holds gets the status `not_found`. A row of another type is skipped in the same way.
  - The script reads no `TELEFON`.
  - The status comes from the whole `STARE` string (STATUS_RULE). An unknown label stops the script. An empty
    label on one of our CUIs also stops the script.
  - A CUI that the files do not hold gets `not_found`. The record stays visible. Absence is not `radiat`.
  - `status_date` is `DATA_STARE` as YYYY-MM-DD. The script does not read `DATA_RADIERE`.
  - `checked_at` is the snapshot date: the latest `DATA_PRELUCRARE` of the rows that are not natural persons.
  - `county` and `locality` are the MF texts. For Bucharest with a sector 1-6, `locality` is "Sectorul N".

Usage: python3 scripts/lookup_status.py [--mf DIR] [--csv institutii.csv] [--out data/lookup/status.csv]
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MF_DIR = Path("/Volumes/geana/NAS-devbox/gov2/data.gov.ro-mf-platitori-2026-07")
MF_FILES = ("date_identificare_platitori_2026_a_actualizat_iulie.txt",
            "date_identificare_platitori_2026_b__actualizat_iulie.txt")
INSTITUTII_CSV = ROOT / "data/consolidated/institutii.csv"
OUT_CSV = ROOT / "data/lookup/status.csv"
COLS = ["cui", "name", "status", "status_label", "status_date", "county", "locality", "source", "checked_at"]

# Whole STARE string -> status. `listat` does not claim "active": MODIFICARE PUBLICI can hide a later dissolution.
STATUS_RULE = {
    "RADIERE": "radiat",
    "LICHIDAT": "radiat",
    "DIZOLVARE FARA LICHIDARE(FUZIUNE)": "fuzionat",
    "DIZOLVARE FARA LICHIDARE(DIVIZARE)": "fuzionat",
    "DIZOLVARE CU LICHIDARE(INCEPUT LICHIDARE)": "in_lichidare",
    "INREGISTRAT": "listat",
    "MODIFICARE PUBLICI": "listat",
    "TRANSFER(SOSIRE)": "listat",
    "RELUARE ACTIVITATE": "listat",
    "SUSPENDARE ACTIVITATE": "listat",
}
DATE_RE = re.compile(r"^(\d\d)\.(\d\d)\.(\d{4})(?:\s|$)")


def status_of(label):
    """STARE label -> status. Stops on an empty or unknown label."""
    label = (label or "").strip()
    if label not in STATUS_RULE:
        raise SystemExit(f"STARE label outside the rule: {label!r}")
    return STATUS_RULE[label]


def iso_date(text):
    """'dd.mm.yyyy' (a time may follow) -> 'yyyy-mm-dd'. An empty text gives ''. Stops on any other text."""
    text = (text or "").strip()
    if not text:
        return ""
    m = DATE_RE.match(text)
    if not m:
        raise SystemExit(f"date outside the format dd.mm.yyyy: {text!r}")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"


def mf_row(cols, ix):
    """The kept fields of one MF row (no phone, no street). Stops when the row is too short."""
    if len(cols) < len(ix):
        raise SystemExit(f"MF row of CUI {cols[0]} has {len(cols)} columns, expected {len(ix)}")
    g = lambda name: cols[ix[name]].strip()
    county, locality = g("JUDET"), g("LOCALITATE")
    if county.upper().startswith("MUNICIPIUL BUCURE") and g("SECTOR") in tuple("123456"):
        locality = "Sectorul " + g("SECTOR")
    return {"status_label": g("STARE"), "status_date": iso_date(g("DATA_STARE")), "county": county,
            "locality": locality}


def read_mf(mf_dir, cuis, files=MF_FILES):
    """Scan the MF files once. -> ({cui: row} for the CUIs in `cuis`, snapshot date YYYY-MM-DD, stats).
    A natural person (PF) or another type is skipped before any field is read. A CUI on two rows stops the script."""
    found, latest, stats = {}, "", Counter()
    wanted = {c.encode() for c in cuis}
    for name in files:
        with open(Path(mf_dir) / name, "rb") as fh:
            header = fh.readline().decode("utf-8-sig").rstrip("\r\n").split("^")
            ix = {h: i for i, h in enumerate(header)}
            for line in fh:
                head = line.split(b"^", 10)
                if len(head) < 10:
                    stats["short"] += 1
                    continue
                if head[4] != b"PJ":
                    stats["pf" if head[4] == b"PF" else "other"] += 1
                    continue
                stats["pj"] += 1
                d = head[9][:10].decode("ascii", "replace")
                if re.fullmatch(r"\d\d\.\d\d\.\d{4}", d):
                    latest = max(latest, d[6:] + "-" + d[3:5] + "-" + d[:2])
                if head[0] in wanted:
                    cui = head[0].decode()
                    if cui in found:
                        raise SystemExit(f"CUI {cui} is on two MF rows")
                    found[cui] = mf_row(line.decode("utf-8").rstrip("\r\n").split("^"), ix)
    return found, latest, stats


def build_rows(records, found, checked_at):
    """One status row per CUI of `records` ({cui, name}), sorted by CUI."""
    out = {}
    for r in records:
        cui = r["cif"]
        if cui in out:
            continue
        mf = found.get(cui)
        row = {"cui": cui, "name": r["name"], "source": "mf", "checked_at": checked_at}
        if mf:
            row.update(status=status_of(mf["status_label"]), status_label=mf["status_label"],
                       status_date=mf["status_date"], county=mf["county"], locality=mf["locality"])
        else:
            row.update(status="not_found", status_label="", status_date="", county="", locality="")
        out[cui] = row
    return [out[c] for c in sorted(out, key=int)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--mf", type=Path, default=MF_DIR, help="folder with the two MF July files")
    ap.add_argument("--csv", type=Path, default=INSTITUTII_CSV, help="institutii.csv from consolidate.py")
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    args = ap.parse_args()
    with args.csv.open(encoding="utf-8", newline="") as fh:
        records = [r for r in csv.DictReader(fh) if r["cif"] and r["cif_source"] in ("seap", "curation")]
    found, checked_at, stats = read_mf(args.mf, {r["cif"] for r in records})
    rows = build_rows(records, found, checked_at)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"snapshot {checked_at}; MF rows read: {stats['pj']} PJ; skipped unread: {stats['pf']} PF, "
          f"{stats['other']} other type, {stats['short']} short", file=sys.stderr)
    print(f"{len(rows)} CUIs from {len(records)} records -> {args.out}", file=sys.stderr)
    for status, n in Counter(r["status"] for r in rows).most_common():
        print(f"  {status:14s} {n}", file=sys.stderr)


if __name__ == "__main__":
    main()
