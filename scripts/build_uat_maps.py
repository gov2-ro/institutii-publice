#!/usr/bin/env python3
"""Split the UAT boundary file into one small map file per county, for the explorer's county profile.

Input: docs/reference/gis/ro_admin_lau_simplified_polygon.geojson (LAU polygons, one feature per UAT,
SIRUTA code in `natCode`, county code in `countyMn`). The file is not in git; copy it from the owner's
checkout.

Output: explorer/assets/gis/uat/<COD>.json, one per county (B = București, by sector):
  {"county": "CJ", "version": "...", "uats": [{"s": siruta, "n": "COMUNA X", "l": "X", "k": "c",
   "p": [lon, lat], "g": [[[[lon, lat], ...], ...], ...]}]}
`n` is the ANAF-style name that the page joins on, `l` the display label, `k` the kind (m/o/c/s),
`p` the label point (pole of inaccessibility of the largest polygon), `g` the polygons.
Coordinates keep 4 decimals (about 10 m).

    python3 scripts/build_uat_maps.py [--src PATH]
"""
import argparse
import heapq
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'docs/reference/gis/ro_admin_lau_simplified_polygon.geojson'
OUT = ROOT / 'explorer/assets/gis/uat'
KIND = {'Comuna': ('c', 'COMUNA'), 'Oras': ('o', 'ORASUL'),
        'Municipiu resedinta de judet': ('m', 'MUNICIPIUL'),
        'Municipiu, altul decat resedinta de judet': ('m', 'MUNICIPIUL'),
        'Sectoarele municipiului Bucuresti': ('s', 'SECTORUL')}


def label_of(name):
    # the source capitalizes the letter after a diacritic ("MăGura", "șTefan"): a capital right after a letter is that bug,
    # and a word that starts with a diacritic lost its capital
    name = re.sub(r'(?<=[^\W\d_])([A-ZĂÂÎȘȚŞŢ])', lambda m: m.group(1).lower(), name)
    return re.sub(r'(?:^|(?<=[ -]))([ăâîșțşţ])', lambda m: m.group(1).upper(), name)


def round_ring(ring):
    out = []
    for x, y in ring:
        p = [round(x, 4), round(y, 4)]
        if not out or p != out[-1]:
            out.append(p)
    return out if len(out) >= 4 else None


def ring_area(r):
    return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(r, r[1:])) / 2


def point_dist(x, y, poly):
    """Signed distance from (x, y) to the polygon outline: positive inside."""
    inside, best = False, math.inf
    for ring in poly:
        for (ax, ay), (bx, by) in zip(ring, ring[1:]):
            if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                inside = not inside
            dx, dy = bx - ax, by - ay
            t = 0 if dx == dy == 0 else max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
            best = min(best, (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2)
    return math.sqrt(best) * (1 if inside else -1)


def polylabel(poly, precision=0.001):
    """Pole of inaccessibility (Mapbox polylabel), on lon scaled by cos(lat) so distances are even."""
    k = math.cos(math.radians(sum(y for _, y in poly[0]) / len(poly[0])))
    poly = [[(x * k, y) for x, y in ring] for ring in poly]
    xs, ys = [x for x, _ in poly[0]], [y for _, y in poly[0]]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    size = min(x1 - x0, y1 - y0)
    if size == 0:
        return [x0 / k, y0]
    cell = lambda x, y, h: (-(point_dist(x, y, poly) + h * math.sqrt(2)), x, y, h, point_dist(x, y, poly))
    heap, h = [], size / 2
    x = x0
    while x < x1:
        y = y0
        while y < y1:
            heapq.heappush(heap, cell(x + h, y + h, h))
            y += size
        x += size
    a = ring_area(poly[0]) * 3
    cx = sum((p[0] + q[0]) * (p[0] * q[1] - q[0] * p[1]) for p, q in zip(poly[0], poly[0][1:])) / a if a else x0
    cy = sum((p[1] + q[1]) * (p[0] * q[1] - q[0] * p[1]) for p, q in zip(poly[0], poly[0][1:])) / a if a else y0
    best = (0, cx, cy, 0, point_dist(cx, cy, poly))
    while heap:
        c = heapq.heappop(heap)
        if c[4] > best[4]:
            best = c
        if -c[0] - best[4] <= precision:
            continue
        h = c[3] / 2
        for dx in (-h, h):
            for dy in (-h, h):
                heapq.heappush(heap, cell(c[1] + dx, c[2] + dy, h))
    return [round(best[1] / k, 4), round(best[2], 4)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--src', type=Path, default=SRC)
    args = ap.parse_args()
    if not args.src.exists():
        sys.exit(f'missing input: {args.src} (copy it from the owner\'s checkout)')
    features = json.loads(args.src.read_text())['features']
    by_county = defaultdict(list)
    version = ''
    for f in features:
        p, g = f['properties'], f['geometry']
        version = version or p.get('version', '')
        kind, prefix = KIND[p['natLevName']]
        label = label_of(p['name'])
        if kind == 's':
            num = label.rsplit(' ', 1)[1]
            name, label = f'SECTORUL {num} AL MUNICIPIULUI BUCURESTI', f'Sector {num}'
        else:
            name = f'{prefix} {label.upper()}'
        polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
        polys = [[r for r in map(round_ring, poly) if r] for poly in polys]
        polys = [poly for poly in polys if poly]
        main_poly = max(polys, key=lambda poly: abs(ring_area(poly[0])))
        by_county[p['countyMn']].append({'s': p['natCode'], 'n': name, 'l': label, 'k': kind,
                                         'p': polylabel(main_poly), 'g': polys})
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for code, uats in sorted(by_county.items()):
        uats.sort(key=lambda u: u['s'])
        path = OUT / f'{code}.json'
        path.write_text(json.dumps({'county': code, 'version': version, 'uats': uats},
                                   ensure_ascii=False, separators=(',', ':')))
        total += path.stat().st_size
        print(f'{code:3} {len(uats):4} UATs {path.stat().st_size // 1024:5} KB', file=sys.stderr)
    print(f'{len(by_county)} counties, {sum(map(len, by_county.values()))} UATs, {total // 1024} KB', file=sys.stderr)


if __name__ == '__main__':
    main()
