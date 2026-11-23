# Implementation brief: review the transparenta.eu candidates and parents

Status: built by Sonnet and accepted by Opus, 2026-11-23. Owner decisions open. Owner request, 2026-11-23.
Owner: Sonnet builds; Opus reviews and commits. Any new record or parent in the published data needs an owner decision.

## Context

- `scripts/transparenta_compare.py` wrote `data/transparenta/review.csv` from the cached pull
  `data/transparenta/entities-2026-11-23.jsonl`: 552 `missing_here`, 1,303 `non_anaf_here`, 11 `parents_differ`, 33 `missing_there`.
- Opus checked the 552 against the MF files: 102 `listat`, 100 `fuzionat`, 350 not in MF. transparenta.eu keeps bodies of past years.
- The API `https://api.transparenta.eu/graphql` has `entity(cui: ID!)` and, on `Entity`,
  `reports(limit, offset, year, period, type, sort, main_creditor_cui)` with `nodes { report_date report_type }`.
  Read `src/modules/report/shell/graphql/schema.ts` of `ClaudiuBogdan/hack-for-facts-eb-server` for `SortOrder`.
  Introspection is off. The server returns at most 100 rows per page.

## Tasks

1. **Latest report per candidate.** For each of the 552 `missing_here` CUIs, get the date of the latest report.
   - Put about 25 `entity(cui:)` queries in one request with GraphQL aliases (`e1: entity(cui: "…") { cui reports(limit: 1, sort: …) { nodes { report_date } } }`).
     If the server refuses aliases or the query is too complex, use fewer per request.
   - Wait 2 s between requests. Use `User-Agent: institutii-publice-check`. Stop on HTTP 429 or 5xx.
   - Cache the answers in `data/transparenta/last-report-<date>.jsonl`. Add the code to `transparenta_compare.py` (option `--last-report`), stdlib only.
2. **Current data from ANAF.** For the CUIs with a report in 2025 or 2026, call ANAF `PlatitorTvaRest/v9/tva`, at most 100 CUIs per
   request and 1 request per second (see the rows of 2026-11-04 in `docs/external-lookups.md`). Keep the name, address, county,
   registration status and `stare_inregistrare`. Do not keep any field about a natural person. Cache in `data/transparenta/anaf-<date>.json`.
3. **Candidate queue.** Write `data/transparenta/candidates.csv`: `cui, their_name, anaf_name, entity_type, county, their_parents,
   parent_in_our_data (id or empty), last_report, anaf_status, mf_status, proposal`. `proposal` is one of:
   - `add`: a report in 2025 or 2026, active in ANAF, and the parent is in our data;
   - `check`: active, but the parent is missing, or the name or county disagrees;
   - `skip`: no report since 2024, or ANAF or MF says the body is dissolved or merged.
   Report the counts per `proposal`, and 10 examples of each.
4. **Parents for the 1,303 `non_anaf_here` records.** No new calls. For each record, take their parents and find our record with that CIF.
   Write `data/transparenta/parent-proposals.csv`: `our_id, our_name, cui, their_parents, parent_ids, parent_names, our_family, conflict`.
   `conflict` is set when the parent kind does not fit our record (for example a school under a ministry, not under a UAT or ISJ).
   Report the counts: parent found, parent not in our data, conflicts. Read 30 rows by eye and report the precision.
5. **Docs.** Log every call in `docs/external-lookups.md`. Add an activity log entry with the measured numbers.
   Add the review items to `docs/BACKLOG.md`. Update `docs/pipeline.md` for the new option.

## Limits

- Change no published data and no curation file. Opus and the owner decide on a rule after the review.
- Do not request `profile`. Do not send any data other than CUIs of public bodies.
- Do not commit. Stop and ask if an API answers differently from this brief.
