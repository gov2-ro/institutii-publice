# Implementation brief: compare our list with the transparenta.eu entities

Status: brief ready (Opus, 2026-11-23). Owner request, 2026-11-23.
Owner: Sonnet builds; Opus reviews and commits.

## Context

- transparenta.eu shows the budget execution of public bodies. The code is open: `github.com/ClaudiuBogdan/hack-for-facts-eb-server`.
- Its `Entities` table holds each body that files budget execution reports with ANAF. A row has `cui`, `name`, `entity_type`,
  `is_uat`, `address`, a UAT, and two parents: `main_creditor_1_cui` and `main_creditor_2_cui`.
- These parents are the same two parent columns as in our ANAF list (`parent_cifs` in `consolidate.py`).
- Spot check of 2026-11-23: Ministerul Culturii (4192812) has 91 children on the site and 91 in our data.
- The public GraphQL API is `https://api.transparenta.eu/graphql`. The query is
  `entities(filter: EntityFilter, limit: Int = 20, offset: Int = 0) { nodes { ... } pageInfo { ... } }`.
  The `Entity` type gives `parents { cui }`. Read the schema in `src/modules/entity/shell/graphql/schema.ts` of the server repo.
- Terms (`/terms`, read 2026-11-23): open data follows the licence of its source. A user must not harm the service.
  A user must not remove attribution notices. Shared visual results name the data source and Transparenta.eu.
  The terms say nothing about API rate limits. `robots.txt` allows `/`.

## Goal

A repeatable, read-only comparison. It answers three questions:

1. Which CUIs does transparenta.eu have that our list does not have, or has only as a non-ANAF record?
2. Which CUIs of our ANAF records does transparenta.eu not have?
3. For a CUI in both lists, which parent pairs differ?

## Tasks

1. **Script `scripts/transparenta_compare.py`** (stdlib only; `urllib`, no new dependency).
   - Fetch all entities, page by page. Ask for `cui name entity_type is_uat address parents { cui } uat { county_code }`
     (check the field names in the schema). Do not ask for `profile`.
   - Find the largest `limit` that the server accepts. Start at 500. Wait 2 s between requests. Stop on HTTP 429 or 5xx, and
     report it. Send the header `User-Agent: institutii-publice-check`.
   - Save the raw pages to `data/transparenta/entities-<date>.jsonl` (ignored by git). With `--cached`, the script reads that
     file and makes no request.
   - Compare with `data/consolidated/institutii.csv`. Write `data/transparenta/review.csv` with one row per difference:
     `kind` (`missing_here`, `missing_there`, `parents_differ`, `non_anaf_here`), `cui`, `their_name`, `our_id`, `our_name`,
     `their_parents`, `our_parents`, `entity_type`, `county`.
   - Print counts per `kind` to stderr. The script changes no data and writes no curation file.
2. **Run it once.** Report the counts and 20 examples per `kind`. For `missing_here`, say how many are UATs, schools,
   companies (`entity_type`). Say whether `missing_there` is mostly bodies that file no budget report (for example companies).
3. **Docs.** Add the source to `docs/pipeline.md` (*Sources not used in the published data*) and the command to `CLAUDE.md`.
   Log every request in `docs/external-lookups.md`: number of requests, page size, time, result.
   Add an activity log entry with the measured numbers.
4. **Recurring check.** Add a step to `docs/pipeline.md`: run the script after each new ANAF list, and at least every
   three months. Read the `missing_here` rows first.

## Limits

- Do not read or store `profile` (it holds leader names and parties, which are personal data). The use of the profile
  websites needs an owner decision and maybe a request to the author of transparenta.eu.
- Do not add any transparenta.eu row to the published data. A new record or parent needs a separate owner decision.
- Do not send our CUIs or any other record data to the API, except a filter on one CUI to check one row by hand.
- Stop and ask when the API needs a key, refuses the page size, or answers with 429.
