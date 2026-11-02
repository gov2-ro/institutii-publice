# Implementation brief: posturi.gov.ro employers as a source

Status: ready for Sonnet, 2026-11-02. Owner request (pax), from the posturi.gov.ro session:
"match duplicates with ~5,900 names already existing, and propose new institutions to org.gov2.ro".
Owner: Sonnet builds; Opus reviews.

## Context

posturi.gov2.ro lists public-sector job postings. Each posting names an employer, so posturi has ~5,900 distinct employer
names, each with a county and usually a locality. Two needs meet here:

- posturi wants each employer linked to an org.gov2.ro record, for CUI, address and contact data. Its employer assistant
  (`/pentru-angajatori/anunt/`) already reads a snapshot of `institutii.csv`.
- org.gov2.ro gains a source of institutions that actually hire. An employer that no tier links becomes a standalone
  record. These records are the "proposed new institutions", and a person reviews them before they count as institutions.

This follows the pattern of the ANI source: a source-only input, linked through the existing tiers, with provenance in
`sources` and `link`.

## Tasks

1. **Export, in the posturi repo.** `ops/export-employers-for-org.py` in `~/devbox/gov2/posturi.gov.ro` (stdlib).
   - It reads the posturi SQLite export (`--db`, default `webapp-php/posturi.sqlite`).
   - It writes `data/posturi/employers.csv` in this repo (`--out`).
   - Columns: `slug, name, county, locality, postings, first_seen, last_seen`. One row per posturi employer.
   - `county` and `locality` are the most frequent values over that employer's postings. On a tie, take the newest posting.
   - Print the row count and the number of rows without a county.
   - The input is not tracked in git, like the other inputs. Add it to the data-flow list in `CLAUDE.md`.
2. **Source in `consolidate.py`.** Load `data/posturi/employers.csv`. Link each row by `(county, name)` through the
   existing linker tiers: `exact`, `canonical`, `unit`, `tokens`. Do not use `prefix`; it is for ANI cut-off names only.
   - A linked row adds `posturi` to `sources` of the ANAF record, and its slug to a new column `posturi_slugs`
     (`|`-separated). In JSON, use a compact key as the other columns do.
   - An unlinked row becomes a standalone record. Id: `P<slug>`. Source: `posturi`.
   - A `weak` candidate (0.5–0.75) sets `possible_duplicate_of`, as it does today.
   - Source-only records of other sources with the same folded name and county combine, as the existing `same_name` rule does.
3. **Proposed new institutions.** Write `data/consolidated/posturi-review.csv` with each standalone `P` record:
   `id, name, county, locality, postings, possible_duplicate_of, candidate_name`, sorted by `postings` descending.
   This file is the review queue. A reviewed decision goes to `curation/merges.csv` or `curation/aliases.csv` by their
   existing rules. Do not add a new curation file.
4. **Explorer.** Show `posturi` as a source label. The `P` records stay visible, like the other source-only records.
   Add a link from a record with `posturi_slugs` to `https://posturi.gov2.ro/angajator/<slug>/` (the first slug).
5. **Report in the `consolidate.py` summary:** posturi rows, links by tier, weak candidates, standalone records,
   and standalone records with 10 or more postings.

## Verification

- `python3 -m unittest discover -s tests`: add fixtures for a posturi name in each tier, a weak case,
  and a standalone case. Use real names from the export.
- `sh tests/determinism.sh` passes.
- Compare the `consolidate.py` summary before and after. Only the posturi lines and the counts that they explain may change.
- Report the measured link rate. Report the 20 standalone records with the most postings, by hand-checked category:
  truly missing institution, a name variant that a tier should catch, or a non-institution.
  This tells Opus whether a new alias rule is worth it.

## Not in scope

- Writing org.gov2.ro ids back into posturi. posturi reads `posturi_slugs` from `institutii.csv` later, in its own brief.
- Publishing (`publish_pages.sh`). The owner publishes after review.
