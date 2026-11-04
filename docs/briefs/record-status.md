# Implementation brief: status of a legal body, and the county of `S` records

Status: draft, 2026-11-05. It waits for the source decision in "Gate". Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-05): keep defunct records, add a status field, hide them by default.

## Context

Survey of 2026-11-04 (ANAF `PlatitorTvaRest/v9/tva`, 2,747 `S` CUIs, 28 requests; output in `data/lookup-survey/`, not in git):

- 2,728 found, 19 not found. All found rows have a seat county and a locality. ANAF fills the county of 2,048 records.
  Of the 680 records with a county, 668 agree with ANAF.
- 422 `RADIERE`, 386 `DIZOLVARE FARA LICHIDARE(FUZIUNE)`, 1 `DIZOLVARE CU LICHIDARE`. Total 809 (29.5%). 359 of them date from 2025.
- `statusInactivi` (fiscally inactive, 57 rows) is another thing. It does not mean that the body is defunct.
- Conflict seen: CUI 4515077 has `RADIERE` 2017, and SEAP lists 354 rows up to 2026-Q3.

## Gate: source

ANAF states no terms on re-use, so its right to republish is unknown. `institutii.csv` is public, under EUPL v1.2.
Opus selects the source after the column check of the Finance Ministry dataset (CC-BY-4.0). Do not start before Opus
names the source here. The design below does not depend on the source.

## Tasks

1. **Lookup script** `scripts/lookup_status.py` writes the ignored input `data/lookup/status.csv`:
   `cui, name, status, status_label, status_date, county, locality, source, checked_at`.
   - It covers every record with a CIF that is not from ANAF (`cif_source` `seap` or `curation`).
   - It keeps the service limits. For ANAF: 100 CUIs per request, 1 request per second.
   - A CUI that the source does not know gets the status `not_found`.
2. **Status rule** (`status` values):
   - `radiat`: `RADIERE`, or `DIZOLVARE CU LICHIDARE`.
   - `fuzionat`: `DIZOLVARE FARA LICHIDARE(FUZIUNE)`. This body continues in another body, so the page must not say "closed".
   - `activ`: any other label that the source returns.
   - `not_found`: the record stays visible.
   - An empty status means "not checked". Never read an empty status as `activ`. ANAF list records stay empty.
   - An unknown label stops the script.
3. **`consolidate.py`**: read `status.csv`. A missing file skips the source with a warning, as for the other inputs.
   - Add the CSV columns `status`, `status_date`, `status_source`.
   - Do not apply `radiat` or `fuzionat` if SEAP lists the CUI in a year after the status year plus one.
     Write this case to `data/consolidated/status-review.csv`; the record stays visible with the status empty.
   - Do not change matching, merges or categories. A defunct record stays a record, and it keeps its id.
4. **County of `S` records**: fill `county` and `uat` from `status.csv` only if `county` is empty. Add the CSV column
   `county_source`. Show the same mark as `uat_source` (row key `us`). Never replace a county that a record already has.
   List the disagreements in `status-review.csv`.
5. **Explorer** (`write_explorer_data` and the decoding in `index.html`):
   - Add the row keys `st` (1 = `radiat`, 2 = `fuzionat`, empty otherwise) and `sd` (status date).
   - The default views hide rows with `st`: list, county profile, landing counts and families.
   - Add a filter in "Mai multe": "Include entități radiate sau fuzionate". Keep it in the hash, as for `web`.
   - The empty state counts the hidden rows and offers a button, with the same behaviour as for the `web` filter (issue #4).
   - A search by exact CIF finds the row in all cases, and the filter does not hide it.
   - The record detail shows "Radiată din <dată>" or "Fuzionată din <dată>", with the source.
   - Records with `st` are not state-tree roots already (key `nc`). `reachableRoots()` must still equal `expectedRoots()`.
   - Use the DS components and tokens. Put local styles in `@layer app` with the prefix `org-`.

## Tests (named, no network, no inputs)

- `test_status_rule`: each label maps to its status; an unknown label stops the script.
- `test_empty_status_is_not_active`.
- `test_status_conflict_with_seap`: the 4515077 case goes to the review file and the status stays empty.
- `test_county_fill_only_when_empty`.
- `test_defunct_record_keeps_id`: a `radiat` record stays in the output, with its id and its CIF.

## Done when

- The tests above pass, `tests/determinism.sh` passes, and the "neclasificate" roots stay at 2.
- Without `data/lookup/status.csv`, the CSV differs from the previous one only by the new empty columns.
- A browser check gives: default list without `st` rows; the filter shows them; `reachableRoots()` = `expectedRoots()`; no console error.
- The report gives counts per status and category, and the records hidden by default.

## Stop and ask

Stop if a step changes a spec, an invariant, or a dependency. Stop if the source returns a label outside the rule in task 2.

## Not in this brief

ONRC identities for `D` records. Contacts. Removal of any record.
