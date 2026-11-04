#!/usr/bin/env python3
# /// script
# dependencies = ["openpyxl", "xlrd"]
# ///
"""Extract the contracting authorities (name + CUI) from the SEAP procurement dump on data.gov.ro.

The dump is the "Achizitii publice <year>" datasets (publisher ADR). Every report has the authority name in
column 0 and its CUI in column 1. Files come as .xls (some are xlsx inside), .xlsx, .ods and `|`-separated .csv.

    uv run scripts/extract_seap.py [--dump DIR] [--trust ID_PREFIX ...]

Reads `DIR/packages.json` (CKAN metadata). A local file belongs to the resource whose id starts with the 8
characters before the first "-" of the file name. A file is read only if its byte size equals the resource `size`.
`--trust` reads a file whose metadata is known to be wrong.

Writes data/seap/authorities.csv, data/seap/manifest.json and one cache file per resource in data/seap/cache/.
A cache file is valid for the same file size and SHA-256, so a re-run reads only new or changed files.
The outputs depend only on the input files: not on the hash seed, the clock or the file order.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote, unquote
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DUMP = Path("/Volumes/geana/NAS-devbox/gov2/data.gov.ro-adr-achizitii-publice-dump")
OUT_DIR = ROOT / "data/seap"

EXTRA_COLS = ("tip_autoritate", "tip_activitate", "locality", "county")
EXTRA_HEADERS = (("tip autoritate", "tip_autoritate"), ("tip activitate", "tip_activitate"),
                 ("localitate", "locality"), ("judet", "county"))
CACHE_FORMAT = "3"
CACHE_COLS = ["cui", "name", *EXTRA_COLS, "rows"]
AUTH_COLS = ["cui", "name", "names", "first_seen", "last_seen", "rows", "report_types", *EXTRA_COLS]
NBSP = "   "


def squash(s):
    """Whitespace (nbsp too) collapsed to single spaces; None -> ''."""
    s = "" if s is None else str(s)
    for ch in NBSP:
        s = s.replace(ch, " ")
    return re.sub(r"\s+", " ", s).strip()


# --- CUI -------------------------------------------------------------------------------------------------

SCI = re.compile(r"(\d+)(?:[.,](\d+))?E([+-]?\d+)")


def normalize_cui(raw):
    """A raw CUI cell -> the CUI as a string of 2-10 digits with no leading zero, or None (reject).
    Removes spaces, an RO (or R) prefix and a trailing trade register number. Expands scientific notation only if no digit is invented: the exponent must
    not exceed the number of decimals ("1.2345E+4" = 12345; "1.8839E+14" is a rounded 15-digit value: reject)."""
    s = re.sub(r"\s+", "", squash(raw)).upper()
    s = re.sub(r"^(?:RO|R)(?=\d)", "", s)                   # RO or a typo R in front of the digits
    s = re.sub(r"(?<=\d)/J\d.*$", "", s)                    # a trade register number after the CUI ("RO123/J13/60/1")
    m = SCI.fullmatch(s)
    if m:
        exp = int(m.group(3))
        if exp < 0 or exp > len(m.group(2) or ""):
            return None
        try:
            s = str(int(Decimal(f"{m.group(1)}.{m.group(2) or '0'}E{exp}")))
        except (InvalidOperation, ValueError):
            return None
    elif re.fullmatch(r"\d+\.0+", s):
        s = s.split(".")[0]
    if not s.isdigit():
        return None
    s = s.lstrip("0")
    return s if 2 <= len(s) <= 10 else None


# --- file readers (rows of str) ------------------------------------------------------------------------------

def cell_str(v):
    if v is None:
        return ""
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def iter_ods(path):
    """Rows of an .ods file. pandas+odfpy is too slow: stream `content.xml`."""
    ns = "{urn:oasis:names:tc:opendocument:xmlns:"
    t_, x_ = ns + "table:1.0}", ns + "text:1.0}"
    with zipfile.ZipFile(path) as z, z.open("content.xml") as f:
        for ev, el in ET.iterparse(f, events=("end",)):
            if el.tag != t_ + "table-row":
                continue
            row = []
            for c in el:
                if c.tag not in (t_ + "table-cell", t_ + "covered-table-cell"):
                    continue
                rep = int(c.get(t_ + "number-columns-repeated", "1"))
                v = "".join("".join(p.itertext()) for p in c.findall(x_ + "p"))
                row.extend([v] * (1 if rep > 50 and v == "" else min(rep, 50)))
            while row and row[-1] == "":
                row.pop()
            if row or int(el.get(t_ + "number-rows-repeated", "1")) == 1:
                yield row
            el.clear()


def iter_rows(path):
    """Rows (list of str) of every sheet. The format follows the magic bytes, not the extension."""
    path = Path(path)
    with path.open("rb") as fh:
        magic = fh.read(4)
    if magic == b"\xd0\xcf\x11\xe0":
        import xlrd
        wb = xlrd.open_workbook(str(path), on_demand=True, logfile=open("/dev/null", "w"))
        for i in range(wb.nsheets):
            sh = wb.sheet_by_index(i)
            for r in range(sh.nrows):
                yield [cell_str(v) for v in sh.row_values(r)]
            wb.unload_sheet(i)
    elif magic[:2] == b"PK":
        with zipfile.ZipFile(path) as z:
            is_ods = "content.xml" in z.namelist()
        if is_ods:
            yield from iter_ods(path)
        else:
            import openpyxl
            wb = openpyxl.load_workbook(str(path), read_only=True)
            for ws in wb.worksheets:
                ws.reset_dimensions()               # some exports declare a wrong sheet size
                for r in ws.iter_rows(values_only=True):
                    yield [cell_str(v) for v in r]
            wb.close()
    else:
        csv.field_size_limit(1 << 28)
        data = path.read_bytes()
        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = data.decode("cp1250", errors="replace")      # some exports are Windows-1250
        del data
        head = text[:text.find("\n")]
        if "|,|" in head:                       # 2022 style: |value|,|value| (comma-separated, "|" is the quote)
            yield from csv.reader(io.StringIO(text, newline=""), delimiter=",", quotechar="|")
        else:
            yield from csv.reader(io.StringIO(text, newline=""), delimiter=max("|;\t,", key=head.count))


# --- one file ------------------------------------------------------------------------------------------------

def extra_columns(header):
    """{column index: field} for the 2023 columns: type of authority and activity, locality, county."""
    out = {}
    for i, h in enumerate(header):
        h = header_text(h)
        for prefix, field in EXTRA_HEADERS:
            if i > 0 and field not in out.values() and h.startswith(prefix):
                out[i] = field
    return out


NOT_AUTHORITY = re.compile(r"ofert|castigator|furnizor")
NAME_HEADER = re.compile(r"autorit|denumire|nume|contractant")


def header_text(cell):
    return squash(str(cell).replace("_", " ")).lower()


def cui_column(row):
    """The index of the authority CUI column in a header row, or None. It is the first cell that contains "CUI"
    (or ends the long form "autoritate contractanta c" of the 2018-2021 reports) and is not a bidder column.
    The authority name must be the cell before it (columns 0 and 1 in almost every report). A header whose
    previous cell does not look like an authority name is not accepted: it would read a bidder as an authority."""
    for i, cell in enumerate(row):
        h = header_text(cell)
        if i > 0 and len(h) < 80 and not NOT_AUTHORITY.search(h) and (
                "cui" in h or re.fullmatch(r"autoritate contractanta c", h)):
            return i if NAME_HEADER.search(header_text(row[i - 1])) and not NOT_AUTHORITY.search(header_text(row[i - 1])) else None
    return None


def read_authorities(rows, sample=None):
    """Iterable of rows -> (Counter {(cui, name, *extra): rows}, data rows, rejected rows, header found).
    The header is the first row with a CUI cell (`cui_column`). Rows above it are title rows.
    A blank row is skipped. A header row inside the data starts a new layout (some files join two reports).
    A row whose CUI does not normalize is a reject (blank CUI, text, 15-digit value...)."""
    counts, ci, extras, n, rejects = Counter(), None, {}, 0, 0
    for r in rows:
        if ci is None:
            ci = cui_column(r)
            if ci is not None:
                extras = extra_columns(r)
            continue
        cell = lambda k: r[k] if k < len(r) else ""
        if not squash(cell(ci - 1)) and not squash(cell(ci)):
            continue
        n += 1
        cui = normalize_cui(cell(ci))
        if cui is None:
            head = cui_column(r)
            if head is not None:                    # a header row inside the data: a new section with its own layout
                ci, extras = head, extra_columns(r)
                n -= 1
            else:
                rejects += 1
                if sample is not None and len(sample) < 400:
                    sample.append(squash(cell(ci))[:30])
            continue
        got = {f: squash(cell(i)) for i, f in extras.items()}
        counts[(cui, squash(cell(ci - 1)).replace("|", "/"), *(got.get(f, "") for f in EXTRA_COLS))] += 1
    return counts, n, rejects, ci is not None


# --- dump metadata ---------------------------------------------------------------------------------------------

def report_type(text):
    f = re.sub(r"[^a-z0-9]+", " ", text.lower())
    for pat, label in ((r"modificare", "modificare_contract"), (r"\b(fara|fr)\b.*\banun", "atribuire_fara_anunt"),
                       (r"invita", "invitatii_sad"), (r"notific", "notificari_directa"),
                       (r"ini\w*ere|intiere", "anunturi_initiere"), (r"contract", "contracte"),
                       (r"direct", "achizitii_directe")):
        if re.search(pat, f):
            return label
    return "other"


QUARTER = re.compile(r"(?<![a-z])t[ _-]?(iv|iii|ii|i|[1-4])(?![a-z])")
QUARTER_NO = {"i": 1, "ii": 2, "iii": 3, "iv": 4}


def period(file_name, title):
    """'2025-Q2' from the quarter and the year in the file name; '2025' for no quarter. A file name without a year
    takes the first year in the dataset title (the title "Achizitii publice 2007-2015" covers files of 2008-2016)."""
    year = re.search(r"(?<![0-9a-z])(20\d\d)(?![0-9a-z])", file_name.lower().replace("_", " ")) \
        or re.search(r"\b(20\d\d)\b", title)
    year = year.group(1) if year else ""
    m = QUARTER.search(file_name.lower().replace(".", " "))
    if not m:
        return year
    q = m.group(1)
    return f"{year}-Q{QUARTER_NO.get(q) or int(q)}"


def load_resources(dump):
    """{8-character id prefix: resource dict with title and package} from packages.json."""
    out = {}
    for pkg in json.loads((dump / "packages.json").read_text(encoding="utf-8")):
        for res in pkg["resources"]:
            prefix = res["id"][:8]
            if prefix in out:
                raise SystemExit(f"packages.json: resource id prefix {prefix} is not unique")
            out[prefix] = {"id": res["id"], "name": res.get("name") or "", "size": res.get("size"),
                           "url_file": res["url"].rsplit("/", 1)[-1], "title": pkg["title"]}
    return out


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 22), b""):
            h.update(block)
    return h.hexdigest()


def read_cache(path, size=None, sha=None):
    """A cache file -> {"counts", "rows", "rejects", "meta"}, or None. With `size` and `sha`, it must match them
    (the file is there). Without them, any cache of the current format is valid (the file is gone). The meta holds
    size, sha256, file, period and report_type: all that the manifest and authorities.csv need."""
    if not path.exists():
        return None
    with path.open(encoding="utf-8", newline="") as fh:
        meta = {k: unquote(v) for k, v in (kv.split("=", 1) for kv in fh.readline().lstrip("# ").split())}
        if meta.get("format") != CACHE_FORMAT or (size is not None and (
                meta.get("size") != str(size) or meta.get("sha256") != sha)):
            return None
        rows = list(csv.DictReader(fh))
    return {"counts": Counter({tuple(r[c] for c in CACHE_COLS[:-1]): int(r["rows"]) for r in rows}),
            "rows": int(meta["rows"]), "rejects": int(meta["rejects"]), "meta": meta}


def write_cache(path, counts, rows, rejects, **meta):
    """meta: size, sha256, file, period, report_type (None is written as an empty value)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    head = " ".join(f"{k}={quote(str(v if v is not None else ''), safe='')}" for k, v in meta.items())
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(f"# format={CACHE_FORMAT} rows={rows} rejects={rejects} {head}\n")
        w = csv.writer(fh)
        w.writerow(CACHE_COLS)
        for key in sorted(counts):
            w.writerow([*key, counts[key]])


# --- aggregation -----------------------------------------------------------------------------------------------

def aggregate(files):
    """files: [{"period", "report_type", "counts"}] -> sorted list of authority dicts (one per CUI).
    `name`: the most frequent name; ties go to the newest period, then to the alphabetical order."""
    per = defaultdict(lambda: {"names": defaultdict(lambda: [0, ""]), "rows": 0, "periods": set(), "types": set(),
                               **{f: Counter() for f in EXTRA_COLS}})
    for f in files:
        for (cui, name, *extra), n in f["counts"].items():
            a = per[cui]
            a["rows"] += n
            a["periods"].add(f["period"])
            a["types"].add(f["report_type"])
            if name:
                cnt = a["names"][name]
                cnt[0] += n
                cnt[1] = max(cnt[1], f["period"])
            for field, v in zip(EXTRA_COLS, extra):
                if v:
                    a[field][v] += n
    out = []
    for cui in sorted(per, key=int):
        a = per[cui]
        ranked = sorted(a["names"].items(), key=lambda kv: (-kv[1][0], _neg(kv[1][1]), kv[0]))
        row = {"cui": cui, "name": ranked[0][0] if ranked else "",
               "names": "|".join(n for n, _ in ranked[1:]),
               "first_seen": min(a["periods"]), "last_seen": max(a["periods"]), "rows": a["rows"],
               "report_types": "|".join(sorted(a["types"]))}
        for field in EXTRA_COLS:
            row[field] = min(a[field].items(), key=lambda kv: (-kv[1], kv[0]))[0] if a[field] else ""
        out.append(row)
    return out


def _neg(s):
    """Sort key: the newest period first (a string sorted in reverse)."""
    return tuple(-ord(c) for c in s)


# --- main --------------------------------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
    ap.add_argument("--trust", action="append", default=[], metavar="ID_PREFIX",
                    help="read this file although its size differs from the metadata (checked by hand)")
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    dump, out = args.dump, args.out
    resources = load_resources(dump)
    unknown = sorted(set(args.trust) - set(resources))
    if unknown:
        raise SystemExit(f"--trust: no resource with the id prefix {unknown}")
    local = defaultdict(list)
    for p in sorted(dump.rglob("*")):
        if p.is_file() and p.name != "packages.json":
            local[p.name.split("-", 1)[0]].append(p)
    manifest, parsed = [], []
    for prefix in sorted(set(resources) | set(local)):
        res, paths = resources.get(prefix), local.get(prefix, [])
        if len([p for p in paths if p.suffix != ".part"]) > 1:
            raise SystemExit(f"{prefix}: several local files {[p.name for p in paths]}")
        path = next((p for p in paths if p.suffix != ".part"), None)
        part = next((p for p in paths if p.suffix == ".part"), None)
        entry = {"resource": res["id"] if res else prefix, "file": None, "size": None, "metadata_size": None,
                 "sha256": None, "rows": None, "authorities": None, "rejects": None, "status": None,
                 "report_type": None, "period": None}
        if res:
            entry.update(metadata_size=res["size"], name=res["name"])
        cache = out / "cache" / f"{res['id']}.csv" if res else None
        if path is None and part is None and res and (got := read_cache(cache)) and (
                got["meta"]["size"] == str(res["size"]) or prefix in args.trust):
            m = got["meta"]                 # the file is gone, the cache stays: it holds all that authorities.csv needs
            entry.update(file=m.get("file") or None, size=int(m["size"]), sha256=m["sha256"], rows=got["rows"],
                         rejects=got["rejects"], authorities=len({k[0] for k in got["counts"]}), status="cached",
                         report_type=m.get("report_type") or report_type(res["url_file"]),
                         period=m.get("period") or period(res["url_file"], res["title"]))
            parsed.append({"period": entry["period"], "report_type": entry["report_type"], "counts": got["counts"]})
            manifest.append(entry)
            continue
        if path is None:
            entry["file"] = part.relative_to(dump).as_posix() if part else None
            entry["status"] = "part" if part else "missing"
            try:
                entry["size"] = part.stat().st_size if part else None
            except FileNotFoundError:               # the download finished while this script ran
                entry["size"] = None
            manifest.append(entry)
            continue
        entry.update(file=path.relative_to(dump).as_posix(), size=path.stat().st_size,
                     report_type=report_type(res["name"] if prefix in args.trust else path.name), period=period(path.name, res["title"]) if res else None)
        if not res:
            entry["status"] = "no_resource"
        elif res["size"] is None and prefix not in args.trust:
            entry["status"] = "no_size"             # the metadata has no size (2016-2019 datasets): completeness is unknown
        elif entry["size"] != res["size"] and prefix not in args.trust:
            entry["status"] = "incomplete"
        else:
            sha = sha256_of(path)
            got = read_cache(cache, entry["size"], sha)
            if got is not None and got["meta"].get("period") != entry["period"]:   # no period in the meta, or a stale one
                write_cache(cache, got["counts"], got["rows"], got["rejects"], size=entry["size"], sha256=sha,
                            file=entry["file"], period=entry["period"], report_type=entry["report_type"])
            if got is None:
                sample = []
                counts, n, rejects, found = read_authorities(iter_rows(path), sample)
                got = {"counts": counts, "rows": n, "rejects": rejects}
                if found:
                    write_cache(cache, counts, n, rejects, size=entry["size"], sha256=sha, file=entry["file"],
                                period=entry["period"], report_type=entry["report_type"])
                print(f"read {path.name[:70]}: {n} rows, {len(counts)} distinct, {rejects} rejects"
                      + ("" if found else " (NO HEADER)")
                      + (f"; reject samples {Counter(sample).most_common(4)}" if rejects > 200 else ""), file=sys.stderr)
                if not found:
                    entry["status"] = "no_header"
            if entry["status"] is None:
                entry["status"] = "trusted" if entry["size"] != res["size"] else "read"
            entry.update(sha256=sha, rows=got["rows"], rejects=got["rejects"],
                         authorities=len({k[0] for k in got["counts"]}))
            if entry["status"] in ("read", "trusted"):
                parsed.append({"period": entry["period"], "report_type": entry["report_type"],
                               "counts": got["counts"]})
        manifest.append(entry)
    authorities = aggregate(parsed)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "authorities.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=AUTH_COLS, lineterminator="\n")
        w.writeheader()
        w.writerows(authorities)
    (out / "manifest.json").write_text(json.dumps({"dump": dump.name, "files": manifest}, ensure_ascii=False,
                                                  indent=1, sort_keys=True) + "\n", encoding="utf-8")
    summary(manifest, authorities)


def summary(manifest, authorities):
    st = Counter(e["status"] for e in manifest)
    print(f"\nresources: {len(manifest)}; status {dict(sorted(st.items()))}", file=sys.stderr)
    used = [e for e in manifest if e["status"] in ("read", "trusted", "cached")]
    print(f"files used: {len(used)}; data rows {sum(e['rows'] for e in used)}; "
          f"rejected rows {sum(e['rejects'] for e in used)}", file=sys.stderr)
    for e in manifest:
        if e["status"] not in ("read", "trusted", "cached", "missing"):
            print(f"  {e['status']}: {e['file']}", file=sys.stderr)
    for e in used:
        if e["rows"] and e["rejects"] / e["rows"] > 0.05:
            print(f"  warning: {e['file']}: {e['rejects']} of {e['rows']} rows rejected", file=sys.stderr)
    print(f"distinct authority CUIs: {len(authorities)}", file=sys.stderr)


if __name__ == "__main__":
    main()
