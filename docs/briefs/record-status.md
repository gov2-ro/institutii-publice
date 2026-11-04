# Implementation brief: status of a legal body, and the county of `S` records

Status: ready for Sonnet with the MF source, 2026-11-05. Start it after the ONRC build ends: both rebuild `institutii.csv`. Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-05): keep defunct records, add a status field, hide them by default.

## Context

Survey of 2026-11-04 (ANAF `PlatitorTvaRest/v9/tva`, 2,747 `S` CUIs, 28 requests; output in `data/lookup-survey/`, not in git):

- 2,728 found, 19 not found. All found rows have a seat county and a locality. ANAF fills the county of 2,048 records.
  Of the 680 records with a county, 668 agree with ANAF.
- 422 `RADIERE`, 386 `DIZOLVARE FARA LICHIDARE(FUZIUNE)`, 1 `DIZOLVARE CU LICHIDARE`. Total 809 (29.5%). 359 of them date from 2025.
- `statusInactivi` (fiscally inactive, 57 rows) is another thing. It does not mean that the body is defunct.
- Conflict seen: CUI 4515077 has `RADIERE` 2017, and SEAP lists 354 rows up to 2026-Q3.

## Gate: source

Source decision (Opus, 2026-11-05), measured on the full Finance Ministry (MF) files, snapshot 2026-06-11:

- **Base: MF**, `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-mf-platitori-2026-07/`, CC-BY-4.0. It finds 2,273 of 2,747 `S` and 13,443 of 13,485 `A`.
  County equals ANAF on 2,273 of 2,273; label on 2,199 of 2,273. It has 344 of the 386 mergers.
- **MF alone is not enough.** 391 of the 422 ANAF `RADIERE` are absent from MF, and 73 more defunct bodies carry another label. So 464 of the 809 defunct bodies are missing or masked.
  Absence from MF does not prove that a body is defunct: 64 of the 474 absent `S` are live by ANAF. Never read absence as `radiat`.
- **ANAF for the rest: blocked on the owner.** ANAF states no terms on re-use, and `institutii.csv` is public under EUPL v1.2. Build task 1 for MF only. Do not add ANAF rows to `status.csv`
  until the owner accepts them and this line says so. Without ANAF, an absent CUI gets `not_found`, and the record stays visible.

MF rows with `TIP_CONTRIB` PF are natural persons: skip them, and treat a CUI that only such a row holds as `not_found`. Do not read or publish `TELEFON` in this brief (see the backlog).

## Tasks

1. **Lookup script** `scripts/lookup_status.py` writes the ignored input `data/lookup/status.csv`:
   `cui, name, status, status_label, status_date, county, locality, source, checked_at`.
   - It covers every record with a CIF that is not from ANAF (`cif_source` `seap` or `curation`).
   - It reads the two UTF-8 July files: delimiter `^`, CRLF, no quoting, a trailing `^`. It writes the snapshot date (the latest `DATA_PRELUCRARE`) as `checked_at`.
   - A CUI that the source does not know gets the status `not_found`.
2. **Status rule** (`status` values, from the whole `STARE` string, on the date `DATA_STARE`). Do not use `DATA_RADIERE`: it is filled only for mergers.
   - `radiat`: `RADIERE`, `LICHIDAT`.
   - `fuzionat`: `DIZOLVARE FARA LICHIDARE(FUZIUNE)`, `DIZOLVARE FARA LICHIDARE(DIVIZARE)`. This body continues in another body, so the page must not say "closed".
   - `in_lichidare`: `DIZOLVARE CU LICHIDARE(INCEPUT LICHIDARE)`. The body still exists, and the record stays visible.
   - `listat`: `INREGISTRAT`, `MODIFICARE PUBLICI`, `TRANSFER(SOSIRE)`, `RELUARE ACTIVITATE`, `SUSPENDARE ACTIVITATE`. `MODIFICARE PUBLICI` can hide a later dissolution, so show `listat` to nobody as a claim of "active": the page shows only `radiat`, `fuzionat` and `in_lichidare`.
   - `not_found`: the record stays visible.
   - An empty status means "not checked". Never read an empty status as `listat`. ANAF list records stay empty.
   - An unknown label stops the script. The one PJ row with an empty `STARE` is not ours: an empty label on one of our CUIs also stops the script.
3. **`consolidate.py`**: read `status.csv`. A missing file skips the source with a warning, as for the other inputs.
   - Add the CSV columns `status`, `status_date`, `status_source`.
   - Do not apply `radiat` or `fuzionat` if SEAP lists the CUI in a year after the status year plus one.
     Write this case to `data/consolidated/status-review.csv`; the record stays visible with the status empty.
   - Name the source, its licence and its snapshot date in `metadata.json` (`dataset`) and in `README.md` (CC-BY-4.0 attribution).
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
