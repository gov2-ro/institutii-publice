# Data pipeline: sources, build and checks

This document describes how the project makes the published list, from each source to https://org.gov2.ro.
Update it in the same change when you add a source, a build step or a check.
The counts are from the build of 2026-11-05 (v0.56.0, 28,308 records).

## Overview

```text
SOURCES (not in git)                   SCRIPT                    INTERMEDIATE FILE
roepas.ro ---------------------------> scrape_roepas.py -------> data/roepas/institutii.json
SEAP dump, data.gov.ro --------------> extract_seap.py --------> data/seap/authorities.csv
posturi.gov.ro database -------------> posturi repo export ----> data/posturi/employers.csv
ANI Kibana, manual CSV exports ------------------------------->  data/declaratii-integritate/
ANAF list, Registrul ----------------------------------------->  docs/reference/
MF files + institutii.csv -----------> lookup_status.py -------> data/lookup/status.csv

                  all of the above + curation/*.csv (in git)
                                  |
                                  v
                          consolidate.py
                                  |
          +-----------------------+------------------------+
          v                       v                        v
   institutii.csv (in git)   rows.json, metadata.json   review queues
   institutii.json           (explorer data)            (for a person)
          |                       |
          +-----------+-----------+
                      v
             publish_pages.sh --> gh-pages --> https://org.gov2.ro

ONRC files + institutii.csv --> onrc_candidates.py --> onrc-review.csv --> curation/*.csv (rule or person)
```

`consolidate.py` does not read the ONRC files. An ONRC match reaches the list only through a row in `curation/`.

## Run order

Run only the steps whose source changed. Steps 1 to 3 need the source files.

| Step | Command | Run it when |
|---|---|---|
| 1 | `python3 scripts/scrape_roepas.py` | You want new ROePAS data. |
| 2 | `uv run scripts/extract_seap.py` | The SEAP dump has new files. A cached file needs no local copy. |
| 3 | `ops/export-employers-for-org.py` in the posturi repo | You want new posturi data. |
| 4 | `uv run scripts/consolidate.py` | Always. |
| 5 | `python3 scripts/lookup_status.py` | The list has new CUIs, or the MF files changed. |
| 6 | `uv run scripts/consolidate.py` | You ran step 5. |
| 7 | `python3 scripts/onrc_candidates.py` | You want a new ONRC queue. It changes no data. |
| 8 | `python3 -m unittest discover -s tests` and `sh tests/determinism.sh` | Always, before a commit. The determinism check is a step for a person: it takes minutes and rebuilds the data. `publish_pages.sh` does not run it. |
| 9 | Browser check (see *Checks*) | The explorer or the data changed. |
| 10 | `sh scripts/publish_pages.sh --dry-run`, then without `--dry-run` | The owner approved the publish. Commit your changes first. |

Steps 5 and 7 read `institutii.csv`, so they use the list of the previous build. Thus a new CUI needs steps 4, 5 and 6.

## Sources

The licence column gives only what this repository records. "Not recorded" means that nobody has checked and written down the terms.

| Source | Input | Script | Date of the copy | Licence | Gives | Records in the source |
|---|---|---|---|---|---|---|
| ANAF list of public entities | `docs/reference/Lista_EP_portal_01102026.xlsx` | `load_anaf` | 2026-10-01, from the file name | Not recorded | Backbone: CIF, UAT, address, parent CIFs | 13,485 (`A`) |
| ROePAS | `data/roepas/institutii.json` | `scrape_roepas.py` | Scrape of 2026-10-05 | Not recorded | Website, e-mail, phone, coordinates, procedures | 2,872 (481 `R`) |
| Registrul Național | `docs/reference/Registrul-…pdf.csv`, a damaged PDF extraction | `load_registrul` | File of 2025-11-12 | Not recorded | Register number, more names | 11,776 (5,935 `G`) |
| ANI declarații de integritate | `data/declaratii-integritate/Lens Visualization*.csv` | `load_declaratii` | Exports of 2026-10-19 | Not recorded | Number of declarations; names that ANAF does not list, mostly companies | 14,547 (4,888 `D`) |
| posturi.gov.ro employers | `data/posturi/employers.csv` | Export in the posturi repo | 2026-11-02 | Not recorded | Employers, postings, locality | 4,342 (939 `P`) |
| SEAP contracting authorities (ADR, data.gov.ro) | `data/seap/authorities.csv`, rebuilt from `data/seap/cache/` | `extract_seap.py` | Dump of 2026-11-03 | CC-BY-4.0 on 6 datasets, OGL-ROU-1.0 on 6 | CUI, activity years, type, locality | 16,178 (2,580 `S`) |
| Finance Ministry (MF), "Date de identificare plătitori" | `data/lookup/status.csv`, from the files on geana | `lookup_status.py` | Snapshot of 2026-06-11 | CC-BY-4.0 | Status of a legal body; county of records with no county | No records; 3,406 CUIs checked |
| ONRC, "Firme înregistrate la Registrul Comerțului" | Files on geana, `data.gov.ro-onrc-firme-2026-10-19` | `onrc_candidates.py` | 2026-10-19 | CC-BY-4.0 | CUI of `D` records, through `curation/` | No records; 245 identities and 36 merges |
| Maps | `docs/reference/gis/*.geojson` | `build_uat_maps.py` | Not recorded | To confirm (see the backlog) | County and UAT maps | No records |

`metadata.json` (`dataset`) records the path, size, SHA-256, date and row count of each input file that `consolidate.py` reads.

Sources that the project does not use in the published data:

- **ANAF `PlatitorTvaRest` service.** ANAF states no terms on re-use. The owner decided on 2026-11-05 to keep it out for now.
- **MF `TELEFON`.** The column can hold personal numbers. The owner decided on 2026-11-05 not to publish it for now.
- **MF rows with `TIP_CONTRIB` PF.** These rows are natural persons. `lookup_status.py` skips them, and they never enter the repository.

Every call to an external service and every dataset download goes in [external-lookups.md](external-lookups.md).

## Curated files (in git)

| File | Rows | What a row does |
|---|---|---|
| `curation/identities.csv` | 826 | Gives a CIF to a record with no CIF. A CIF on a `D` record absorbs the `S` record with that CUI. |
| `curation/merges.csv` | 117 | Merges a record into another, sets a parent, or renames a record. It cannot name an `S` id. |
| `curation/same_body.csv` | 57 | Links names of one body. |
| `curation/aliases.csv` | 200 | Adds names for search, and for the linker on `A` ids when reviewed. Other projects use this file as a master. |
| `curation/websites.csv` | 121 | Fills or replaces the website of an ANAF record. |
| `curation/unmerged.csv` | None now | Allows an absorbed id to become a record again, with a reason. |

The rule for a merge: a CUI is one legal body; a wrong merge costs more than a duplicate; in doubt, the row stays open.

## Build steps of `consolidate.py`

`main()` runs these steps in this order. The order matters where the table says why.

| # | Step | Function | Note |
|---|---|---|---|
| 1 | Read the sources | `load_*` | A missing posturi, SEAP or status file skips that source with a warning. |
| 2 | Link rows to ANAF records | `Linker.link`, `link_declaratii` | Tiers: `exact`, `canonical`, `unit`, `tokens`. `prefix` is for ANI only. A tie or a weak candidate does not merge. |
| 3 | Make the records | `main` | `A`, then `R`, `G`, `D`, `P`. |
| 4 | Apply curated websites | `apply_curated_websites` | |
| 5 | Merge source-only records | `merge_same_name`, `merge_loose_names` | ANAF records never take part. |
| 6 | Apply curated merges | `apply_curated_merges` | |
| 7 | Clean up sectors and check aliases | `strip_sector_suffix`, `check_aliases`, `apply_same_body`, `infer_sectors` | |
| 8 | Apply curated identities | `apply_curated_identities` | After the sector steps, because those steps treat a record with a CIF as an ANAF record. |
| 9 | Link SEAP by CUI, never by name | `link_seap`, `seap_standalone` | `SEAP_PRIVATE` excludes private bodies. |
| 10 | Check absorbed ids | `check_absorbed_ids` | Compares with the released tags. |
| 11 | Set families and aliases | `assign_families`, `apply_curated_aliases`, `unique_aliases` | |
| 12 | Apply status and fill counties | `apply_status` | After the families, so that a filled county moves no record between families. |
| 13 | Write the outputs and the report | `write_csv`, `write_explorer_data`, `report` | |

## Checks

### The build stops

The script stops with an error and writes no output after that point.

| Script | Stops on |
|---|---|
| `consolidate.py` | A curated row with an unknown id, a duplicate id or a chained link. |
| | An identity on a record that has a CIF, a CIF that is not digits, a duplicate CIF, or a CIF of an ANAF record. |
| | A website value that is not a website, or a CIF listed twice in `websites.csv`. |
| | An alias with an id that is not a record of this build. |
| | An id that a released tag absorbed and that is a record again, or an id of the latest release that is lost. |
| | A CUI that links to more than one record. A duplicate CUI or an empty name in the SEAP file. |
| | A duplicate CUI or an unknown status in `status.csv`. A duplicate slug or name in the posturi file. |
| `lookup_status.py` | A `STARE` label outside the rule, or an empty one on one of our CUIs. A date outside the format. A row with another column count. A CUI on two MF rows. |
| `extract_seap.py` | A `--trust` prefix with no resource or more than one, or several local files for one resource. |
| `publish_pages.sh` | Uncommitted changes in `scripts/`, `curation/`, `explorer/` or `data/consolidated/institutii.csv`, also untracked files. A missing data file. An absolute local path in `metadata.json`. |
| | A failing unit test (the script runs `python3 -m unittest discover -s tests`). |
| | A missing `dataset.build_hash` in `metadata.json`, or a hash that differs from the hash of the same files at `HEAD`. The data was built from other code or curated files than the committed ones. |

The build hash is a SHA-256 over `scripts/consolidate.py` and each `curation/*.csv`, in sorted path order (path, length and content of each file). `consolidate.py` writes it as `dataset.build_hash`. `publish_pages.sh` calls the same function, `build_hash`, on the files of `HEAD`. The checks run in the dry run too. The hash depends on the content, so you can build before or after the commit. If the hash differs, run `uv run scripts/consolidate.py` on the committed files.

After a real push, `publish_pages.sh` polls `https://org.gov2.ro/metadata.json` for at most 3 minutes. If `dataset.generated_at` matches, it prints the record count of the live `rows.json`. If not, it prints a warning and exits 0, because the push is done and Pages or Cloudflare can lag.

### The build warns and continues

- A missing posturi, SEAP or status file: the build skips the source.
- An ANI export with 10,000 rows, the cap of Kibana: the rarest names are missing. Two exports hit the cap now.
- A CIF of the state tree that is not an ANAF root.
- Git tags that the script cannot read: the build skips the absorbed-id check.
- A SEAP file with rejected rows.

`extract_seap.py` reads a file only if its size equals the size in `packages.json`. The current manifest has 291 files. The script took rows from 182 of them (one with `--trust`). It did not read 62 files, because the metadata gives no size (datasets of 2016 to 2019). It took no rows from 47 files, because it found no header. So the SEAP history has gaps.

### Tests

`python3 -m unittest discover -s tests` runs 124 tests. They need no inputs and no network.

| File | Covers |
|---|---|
| `tests/test_consolidate.py` | Link tiers, ties, categories, sectors, merges, absorbed ids, aliases, websites, posturi rules, the build hash. |
| `tests/test_seap.py` | CUI format, report layouts, periods, the cache, the private-name rule, identities, pairs, SEAP links. |
| `tests/test_onrc.py` | Name key, tiers, the identity rule and its rejects, reading raw `"`. |
| `tests/test_status.py` | The status rule, absent CUIs, natural-person rows, SEAP conflicts, the county fill, explorer codes. |

### Checks on the full data

- **Determinism.** `sh tests/determinism.sh` builds twice with different hash seeds and compares the CSV. It needs the inputs. It takes minutes and rebuilds the data, so a person runs it. `publish_pages.sh` does not.
- **Regression.** Compare the summary that `consolidate.py` prints to stderr, before and after a change. Compare the diff of `institutii.csv`. The activity log keeps the numbers.
- **Roots.** "Neclasificate" roots stay at 2.

### Browser checks (by hand)

Serve the repository with `python3 -m http.server`, open `/explorer/`, and use the page console.

- `explorer.reachableRoots()` must equal `explorer.expectedRoots()`. Now: 3,296.
- `explorer.descendantVisibility().failures` must be empty. Now: 8 checked.
- The console must show no errors.
- The default list hides `st` 1 and 2 (27,922 records). With `rad=1&web=0` it shows all 28,308.
- A search by exact CIF finds a hidden record.

### Review queues (a person or Opus reads them)

These files are in `data/consolidated/` and are not in git. A queue never changes the data.

| File | Rows | Holds |
|---|---|---|
| `seap-review.csv` | 4,423 | SEAP rows and their decision, with the best CIF-less record as a proposal. |
| `seap-pairs.csv` | 11 | CUIs with two candidate records. |
| `posturi-review.csv` | 930 | Standalone posturi records, by number of postings. |
| `onrc-review.csv` | 4,656 | ONRC matches for `D` records, by tier. |
| `status-review.csv` | 23 | 6 SEAP conflicts and 17 county disagreements. |

### Sampling for rules

A rule enters only after a sample read by eye, with the result in the activity log. Doubtful rows stay open. Sample sizes limit what we know: for ONRC, 0 wrong of 30 cannot rule out about 10% wrong.

## Known gaps

- `publish_pages.sh` runs the unit tests and checks that the data comes from the committed code, but it runs no determinism check. A person must run `sh tests/determinism.sh` first.
- The build hash covers `scripts/consolidate.py` and `curation/*.csv` only. A change to another script or to an input file does not change it.
- No check runs in CI. CI cannot rebuild the data, because the inputs are not in git.
- The browser checks are by hand. No check confirms that every link of `organizare.html` opens a non-empty view.
- The check after a push compares only `dataset.generated_at` and counts the live records. It does not compare the live files with `main`.
- This repository records no licence for the ANAF list, ROePAS, Registrul, ANI or the maps, but the list is published under EUPL v1.2.
- The page CSV export has no `status` column.

## Adding a source

1. Measure the source, and record its licence and date.
2. Write a brief in `docs/briefs/`. Keep the input out of git.
3. Make a missing input skip the source with a warning.
4. Add its files to `dataset` in `metadata.json`, and add the attribution to `README.md`.
5. Add the source to this document, to `CLAUDE.md` and, for a call or a download, to [external-lookups.md](external-lookups.md).
