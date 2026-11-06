# Implementation brief: links to tipizatul.eu and transparenta.eu

Status: ready for Sonnet, 2026-11-06. Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-06): add both links, group all external links on the record page, and use a tracked map that starts with the names that link to ANAF. The survey is in `docs/activity-log.md` (2026-11-06).

## Goal

A record page shows one group of links to other sites. A wrong link is worse than no link.

## Facts already measured

- tipizatul.eu has no institution page and no CIF. `https://www.tipizatul.eu/proceduri?q=<institution name>` filters the list. The search ignores diacritics and case, and it searches the title, the institution and the county.
- The page opens every institution when a search gives 200 procedures or fewer. The largest institution has 184 procedures.
- The bundle is `https://www.tipizatul.eu/procedures.json` (19.5 MB, built 2026-08-18). The page hides procedures with no documents. Count only procedures with documents: 3,575 procedures, 688 names.
- The survey linked 461 of the 688 names to ANAF, and these names give 451 CIFs that are records. The survey script is `match_tipizatul.py`. It is short: rebuild it in the project (part 1).
- `https://transparenta.eu/entities/<CUI>` shows a budget page. An unknown CUI gives HTTP 200 and the title `Entity <CUI> - Buget 2025 | Transparenta.eu`. A known CUI gives the entity name in the title.
- The terms of transparenta.eu say nothing about links or automated access. One person operates the site, so keep the load low.

## Part 1: the tipizatul.eu map

1. Download the bundle once to `data/tipizatul/procedures.json` (ignored by git).
2. Add `scripts/tipizatul_candidates.py`. It reads the bundle and the ANAF rows and runs `consolidate.Linker` on each name with documents.
   Take the county from `Județ X` at the end of `fields.institutiaResponsabila`, else from the field `county`.
   It writes the ignored queue `data/tipizatul/review.csv`: name, county, tier, CIF, ANAF name, procedures.
   It also prints the names of `curation/tipizatul.csv` that are no longer in the bundle. It changes no data.
3. Write the tracked file `curation/tipizatul.csv` with the columns `id, institution, tier, checked_at`. Use the exact spelling of the bundle in `institution`. Use only the tiers `exact`, `canonical` and `tokens`. Do not add the 227 other names.

Apply these rules (Opus) to fill the file:

- **Exact and canonical tiers:** keep the row, unless a rule below rejects it.
- **Tokens tier:** read each row. Keep it only if the name and the ANAF name are the same body. Record each rejection and its reason.
- **Subunits:** a name with a part after ` - ` that names a directorate, a branch or a compartment is not its parent. Reject it, unless the ANAF row has the same part.
- **One name for one record:** if several names link to one record, keep the name with the best tier and the same words as the ANAF name. If this leaves a tie, reject all of them and list the tie.
- **The surviving record:** the row in the output may have another id after a merge. Use the id of the surviving record. Stop and report if a CIF has no record.

Doubtful rows stay out. List every rejected row in the report.

## Part 2: the build

In `scripts/consolidate.py`, follow the pattern of `load_curated_websites`:

- A missing file means no links. The script stops on an unknown id, a duplicate id or a duplicate institution.
- Add the CSV column `tipizatul_name` and the row key `tz`. No other field of any record changes.

Add tests to `tests/test_consolidate.py` for the stop conditions and for the applied value.

## Part 3: the transparenta.eu coverage

Measure coverage before the link is built. Do not crawl all the CIFs.

- Take a random sample with a fixed seed: 200 records with `cif_source` `anaf`, 50 with `curation` and 50 with `seap`. Use only records that are not `radiat` or `fuzionat`. Exclude `seap` records that the sample shows to be private bodies, and report them.
- Make one request every 2 seconds. Read only the first 64 KB of each page, then close the connection. Stop on any HTTP 429 or 5xx response and report it.
- A record is covered if the page title has a name and not `Entity <CUI>`. Compare the name with our name, and report the mismatches.
- Save the result to `data/tipizatul/transparenta-sample.csv` (ignored). Add a row to `docs/external-lookups.md`.

**Rule (Opus):** show the link for a `cif_source` only if at least 95% of its sample is covered and has no wrong name. Do not check each record. Report the numbers for each `cif_source`, including the ones below the limit.

## Part 4: the record page

Change `explorer/index.html`, in the record dialog:

- Add a section `Pe alte site-uri` after `Contact` and before `Identificare`. Hide the section if it has no link.
- The rows and their order:

  | Label | Link text | Target | Condition |
  |---|---|---|---|
  | `Proceduri și formulare` | `tipizatul.eu` | `https://www.tipizatul.eu/proceduri?q=<tz>` | The row has `tz`. |
  | `Buget` | `transparenta.eu` | `https://transparenta.eu/entities/<f>` | The `cif_source` of the record passes part 3. |
  | `Proceduri` | `roepas.ro` | the value of `ru` | The row has `ru`. |
  | `Angajator` | `posturi.gov2.ro` | the current posturi link | The row has `ps`. |

- Move the ROePAS page link and the posturi employer link into this section. They leave their current places. The other ROePAS and posturi rows stay. The OpenStreetMap link stays with the coordinates.
- Encode each value with `encodeURIComponent`. Use `target="_blank"` and `rel="noopener noreferrer"`, as the other links do.
- Use the DS summary list that the other sections use. Add no new CSS unless the layout needs it.

Also change these:

- `explorer/despre.html`: add one short Romanian sentence that links both sites. It says that these are links to other projects and that we take no data from them to show on the page.
- `docs/reports/source-licences.md`: add a short section. tipizatul.eu: MIT covers the code, no data licence found, we keep only the institution names for the map. transparenta.eu: only links, the terms say that open data follows the licence of the source.
- `CLAUDE.md`: add the map to "Data flow", the script to "Commands", and `tz` to the row schema.

## Checks

- `python3 -m unittest discover -s tests` passes. `sh tests/determinism.sh` passes.
- CSV before and after the build: the same records and ids, and only the column `tipizatul_name` differs.
- In the page console, `explorer.reachableRoots()` equals `explorer.expectedRoots()`.
- Open 3 record pages over HTTP and check the section: one with all the links, one with no link, one with diacritics in `tz`.
- Do not test the live tipizatul.eu links in a browser if you have no browser tool. Opus checks them in review.

## Limits

- Do not commit, tag, push or publish. Opus reviews first. Publishing needs the approval of the owner.
- Do not contact the author of tipizatul.eu. This is a separate backlog item.
- Do not import any other tipizatul.eu or transparenta.eu data. Contact details stay out.
- Stop and ask if a step would change a spec or add a dependency, or if the numbers differ from the survey by more than 5%.

## Report

Say what you measured and what you assumed: rows kept per tier, rejected rows with reasons, ties, the coverage per `cif_source`, the CSV diff and the test results. Add the activity entry and flip the backlog items that the work finishes.
