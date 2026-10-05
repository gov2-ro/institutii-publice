#!/usr/bin/env python3
"""Scrape the public institutions listed on https://roepas.ro/ro/institutii.

The page is an Angular widget backed by a Solr proxy (GET /search/search, filter
typeId=2 = institutions). Two steps:

1. list    - one API call returns every institution (name, address, county, city,
             procedure counts).
2. details - each institution has a page /ro/e/institutie/549157/<id> with contact
             data (phone, fax, email, website, map coordinates, org structure,
             assistance services). Fetched concurrently; results are appended to
             details.jsonl so an interrupted run resumes where it stopped.

Outputs (data/roepas/): list_response.json (raw API reply), details.jsonl,
institutii.json, institutii.csv.

Usage: python3 scripts/scrape_roepas.py [--workers 4] [--limit N]
"""
import argparse
import csv
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from lxml import html as lxml_html

BASE = "https://roepas.ro"
SEARCH_URL = f"{BASE}/search/search"
DETAIL_URL = f"{BASE}/ro/e/institutie/549157/{{id}}"
INSTITUTION_TYPE_ID = "2"
# Field list the site's own widget requests.
SOLR_FIELDS = (
    "id,nume,descriere,categorie_id,categorie_nume,domeniu_id,domeniu_nume,tip_id,tip_nume,tip,"
    "tipdisponibilitate_id,tipdisponibilitate_nume,judet_id,judet_nume,localitate_id,localitate_nume,"
    "institutie_id,institutie_nume,anexe_categ,publictinta_categ,tiparie_categ,proceduri_count,"
    "proceduri_online_count"
)
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "roepas"

session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0 (compatible; institutii-publice-research/0.1)"


def get(url, **kwargs):
    """GET with retries on network errors / 429 / 5xx. 404 is returned as-is."""
    for attempt in range(5):
        try:
            resp = session.get(url, timeout=30, **kwargs)
            if resp.status_code == 429 or resp.status_code >= 500:
                raise requests.HTTPError(f"{resp.status_code} for {url}")
            return resp
        except requests.RequestException:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def fetch_list():
    params = {
        "q": "*:*", "lang": "ro", "start": 0, "fl": SOLR_FIELDS, "wt": "json",
        "searchFields": "all", "sort": "nume_str asc", "typeId": INSTITUTION_TYPE_ID,
    }
    total = get(SEARCH_URL, params={**params, "rows": 1}).json()["total"]
    data = get(SEARCH_URL, params={**params, "rows": total}).json()
    ids = {r["id"] for r in data["results"]}
    if len(data["results"]) != total or len(ids) != total:
        sys.exit(f"list mismatch: total={total} rows={len(data['results'])} unique={len(ids)}")
    return data


def text_lines(el):
    """Non-empty stripped text nodes under el."""
    return [t.strip() for t in el.itertext() if t.strip()]


def section_body(tree, heading):
    """Body of a 'fragment-two-rows-visibility' block (heading row + content row) by heading text."""
    for h3 in tree.xpath(f'//h3[contains(normalize-space(.), "{heading}")]'):
        blocks = h3.xpath('ancestor::div[contains(@class,"fragment-two-rows-visibility")][1]')
        if blocks and len(blocks[0]) > 1:
            return blocks[0][1]
    return None


def parse_detail(page):
    tree = lxml_html.fromstring(page)

    def field(el_id):
        els = tree.xpath(f'//*[@id="{el_id}"]')
        return els[0].text_content().strip() or None if els else None

    website = tree.xpath('//*[@id="institution-website"]/@href')
    coords = field("map-coords")
    lat = lon = None
    if coords and re.fullmatch(r"\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*", coords):
        lat, lon = (float(x) for x in coords.split(","))

    def items(heading):
        body = section_body(tree, heading)
        if body is None or body.xpath('.//*[contains(@class,"c-empty-state")]'):
            return []
        return text_lines(body)

    return {
        "phone": field("institution-phone"),
        "fax": field("institution-fax"),
        "email": field("institution-email"),
        "website": (website[0].strip() or None) if website else None,
        "address_detail": field("institution-address"),
        "lat": lat,
        "lon": lon,
        "org_units": items("Organizare institu"),
        "assistance_services": items("Servicii de asisten"),
    }


def fetch_detail(inst_id):
    url = DETAIL_URL.format(id=inst_id)
    resp = get(url)
    out = {"id": inst_id, "detail_url": url, "detail_status": resp.status_code}
    if resp.status_code == 200:
        out.update(parse_detail(resp.text))
    return out


def website_url(raw):
    """Mirror the site's JS: add https:// when the scheme is missing; '-' / empty -> None."""
    if not raw or raw.strip() in {"-", "."}:
        return None
    raw = raw.strip()
    return raw if re.match(r"https?://", raw, re.I) else f"https://{raw}"


def load_done(path):
    done = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                done[rec["id"]] = rec
    return done


def fetch_details(ids, path, workers):
    done = load_done(path)
    todo = [i for i in ids if i not in done]
    print(f"details: {len(done)} cached, {len(todo)} to fetch", file=sys.stderr)
    with path.open("a", encoding="utf-8") as fh, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(fetch_detail, i): i for i in todo}
        for n, fut in enumerate(as_completed(futures), 1):
            rec = fut.result()
            done[rec["id"]] = rec
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
            if n % 250 == 0:
                print(f"  {n}/{len(todo)}", file=sys.stderr)
    return done


def merge(row, detail):
    rec = {
        "id": row["id"],
        "name": row["name"],
        "address": row["description"] or None,
        "county_id": row["countyId"],
        "county": row["countyLabel"],
        "city_id": row["cityId"],
        "city": row["cityLabel"],
        "procedures_count": row["proceduresCount"],
        "online_procedures_count": row["onlineProceduresCount"],
    }
    rec.update({k: detail.get(k) for k in ("phone", "fax", "email", "website")})
    rec["website_url"] = website_url(rec["website"])
    rec.update({k: detail.get(k) for k in ("lat", "lon")})
    rec["org_units"] = detail.get("org_units", [])
    rec["assistance_services"] = detail.get("assistance_services", [])
    # Detail-page address only kept when it disagrees with the list one (ignoring whitespace).
    squash = lambda a: " ".join((a or "").split())
    if detail.get("address_detail") and squash(detail["address_detail"]) != squash(rec["address"]):
        rec["address_detail"] = detail["address_detail"]
    rec["detail_url"] = detail["detail_url"]
    rec["detail_status"] = detail["detail_status"]
    return rec


def write_csv(path, records):
    cols = list(records[0])
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow({k: " | ".join(v) if isinstance(v, list) else v for k, v in r.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, help="only fetch details for the first N institutions (testing)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = fetch_list()
    (OUT_DIR / "list_response.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    rows = data["results"][: args.limit] if args.limit else data["results"]
    print(f"list: {len(rows)} institutions (site total {data['total']})", file=sys.stderr)

    details = fetch_details([r["id"] for r in rows], OUT_DIR / "details.jsonl", args.workers)
    records = [merge(r, details[r["id"]]) for r in rows]
    (OUT_DIR / "institutii.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=1), encoding="utf-8")
    write_csv(OUT_DIR / "institutii.csv", records)
    print(f"wrote {len(records)} records to {OUT_DIR}", file=sys.stderr)


if __name__ == "__main__":
    main()
