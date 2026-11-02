# Implementation brief: SEAP contracting authorities as a source, and curated CIF identities

Status: ready for Sonnet, 2026-11-02. Owner: Sonnet builds; Opus reviews.
Owner requests (pax, 2026-11-02): "extract all institutii (Autoritate contractanta) with relevant info cui, contact etc
and add as another source" from the SEAP dump; and the curated CIF identities of issue #6 ("that would be nice, proceed").

## Context

The dump is the data.gov.ro "Achiziții publice <year>" datasets (publisher ADR, licence CC-BY 4.0 for 2021–2026),
at `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-adr-achizitii-publice-dump`. The download is still running: files arrive
over time, and some are incomplete. `packages.json` is the CKAN metadata, with a `size` for each resource.

Survey of 2026-11-02 (Sonnet, scripts in the session scratchpad, not kept). The numbers are the baseline:

- Every report type has the authority name in column 0 and its CUI in column 1. No report has an address, email,
  phone, website or contact person. Some 2023 files add `Tip autoritate`, `Tip activitate principala`, locality and county.
- 2026 (21 files, 2.9 M rows): 14,126 distinct authority CUIs. 12,418 match a project `cif`, 92 match only `cif_tva`,
  1,616 match nothing. The achizitii directe report alone has 98.5% of the CUIs.
- CUI defects: leading zeros, Excel scientific notation (`1.8839E+14`), 15-digit values, blanks, header rows repeated
  inside the data. No authority CUI has an `RO` prefix.
- Formats: `.xls` (some are really xlsx: detect by magic bytes), `.xlsx`, `.ods` (pandas+odfpy is too slow; use
  zipfile + iterparse on `content.xml`), and a `|`-separated 2023 CSV with BOM. 2023 T1 files have a title row
  above the header. The 2026 TIII directe file names both CUI columns just "CUI".
- Many bodies that the project has only as CIF-less records are in SEAP with a CUI: BNR 361684, CNAIR 16054368,
  RAAPPS 2351555, Imprimeria BNR 361242, UNCJR 4696968, AMR 11036662 (2023 only), and 38 of 41 INCD.
- Metadata defect: resource `38e601a9` (2025 TII) has the name and size of `e40a48ed` in `packages.json`.

Decisions (owner, 2026-11-02):
- Unmatched authorities become records, except obviously private bodies (task 3).
- Contacts are not in the dump. A phase-2 spike checks the authority profiles on e-licitatie.ro. Not in this brief.
- AMR and UNCJR come in as SEAP records. Consiliul Fiscal, CSAT and Autoritatea de Audit get an alias on their host
  body, with no record of their own (task 6).

## Tasks

1. **Extractor `scripts/extract_seap.py`** (`--dump DIR`, default the path above; dependencies inline, as `consolidate.py`).
   - Read `packages.json`. Match each local file to its resource by the 8-character id prefix of the file name.
   - Read a file only if its byte size equals the resource `size`. Skip `*.part` files and files with no resource.
     Exception: a `--trust <id-prefix>` option reads a file whose metadata is known to be wrong (use it for `38e601a9`
     only after you checked by hand that the file is complete, and say so in the report).
   - Find the header as the first row whose second cell contains "CUI". Take column 0 (name) and column 1 (CUI).
     From 2023 files, also take tip autoritate, tip activitate, locality and county where the columns exist.
   - Normalize the CUI: remove spaces and an `RO` prefix, expand scientific notation only if it is exact, drop leading
     zeros. Reject a CUI that is not 2–10 digits. Count the rejects per file.
   - Cache the per-file result in `data/seap/cache/<resource-id>.csv`, keyed by size and SHA-256, so that a re-run
     reads only new or changed files. The dump grows; the full read takes minutes.
   - Write `data/seap/authorities.csv`: `cui, name, names, first_seen, last_seen, rows, report_types, tip_autoritate,
     tip_activitate, locality, county`. `name` is the most frequent name (ties: the newest, then alphabetical);
     `names` holds the other variants (`|`-separated). `first_seen`/`last_seen` are the year-quarter of the files.
   - Write `data/seap/manifest.json`: per resource the file, size, SHA-256, rows, authorities, rejects, and status
     (`read`, `incomplete`, `missing`, `part`, `trusted`). Print a summary to stderr.
   - Same input files give byte-identical outputs under any `PYTHONHASHSEED`.
2. **Source `seap` in `consolidate.py`.** Load `data/seap/authorities.csv`; skip the source with a warning if it is missing.
   - Link by CUI equality with a record's `cif` (or else `cif_tva`), after curated identities (task 4) are applied.
     A linked row adds `seap` to `sources`. Source bit 32 (`SRC_BIT`, explorer `SRC_NAMES`/`SOURCES`, label "SEAP").
   - Do not name-link SEAP rows. SEAP has a CUI; a name match goes to the review file instead (task 3).
   - Put the inputs of `manifest.json` into `metadata.dataset`, as for the other sources (paths relative to the dump).
3. **Standalone SEAP records.** An unlinked row becomes a record `S<cui>`, with `cif` = the CUI, source `seap`,
   county and locality from the 2023 columns when present. The normal `RULES` give its category.
   - Exclude obviously private bodies by a name rule, `SEAP_PRIVATE`: parishes, monasteries and other church units,
     foundations, associations other than `asociatia de dezvoltare intercomunitara`, and sports clubs other than
     municipal, school, university or army clubs. Also exclude a 2023 tip "Operatorii economici care beneficiază de
     finanțare din instrumente structurale". Keep SRL and SA companies: many are municipal.
   - Write `data/consolidated/seap-review.csv`: every standalone or excluded row, with `cui, name, rows, tip_autoritate,
     decision (record|excluded), rule, candidate_id, candidate_name`. `candidate_*` is the best CIF-less record by the
     existing linker (`tokens` or better, nationwide), as a proposal only. Sort by `rows`, descending.
4. **Curated identities `curation/identities.csv`** (tracked): `id, cif, checked_at, evidence`.
   - A row sets `cif` of a record that has none. CSV column `cif_source`: `anaf` or `curation` (empty without a CIF).
   - Resolve ids absorbed by a merge to the survivor. The script stops on: an unknown id, a duplicate id or CIF,
     a CIF that is not digits, a record that already has a CIF, or a CIF that belongs to an ANAF record (that case
     belongs in `curation/merges.csv`; say so in the message).
5. **Seed the identities.** From `seap-review.csv`, add rows for the CIF-less records whose SEAP match is certain:
   the INCD, BNR, CNAIR, RAAPPS, Imprimeria BNR, and others you find. `evidence` names the SEAP name and CUI and why
   the names are the same body. When two project records are candidates for one CUI, add no row; report the pair.
6. **Aliases for hosted bodies** in `curation/aliases.csv`, kind `hosted_body`, status `reviewed`: "Consiliul Fiscal" on
   Academia Română, "CSAT" and "Consiliul Suprem de Apărare a Țării" on the Administrația Prezidențială, "Autoritatea
   de Audit" on the Curtea de Conturi. `basis` states the legal link. Find the ids in `institutii.csv`.
7. **Docs.** The data-flow entry in `CLAUDE.md` (SEAP and identities, one bullet each), the `s` bitmask list in the
   Explorer section, `docs/BACKLOG.md`, and one `docs/activity-log.md` entry with the measured numbers.

## Verification

- `python3 -m unittest discover -s tests`: fixtures for CUI normalization (zeros, scientific notation, 15 digits,
  header rows), the private-name rule (each kind, plus the kept exceptions), and each identities stop condition.
- `sh tests/determinism.sh` passes. Run the extractor twice on the same files and compare the outputs with `cmp`.
- Compare the `consolidate.py` summary before and after. Only the SEAP lines, the identities and the counts that
  they explain may change. Report the change in total records, by category.
- Report: files read and skipped (with reasons), distinct CUIs, link rate, standalone records, excluded rows by rule,
  identity rows added, and 20 standalone records sampled at random with your judgement (public body, state or municipal
  company, private).

## Stop and ask

- If the private-name rule would exclude more than 15% of the unmatched rows, or keep obvious private bodies you can't
  catch with a name rule.
- If a CUI links to more than one record.
- Before any change to the linker tiers or to an existing curation file other than `aliases.csv`.

## Not in scope

- Contacts (phase 2: spike on the e-licitatie.ro authority profiles).
- Winners and bidders (`Ofertant castigator`): they are suppliers, not authorities.
- Publishing. The owner publishes after review.
