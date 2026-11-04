#!/usr/bin/env python3
"""Match the CIF-less ANI records (`D...`) to the ONRC company register by name and county.

Inputs (not in git):
  - ONRC open data (data.gov.ro, CC-BY-4.0): OD_FIRME.csv, OD_STARE_FIRMA.csv, N_STARE_FIRMA.csv.
    Delimiter `^`, UTF-8 with BOM, CRLF. Names hold raw `"`, so the files are read without quote handling.
  - data/consolidated/institutii.csv (output of consolidate.py)
Output (ignored by git): data/consolidated/onrc-review.csv, one row per (record, ONRC row).
The script writes no curation file. A person reads the queue and decides.

Key: the folded name without the legal form (a leading SC, and SA, SRL, RA anywhere in the name) and without
punctuation. An ONRC row with CUI 0 or no CUI is dropped. Tiers:
  exact_county     exactly one ONRC row with the key lies in the county of the record
  exact_elsewhere  exactly one ONRC row has the key, and it lies in another county
  ambiguous        several ONRC rows have the key (at most 5 are listed)
  none             no ONRC row has the key
The last column `onrc_code` is the ONRC registration number of the listed row (the survey queue had no such column).
`identity_rejects` is the rule of the brief for a new identity; the script writes no curation file.
Status:
  identity_candidate  no other record holds the CUI
  merge_candidate     another record holds the CUI (`cui_other_record`)
  ambiguous           the tier is ambiguous and no other record holds the CUI

Usage: python3 scripts/onrc_candidates.py [--onrc DIR] [--csv institutii.csv] [--out onrc-review.csv]
"""
import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from consolidate import fold  # noqa: E402  (consolidate.py imports openpyxl only inside its loaders)

ONRC_DIR = Path("/Volumes/geana/NAS-devbox/gov2/data.gov.ro-onrc-firme-2026-10-19")
INSTITUTII_CSV = ROOT / "data/consolidated/institutii.csv"
OUT_CSV = ROOT / "data/consolidated/onrc-review.csv"

MAX_LISTED = 5          # rows listed for one record in the tier `ambiguous`

COLUMNS = ["id", "record_name", "record_county", "category", "has_company_form", "tier", "status", "cui",
           "cui_other_record", "onrc_name", "onrc_county", "onrc_locality", "legal_form", "onrc_states",
           "in_function", "onrc_registration_date", "onrc_rows_total", "onrc_rows_same_county", "onrc_code"]

# State codes of N_STARE_FIRMA.csv. A company is not in function when one of these is set.
STATE_FUNCTION = {"1048", "1112"}
STATE_ENDED = {"1049", "1050", "1051", "1052", "1070", "1084", "1094", "1098", "1100", "1109", "1113", "1145"}


# ---------------------------------------------------------------- name key

def _strip_form(tokens):
    """Remove SA / S A / SRL / S R L / RA / R A wherever they stand in the token list."""
    forms = (["s", "r", "l"], ["s", "a"], ["r", "a"], ["srl"], ["sa"], ["ra"])
    out, i = [], 0
    while i < len(tokens):
        for f in forms:
            if tokens[i:i + len(f)] == f:
                i += len(f)
                break
        else:
            out.append(tokens[i])
            i += 1
    return out


def name_key(name):
    """Folded name without a leading SC (SC, S C, S.C.) and without the legal form at either end."""
    tokens = fold(name).split()
    if tokens[:2] == ["s", "c"] and len(tokens) > 2:
        tokens = tokens[2:]
    elif tokens[:1] == ["sc"] and len(tokens) > 1:
        tokens = tokens[1:]
    return " ".join(_strip_form(tokens))


def has_company_form(name):
    """True when the folded name holds SC / S C or SA, SRL, RA as a separate word (with the spaced spellings)."""
    t = fold(name).split()
    spaced = [t[i:i + 2] for i in range(len(t) - 1)] + [t[i:i + 3] for i in range(len(t) - 2)]
    return (any(x in ("sa", "srl", "ra", "sc") for x in t)
            or any(s in (["s", "a"], ["r", "a"], ["s", "r", "l"], ["s", "c"]) for s in spaced))


def name_forms(name):
    """The legal forms (SA, SRL, RA) that stand in the folded name as separate words, with the spaced spellings."""
    t = fold(name).split()
    found = {x.upper() for x in t if x in ("sa", "srl", "ra")}
    for i in range(len(t)):
        if t[i:i + 2] == ["s", "a"]:
            found.add("SA")
        elif t[i:i + 2] == ["r", "a"]:
            found.add("RA")
        elif t[i:i + 3] == ["s", "r", "l"]:
            found.add("SRL")
    return found


def identity_rejects(row, d_per_cui):
    """Rule for a new identity (brief onrc-identities, task 4). -> the reason a queue row fails, or "" when it passes.
    `d_per_cui` maps a CUI to the number of distinct D records that the whole queue matches to it."""
    if row["tier"] != "exact_county":
        return "tier " + row["tier"]
    if not has_company_form(row["record_name"]):
        return "no company form in the name"
    forms = name_forms(row["record_name"])
    if not forms:
        return "no form word in the name (only SC)"
    if row["legal_form"] not in forms:         # "R A T SRL" holds a false RA: the ONRC form must be one of the forms found
        return f"form conflict: name {'/'.join(sorted(forms))}, ONRC {row['legal_form']}"
    if str(row["onrc_rows_same_county"]) != "1":
        return "second ONRC row in the county"
    if row["cui_other_record"]:
        return "CUI on another record"
    if d_per_cui.get(row["cui"], 0) > 1:
        return "CUI matches another D record"
    if row["in_function"] != "yes":
        return "not in function: " + row["in_function"]
    return ""


# ---------------------------------------------------------------- ONRC readers

def read_rows(path):
    """Yield the data rows of an ONRC file as lists, split on `^` with no quote handling. The BOM is removed."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        next(fh)
        for line in fh:
            yield line.rstrip("\r\n").split("^")


def read_firme(path):
    """Yield OD_FIRME.csv rows as dicts. A row with a wrong column count is yielded as None.
    The split is on `^` only: a raw `"` in a name must not join lines or columns."""
    with open(path, encoding="utf-8-sig", newline="") as fh:
        header = next(fh).rstrip("\r\n").split("^")
        for line in fh:
            cells = line.rstrip("\r\n").split("^")
            yield dict(zip(header, cells)) if len(cells) == len(header) else None


def in_function(codes):
    """yes: in function and no ending state. no: an ending state is set. unknown: neither (for example insolvency)."""
    if not codes:
        return "unknown"
    if STATE_ENDED & set(codes):
        return "no"
    return "yes" if STATE_FUNCTION & set(codes) else "unknown"


# ---------------------------------------------------------------- matching

def match_rows(key, county_fold, onrc_by_key):
    """-> (tier, listed rows, rows total, rows in the county)."""
    rows = onrc_by_key.get(key, [])
    same = [r for r in rows if fold(r["ADR_JUDET"]) == county_fold]
    if not rows:
        return "none", [], 0, 0
    if len(same) == 1:
        return "exact_county", same, len(rows), 1
    if not same and len(rows) == 1:
        return "exact_elsewhere", rows, 1, 0
    return "ambiguous", (same or rows)[:MAX_LISTED], len(rows), len(same)


def load_records(path):
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def holders(records):
    """{cui: [record ids]} over the `cif` of all records."""
    out = defaultdict(list)
    for r in records:
        if r["cif"]:
            out[r["cif"]].append(r["id"])
    return out


def build_queue(records, onrc_by_key, states_by_code, state_names):
    """The rows of the review queue. `onrc_by_key` maps a name key to the ONRC row dicts."""
    held = holders(records)
    out = []
    for rec in sorted(records, key=lambda r: r["id"]):
        if not rec["id"].startswith("D") or rec["cif"]:
            continue
        key = name_key(rec["name"])
        base = {"id": rec["id"], "record_name": rec["name"], "record_county": rec["county"],
                "category": rec["category"], "has_company_form": int(has_company_form(rec["name"]))}
        tier, listed, total, same = match_rows(key, fold(rec["county"]), onrc_by_key) if key else ("none", [], 0, 0)
        if tier == "none":
            out.append({**base, "tier": "none", "status": "none", "cui": "", "cui_other_record": "",
                        "onrc_name": "", "onrc_county": "", "onrc_locality": "", "legal_form": "", "onrc_states": "",
                        "in_function": "", "onrc_registration_date": "", "onrc_rows_total": 0,
                        "onrc_rows_same_county": 0, "onrc_code": ""})
            continue
        for r in listed:
            cui = r["CUI"]
            other = " | ".join(held.get(cui, [])) if cui not in ("", "0") else ""
            codes = states_by_code.get(r["COD_INMATRICULARE"], [])
            status = "merge_candidate" if other else ("ambiguous" if tier == "ambiguous" else "identity_candidate")
            out.append({**base, "tier": tier, "status": status, "cui": cui, "cui_other_record": other,
                        "onrc_name": r["DENUMIRE"], "onrc_county": r["ADR_JUDET"], "onrc_locality": r["ADR_LOCALITATE"],
                        "legal_form": r["FORMA_JURIDICA"],
                        "onrc_states": "; ".join(state_names.get(c, c) for c in codes),
                        "in_function": in_function(codes), "onrc_registration_date": r["DATA_INMATRICULARE"],
                        "onrc_rows_total": total, "onrc_rows_same_county": same,
                        "onrc_code": r["COD_INMATRICULARE"]})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--onrc", type=Path, default=ONRC_DIR, help="folder with OD_FIRME.csv and the state files")
    ap.add_argument("--csv", type=Path, default=INSTITUTII_CSV)
    ap.add_argument("--out", type=Path, default=OUT_CSV)
    args = ap.parse_args()

    records = load_records(args.csv)
    wanted = {name_key(r["name"]) for r in records if r["id"].startswith("D") and not r["cif"]}
    wanted.discard("")
    print(f"{len(wanted)} distinct keys for the CIF-less D records", file=sys.stderr)

    onrc_by_key, bad, n = defaultdict(list), 0, 0
    for row in read_firme(args.onrc / "OD_FIRME.csv"):
        n += 1
        if row is None:
            bad += 1
            continue
        key = name_key(row["DENUMIRE"])
        if key in wanted and row["CUI"] not in ("", "0"):
            onrc_by_key[key].append(row)
    print(f"OD_FIRME: {n} rows, {bad} with a wrong column count, "
          f"{sum(len(v) for v in onrc_by_key.values())} matching a key", file=sys.stderr)

    codes_needed = {r["COD_INMATRICULARE"] for v in onrc_by_key.values() for r in v}
    states = defaultdict(list)
    for cells in read_rows(args.onrc / "OD_STARE_FIRMA.csv"):
        if cells[0] in codes_needed:
            states[cells[0]].append(cells[1])
    state_names = {cells[0]: cells[1] for cells in read_rows(args.onrc / "N_STARE_FIRMA.csv")}

    queue = build_queue(records, onrc_by_key, states, state_names)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(queue)
    ids = {}
    for q in queue:
        ids.setdefault(q["id"], q)
    counts = defaultdict(int)
    for q in ids.values():
        counts[q["tier"]] += 1
    print(f"{len(ids)} records, {len(queue)} rows: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())),
          file=sys.stderr)
    print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
