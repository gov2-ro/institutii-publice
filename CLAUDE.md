# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is
A consolidated list of Romanian public institutions **and state-owned/state-run companies**, enriched with
website, contacts, etc. It also feeds [gov2-ro/stiri](https://github.com/gov2-ro/stiri) (the institution websites).
Names, comments and UI text mix Romanian and English; the explorer UI is Romanian.

## Commands
No linter or build step. Two scripts, a static page and standard-library tests:

    uv run scripts/consolidate.py              # rebuild data/consolidated/ (needs openpyxl; inline uv script deps)
    python3 scripts/scrape_roepas.py [--workers 4] [--limit N]   # re-scrape roepas.ro -> data/roepas/ (requests, lxml)
    python3 -m http.server                     # then open http://localhost:8000/explorer/
    python3 -m unittest discover -s tests      # matching and category fixtures; no inputs, no openpyxl needed
    sh tests/determinism.sh                    # full data: same CSV under PYTHONHASHSEED=1 and 2

`consolidate.py` prints a summary to stderr (record counts per source combination, link tiers, ANI umbrella
stats, category counts). Compare it before/after a change to the matching rules — it is the de facto regression check.
`scrape_roepas.py` appends to `data/roepas/details.jsonl`, so an interrupted run resumes.

## Data flow
The ignored inputs listed here are not in git. Copy them from the owner's checkout, at the same relative paths.
Inputs -> `scripts/consolidate.py` -> `data/consolidated/`:
- **ANAF** public-entity list `docs/reference/Lista_EP_portal_01102026.xlsx` — the backbone (CIF, UAT, address, parent CIFs). Record id `A<cif>`.
- **ROePAS** scrape `data/roepas/institutii.json` — website, email, phone, coords, procedures. Standalone id `R<id>`.
- **Registrul Național** `docs/reference/Registrul-...pdf.csv` — a damaged PDF extraction, parsed line by line
  (`load_registrul`), not with the csv module. Standalone id `G<num>`.
- **ANI declarații de integritate** `data/declaratii-integritate/Lens Visualization*.csv` (Kibana exports,
  `NAME|COUNTY` + count). Merged into `declaratii.csv` as a side effect. Standalone id `D<sha1[:8]>`.
  Exports cap at 10,000 rows; the script warns when a file hits the cap. Overlapping exports are deduped by max.

Outputs: `institutii.json`, `institutii.csv` (the only consolidated file tracked in git), and the explorer's
`metadata.json` + `rows.json`. `explorer/metadata.json` and `explorer/rows.json` are symlinks into
`data/consolidated/`. `data/consolidated/explorer-data.js` is a stale leftover of an older format; nothing reads it.

Git: `.gitignore` excludes `data/*` except `data/consolidated/institutii.csv`, so the source inputs
(`data/roepas/`, `data/declaratii-integritate/`) and the full outputs are local only.

## How consolidation works (consolidate.py)
- **Normalization**: `squash` (nbsp, unicode hyphens, whitespace) and `fold` (ascii, lowercase, alnum) underlie all matching.
- **Linker** links `(county, name)` to an ANAF row in tiers: `exact` -> `canonical` (`prep` collapses local
  authorities — Primăria/Comuna/Consiliul Local X — to `uat:<locality>`, county councils to `uat:judet:<x>`,
  plus school-name `ALIASES`) -> `unit` (military unit number, nationwide) -> `tokens` (IDF-weighted overlap
  >= 0.75, numbers must agree). Only those tiers merge into the ANAF record. `weak` (0.5–0.75) is NOT merged:
  the row stays its own record with `possible_duplicate_of` = the candidate CIF. Output is a union with
  provenance in `sources` and `link`.
- **ANI-specific** (`link_declaratii`, `umbrella_labels`, `split_umbrella`, `declaratii_standalone`): the ANI
  institution field is a form dropdown with umbrella entries ("ALTE INSTITUTII DIN SUBORDINEA ...", bare
  "PRIMARIA") that are excluded unless a specific name was typed after them; the ANI county is unreliable, so
  fallbacks try a county named in the text, then Bucharest bodies (`national`), then a unique name anywhere
  (`elsewhere`). Local kinds (`DECL_LOCAL_KIND`: schools, clubs...) skip those fallbacks. Tuning knobs:
  `DECL_SPREAD`, `DECL_MIN_COUNT`.
- **Categories**: `RULES` (ordered regexes on folded names, first match wins), falling back to `ANCESTOR_HINTS`
  on parent names. Category labels are Romanian with diacritics.
- **Families**: curated `FAMILY_HEADS` first, then "network families" (name minus county/locality words shared
  across >= 5 members in >= 4 counties), merged by `merge_variants`; `pretty` + `DIACRITICS` restore display text.

## Explorer (explorer/index.html)
Single self-contained vanilla-JS page (no build, no deps) that fetches `metadata.json` + `rows.json`; it must be
served over HTTP, not opened as file://. Rows use the compact schema from `write_explorer_data`: short keys
(`n` name, `c` category idx, `k` county idx, `m` family idx, `s` source bitmask anaf=1/roepas=2/registrul=4/
declaratii=8, `f` cif, `p` parent cifs, `i` full record id such as `A4400956`, `mc` CIFs of unresolved match
candidates, ...), empty values omitted. A known 0 stays: `pc`/`po` (procedure counts) are present when 0, absent when unknown. Adding a field means changing both
`write_explorer_data` and the decoding in `index.html`.
`metadata.json` also carries `dataset` (generation time; per input file the path, bytes, SHA-256, mtime, row count;
ANI exports add `exported_at` and `capped`). Ambiguous source rows stay separate records with `match_candidates`
(CSV column `match_candidate_cifs`). It also carries `state`, the "Structura statului" tree: the curated top layer (`STATE_NODES`,
`STATE_MEMBERS`, `STATE_ATTACH` in `consolidate.py`, keyed by CIF) plus the UAT and unclassified root CIFs.
Views: `acasa` (landing: overview, families, county choropleth; opened by an empty hash), `list`, `stat`, `fam`,
`loc` (`k=<county>` gives the county profile: coat of arms, UAT map, seat/municipii/orașe/comune groups).
Maps are inline SVG from `explorer/assets/gis/` (TopoJSON decoded in the page), loaded on first use;
coats of arms are `explorer/assets/steme-judete/<COD>_<Name>.png`. County seats are the `SEATS` constant.
Spec: `docs/specs/structura-statului.md`. In the page console, `explorer.reachableRoots()` must equal
`explorer.expectedRoots()`.

## Scope
ANI-only names (mostly state companies missing from ANAF) belong in the list as candidates to resolve, not
noise — don't drop records just because they lack an ANAF CIF. Open roadmap items are in README.md.



## Tone of voice

Follow Simplified Technical English (ASD-STE100) for docs, error messages and agent-facing
text:

- One instruction per sentence; at most ~20 words (procedures), ~25 (descriptive).
- Active voice; name the actor.
- Simple tenses.
- One word, one meaning; the same term every time.
- No noun clusters over three words; keep the articles.
- Keep every condition and qualifier.

## Process notes

Two files carry the project's memory between sessions. Create each one with the first work
that needs it, and read both before starting.

**`docs/BACKLOG.md`** — roadmap, tasks, bugs. Statuses: `[ ]` open, `[~]` in progress, `[x]`
done, `[-]` dropped.
- Flip an item to `[x]` in the same change that finishes it.
- Add a defect or deferred work when you find it.
- Mark a dead end `[-]` **with the reason**, under *Verified limits*, so that nobody
  investigates it again.

**`docs/activity-log.md`** — dated entries, newest first, each with **Done / Hard / Decided**.
- Add an entry when a chunk of work lands.
- A decision carries its rationale and the cost of the alternative.
- Record wrong turns, and say what was measured and what was assumed. Keep the measured
  numbers: they are the baseline for regressions.


## Opus designs, Sonnet builds

The work splits by model. **When you are Opus**, defer implementation and well-defined
future work to Sonnet by default:

- **Opus** writes specs, ADRs and briefs; makes and records decisions; and reviews Sonnet's
  results against the brief before they are accepted.
- **Sonnet** carries out a brief: code, spikes, measurements, fixture changes, and the
  activity and backlog entries for that work.
- **Opus does the work itself** when the task is a few lines, or when the design is still
  moving and the doing is part of the deciding.

**Sonnet stops and asks** when a step would change a spec, an ADR, an invariant or a
dependency. It reports what it measured and what it assumed.

To hand over, Opus tells the owner that the brief is ready. The owner asks Opus to start a Sonnet agent on it.

**Versions follow the work and the process state.** The project is spec-driven, so a spec, an
ADR, a decision, a brief, a set of named tests, and a measured spike are deliverables, as much
as a user capability is. A version also marks where the process stands (for example "brief
ready", "build accepted"). After each committed chunk, tag it: bump the minor version for any
new work, documentation and spec work included; bump the patch only for a correction. The
version lives in annotated git tags (`vMAJOR.MINOR.PATCH`).
Do this without asking, and say when you did.