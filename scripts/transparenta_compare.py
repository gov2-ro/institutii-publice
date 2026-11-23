#!/usr/bin/env python3
"""Compare the entities of transparenta.eu with data/consolidated/institutii.csv.

Read-only. Changes no published data and writes no curation file.
Output: data/transparenta/entities-<date>.jsonl (raw pages) and data/transparenta/review.csv.
Stdlib only. The script never asks for `profile` (personal data).

  python3 scripts/transparenta_compare.py            # fetch, then compare
  python3 scripts/transparenta_compare.py --cached   # no request; read the newest entities-*.jsonl
  python3 scripts/transparenta_compare.py --last-report   # --cached, then the date of the latest report of each
                                                          # `missing_here` CUI -> last-report-<date>.jsonl
  python3 scripts/transparenta_compare.py --candidates     # no transparenta.eu request. ANAF for the CUIs with a report in
                                                          # 2025 or 2026 -> anaf-<date>.json; MF status; then
                                                          # candidates.csv and parent-proposals.csv

Both options resume from a cache file of the same day. The queue files change no published data.
"""
import argparse
import csv
import datetime
import glob
import json
import os
import re
import sys
import unicodedata
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "data", "transparenta")
CSV_IN = os.path.join(ROOT, "data", "consolidated", "institutii.csv")
API = "https://api.transparenta.eu/graphql"
AGENT = "institutii-publice-check"
PAUSE = 2.0  # seconds between requests
QUERY = """query($limit: Int!, $offset: Int!) {
  entities(limit: $limit, offset: $offset) {
    nodes { cui name entity_type is_uat address parents { cui } uat { county_code } }
    pageInfo { totalCount hasNextPage }
  }
}"""
ANAF_API = "https://webservicesp.anaf.ro/api/PlatitorTvaRest/v9/tva"
ANAF_BATCH = 100  # CUIs per request (published limit)
ANAF_PAUSE = 1.1  # seconds between requests (published limit: 1 per second)
LAST_BATCH = 25  # aliased entity queries per request
MF_DIR = "/Volumes/geana/NAS-devbox/gov2/data.gov.ro-mf-platitori-2026-07"
CAND_FIELDS = ["cui", "their_name", "anaf_name", "entity_type", "county", "their_parents", "parent_in_our_data",
               "last_report", "anaf_status", "mf_status", "proposal"]
PARENT_FIELDS = ["our_id", "our_name", "cui", "their_parents", "parent_ids", "parent_names", "our_family", "conflict"]
FIELDS = ["kind", "cui", "their_name", "our_id", "our_name", "their_parents", "our_parents", "entity_type", "county"]


def norm(cui):
    """Digits only, no leading zeros."""
    d = "".join(ch for ch in str(cui or "") if ch.isdigit())
    return d.lstrip("0")


def post(limit, offset):
    body = json.dumps({"query": QUERY, "variables": {"limit": limit, "offset": offset}}).encode()
    req = urllib.request.Request(API, data=body, headers={
        "User-Agent": AGENT, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 or e.code >= 500:
            sys.exit(f"STOP: HTTP {e.code} at offset {offset}. Report it; do not retry.")
        sys.exit(f"STOP: HTTP {e.code} at offset {offset}: {e.read()[:300]!r}")


def fetch(limit, path):
    """Fetch all pages. Save the raw responses, one per line."""
    offset, requests, t0 = 0, 0, time.time()
    with open(path, "w", encoding="utf-8") as out:
        while True:
            if requests:
                time.sleep(PAUSE)
            resp = post(limit, offset)
            requests += 1
            if resp.get("errors") or not resp.get("data"):
                sys.exit(f"STOP: the server refused limit={limit} or needs a key: {json.dumps(resp.get('errors'))[:500]}")
            conn = resp["data"]["entities"]
            out.write(json.dumps({"offset": offset, "limit": limit, "response": resp}, ensure_ascii=False) + "\n")
            n = len(conn["nodes"])
            print(f"offset {offset}: {n} nodes, total {conn['pageInfo'].get('totalCount')}", file=sys.stderr)
            if not conn["pageInfo"].get("hasNextPage") or n == 0:
                break
            offset += n  # the server may cap the page below `limit`
    print(f"requests: {requests}, limit: {limit}, seconds: {time.time() - t0:.0f}", file=sys.stderr)


def read_entities(path):
    ents = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            for node in json.loads(line)["response"]["data"]["entities"]["nodes"]:
                ents[norm(node["cui"])] = node
    return ents


def load_ours():
    with open(CSV_IN, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parent_set(text):
    return {norm(p) for p in (text or "").split("|") if norm(p)}


def compare(ents, ours):
    by_cui = {}
    for r in ours:
        c = norm(r["cif"])
        if c:
            by_cui.setdefault(c, []).append(r)
    rows = []

    def theirs(cui, node):
        county = ((node.get("uat") or {}).get("county_code")) or ""
        return {"cui": cui, "their_name": node["name"], "entity_type": node.get("entity_type") or "",
                "their_parents": " | ".join(p["cui"] for p in node.get("parents") or []), "county": county}

    for cui, node in ents.items():
        recs = by_cui.get(cui, [])
        anaf = [r for r in recs if r["id"].startswith("A")]
        if anaf:
            r = anaf[0]
            if {norm(p["cui"]) for p in node.get("parents") or []} != parent_set(r["parent_cifs"]):
                rows.append({"kind": "parents_differ", **theirs(cui, node), "our_id": r["id"], "our_name": r["name"],
                             "our_parents": r["parent_cifs"]})
        elif recs:
            r = recs[0]
            rows.append({"kind": "non_anaf_here", **theirs(cui, node), "our_id": r["id"], "our_name": r["name"],
                         "our_parents": r["parent_cifs"]})
        else:
            rows.append({"kind": "missing_here", **theirs(cui, node), "our_id": "", "our_name": "", "our_parents": ""})
    for cui, recs in by_cui.items():
        if cui in ents:
            continue
        for r in recs:
            if r["id"].startswith("A"):
                rows.append({"kind": "missing_there", "cui": r["cif"], "their_name": "", "our_id": r["id"],
                             "our_name": r["name"], "their_parents": "", "our_parents": r["parent_cifs"],
                             "entity_type": "", "county": r["county"]})
    order = {"missing_here": 0, "non_anaf_here": 1, "parents_differ": 2, "missing_there": 3}
    rows.sort(key=lambda x: (order[x["kind"]], x["cui"]))
    return rows


def http_json(url, body, what):
    """POST a JSON body. Stop on 429 or 5xx. Returns the decoded answer."""
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "User-Agent": AGENT, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 429 or e.code >= 500:
            sys.exit(f"STOP: HTTP {e.code} at {what}. Report it; do not retry.")
        sys.exit(f"STOP: HTTP {e.code} at {what}: {e.read()[:300]!r}")


def date_of_ms(ms):
    """Epoch milliseconds (a string from the API) -> YYYY-MM-DD, or ''."""
    if not ms:
        return ""
    return datetime.datetime.fromtimestamp(int(ms) / 1000, datetime.timezone.utc).strftime("%Y-%m-%d")


def fetch_last_reports(cuis, path):
    """One aliased request per LAST_BATCH CUIs. One cache line per CUI: {cui, last_report_ms, report_type}.
    A CUI that the cache holds is not asked again. The query never asks for `profile`."""
    done = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            done = {json.loads(l)["cui"]: 1 for l in f if l.strip()}
    todo = [c for c in cuis if c not in done]
    requests, t0 = 0, time.time()
    with open(path, "a", encoding="utf-8") as out:
        for i in range(0, len(todo), LAST_BATCH):
            chunk = todo[i:i + LAST_BATCH]
            if not all(c.isdigit() for c in chunk):
                sys.exit("STOP: a CUI is not digits")
            if requests:
                time.sleep(PAUSE)
            q = "{" + " ".join(
                f'e{n}: entity(cui: "{c}") {{ cui reports(limit: 1, sort: {{by: "report_date", order: "DESC"}}) '
                f'{{ nodes {{ report_date report_type }} }} }}' for n, c in enumerate(chunk)) + "}"
            resp = http_json(API, {"query": q}, f"last-report batch {i}")
            requests += 1
            if resp.get("errors") or not resp.get("data"):
                sys.exit(f"STOP: the server refused the batch: {json.dumps(resp.get('errors'))[:500]}")
            for n, c in enumerate(chunk):
                e = resp["data"].get(f"e{n}")
                nodes = ((e or {}).get("reports") or {}).get("nodes") or []
                out.write(json.dumps({"cui": c, "found": e is not None,
                                      "last_report_ms": nodes[0]["report_date"] if nodes else "",
                                      "report_type": nodes[0]["report_type"] if nodes else ""}) + "\n")
            out.flush()
            print(f"last-report: {min(i + LAST_BATCH, len(todo))}/{len(todo)}", file=sys.stderr)
    print(f"last-report requests: {requests}, CUIs asked: {len(todo)}, seconds: {time.time() - t0:.0f}", file=sys.stderr)


def read_last_reports(path):
    with open(path, encoding="utf-8") as f:
        return {d["cui"]: d for d in map(json.loads, (l for l in f if l.strip()))}


def fetch_anaf(cuis, path):
    """ANAF PlatitorTvaRest v9, at most ANAF_BATCH CUIs per request, 1 request per second.
    Keeps only company fields: name, address, county, registration text, inactive flag. Resumes from `path`."""
    cache = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cache = json.load(f)
    todo = [c for c in cuis if c not in cache]
    today = datetime.date.today().isoformat()
    requests, t0 = 0, time.time()
    for i in range(0, len(todo), ANAF_BATCH):
        chunk = todo[i:i + ANAF_BATCH]
        if requests:
            time.sleep(ANAF_PAUSE)
        resp = http_json(ANAF_API, [{"cui": int(c), "data": today} for c in chunk], f"ANAF batch {i}")
        requests += 1
        if resp.get("cod", 200) != 200 or not ("found" in resp or "notFound" in resp):
            sys.exit(f"STOP: ANAF answered {str(resp)[:300]}")
        for d in resp.get("found") or []:
            g, inact, sed = d["date_generale"], d.get("stare_inactiv") or {}, d.get("adresa_sediu_social") or {}
            cache[str(g["cui"])] = {"denumire": g.get("denumire", ""), "adresa": g.get("adresa", ""),
                                    "county": sed.get("scod_JudetAuto", ""), "county_name": sed.get("sdenumire_Judet", ""),
                                    "stare_inregistrare": g.get("stare_inregistrare", ""),
                                    "inactive": bool(inact.get("statusInactivi")), "data_radiere": inact.get("dataRadiere", "")}
        for c in resp.get("notFound") or []:
            cache[str(c)] = None
        for c in chunk:
            cache.setdefault(c, None)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        print(f"anaf: {min(i + ANAF_BATCH, len(todo))}/{len(todo)}", file=sys.stderr)
    print(f"anaf requests: {requests}, CUIs asked: {len(todo)}, seconds: {time.time() - t0:.0f}", file=sys.stderr)
    return cache


def fold(text):
    t = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def same_name(a, b):
    """Token overlap of the folded names (the smaller set counts) >= 0.6."""
    ta, tb = set(fold(a).split()), set(fold(b).split())
    return bool(ta and tb) and len(ta & tb) / min(len(ta), len(tb)) >= 0.6


def anaf_state(rec):
    """-> text for the column anaf_status: active, inactive, radiat, not_found, or other:<text>."""
    if rec is None:
        return "not_found"
    stare = (rec["stare_inregistrare"] or "").upper()
    if stare.startswith("RADIERE") or rec["data_radiere"]:
        return "radiat"
    if rec["inactive"]:
        return "inactive"
    if stare.startswith(("INREGISTRAT", "MODIFICARE PUBLICI", "TRANSFER", "RELUARE ACTIVITATE")):
        return "active"
    return "other:" + stare[:40]


def ours_by_cui(ours):
    """CUI -> our record; an ANAF record wins over another kind."""
    by = {}
    for r in ours:
        c = norm(r["cif"])
        if c and (c not in by or (r["id"].startswith("A") and not by[c]["id"].startswith("A"))):
            by[c] = r
    return by


def build_candidates(rows, ents, last, anaf, mf, by_cui):
    out = []
    for r in rows:
        if r["kind"] != "missing_here":
            continue
        cui = r["cui"]
        ms = (last.get(cui) or {}).get("last_report_ms", "")
        lr = date_of_ms(ms)
        a = anaf.get(cui) if cui in anaf else "not_called"
        parents = [norm(p) for p in r["their_parents"].split("|") if norm(p)]
        found = [by_cui[p]["id"] for p in parents if p in by_cui]
        astate = "not_called" if a == "not_called" else anaf_state(a)
        mst = mf.get(cui, "not_found")
        recent = lr[:4] in ("2025", "2026")
        if not recent or astate == "radiat" or mst in ("radiat", "fuzionat"):
            prop = "skip"
        else:
            ok_name = a not in (None, "not_called") and same_name(r["their_name"], a["denumire"])
            ok_county = a not in (None, "not_called") and (not r["county"] or not a["county"] or r["county"] == a["county"])
            prop = "add" if (astate == "active" and mst != "in_lichidare" and found and ok_name and ok_county) else "check"
        out.append({"cui": cui, "their_name": r["their_name"],
                    "anaf_name": a["denumire"] if isinstance(a, dict) else "", "entity_type": r["entity_type"],
                    "county": r["county"], "their_parents": r["their_parents"], "parent_in_our_data": " | ".join(found),
                    "last_report": lr, "anaf_status": astate, "mf_status": mst, "proposal": prop})
    return out


SCHOOL_RE = re.compile(r"\b(scoala|gradinita|liceul|colegiul|liceu|scolar)\b")


def build_parent_proposals(rows, ours, by_cui):
    """For each non_anaf_here row: our record of each parent CUI. `conflict` when the pair of categories is rare
    (under 1% of the parents of that category among ANAF records) for every parent, or when a school has no
    parent that is a local authority or an ISJ (a school with a ministry and a UAT is normal: two parent columns)."""
    anaf = {norm(r["cif"]): r for r in ours if r["id"].startswith("A")}
    pairs, tot = {}, {}
    for r in anaf.values():
        for p in parent_set(r["parent_cifs"]):
            if p in anaf:
                k = (r["category"], anaf[p]["category"])
                pairs[k] = pairs.get(k, 0) + 1
                tot[r["category"]] = tot.get(r["category"], 0) + 1
    by_id = {r["id"]: r for r in ours}
    out = []
    for r in rows:
        if r["kind"] != "non_anaf_here":
            continue
        rec = by_id[r["our_id"]]
        parents = [norm(p) for p in r["their_parents"].split("|") if norm(p)]
        pr = [by_cui[p] for p in parents if p in by_cui]
        conflict = []
        if pr:
            rare = [tot.get(rec["category"]) and pairs.get((rec["category"], p["category"]), 0) / tot[rec["category"]] < 0.01
                    for p in pr]
            if all(rare):
                conflict.append("category")
            if SCHOOL_RE.search(fold(rec["name"])) and not any(
                    p["category"] == "Administrație locală" or fold(p["name"]).startswith("inspectoratul") for p in pr):
                conflict.append("school without UAT or ISJ parent")
        out.append({"our_id": r["our_id"], "our_name": r["our_name"], "cui": r["cui"], "their_parents": r["their_parents"],
                    "parent_ids": " | ".join(p["id"] for p in pr), "parent_names": " | ".join(p["name"] for p in pr),
                    "our_family": rec["family"], "conflict": ", ".join(sorted(set(conflict)))})
    return out


def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cached", action="store_true", help="read the newest entities-*.jsonl; make no request")
    ap.add_argument("--last-report", action="store_true", help="read the cache, ask the latest report date of each missing_here CUI")
    ap.add_argument("--candidates", action="store_true", help="ANAF + MF for the CUIs with a recent report; write candidates.csv and parent-proposals.csv")
    ap.add_argument("--mf", default=MF_DIR, help="folder with the two MF July files (for --candidates)")
    ap.add_argument("--limit", type=int, default=500, help="page size asked (default 500); the server caps it at 100")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.cached or a.last_report or a.candidates:
        files = sorted(glob.glob(os.path.join(OUT_DIR, "entities-*.jsonl")))
        if not files:
            sys.exit("No cached file in data/transparenta/")
        path = files[-1]
    else:
        path = os.path.join(OUT_DIR, f"entities-{datetime.date.today().isoformat()}.jsonl")
        fetch(a.limit, path)
    ents = read_entities(path)
    ours = load_ours()
    rows = compare(ents, ours)
    write_csv(os.path.join(OUT_DIR, "review.csv"), FIELDS, rows)
    today = datetime.date.today().isoformat()
    if a.last_report or a.candidates:
        lpath = os.path.join(OUT_DIR, f"last-report-{today}.jsonl")
        missing = [r["cui"] for r in rows if r["kind"] == "missing_here"]
        if a.last_report:
            fetch_last_reports(missing, lpath)
    if a.candidates:
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import lookup_status
        last = read_last_reports(lpath)
        recent = [c for c in missing if date_of_ms((last.get(c) or {}).get("last_report_ms", ""))[:4] in ("2025", "2026")]
        anaf = fetch_anaf(recent, os.path.join(OUT_DIR, f"anaf-{today}.json"))
        found, snap, _ = lookup_status.read_mf(a.mf, set(missing))
        mf = {c: lookup_status.status_of(v["status_label"]) for c, v in found.items()}
        by_cui = ours_by_cui(ours)
        cands = build_candidates(rows, ents, last, anaf, mf, by_cui)
        write_csv(os.path.join(OUT_DIR, "candidates.csv"), CAND_FIELDS, cands)
        props = build_parent_proposals(rows, ours, by_cui)
        write_csv(os.path.join(OUT_DIR, "parent-proposals.csv"), PARENT_FIELDS, props)
        from collections import Counter
        print(f"MF snapshot {snap}; candidates: {dict(Counter(c['proposal'] for c in cands))}", file=sys.stderr)
        print(f"parent proposals: {len(props)}; parent found: {sum(1 for p in props if p['parent_ids'])}; "
              f"conflicts: {sum(1 for p in props if p['conflict'])}", file=sys.stderr)
    counts = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"entities there: {len(ents)}; file: {os.path.basename(path)}", file=sys.stderr)
    for k in ("missing_here", "non_anaf_here", "parents_differ", "missing_there"):
        print(f"{k}: {counts.get(k, 0)}", file=sys.stderr)


if __name__ == "__main__":
    main()
