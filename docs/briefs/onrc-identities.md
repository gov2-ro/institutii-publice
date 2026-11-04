# Implementation brief: ONRC identities for ANI-only companies

Status: ready for Sonnet, 2026-11-05. Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-05): apply the ONRC matches through a brief. The record status is a separate brief (`record-status.md`).

## Context

Inputs, not in git:
- `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-onrc-firme-2026-10-19/`: `OD_FIRME.csv`, `OD_STARE_FIRMA.csv`, `N_STARE_FIRMA.csv`, `SHA256SUMS`.
  Licence CC-BY-4.0. Delimiter `^`, UTF-8 with BOM, CRLF. Names hold raw `"`, so read with `QUOTE_NONE`.
- `data/lookup-survey/onrc-review.csv`: the survey queue of 2026-11-05. The survey script is in a session scratchpad and is not kept.

Baseline of 2026-11-05 (records 28,511). 4,634 `D` records have no CIF:

| Tier | Records | Sample by eye |
|---|---|---|
| `exact_county` | 315 | 0 of 30 wrong. A sample of this size cannot show a share under about 10%. |
| `exact_elsewhere` | 33 | 14 of 30 wrong, 3 doubtful. |
| `ambiguous` | 12 | Not read as usable. |
| none | 4,274 | |

Of the 348 exact matches, 128 give a new CUI and 220 name a CUI that another record holds (178 `S`, 24 `G`, 15 `D`, 2 `R`, 1 `P`).
17 CUIs match more than one `D` record. A strict rule leaves 96 new `exact_county` identities (79 in function, 14 dissolved).

How the build treats a CIF (`consolidate.py`, read `apply_curated_identities` and `link_seap`):
- `S` records appear after the identities. A CIF on a `D` record should make SEAP link to it, and no `S` record then appears. Task 2 tests this.
- `identities.csv` stops on a CIF that an ANAF record holds. Such a pair belongs in `merges.csv`.
- `merges.csv` cannot name an `S` id.

## Tasks

1. **Candidate script** `scripts/onrc_candidates.py` (stdlib only). It reads the ONRC files and `institutii.csv`, and writes the ignored file
   `data/consolidated/onrc-review.csv`. Its tiers and columns equal the survey queue. Reuse `fold` from `consolidate.py`; do not copy the rules twice
   if an import works without `openpyxl`. Compare with `data/lookup-survey/onrc-review.csv`, and explain every difference in tier.
   The script writes no curation file.
2. **Test the absorption first.** Add identity rows for 3 records whose CUI an `S` record holds. Rebuild. Confirm:
   - the `S` record is gone, and its id is in `merged_ids` of the `D` record;
   - the `D` record has the source `seap`;
   - no other record changed.
   If this fails, stop and report. Do not change the code.
3. **Sample the merge candidates before you apply them.** The earlier samples did not cover them. Read 30 `S` cases, and all 42 others (`G`, `D`, `R`, `P`). Judge by name, county,
   category, legal form and, for `S`, the SEAP name. Report the wrong share to Opus and **stop here for a decision**. Apply nothing else before Opus answers.
4. **New identities by rule** (only after task 3). A row enters `curation/identities.csv` if all of these hold:
   - the tier is `exact_county`, and the record name has a company form;
   - the form in the name agrees with the ONRC legal form;
   - the ONRC row is the only one with this key in the county;
   - no other record holds the CUI, and no other `D` record matches it;
   - the company is in function.
   Evidence: `ONRC 2026-10-19 <COD_INMATRICULARE>, tier exact_county`. `checked_at` is the build date.
5. **Merge candidates** (only with the rule that Opus sets after task 3).
   - CUI on an `S` record: an identity row on the `D` record.
   - CUI on an ANAF record, or on a record with a curated CIF: a `merges.csv` row. The survivor order is ROePAS, Registrul, ANI, posturi.
   - Several `D` records match one CUI: merge them first, and put the identity on the survivor.
6. **Hand-review list.** Do not apply these. Write them to the report, with the evidence: dissolved companies, form conflicts (for example ROMGAZ SA against ROMGAZ RA), and CUIs
   that match two `D` records with other names. Opus decides.
7. **Attribution.** Name ONRC, the dataset and CC-BY-4.0 in `README.md`, next to the other sources, and in the data flow of `CLAUDE.md`.

`exact_elsewhere` and `ambiguous` stay in the queue. A person decides them. They get no rule.

## Tests (named, no network, no inputs)

- `test_onrc_name_key`: removal of the legal form, and a leading `SC` in its spellings.
- `test_onrc_tiers`: a small fixture gives each tier.
- `test_onrc_rule_rejects`: a form conflict, a second row in the county, a CUI on another record, and a dissolved company each stop a row.
- `test_onrc_quote_none`: a name with a raw `"` keeps its columns.

## Done when

- The tests pass. `tests/determinism.sh` passes. "Neclasificate" roots stay at 2.
- The `consolidate.py` summary before and after is in the activity log. The CSV diff shows only the records in the curation rows and the absorbed ids.
- The family counts are compared before and after. A lost family is reported (see "Poliția locală" in the backlog).
- The report gives counts per task, the sample results, the hand-review list and what was assumed.

## Stop and ask

Stop if a step changes `consolidate.py`, a spec, an invariant or a dependency. Stop after task 3. Do not push, tag or publish.

## Not in this brief

Fuzzy matching for the 4,274 records with no match. Record status. Contacts.
