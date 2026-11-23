#!/usr/bin/env python3
"""Compare the entities of transparenta.eu with data/consolidated/institutii.csv.

Read-only. Changes no published data and writes no curation file.
Output: data/transparenta/entities-<date>.jsonl (raw pages) and data/transparenta/review.csv.
Stdlib only. The script never asks for `profile` (personal data).

  python3 scripts/transparenta_compare.py            # fetch, then compare
  python3 scripts/transparenta_compare.py --cached   # no request; read the newest entities-*.jsonl
"""
import argparse
import csv
import datetime
import glob
import json
import os
import sys
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cached", action="store_true", help="read the newest entities-*.jsonl; make no request")
    ap.add_argument("--limit", type=int, default=500, help="page size asked (default 500); the server caps it at 100")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.cached:
        files = sorted(glob.glob(os.path.join(OUT_DIR, "entities-*.jsonl")))
        if not files:
            sys.exit("No cached file in data/transparenta/")
        path = files[-1]
    else:
        path = os.path.join(OUT_DIR, f"entities-{datetime.date.today().isoformat()}.jsonl")
        fetch(a.limit, path)
    ents = read_entities(path)
    rows = compare(ents, load_ours())
    with open(os.path.join(OUT_DIR, "review.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows(rows)
    counts = {}
    for r in rows:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(f"entities there: {len(ents)}; file: {os.path.basename(path)}", file=sys.stderr)
    for k in ("missing_here", "non_anaf_here", "parents_differ", "missing_there"):
        print(f"{k}: {counts.get(k, 0)}", file=sys.stderr)


if __name__ == "__main__":
    main()
