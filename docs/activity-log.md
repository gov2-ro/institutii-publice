# Activity log

## 2026-11-05 — Owner decisions on ANAF and `TELEFON`; state of the published site (Opus)

**Done**
- Recorded the two owner decisions in the backlog. The site was not published in this work.
- Compared `gh-pages` with `main`. The last publish is 25592ae, of 2026-11-02, with 25,829 records.

**Hard**
- The backlog said that landing v2 and the DS adoption wait for a publish. Both are live. The publish has no entry in this log, so I repeated the stale claim to the owner. I checked `gh-pages` only when the owner asked about landing v2.
- Measured differences, `gh-pages` against `main`: `gov2.css` is equal; `organizare.html` and `despre.html` differ by one added line each; `index.html` differs by the status filter, the status display and the SEAP source mark. The data differs by 2,479 records.

**Decided**
- Owner: ANAF stays out of the published data for now. The cost: `radiat` stays 0, and 391 deregistered `S` bodies stay visible as `not_found`. The alternative carries a licence risk, because ANAF states no re-use terms.
- Owner: MF `TELEFON` stays unpublished for now. The cost: about 9,000 possible phone numbers stay unused. The alternative can publish personal numbers.

## 2026-11-05 — Status of a legal body and county of `S` records, MF only (Sonnet, brief `record-status.md`)

**Done**
- `scripts/lookup_status.py` (stdlib, 22 s) reads the two MF July files and writes `data/lookup/status.csv` (ignored by git). It covers the 3,406 records with a CIF
  that is not from ANAF (2,580 `seap`, 826 `curation`). It skips every PF row before any field is read: 818,693 PF rows, 27 rows of another type, 1 short row, 1,829,045 PJ rows read.
  It reads no `TELEFON`. Snapshot (latest `DATA_PRELUCRARE` of the PJ rows) 2026-06-11, equal to the value over all rows.
- Result per CUI: `activ` 2,441; `not_found` 572; `fuzionat` 392; `in_lichidare` 1; `radiat` 0. Every `STARE` label on our CUIs is inside the rule: INREGISTRAT 1,984,
  `DIZOLVARE FARA LICHIDARE(FUZIUNE)` 392, MODIFICARE PUBLICI 369, TRANSFER(SOSIRE) 78, RELUARE ACTIVITATE 9, SUSPENDARE ACTIVITATE 1, `DIZOLVARE CU LICHIDARE(INCEPUT LICHIDARE)` 1. No label stopped the script.
  No CUI is on two PJ rows.
- `consolidate.py`: `load_status`, `apply_status`, `write_status_review`. New CSV columns (at the end): `status`, `status_date`, `status_source`, `county_source`.
  Applied on records: `activ` 2,441, `not_found` 572, `fuzionat` 386, `in_lichidare` 1; 6 `fuzionat` CUIs are SEAP conflicts, so their status is empty.
  `metadata.json` `dataset.inputs` has an entry `source: mf` with the file, `snapshot`, `licence` CC-BY-4.0 and the origin. README, CLAUDE.md and `despre.html` give the attribution.
- Compared with the measurement on the older record set: `S` records with MF data 2,273 of 2,747 then. All 2,273 CUIs are still records and found; 165 of them are now `D` records (ONRC identities),
  so 2,108 `S` records have MF data now (2,103 applied, 5 SEAP conflicts). `S` `fuzionat`: 344 then; now 339 applied + 5 conflicts = 344. `S` not found: 472 of 2,580.
  The 561 other found CUIs are `D` 312, `G` 213, `R` 27, `P` 9 (curated identities).
- Status per kind (applied): `S` activ 1,763, not_found 472, fuzionat 339, in_lichidare 1; `D` activ 450, not_found 58, fuzionat 27; `G` activ 195, not_found 39, fuzionat 17; `R` activ 25, not_found 3, fuzionat 2; `P` activ 8, fuzionat 1.
- Hidden by default (`st` 1 or 2): 386 records, all `fuzionat`: `S` 339, `D` 27, `G` 17, `R` 2, `P` 1. By category: Educație 272, Asistență socială și muncă 25, Altele 21,
  Agricultură mediu și păduri 15, Autorități centrale și deconcentrate 10, Cultură sport și tineret 9, Servicii publice locale și regii 9, Sănătate 8, Ordine publică și urgențe 6, Apărare 6,
  Companii de stat 2, Transport și infrastructură 2, Finanțe publice 1. None has a website or a parent. Dates: 2025 228, 2024 43, 2026 20, older 95.
- County fill: 1,585 `S` records got a county (all with an empty county before; `S` with no county 2,014 -> 429); 1,389 also got a UAT (`uat_source` `status`). 17 disagreements, none replaced:
  `county_differs` 17 (9 `S`, 8 `D`; examples: ELECTRICA FURNIZARE SA SEAP Brasov, MF Bucuresti; ROMARM filials; E-DISTRIBUTIE BANAT SEAP Timis, MF Bucuresti, the seat of the company).
  `status-review.csv`: 23 rows = 6 `seap_conflict` + 17 `county_differs` (0 `county_unknown`). Conflicts: `S14490379` E-DISTRIBUTIE BANAT (fuzionat 2024-11-30, SEAP to 2026), `S14500308` E-DISTRIBUTIE DOBROGEA (same),
  `S14493260` and `S14506181` (SDEE, fuzionat 2020-12-31, SEAP to 2023 and 2024), `S4417176` (fuzionat 1993, SEAP to 2025), `G18039` (fuzionat 1993, SEAP to 2025).
- CSV against v0.55.0: 28,308 records, same ids in the same order; 1,585 records changed; changed old columns: `county` 1,585, `uat` 1,389, `uat_source` 1,389 (all from empty). Every other old column is equal.
  Without `status.csv` the CSV differs only by the 4 new empty columns (measured before the first run with status).
- Explorer: row keys `st` (1 radiat, 2 fuzionat, 3 in_lichidare) and `sd` (ISO date); `us` is now 1 (sector from the name) or 2 (county from MF). The menu "Opțiuni" has the filter "Include entități radiate sau fuzionate"
  (hash `rad=1`). Default views hide `st` 1 and 2: list, facets, county profile, landing counts and map, families, the header count ("27.922 din 27.922" instead of 28.308). The empty state counts the hidden records and has the button "Arată-le".
  A search by the exact CIF finds a hidden row. The record detail shows "Fuzionată din <dată>" (tag, DS `g2-tag`) and the source. The list shows a tag on the shown rows. No new local CSS.
- Checks: 122 unit tests pass (111 before, 11 new in `tests/test_status.py`); `tests/determinism.sh` passes; neclasificate roots 2. Browser check (headless Chrome, own server on port 8765, Chrome on 9333; both stopped):
  default list 2,299 rows with the website filter, 27,922 without it, 0 rows with `st` 1 or 2; `rad=1` gives 28,308 (386 with `st` 2, 1 with `st` 3); exact CIF search finds `S4266197` with the filter off and the website filter on;
  a partial CIF does not; `reachableRoots()` 3,296 = `expectedRoots()` 3,296; `descendantVisibility()` 8 checked, 0 failures; 0 console errors; landing 27,922 (28,308 with `rad=1`); county Alba 589 records (591 with `rad=1`).

**Hard**
- A hidden row has no website, so with the default website filter the empty state found nothing to offer. The count for the button now ignores the website filter too, and the button turns that filter off when it is needed.
- MF writes `Bîrlad`, `Oraş Bragadiru`; ANAF has `Municipiul Barlad`, `Orasul Bragadiru`. The UAT lookup maps a non-initial `î` to `a` and strips the prefix. 217 `S` records still have a county and no UAT (a village, or another spelling).
- The explorer `web` filter is on by default, so "the default list" has two counts: 2,299 (website) and 27,922.

**Decided**
- (Opus review) The CSV value `activ` is renamed `listat` in the code and the docs: MF lists the body and shows no dissolution. `activ` was a claim that `MODIFICARE PUBLICI` can contradict. Numbers in this entry that say `activ` mean `listat`. `county_source` and `uat_source` say `mf`, not `status`. `rows.json` is equal before and after these two changes.
- (Sonnet, assumed) `in_lichidare` gets the row value `st` 3. The page hides only 1 and 2. Cost of the alternative (no key): the detail could not show the label.
- (Sonnet, assumed) `sd` is an ISO date string and the page formats it as dd.mm.yyyy. `activ` and `not_found` give no `st` and no `sd`.
- (Sonnet, assumed) The CSV `status` column holds all values, `activ` and `not_found` too. `activ` means only that MF lists no dissolution; README and `despre.html` say so. Cost of blanking `activ`: an empty value would mean "not checked", so the column would lose that difference.
- (Sonnet, assumed) The county fill runs after the families. Cost of the alternative: a county word in the name would move records between families (the brief forbids changes outside county and uat).
- (Sonnet, assumed) A UAT is set only when the MF locality maps to an ANAF UAT label or to a sector; otherwise the county is set and the UAT stays empty. Cost of the alternative (raw MF locality as UAT): villages would appear as UAT labels and break the county map join.
- (Sonnet, assumed) The exact-CIF search overrides the website filter for a hidden record only; it leaves the website filter of other records as it was.
- (Sonnet, assumed) A SEAP conflict keeps `status` empty but still fills the county. The review file lists it.
- The `S` count in the brief (2,747) fell to 2,580 after the ONRC build. The expected 2,273 found and 344 `fuzionat` match exactly after the 165 records that moved to `D` are added back (see Done).

## 2026-11-05 — ONRC identities and merges applied (Sonnet, rule by Opus)

**Done**
- `scripts/onrc_candidates.py` (stdlib) writes the queue `data/consolidated/onrc-review.csv`. Run on the baseline (4,634 CIF-less `D` records), it gives the survey
  counts exactly: `exact_county` 315, `exact_elsewhere` 33, `ambiguous` 12, none 4,274; 4,659 rows; every column equal to `data/lookup-survey/onrc-review.csv`
  (only the row order inside 2 ambiguous records differs). The survey script was not kept, so the rules were rebuilt from the data: the key drops a leading SC and the words
  SA, SRL, RA anywhere in the name; ONRC rows with CUI `0` or empty are dropped; `ambiguous` lists at most 5 rows. One column is new: `onrc_code` (the evidence needs it).
  `identity_rejects` holds the rule of the brief for a new identity. Runtime 26 s. Tests `tests/test_onrc.py`: 9 new, 111 in all, pass.
- Task 2 test: 3 identities (MEDITUR `D008ce49e`, TEGA `D78f77c4a`, HIDRO PRAHOVA `D22d54b26`) absorbed their `S` records; each `D` record changed in `cif`, `cif_source`,
  `sources`, `merged_ids` only; no other record changed. The rows stay.
- Sample of the merge candidates (by eye, no independent source): 30 of 171 `S` holders `exact_county` (seed 20261105): 30 right. All 27 other holders `exact_county`: 26 right,
  1 doubtful. All 7 `S` holders `exact_elsewhere`: right. The 15 other holders `exact_elsewhere`: 2 right, 13 wrong (generic names). A flag scan of all 171 `S` cases (name key, county,
  generic name with no `S` county) found 2 form conflicts. 0 wrong in 30 cannot rule out a wrong share up to about 10%. The other 141 `S` cases had only the flag scan.
- Applied (rule below). Records 28,511 -> 28,308 (-203: 167 `S`, 35 `D`, 1 `P`). `curation/identities.csv` 581 -> 826 rows; `curation/merges.csv` 81 -> 117 rows.
  - Item 1, `S` holder `exact_county`: 165 records, 158 identity rows (7 `D` copies of a CUI merged first). With the 3 test rows: 168 of the 171.
  - Item 2, `S` holder `exact_elsewhere`: 7 records (`D1045fb36`, `D813a80a4` one CUI, `D3ae4624e`, `D418881c1`, `D49b57100`, `Dd5b7d64a`, `Df65a22bf`): 6 identity rows, 1 copy merged.
  - Item 3, other holders `exact_county`: 26 merge rows (22 `G`, 2 `R`, 1 `P`, 1 `D`). The `P` holder is absorbed into the ANI record (order ROePAS, Registrul, ANI, posturi); its
    existing identity row moves to the survivor `D5352a16a`.
  - Item 4, `exact_elsewhere`: `D3d5ab95f` (to `G10286`) and `D8bb7fdd6` (to `G15383`): 2 merge rows.
  - Item 5, several `D` records on one CUI: 8 merge rows (7 in item 1, 1 in item 2). CUI 27515874 is excluded.
  - Task 4, new identities by the rule of the brief: 78 rows (48 SA, 30 SRL) of the 117 `exact_county` identity candidates. Rejected: 13 (CUI matches another `D` record), 17 (not in function: 14 `no`,
    3 `unknown`), 6 (no company form in the name), 3 (form conflict). Evidence on every row: `ONRC 2026-10-19 <COD_INMATRICULARE>, tier <tier>`; `checked_at` 2026-11-05.
- `consolidate.py` summary after the build: linked SEAP CUIs 13,470 -> 13,654 of 18,077 (75.5%); new `S` records 2,744 -> 2,580; records of their own from ANI 4,596 -> 4,377 (all "from" values are the run of task 2; the baseline has 2,747 new `S` records);
  curated identities 826 (was 581); curated merges 111 (was 75); neclasificate roots 2. Companii de stat 1,406 -> 1,236 (run of task 2 -> now).
- CSV diff against the committed file: 203 records removed, 0 added, 271 changed; all 271 are in the curation rows (survivors and their holders). Every removed id is in `merged_ids` of a survivor.
  Changed columns: `cif`, `cif_source` 246; `sources` 210; `merged_ids` 193; `declaratii_count` 22; `aliases`, `aliases_unique` 33; `link_declaratii` 31; `declaratii_group` 6; `category` 1; posturi columns 1.
- Families: 184 before, 184 after, none lost. Members lost by merges: Institut național 123 -> 116, Regie autonomă 99 -> 96, Muzeu 129 -> 128, Centru de sănătate 29 -> 28.
- Checks: 111 unit tests pass; `tests/determinism.sh` passes (identical CSV under `PYTHONHASHSEED` 1 and 2); browser check (headless Chrome, own server): `reachableRoots()` 3,296 = `expectedRoots()` 3,296,
  `descendantVisibility()` 8 checked, 0 failures, 0 console errors.
- Attribution to ONRC, the dataset and CC-BY-4.0: `README.md`, and the data flow of `CLAUDE.md`.

**Hard**
- The first form check treated "R A T SRL" as a company with the form RA. A spaced "R A" is not a safe form word. The rule now needs the ONRC form to be one of the forms found in the name.
- The 3 test rows ran before the rule existed, so the sample and the final build use the same data but the queue changed from 4,634 to 4,631 records.
- `absorb` gave `G02187` the category of the absorbed ANI record (Altele -> Companii de stat). It is the existing rule for the category Altele; not changed.
- `onrc_candidates.py` and the unit tests cannot test the ONRC files; the zero-difference result against the survey queue is the regression check for the rules.

**Decided**
- (Opus) `S` holder, `exact_county`: identity row on the `D` record, also when the company is dissolved (one body; the status brief handles the state). Form conflicts and CUI 27515874 go to hand review.
- (Opus) `S` holder, `exact_elsewhere`: the 7 ids that were read enter (specific names). Other holders, `exact_county`: `merges.csv` rows, survivor order ROePAS, Registrul, ANI, posturi; `Dffbbf1ee` stays open.
- (Opus) In `exact_elsewhere`, only `D3d5ab95f` and `D8bb7fdd6` enter among the other holders. The 13 generic cases never enter (see Verified limits in the backlog).
- (Opus) Several `D` records on one CUI: merge first, identity on the survivor.
- (Sonnet, assumed) Survivor of a `D` copy group: the record without a leading SC in the name, then the larger `declaratii_count`, then the lower id. Cost of the alternative: none seen; the survivor only changes the display name.
- (Sonnet, assumed) A name with only "SC" and no form word is "no form in the name": the rule does not apply (6 records). The brief is silent on this case.
- (Sonnet, assumed) The ONRC form `INCD` never agrees with a form word in the name. No `INCD` record passed the rule; the `INCD` records that entered are merges with a `G` holder or have no form word in the name.
- (Sonnet) Hand-review list (dissolved, form conflicts, shared CUIs, no form, `Dffbbf1ee`) is in the backlog, open. Nothing from it is applied.

## 2026-11-05 — Finance Ministry dataset measured; source of the status brief (Sonnet measure, Opus decision)

**Done**
- MF July files on geana: 2,647,766 rows; 1,829,046 PJ, 818,693 PF, 27 other. No duplicate `COD_FISCAL`. Snapshot 2026-06-11 (latest `DATA_PRELUCRARE`), not July.
- Coverage: `S` 2,273 of 2,747 (ANAF: 2,728); `A` 13,443 of 13,485. With ANAF on 2,273 `S`: county 2,273 agree; locality 3 real differences; label 2,199 agree, 74 differ. No row is defunct in MF and active in ANAF.
- Of 809 defunct by ANAF: 345 defunct in MF, 391 absent, 73 under another label (67 `MODIFICARE PUBLICI`, 6 `INREGISTRAT`). MF has only 41 `RADIERE` rows. Of 474 absent `S`, 64 are live by ANAF and 19 are unknown to both.
- CUI 4515077 is absent from MF, so MF does not settle that conflict.

**Hard**
- `DATA_RADIERE` is filled only for mergers. `MODIFICARE PUBLICI` is a registration event of 1993 and 2011, not a public-entity flag: 12% of `A` lack it and it covers parishes. Its meaning is not documented.

**Decided**
- (Opus) MF is the base source of `record-status.md`: clear licence, bulk, no API limits. Cost: the 464 masked or absent defunct bodies stay visible unless ANAF also feeds it. Absence from MF never means `radiat`.
- (Opus) `in_lichidare` is a separate status and stays visible. The page never claims "active", because `MODIFICARE PUBLICI` can hide a dissolution.
- (Opus) ANAF re-use is a licence risk, so the owner decides. `TELEFON` is not published: it may hold personal numbers.

## 2026-11-05 — ONRC match measured; Finance Ministry and ANFP columns read (Sonnet)

**Done**
- ONRC files on geana: `OD_FIRME` 4,229,451 rows, `OD_STARE_FIRMA` 4,670,796 rows, `N_STARE_FIRMA`. Sizes equal the CKAN metadata; SHA-256 in `SHA256SUMS` there.
- Match of 4,634 CIF-less `D` records (folded name without the legal form): `exact_county` 315, `exact_elsewhere` 33, `ambiguous` 12, none 4,274. With a company form (560 records): 297, 16, 11, 236.
  Of the 348 exact matches: 297 in function, 43 dissolved, 8 unknown; 128 give a new CUI; 220 name a CUI that another record holds. The rule "form agrees, one row in the county, CUI on no other record" leaves 96 `exact_county`.
- Eyeball samples (name, county, category, form; no independent source): `exact_county` 0 of 30 wrong; `exact_elsewhere` 14 of 30 wrong, 3 doubtful (generic local names matched to an unrelated SRL). Missed matches are not measured.
- Finance Ministry sample (5 MB of 3 files): see the backlog. ANFP list 2025 read in full: 4,325 rows, no CUI, no contacts.

**Hard**
- ONRC names hold raw `"`, so a reader needs `QUOTE_NONE`. The Finance Ministry `.csv` files are ISO-8859-2; the July `.txt` files are UTF-8. Its title says June, but the July files are newer.

**Decided**
- (Opus) No ONRC match enters the curation without a review of the rule. `exact_elsewhere` and `ambiguous` get no rule.

## 2026-11-05 — lookup survey: ANAF, ONRC, alternatives; brief for record status (Sonnet survey, Opus brief)

**Done**
- ANAF `PlatitorTvaRest/v9/tva` on 2,747 `S` CUIs (28 requests, no key): 2,728 found, 19 not found. County and locality on all found rows;
  this fills the county of 2,048 records; 668 of 680 existing counties agree. 422 `RADIERE`, 386 `DIZOLVARE FARA LICHIDARE(FUZIUNE)`, 1 `DIZOLVARE CU
  LICHIDARE`: 809 (29.5%). Of the 253 `S` records found only in the 2014 files, 187 (74%) are defunct or not found; of the others, 26%.
- ONRC on data.gov.ro: `OD_FIRME` and `OD_STARE_FIRMA` are CC-BY-4.0, `^`-separated, with name, CUI, county, legal form and status. Commercial-register
  entities only. About 498 of 4,634 CIF-less `D` records have a company form in the name (rough regex). The match rate is not measured yet.
- Alternatives compared: see *Verified limits* in the backlog. The Finance Ministry dataset is the open lead.
- Brief `docs/briefs/record-status.md`, draft.

**Hard**
- The survey broke the "no full download" rule: data.gov.ro ignored the Range header and sent 788 MB. The agent cut the files to samples and deleted the full copies.
- The survey reported 2,045 filled counties. The recount from its CSV gives 2,048.

**Decided**
- (Owner) Keep defunct records, add a status, hide them by default. Download the ONRC files to geana. Check the Finance Ministry columns first.
- (Opus) `fuzionat` differs from `radiat`: 386 bodies, mostly schools, continue inside another body. An empty status means "not checked", never "active".
  A status that conflicts with later SEAP activity goes to review (CUI 4515077: `RADIERE` 2017, SEAP rows up to 2026-Q3). Cost: some defunct records stay visible.
- (Opus) The build waits for the source decision: ANAF states no re-use terms and `institutii.csv` is public.

## 2026-11-05 — SEAP: period() fix and cache-only check (Sonnet)

**Done**
- `period()` in `scripts/extract_seap.py`: a year in the file name wins over the year in the dataset title. The year must stand alone
  (not inside the 8-character id prefix). Compared with the old function on the 291 resources: 233 keep their period, 58 change. All 58 are in
  the dataset "Achizitii publice 2007-2015 (Contracte)" (files of 2008-2016, title year 2007). No other dataset has a year in the name that
  differs from the year in the title.
- Cache: the refresh now runs when the period in the cache differs from the computed period (was: when the period is missing). It rewrites
  only the cache header. No `CACHE_FORMAT` bump, no full read. Two new tests: `period()` with real names, and the stale-period refresh. 102 tests pass.
- `extract_seap.py --trust 38e601a9` on the full dump: 291 resources; status 181 `read`, 1 `trusted`, 62 `no_size`, 47 `no_header`, 0 `missing`
  (as before); data rows 24,919,088; rejected 12,528; distinct CUIs 18,077. `first_seen` 2007: 4,935 -> 0 CUIs; `last_seen` 2007: 294 -> 0.
  Compared with the file before the run: 18,077 CUIs in both; only `first_seen` (4,935 rows) and `last_seen` (294 rows) differ. In the manifest only
  `period` differs (58 entries).
- Cache-only check: `--dump` pointed at a folder with `packages.json` only, `--out` at a copy of the cache. Result: 182 resources `cached`
  (181 `read` and 1 `trusted` before), 109 `missing` (62 `no_size`, 47 `no_header`); `authorities.csv` byte-identical (`cmp`); 18,077 CUIs; the
  manifest fields of the 182 cached entries (size, sha256, rows, rejects, authorities, report_type, period, file) equal the run with the dump.
- `consolidate.py`: `institutii.csv` unchanged. `tests/determinism.sh` passes.

**Hard**
- The cache stores the period, and a cache hit never ran `period()` again. The old check only filled a missing period. The new check compares.
- The 47 `no_header` files have no cache. The extractor reads them again on every run with the dump (no rows, a few seconds each).
- A file name like `...-2025.xlsx` contains the 8-character id prefix `3a2f2079`. A plain regex `20\d\d` would match `2079`, so the year must stand alone.

**Decided**
- (Opus order, 2026-11-04) Fix the defect first, then the owner deletes the dump.
- (Owner, 2026-11-04) The loss of the 62 `no_size` and 47 `no_header` files is accepted.
- (Sonnet) A stale period is corrected in the cache header, not by a `CACHE_FORMAT` bump. Cost of the alternative: a full read of the dump
  (15 minutes or more) for an unchanged result. Risk of this choice: none seen; the test and the run above cover it.
- (Sonnet, assumed) A name with no year (for example `raport-contracte-tiii.xlsx`) keeps the year of the title. This holds for 30 resources of 2021, 2024 and 2026 (titles with one year, so the year is right).

## 2026-11-04 — SEAP re-run, ANAF lookup for the pairs, browser check (Sonnet, Opus decisions)

**Done**
- `extract_seap.py --trust 38e601a9` on the full dump: 291 resources; 181 read (was 178), 1 trusted, 62 `no_size`, 47 `no_header` (was 4), 0
  `missing` (was 46). The 46 missing files exist now: 3 were read (`cumparari-directe` 2014 T3 and T4, 716,285 rows) and 43 are `^`-separated
  files of 2007-2014 (`no_header`). Data rows 24,202,803 -> 24,919,088; rejected 12,477 -> 12,528. Distinct CUIs 17,783 -> 18,077 (+294,
  all with no county, all from the 3 new files).
- After the re-run: records 28,294 -> 28,548; linked 13,449 of 18,077 CUIs (74.4%); new `S` records 2,511 -> 2,765; `seap-pairs.csv` 26 -> 29
  rows (18 `two_records`, 11 `two_seap_rows`). Three new rows: `11446310`, `15221670`, `17329505`.
- ANAF web service (`PlatitorTvaRest/v9/tva`, POST, no key) sent the 29 CUIs of `seap-pairs.csv` in one request: 28 found (96.6%), 1 not found
  (`448001922`, 9 digits). 24 of the 28 have no VAT registration; several have the status RADIERE or DIZOLVARE. No body is flagged inactive.
  The answer gives name, seat county, seat locality and status. Raw answer: `data/seap/anaf-lookup-pairs.json` (not in git).
- Curation: 19 merges in `curation/merges.csv`, 18 identities in `curation/identities.csv`. Applied: Registrul Auto Roman, Camera de Comert
  Braila, FRDS, Politia Locala Sector 2, Fondul Roman de Contragarantare, CNEE, Politia Locala Chitila, Politia Locala Bistrita, Spitalul
  Orasenesc Videle, ADP Oradea, CNIT, APM Ilfov, Centrul Cultural Lumina, Electrica Serv; identity only: Serviciul Public Piete Oboare (Calarasi), Camin pentru persoane
  varstnice (Mures), Gestionare a cainilor (Sibiu and Olt).
- Rebuild: records 28,548 -> 28,511 (19 merged, 18 `S` records now linked by CIF); new `S` records 2,747; `seap-pairs.csv` 11
  rows (4 + 7). In the CSV only the 18 survivors changed on old records, plus `family` of 4 records (see Hard). 100 tests pass; determinism
  passes; neclasificate roots stay at 2.
- Browser check, run before the Opus review changes below and not repeated (headless Chrome, page served from the repo root): `reachableRoots()` 3,296 = `expectedRoots()` 3,296;
  `descendantVisibility()` checked 8, 0 failures; 0 console errors.

**Hard**
- The 4 `no_header` files of 2026-11-03 became 47 because the download added 43 more `^` files. They stay unread by the earlier decision.
- The 3 files of 2014 get the period 2007-Q3 or 2007-Q4 (defect in `period()`); `first_seen` of 4,935 CUIs now says 2007.
- Merging 3 ANI copies of "Politia Locala Sector 2" (counties Ilfov, Calarasi, Giurgiu) dropped the family "Poliția locală" from 4 records
  (Sector 1, 2, 4, 5): the rule of 5 members in 4 counties no longer holds. The family lists 62 -> 53 records.
- Several ANAF names differ from the SEAP name (for example `11446310` "CAMERA AGRICOLA DOLJ", `15221670` the Mangalia body, `4515077` DADR
  Constanta with the status RADIERE 2017 and SEAP rows up to 2026-Q3). Those rows stay open.

**Decided**
- (Opus) A CUI is one legal body. A wrong merge costs more than a duplicate, so in any doubt the row stays open.
- (Opus) Specific names (Registrul Auto Roman, FRDS, Politia Locala Sector 2, CNEE and others): merge, and the ANI county is noise.
- (Opus) Generic names: identity only, never a merge. Rule: exactly one candidate lies in the ANAF county; its `uat`, if any, equals the ANAF
  locality; no other CUI of the same name lies in that county. Otherwise the row stays open.
- (Opus) 448001922 (9 digits) is applied only if ANAF confirms it. ANAF does not know it, so the row stays open.
- (Opus) "A.B.A." is not a defect: only 3 posturi names use the spelling, all three name SGA units. A change in `fold` would alter every
  initialism. The backlog item is dropped.
- (Sonnet, assumed) For `4515077` the ANAF name differs from the SEAP name, so the row stays open although the county rule holds.
- (Opus review) `14198936` Piete Oboare: the Sonnet merge of D22bd9669 (Arges) is undone. The name is generic, so the ANAF seat of the CUI says
  nothing about the Arges record. The identity on G12310 stays. Cost: a possible duplicate. `39466317` Lumina stays merged: ANI often files
  Bucuresti bodies under Ilfov. `17329505` Electrica Serv is merged (specific name, same county in both records).

## 2026-11-04 — SEAP pairs review (Sonnet)

**Done**
- 44 duplicate project records merged in `curation/merges.csv` and 41 identities added to `curation/identities.csv`, for the pairs of
  `seap-pairs.csv` whose records name one county (or one Bucuresti sector, where ANI files the body under Ilfov). Rule: same
  normalized name as the SEAP authority, 3 or more words. Survivor order: ROePAS, Registrul, ANI, posturi.
- Records 28,379 -> 28,294. Linked 13,421 of 17,783 CUIs (75.5%); new `S` records 2,511; `seap-pairs.csv` 26 rows (15 + 11).
- 100 tests pass; determinism passes; neclasificate roots stay at 2.

**Hard**
- The release tag v0.48.0 lists `S` ids. `check_absorbed_ids` ran before the `S` records existed and stopped the build. It now runs
  after the SEAP step; an `S` record that a CIF links into another record goes to that record's `merged_ids`, and an `S` id that
  a rule excludes counts as retired.
- The Chrome extension was not connected, so the browser check of `reachableRoots()` is still open.

**Decided**
- The 15 `two_records` rows with different counties and the 11 `two_seap_rows` rows stay for a person: a wrong merge of two bodies
  with one name costs more than a duplicate.

## 2026-11-03 — SEAP source, CIF identities, hosted-body aliases (Sonnet build, Opus decisions)

**Done**
- `scripts/extract_seap.py`: reads the data.gov.ro "Achiziții publice" dump (xls, xlsx, ods, csv) into `data/seap/authorities.csv`,
  `manifest.json` and a per-file cache. The same input files give byte-identical outputs (checked under `PYTHONHASHSEED` 7 and 99).
  A resource with a valid cache and no local file gets the status `cached` (owner request: the dump will be deleted).
- Measured on the dump of 2026-11-03: 291 resources: 178 read, 1 trusted (`38e601a9`, checked by hand), 62 `no_size` (2016-2019: no size
  in `packages.json`), 46 missing, 4 `no_header` (2007-2016 `^`-separated files). 24,202,803 data rows, 12,477 rejected rows
  (nearly all the placeholder `188390213601991`). 17,783 distinct authority CUIs.
- `consolidate.py`: source `seap` (bit 32), `link_seap`, `seap_standalone` (`S<cui>`), rule `SEAP_PRIVATE`, `seap-review.csv`,
  `seap-pairs.csv`, `curation/identities.csv` (`apply_curated_identities`, column `cif_source`). Explorer: SEAP source filter, badge,
  `S` id label, row key `nc`.
- Link: 13,380 of 17,783 CUIs (75.2%) by `cif` (13,235) or `cif_tva` (145). Not linked: 4,403 = 2,552 new records + 1,851 excluded
  (42.0%): association 990, company 394, church 246, foundation 127, tip 72, sports club 22. 794 review rows carry a CIF-less candidate.
- Of the 2,552 new records, 508 have a company form: 351 with a public-service marker, 157 with 100 rows or more and no marker.
- Identities: 522 rows (512 exact-name, 9 INCD by hand, CNAIR). Merges: `Dd8f2fa63` -> `R11040419` (CNAIR), `Ddf110eaa` -> `R11040493` (BNR).
  Aliases: 4 rows (`Consiliul Fiscal`, `CSAT`, `Consiliul Suprem de Aparare a Tarii`, `Autoritatea de Audit`).
- `seap-pairs.csv`: 56 CUIs with two candidate records, 11 with a name that two SEAP rows share. No identity row for these.
- Records 25,829 -> 28,379 (+2,552 `S`, -2 merged). By category (before -> after): Educație 10,046 -> 10,691; Altele 1,302 -> 1,834;
  Companii de stat 1,002 -> 1,464; Asociații 482 -> 804; Agricultură 971 -> 1,270; Cultură 1,569 -> 1,631; Servicii publice locale 793 -> 877;
  Asistență socială 758 -> 814; other categories change by 0 to 27. In the CSV only `sources` (13,330), `cif` (522), `family` (22),
  `aliases_unique` (12), `aliases` (5), `merged_ids` (2) and `declaratii_count` (1) changed on old records. 100 tests; determinism passes.
- State tree: "neclasificate" roots stay at 2. Root CIFs of `rows.json` (rows with `f`, no `nc`, no `p`) equal the CIFs placed in
  `metadata.state`: 3,296 both. Not run in a browser (no DOM in node); `node --check` passes on the page script.

**Hard**
- The brief said "column 0 is the name, column 1 is the CUI". The reports of 2018-2021 start with the bidder (`CASTIGATOR`,
  `CASTIGATOR_CUI`). The first run read 97,107 CUIs, most of them bidders. The header rule is now: the CUI column is the first
  one that is not a bidder column, and the cell before it must look like an authority name. A wrong header is `no_header`.
- One 2022 file joins two reports (a second header at row 415,943). A header inside the data starts a new layout.
- Two CSV styles: `|value|,|value|` (2022) and Windows-1250 text (2023). Typos seen in the CUI: `R 8468440`, `RO1883902 / J13/60/1`.
- Each cache bump cost 15 minutes (the full read). Cache format 3 holds the period and report type for the `cached` status.
- With the first rule set 33.1% of the unlinked rows were excluded and the sample held private SRLs: Sonnet stopped and asked.

**Decided**
- (Opus) The exclusion share is accepted: the 15% limit was a guess, and the full dump has many EU-funded private beneficiaries.
  The typo "asociatia de dezvoltare intracomunitara" counts as an ADI.
- (Opus) A company-form name (SA, SRL, RA) is excluded with rule `company` if the 2023 tip is "Operatorii economici care beneficiază de
  finanțare din instrumente structurale", or if the name has no public-service marker (`SEAP_PUBLIC_COMPANY`) and fewer than 100 rows.
  Only bodies of local authorities (ADI, metropolitan zones, AMR, UNCJR) are exempt from the tip rule. Cost: some small municipal
  companies with an unusual name are lost (they stay in `seap-review.csv`).
- (Opus) Records with a `cif_source` other than `anaf` are not roots of the state tree. They had no place there before this work.
- (Opus) The 62 `no_size` files and the 4 `^` files stay unread (see the backlog).
- SEAP and identities run after the sector steps. A record with a CIF counts as an ANAF record there, so the earlier order
  changed 9 names and 12 sector labels of old records.
- Identity seeding rule: same normalized name (case, diacritics, punctuation, legal form), 3 or more words, not a local kind,
  one SEAP row and one CIF-less record only. Pairs go to `seap-pairs.csv`.

## 2026-11-02 — SEAP source and CIF identities: survey and brief (Opus)

**Done**
- Sonnet surveyed the SEAP dump (data.gov.ro, ADR). 2026: 21 files, 2.9 M rows, 14,126 authority CUIs; 12,418 match a
  `cif`, 92 only a `cif_tva`, 1,616 nothing. The dump was still downloading: 2024 and most 2023 TIII/TIV files are missing.
- Brief `docs/briefs/seap-authorities-source.md`: extractor with a per-file cache, source `seap` linked by CUI,
  standalone `S<cui>` records, `curation/identities.csv`, hosted-body aliases.

**Hard**
- SEAP has no contact data: only the authority name and CUI. The owner asked for contacts; they need a phase-2 scrape.

**Decided**
- Link SEAP by CUI only, never by name. A name match is a proposal in `seap-review.csv`. A wrong name link would
  attach a CUI to the wrong body; the cost is manual review of the CIF-less matches.
- Unmatched authorities become records, except obvious private bodies (owner). Cost: some municipal SRL/SA and ADI
  enter as records with no parent in "Structura statului".
- Curated identities set a CIF only on a record without one. A CIF of an ANAF record must go to `merges.csv`.
- Consiliul Fiscal, CSAT, Autoritatea de Audit: aliases on the host body, no record (owner). AMR, UNCJR: via SEAP.

## 2026-11-02 — issue #6: acronym aliases, ROTLD, two duplicate pairs (Sonnet)

**Done**
- 8 rows in `curation/aliases.csv`: ROTLD and ICI (`R11052491`), INCAS (`G10606`), GeoEcoMar (`G10610`), IFIN-HH (`G26068`),
  INCDFM (`G26071`), CNAIR (`R11040419`), ARACIP (`A18126924`). ANMCS existed (`A34998410`).
- New `apply_curated_aliases` copies reviewed alias rows into `aliases` of every id kind, after the merges, before `unique_aliases`.
  Before this, only the linker read the file and no alias of a `G`, `R` or `D` record reached the search. 163 records gained aliases.
- 2 rows in `curation/merges.csv`: `Dd57bd520` -> `G26071` (INCDFM), `D5b3d7d53` -> `R11040419` (CNAIR).
- Records 25,831 -> 25,829. Records with `aliases_unique` 5,289 -> 5,335. In the CSV only `aliases`, `aliases_unique`,
  `merged_ids` and the merge side effects (`sources`, `link_declaratii`, `declaratii_count`) changed. 68 tests; determinism passes.

**Hard**
- The first run showed that the alias rows did not reach `al`. The cause was in the code, not in the data.

**Decided**
- The two duplicate pairs go to `merges.csv`, not `same_body.csv`: each pair has one tax identity, so a merge is correct.
- The CIF identity file and the absent bodies wait for an owner decision (see the backlog).

## 2026-11-02 — explorer issues #1-#5 (Opus decisions, Sonnet build)

**Done**
- #1: `go()` calls `noWeb()`. The example links carry `web=0`. The landing placeholder equals the list placeholder.
  A `?q=` URL (form without JavaScript) moves to `#v=list&q=…&web=0` on load.
- #2: the landing county row calls `noWeb()` and opens the profile with `web: false`.
- #3: "Caută un tip" uses `norm` and tokens. A per-type map holds the normalized names.
- #4: the empty state counts the records that pass all filters except `web`. It shows the count and a button "Arată-le".
  The landing header counter shows "N înregistrări" without the filter.
- #5: `publish_pages.sh` copies `institutii.csv` to the site root and fails if it is missing. The footer links it, with the
  generation date and the EUPL v1.2 line.
- One commit per issue. 67 tests pass. The dry run of `publish_pages.sh` passes.

**Hard**
- The issue text says 35 columns. The real CSV has 41 (`csv.reader` on the header). The footer says 41.
  The number is hard-coded; a backlog item records it.
- I did not run the page in a browser. I checked the script syntax with `node --check` only.

**Decided**
- Only `institutii.csv` is published, not `institutii.json` (owner decision). The cost of the JSON: 2x the size on Pages.

## 2026-11-02 — name rules for posturi employers (DATA-ORG-03; Opus brief and reviews, Sonnet build)

**Done**
- `posturi_clean()` strips `, județul X` and `U.A.T.`. A bare „UAT X” is read as „Comuna X”.
- Shared word equivalents, for all sources: spital/spitalul, complex/complexul, tg/târgu, dr/doctor, cf. The `tg` rule
  moved out of `DECL_ABBREV`.
- A kindergarten never token-links to a school.
- The linker reads the `status=reviewed` rows of `curation/aliases.csv`. 21 acronym rows were added (USAMV, DGASPC, ABA).
- 9 commits; 67 tests; determinism passes.

**Measured**
- Posturi linked: 4,443 → 4,661 (75.3% → 79.0%; 81.1% of postings). Tokens links: 1,616 → 778; exact: 1,932 → 2,631.
- Review queue: 1,172 → 945; with 10 or more postings: 11 → 6. The 22 „U.A.T. X” → school links now go to the commune.
- Alias wiring changed 222 old-source links, mostly canonical → exact. The agent hand-checked a sample of 40: none worse.

**Hard**
- The stop rule fired twice. Each time the agent stopped before it committed the data.
  - Unifying the words changed the IDF, and Penitenciarul Poarta Albă linked to the prison hospital. Fix: a unified
    token keeps the IDF of its written form. A first attempt, the IDF over written forms only, lost two good links.
  - A kindergarten in Tg Jiu linked to a school. The cause was the `tg` rule, which now applies to both sides, not the IDF.
    The first diagnosis was wrong.
- The alias wiring needed two build fixes:
  - a curated merge that a tier now links counts as `redundant`;
  - `check_absorbed_ids` walks the releases newest first.

**Decided**
- The kindergarten guard is narrow: only „gradinita” against anything else. A broad head-word rule would block real
  renames such as „Grup școlar” → „Liceul Tehnologic”.
- Alias rows are scoped to their record's county, so the ABA bodies with a wrong posturi county stay unlinked (DATA-ORG-07).
  A national scope would let an alias link in a county where a different body has the same acronym.

## 2026-11-02 — posturi.gov.ro employers as a source (DATA-ORG-01; Opus brief, Sonnet build)

**Done**
- `consolidate.py` reads `data/posturi/employers.csv` (5,901 rows, the posturi export of 2026-10-18) and links each row
  through the tiers exact, canonical, unit and tokens. There is no prefix tier.
- An unlinked row becomes a `P<slug>` record. The new rows land in the review queue `posturi-review.csv`.
- The explorer has a "posturi" badge, a source filter and a link to the employer page on posturi.gov2.ro.
- New CSV columns: `posturi_slugs`, `posturi_postings`, `link_posturi`.
- Tests: 47 → 57; determinism passes. Opus re-ran the tests.

**Measured**
- 4,443 rows linked (75.3%; 76.5% of postings): exact 1,932, tokens 1,616, canonical 718, unit 177.
- 662 weak, 15 ambiguous, 781 without a candidate. That gives 1,172 `P` records, 11 of them with 10 or more postings.
- Records 24,981 → 26,153; no old id lost. 3,324 records changed `sources`, 164 `merged_ids`.
- 19 of the top-20 `P` records are name variants (suffix, `U.A.T.`, spital/spitalul, tg/târgu, acronyms), not missing institutions.

**Hard**
- The active-only posturi SQLite gave 4,807 rows without a county. The build used the full `dev.sqlite`.
- One employer can have several posturi slugs. Those made `merge_same_name` skip a group, and `check_absorbed_ids`
  stopped the build. The fix collapses unlinked posturi rows with the same county and name before they become records.

**Decided**
- Name rules come before the manual review (pax): [DATA-ORG-03 brief](briefs/posturi-name-rules.md). A spike links
  96 more rows and turns ~780 token links into exact or canonical. Reviewing first would mean deciding ~1,000 variant
  rows by hand.
- Collapse same-name posturi rows in the builder, not in the "repeated name inside one source" rule, so that the old
  sources keep their behaviour.

## 2026-10-28 — "Despre" in the menu, beta tag (Opus, small change)

**Done**
- index: "Despre" (with the ANI ⚠) moved from the header into the "Opțiuni" menu, after "Cum e organizat statul".
  organizare and despre have no menu, so their header link is removed; the footer keeps "Despre" on every page.
- A DS tag `.g2-tag[data-tone=progress]` "beta" next to the title on the three pages (local size rule `.org-beta`).
- Fixed on the way: on phones the "Opțiuni" panel was cut off at the left edge. It now opens under the header row,
  full width.

**Measured**
- Menu links are 44 px high. No horizontal scroll at 390 and 1,440 px; no page errors; JS syntax and 44 tests pass.

## 2026-10-28 — Despre sources note, negative logo (Opus, small change)

**Done**
- Despre: a note at the top lists the four public sources with their links (data.gov.ro ANAF list, roepas.ro, the
  e-guvernare.ro PDF of the Registrul Național, monitorul.ai/integritate for ANI). The "Fișiere sursă" section and
  its code are removed (owner); the curated websites file is not mentioned. The generation time and the ANI cap
  warning stay.
- Header logo: `assets/img/g2-0-negative-64.png` (106 × 64, from the owner's `g2-0-negative.png`), shown at 50 × 30
  with no tile (owner: no white background).

**Measured**
- JS syntax on the three pages passes. No horizontal scroll at 390 and 1,440 px; no page errors.

## 2026-10-28 — Review (Opus): limited preview polish accepted

**Decided**
- Accepted bdd39ce against `docs/briefs/limited-preview.md`, from screenshots (landing top in dark, footer, Despre
  contact). Accepted the shortened footer text "Surse: …" (it lets the footer fit one row at 1,440 px).
- Not checked: a real share preview of `og.png` (needs the published site; use a share debugger after publishing).

## 2026-10-28 — Limited preview polish (brief limited-preview)

**Done**
- All three pages: Open Graph and Twitter meta (title, description, type, absolute url, image 1,200 × 630 with alt, locale,
  site name, card `summary_large_image`) and a Romanian description (107 to 158 characters); the `favicon.svg` link is removed;
  the header logo is `g2-0-64.png` on a light rounded tile (`.g2-wordmark .g2-logo`, colour token `--g2-color-on-header`).
- Header: the nav links are gone (the views stay, reached from the landing and the footer); the counter reads "2.299 din 24.981"
  (`role="status"`); the "Opțiuni" summary has no border and keeps the 44 px target and the DS focus.
- Landing: the stats line under the search is removed (the examples stay); "Sari la" is bold and ends with "Lista completă"
  (opens `#v=list`).
- Footer, all pages: one row at 1,440 px (text, links, "un proiect gov2.ro", GitHub icon on one centre line); links
  Structura statului, Domenii, Lista completă, Cum e organizat statul, Despre. On the landing the view links keep their
  handlers and scroll to the top. The old `list-link` code is removed.
- Disclaimer: DS notice bar on every page ("Acesta nu este un proiect oficial al Guvernului României."), close button
  (`aria-label="Închide"`, 44 px), `localStorage` key `org-disclaimer-closed` in try/catch; it does not move focus.
- `despre.html`: the ANI source links to https://monitorul.ai/integritate; new section "Contact" (GitHub issues, mailto link).

**Measured**
- Disclaimer: shows, closes, stays closed after a reload (also on the two other pages: same origin); with storage blocked it
  closes for the session and shows again after a reload; Tab (twice from the top) reaches the close button.
- No horizontal scroll at 320, 390, 768, 1,024 and 1,440 px, both schemes, three pages. No target under 44 px (the wordmark,
  the footer text links and the menu link were raised to 44 px). Landing heights: 390 px 3,211 px; 1,440 px 4,075 px.
- Footer at 390 px wraps in three rows; at 1,024 px in two; at 1,440 px in one.
- 44 tests pass; syntax check passes on the three pages; roots check true; legacy hashes `#v=stat`, `#v=fam`, `#v=list`,
  `#v=loc&k=Cluj`, `#id=…` and the empty hash behave as before; no console errors.

**Decided**
- The footer text "Date din surse publice" is now "Surse", so that the row fits at 1,440 px.
- The "Despre" link stays in the header (the brief removes only the three view links).

## 2026-10-27 — Landing top row: no headings or labels, one row on desktop (Opus, small change)

**Done**
- Removed the headings "Caută o instituție…" and "Unde locuiești?" and the labels "Județ" and "Localitate" (owner).
  The search field, the two selects and the two sections carry `aria-label`, so the accessible names stay.
- From 1,024 px the search, the county select, the locality select and "Arată" sit in one row. Phones stack as before;
  the phone placeholder is the short "Nume, localitate sau CIF", so it does not truncate.

**Measured**
- The three controls share one top (76 px) at 1,024 and 1,440 px. No horizontal scroll at 390, 1,024 and 1,440 px.
  No page errors. JS syntax check and 44 unit tests pass.

## 2026-10-27 — Review (Opus): landing round 4 accepted

**Decided**
- Accepted cb8e87d + 85088c3 (Domenii section, Despre page, GitHub footer, map compare by domain, review fixes)
  from screenshots. Accepted the deviation: "Alte instituții din domeniu" links `fam=(fără tip comun)`, so it
  opens the N records, not the whole domain.
- Phone landing: 3,373 px at 390 px collapsed (round 3: 2,560 px). The cost of the Domenii section; accepted.

## 2026-10-27 — Landing round 4, review corrections (Opus: accepted with 5 corrections)

**Done**
- The info line under the search says "Despre" (link to `despre.html`). The ⚠ in the header link has a margin (not a text
  space) and `role="img"` with an `aria-label` that explains it (index and despre).
- Domenii on desktop: an open card spans the whole row and lists its types in columns (about 260 px). A card that opens
  waits until the row before it is full, so no cell stays empty and the DOM order is the visual order. Several domains may
  be open at once. Focus stays on the toggle.
- Footer, all three pages: "un proiect gov2.ro" followed by the GitHub icon link; the centre lines of text and icon are the
  same (854 px and 854 px in the check).
- Phone (below 760 px): the 6 largest domains and a button "Toate cele 17 domenii" (`aria-expanded`); the field "Caută un tip"
  searches all domains.

**Measured**
- Landing at 390 px, collapsed: 3,373 px (was 3,957 px); with all 17 domains shown: 4,013 px. At 320 px: 3,591 px;
  at 1,440 px: 4,139 px (unchanged). No horizontal scroll at 320, 390, 1,024 and 1,440 px, both schemes, three pages;
  no target under 44 px. Tab order in an open domain follows the list down the columns. 44 tests pass; syntax check passes.

## 2026-10-27 — Landing round 4: "Domenii", page "Despre", jump links, map by domain (spec 2b)

**Done**
- `explorer/index.html`: (1) the search and "Unde locuiești?" sit in two columns from 1,024 px (`.org-top`); (2) jump buttons
  "Sari la: Domenii · Structura statului" scroll to the section and focus its heading (`tabindex="-1"`; no hash change);
  (3) the "Toate tipurile" box is now the full-width section "Domenii": 17 collapsible domain cards (4 columns on desktop,
  2 on tablets, 1 on phones, all collapsed), the "Caută un tip" field with a flat result list, and a last row
  "Alte instituții din domeniu" per domain; the tiles are back to 4 columns; the header link "Tip → instituții" is "Domenii"
  (index and organizare); (4) the about dialog, its buttons, `buildAbout` and the accessibility statement are removed;
  the header link "Despre" (with ⚠ when an ANI export is capped) and the footer link "Despre" open `despre.html`;
  (5) above the map, the selects "Domeniu" and "Tip"; the map, the legend classes, the county list and a status line recompute.
- `explorer/despre.html` (new): same header, footer, layers and `data-g2-scheme="auto"`; fetches only `metadata.json`; text of
  the old dialog without the accessibility part. `explorer/organizare.html`: nav link, header link "Despre", footer.
  GitHub mark (inline SVG, `currentColor`, 44 px link, `aria-label="Cod sursă pe GitHub"`) in the footer of all three pages.

**Measured**
- Domains: 17. For each domain, sum(type counts) + N (records without a type) = domain count: 17 of 17 hold, because a type is
  counted by its records inside the domain (so a family that spans two categories shows its part in each). The domain count
  is the number of records of the category (for example Educație 9,620, Justiție 815, Companii de stat 930).
- Links: 234 domain links (217 type links and 17 "Alte instituții" rows) open a non-empty view; the stats counter equals the
  count shown next to every link; the "Alte instituții" link opens the list with `cat=<category>` and `fam=(fără tip comun)`, so
  its count equals N (the spec names `cat=` only; the list with `cat=` alone shows the whole domain, not the N records).
- Map "Justiție" (all 815 records, website filter off), top counties: București 55, Bacău 31, Dolj 31, Timiș 30, Argeș 28
  and Cluj 28. All are seats of a court of appeal (Bacău, Craiova, Timișoara, Pitești, Cluj, București); the median
  county has about 17.
- Landing height at 390 px, all collapsed: 3,957 px (round 3: 2,560 px; 17 domain rows replace one box row). At 1,440 px:
  4,139 px (was 3,574 px). `despre.html`: 2,857 px at 390 px. No horizontal scroll at 320, 390, 768, 1,024 and 1,440 px in
  both schemes on the three pages; no target under 44 px. Keyboard: Tab reaches the field, each domain toggle, the map
  selects and every link with the DS focus; Enter on a jump button moves focus to the heading.
- Tests: 44 pass; JS syntax check passes on the three pages; roots check true; legacy hashes unchanged.

**Hard**
- The Chrome extension was not connected; checks ran in Playwright with the local Chrome.

**Decided**
- Domain cards open on desktop as well (the spec says collapsible cards); an open card makes its row taller, so the grid uses
  `align-items: start`. Cost of the alternative (all open): a 4,000 px page.
- The map keeps its selection in memory only (no hash, no storage), as the spec says.

## 2026-10-27 — Review (Opus): "Toate tipurile" side box accepted

**Decided**
- Accepted c99bea0 from screenshots at 390 and 1,440 px, light and dark, with a category open and "spital" typed.
- Follow-up in the backlog: the box hides the 5,272 records without a family. Companii de stat shows 10 of 930.

## 2026-10-27 — Landing: "Toate tipurile" side box replaces the category tabs (spec section 2, item 5)

**Done**
- `explorer/index.html`: the category tabs and panel are removed from `renderHome` (and their CSS). The new box
  `Toate tipurile (N)` lists the categories (biggest first, collapsed; a button with `aria-expanded` opens one in place)
  and their types with counts. The field "Caută un tip" (label + `.g2-input`) filters the type names folded; while it has
  text the box shows a flat list with the category in grey (first 100 hits). Type links are the tile links: family view,
  `web=0`, `k=<county>` when a county is remembered. The box follows the remembered county ("Șterge" included).
- Desktop (1,024 px and wider): a 300 px right column beside "De ce ai nevoie?", tiles in 3 columns, `position: sticky`
  with `max-height` and inner scroll (it sticks at 12 px from the top; the box is 876 px tall at a 900 px viewport).
  Below 1,024 px: one collapsed row after the tiles, with the same button pattern as the tiles.
  A second media query (`homeNarrow`) re-renders the landing when the width crosses 1,024 px.

**Measured**
- N = 176 types in 17 categories (no county, website filter ignored). 176 of 176 type links open a non-empty view
  and all carry `web=0`. With county Cluj, every type link and every search hit carries `k=Cluj`; after "Șterge" none does.
- Search: "spital" lists 5 types (Spital (alte tipuri), clinic, orășenesc, municipal, județean); "scoala" lists 4 types
  of "Școală".
- Category count = sum of its type counts in every category (by construction). It differs from the number of records
  of the category: 5,272 of 24,981 records have no family, and a family counts in its main category only. Examples
  (box / records of the category / records with no family): Educație 9,436 / 9,620 / 204; Servicii publice locale și
  regii 898 / 763 / 119; Companii de stat 10 / 930 / 914; Altele 182 / 1,235 / 956; Agricultură, mediu și păduri
  432 / 936 / 482.
- Landing height at 390 px, all collapsed: 2,560 px (was 2,909 px); 320 px: 2,771 px. At 1,440 px: 3,574 px (was 3,468 px).
  No horizontal scroll at 320, 390, 768, 1,024 and 1,440 px, both schemes. No control in the box under 44 px.
- Keyboard: Tab from the field reaches each category toggle with the DS yellow focus; Enter opens one; the next Tab
  reaches its first type link. 44 tests pass; JS syntax check passes; roots check true; legacy hashes unchanged.

**Decided**
- The box counts every record of a family once, under the family's main category, so that the category count equals
  the sum of its types. Cost of the alternative (count records per category): the number would not match the list
  under it.

## 2026-10-27 — AJOFM Ilfov alias row approved

**Done**
- The operator approved A11364678 "Agenția Județeană pentru Ocuparea Forței de Muncă Ilfov" (relayed by stiri). `reviewed`.

## 2026-10-27 — Three small stiri requests after the v0.35.0 pin

**Done**
- A4192545 (JUDETUL ILFOV) absorbed G26022 (CONSILIUL JUDETEAN ILFOV) by a curated merge. 24,982 -> 24,981 records.
- Alias row for A11364678: "Agenția Județeană pentru Ocuparea Forței de Muncă Ilfov", `full_name`, `proposed`
  (the operator reviews it).
- `aliases_unique` drops an alias that is a proper subset of the record's name, holds no place word (county or UAT) and only
  common words (every token in 50+ record names). "Inspectoratul de Jandarmi" is gone from A4240995.

**Measured**
- A first rule (any subset) dropped 473 aliases, among them good short names ("Colegiul National Vasile Goldis"). A
  second (common words only) dropped "Directia de Sanatate Publica Bacau". The final rule changes 20 records, of which
  A4192545 gains the council aliases. A few kept names are debatable ("Biblioteca Judeteana Mihai Eminescu" is gone).

## 2026-10-27 — Review round 2 (Opus): landing v2 and `organizare.html` accepted

**Decided**
- Accepted 9fa0cae against the brief and the round 1 corrections. Checked from screenshots at 390 and 1,440 px,
  light and dark. The legal citations on the diagram match the Constitution text (art. 1, 32, 61, 65, 102, 116,
  117, 120–124, 126, 131, 140–142).
- Not published: the owner reviews the screenshots first.

## 2026-10-27 — County council alias rows approved

**Done**
- The operator approved the 41 "Consiliul Județean X" rows (relayed by the stiri session). All are `reviewed` in
  `curation/aliases.csv`. The tag also carries the AJOFM Ilfov fix of the previous entry.

## 2026-10-27 — Fix: AJOFM Ilfov split and a gap in the id check (found by stiri on v0.33.0)

**Done**
- Cause: the linker fix moved the ANI name rows of AJOFM Ilfov from county Ilfov to Bucuresti. G26002 (Ilfov) lost its
  merged id Da0fede1c, and G10049 (Bucuresti) appeared: two records for one body. The check missed Da0fede1c because it
  only looked at ids that were records, not at ids that earlier releases listed in `merged_ids`.
- `curation/merges.csv`: G10049 and G26002 merged into A11364678 (the ANAF record; its name has "PT" for "PENTRU").
- `check_absorbed_ids` now covers every `merged_ids` entry of every release from v0.15.0: the id must be a record or be
  listed, else it follows its old survivor into whatever record absorbed that survivor, else the build stops.
  A11364678 now lists G10049, D79db7f24, G26002, Da0fede1c.

**Decided**
- The check repairs a trail by inheritance. Cost: a survivor that vanished without a trace of its own stops the build.

## 2026-10-27 — Linker fix: county-less ANAF names (A4469183)

**Done**
- `Linker`: an ANAF name that states no county gets its row's county as `_geo`. A source name that states another
  county no longer links to it (tokens and prefix tiers). Cause of the 16 foreign aliases on A4469183.
- Build check: ids that were records in a release and now are not get a trail in `merged_ids` when the source row
  links to an ANAF record (`link_trail`) or the same ANI name sits in one record under another county.

**Measured**
- A4469183: 16 aliases -> 3; declaratii_count 14,415 -> 14,311. 67 records changed counts or sources; 24,983 -> 24,984
  records. 3 old D ids (D83ae5f51, D77016141, Dfa62d78e) now merged into the record that holds their ANI name,
  with a trail; 4 new records appeared (for example G10049, Ilfov AJOFM, no longer pulled into a wrong ANAF row).

**Hard**
- First run of the new check stopped the build on those 3 ids. The check worked as designed; the trail rule was added.

## 2026-10-27 — Landing v2 and the page "Cum e organizat statul" (brief landing-v2-organizare)

**Review round 1 (Opus): accepted with 5 corrections**
- Corrections made (same day): (1) tiles and cards ignore the website filter; their links, counts and selects carry
  `web=0` (a record opened in the dialog keeps the filter); (2) phone: tiles and cards start collapsed (button with
  `aria-expanded`), the county list sits in a `<details>`, the "+ N" button is gone; (3) the two "Nu am verificat…" notes
  on `organizare.html` are replaced by the wording of the review; (4) Curtea Constituțională has its own colour
  (neutral surface) and its own line style (groove); (5) diagram groups use `align-items: start`.
- Measured after the corrections: 40 of 40 `HOME_TASKS` labels visible with the default state (task links 40, was 31
  together with the cards; card links 22; "Instanțe și parchete" tile and the court links of Justiție present; Sănătate
  shows the 6 hospital and health types). With county Cluj: 37 task links, all with `k=Cluj`.
- Landing height at 390 px: 5,970 px (round 1), 2,909 px with everything collapsed; 320 px: 3,209 px. At 1,440 px:
  3,468 px (was 2,895 px, the tiles now show all 40 links). No horizontal scroll at 320 to 1,440 px; no control under 44 px.
- Diagram frame height (light): 2,811 px at 768, 2,579 px at 1,024, 2,025 px at 1,440. 34 of 34 box links still
  open a non-empty view; 62 tile and card links and 22 card links: none empty. 44 tests pass; roots check true.

**Done**
- `explorer/index.html`, `renderHome`: search (writes the same `S.q`, opens the list), "Unde locuiești?" (two selects,
  "Arată", "Șterge", county in `localStorage` key `org-home-county`, try/catch, memory fallback), "De ce ai nevoie?"
  (`HOME_TASKS`, 10 tiles), "Cum e organizat statul" (`HOME_BRANCHES`, 6 cards with a "Vezi" select) and the unchanged
  type tabs and county map. One SVG sprite (16 symbols, `org-icon`). Link to `organizare.html` in the "Opțiuni" menu
  and under the cards. Styles in `@layer app`, prefix `org-`.
- `explorer/organizare.html`: static page, 7 sections, the diagram as HTML and CSS (10 groups, 34 box links).
  Colour tokens are DS tones; the line style (solid, dashed, dotted, double) repeats the relation, and each group
  states it in words.
- Sources opened on legislatie.just.ro (2026-10-27): Constituția (47355), Codul administrativ (215925), Legea 500/2002
  (37954), Legea 273/2006 (73527), OUG 109/2011 (133685; title checked) and Legea 304/2022 (261410, link found with a
  web search; opened and checked).

**Measured**
- Landing height at 390 px: 2,262 px before, 5,970 px after. At 1,440 px: 1,068 px before, 2,895 px after.
- No horizontal scroll at 320, 390, 768, 1,024 and 1,440 px, both schemes (landing and `organizare.html`).
  Controls of the new sections are at least 44 px high.
- `HOME_TASKS` and `HOME_BRANCHES`: no family label is absent from the data (`console.warn` stays silent).
  With the default "are site" filter, 27 of the labels have no record with a website, so their links are hidden
  (for example courts, hospitals, schools); the links return with `web=0`.
- 31 tile links and 18 card links: none opens an empty view. With county Cluj chosen, all 5 visible tile links carry
  `k=Cluj`; after "Șterge" none does. With `localStorage` blocked, the page renders and works.
- `organizare.html`: 34 of 34 box links open a non-empty view. `explorer.reachableRoots()` equals `expectedRoots()`.
- Tests: 44 pass; `node --check` passes.

**Hard**
- The browser extension of Claude in Chrome was not connected. Checks ran in Playwright with the local Chrome.
- Two bugs found by the checks: a nested array passed to `h()` (the example links showed as text) and to
  `replaceChildren` (the locality select stayed empty). Both fixed.

**Decided**
- On a phone a tile shows 3 links and a "+ N" button that opens the rest in place (the spec says a link to the family
  list). Cost of the alternative: a family link does not fit tiles that hold several families.
- Diagram links use `web=0`, so that every box opens a non-empty view. Cost of the alternative: courts and parishes
  show an empty view under the default website filter.
- Claims dropped for lack of a checked source: Academia Română and the branch academies as autonomous; autonomous
  authorities "under parliamentary control" (the page cites art. 117 alin. 3 only); DNA and DIICOT in the diagram;
  "tutela administrativă" (the page describes art. 123 alin. 4 and 5 instead); the Legea 544/2001 guide link;
  the reason why professional bodies are in the ANAF list; the number 5,657 (not shown, to keep the page free of
  counts; measured today: 5,657 records with two parents, 5,609 of them in "Educație").

## 2026-10-27 — `aliases_unique` and county council alias rows

**Done**
- CSV column `aliases_unique` (last): aliases that no other record uses (name or alias, folded), that differ from the
  record's own name, and that are not a bare kind of body. 5,239 records have it (6,088 have `aliases`).
- 41 rows "Consiliul Județean X" in `curation/aliases.csv`, kind `full_name`, status `proposed` (one per
  "JUDETUL X" ANAF record); the operator reviews them. 166 data rows in all.

**Hard**
- A4469183 (generic IPJ record) holds 16 aliases of other counties' IPJs: a linker defect, not a sharing problem.
  `aliases_unique` does not remove it. In the backlog.

## 2026-10-27 — Fix: ids absorbed twice came back (v0.31.0 defect, found by stiri)

**Done**
- Cause: `apply_curated_merges` ran before `merge_loose_names`. The curated merge absorbed D2b2455f7 and D6d6a8ee4 before
  they took Df0d244a8 and Dfadd6216, so those two came back as records. Fix: curated merges run after the loose
  pass, and a curated row that names an absorbed id acts on its survivor. G29409 now lists all 7 ids. 24,983 records.
- Build check `check_absorbed_ids`: reads `institutii.csv` of every release tag from v0.15.0 on (git). The build stops
  when an id that a release listed in `merged_ids` is a record again (override: `curation/unmerged.csv`, id + reason),
  or when an id of the latest release has no record and no trail. Verified: it catches the v0.31.0 state against v0.28.0.
- Tests: 3 new (43 in all).

**Decided**
- The check compares with git tags, so it needs a git checkout; without git it warns and skips. Cost of the
  alternative (a stored list of absorbed ids): one more file to keep in step.

## 2026-10-27 — stiri requests after the v0.28.0 re-pin

**Done**
- New CSV column `aliases` (last): names of absorbed records and other-source names, pipe-joined. 6,088 records have
  it. Chosen over rows in `curation/aliases.csv`, which stays the operator-reviewed master. stiri asked for aliases.csv.
- `curation/merges.csv` has a new kind `rename` (column `new_name`) and 5 new rows: UMF Targu Mures (3 ANI spellings
  merged into G29409, which gets the place in its name), G01302 renamed "Registrul Auto Roman - Reprezentanta Alba",
  Teatrul National Caragiale (D806d2010 into D9b5f549f), CNPEE (D4dbb2462 into D90878a91). 24,988 -> 24,985 records.
- Not merged, two bodies each: DGEP Arges / DGEP Bucuresti (two ANAF CIFs, different parents); ANRSPS A4278663 is a
  sub-unit of A26288978 (parent already set). Curtea de Conturi G18067 (registrul, Dolj) vs D646519bd: unknown; the
  Dolj entry is probably the regional chamber, left unchanged.

**Hard**
- G01302 as the Alba unit is an inference from the naming pattern of the other Registrul entries, not from a source.
- CNPEE in Galati: assumed ANI county error, no unit is known.

## 2026-10-27 — Owner decisions: landing v2 and "Cum e organizat statul"

**Decided**
- Owner accepted all five recommendations of spec section 4: search on the landing page, short section headings,
  six state cards replace the inline state row, the county is remembered in `localStorage` (owner: "useful"),
  and `explorer/organizare.html` is a separate page. The first two reverse choices of 2026-10-26.
- Spec status: accepted. Brief ready for Sonnet.

## 2026-10-27 — Spec and brief: landing v2, page "Cum e organizat statul"

**Done**
- `docs/specs/landing-v2-organizare.md` and `docs/briefs/landing-v2-organizare.md`. No code changed.
- Landing v2 order: search, county and locality picker, need-based tiles (family labels), six state cards
  (India-style), then the type tabs and the map of today.

**Decided (proposed; the owner decides in spec section 4)**
- The new page is a separate static file. Cost of a view in `index.html`: the reader loads 6 MB of rows to read prose.
- Need-based tiles use existing family labels, so no data change. Cost: a renamed family hides a link (logged).

**Hard**
- No official plain-language guide to the whole state structure found. Sources are the laws themselves.
- Codul administrativ art. 5 does not define subordonare, coordonare or autoritate. The text must cite HG examples.

**Measured**
- 24,988 records, 17 categories, 176 families. Family labels for all proposed tiles exist in `metadata.json`.

## 2026-10-27 — Loose-name merge rule (owner decision)

**Decided**
- Owner: same county + same normalised name + not a local body = one body. `merge_loose_names` applies it after
  the other merges. Survivor: the ANAF record, else ROePAS > Registrul > ANI, then the lowest id. A group with
  two ANAF CIFs stays apart. Local bodies: `LOCAL_KIND_RE`, `SAME_NAME_NEVER`, generic names. Cost of the rule: a
  wrong merge hides a body; the trail is `merged_ids`.
- Owner: drop ADR Vest (no record added). Backlog item closed as dropped.

**Measured**
- 87 groups, 93 ids absorbed (24,988 records, was 25,081); 13 groups skipped for two ANAF CIFs. No absorbed id
  without a trail. The review list showed 89 groups; 2 differ because of the stricter local-kind test.
- Romsilva -> D4618737e, salt company -> G10849, IPJ Valcea -> G40002. 57 `same_body_as` links unchanged.

## 2026-10-27 — Same-name review list (read-only)

**Done**
- `docs/reports/2026-10-27-same-name-review.md`: 89 groups of one county and one folded name, outside courts, with no
  two ANAF CIFs and no local kind. No record changed.

**Measured**
- Dropped: 89 groups with two ANAF CIFs, 70 local-kind or generic names. Largest source combination: registrul-only (31).

**Hard**
- ADR Vest: in no source (ROePAS, Registrul, ANAF list). A curated record needs a new id scheme; not built, no CIF known.

## 2026-10-27 — Court link: Curtea de Apel Galati

**Done**
- A47377954 -> A17043103 (same street, number and postcode; parents 4340587 vs 4265841), reported by stiri. 57 links.
  Checked: no other record under parent 4340587 is left unlinked.

## 2026-10-27 — 15 more court links

**Done**
- Operator principle (via stiri): two records of one court are the same body. The 15 courts of the 47372... series
  are linked to their one A4... partner (same county, city and street). 56 `same_body_as` links now.

**Decided**
- Only courts; a Court of Appeal and a Tribunal never link (each pair has the same court type).

## 2026-10-27 — 12 more court links

**Done**
- stiri named courts without an exact-name partner. All 12 have one A4... record in the same county, city and street
  (parents 4265841 vs 4340587): 8 tribunals (Iasi, Vaslui, Braila, Vrancea, Maramures, Caras-Severin, Gorj, Ilfov),
  Sibiu, Valcea, and CA and Tribunal Alba. Linked with `same_body_as`; now 41 links.
- Found: the earlier 29 used the 47373... series only. The 47372... series has 15 more courts, not linked
  (outside the operator decision; backlog).

## 2026-10-27 — DS v0.16.0: the civtech title sweep

**Done**
- Updated `explorer/assets/gov2/gov2.css` to DS tag v0.16.0. Only `.g2-ro-sweep` changes: a soft, wide band
  tilted 100deg, in a continuous 7 s loop (ADR 0010, amendment of 2026-10-27). No **Breaking** item.
- Rewrote the accessibility statement in "Despre date" → "Accesibilitate": a continuous 7 s loop, the band is over
  the glyphs about 6.7 s of 7 s, and the lowest contrast is 1.54:1. Both deviations (WCAG 2.2.2 and 1.4.3) stay.

**Measured** (headless Chrome)
- Animation `g2-ro-sweep 7s infinite`. With reduced motion: no animation, no gradient, white text.
- 5 views × light/dark × 1280/375: no errors, no overflow, roots OK, 0 contrast failures (the check skips the sweep).

## 2026-10-27 — Court pairs linked (`same_body_as`)

**Done**
- Operator decision (via stiri): the 29 court pairs are one body each; no merge, keep both tax IDs.
  `curation/same_body.csv` + new CSV column `same_body_as` on the A47373... record. Build stops on a bad id.
- The regional ADR alias rows (20 new) were already in v0.21.0; this tag carries them too.

**Decided**
- A link instead of a merge: keeps both CIFs and the two parents. Cost: consumers must follow the link.

## 2026-10-27 — Courts register check, regional ADR aliases

**Done**
- Courts check: 4 ANAF requests, report `docs/reports/2026-10-27-courts-cif-check.md`. Identical identity data under
  both CIFs; no merge (see report).
- Operator decision relayed by stiri: bare `ADR` = the digitalization authority; "ADR" + region = regional
  development agency. 20 new alias rows for 7 agencies (ADRBI already existed), status `reviewed`. ADR Vest has no record (backlog).

## 2026-10-27 — DS v0.15.0: the select control

**Done**
- Updated `explorer/assets/gov2/gov2.css` to DS tag v0.15.0 (DS issue #10, brief 08). No **Breaking** item.
- The five selects (four filters, sort) use `class="g2-input"`. Deleted the local copy of the input style,
  the local disabled style and the local select focus rule. `.org-select` is gone.
- The disclosure filters (`.multi > summary`: "Orice sursă", "Opțiuni") draw the same CSS arrow as the DS select,
  with 2.5rem of right padding. In forced colours they show "▾", because forced colours drop gradients.

**Measured** (headless Chrome)
- Selects and the search field are 40 px tall, with a 40 px right padding on the selects. The disabled UAT select
  has the muted text and border. Focus: yellow outline and inner ring, arrow kept, in light and dark.
- 5 views × light/dark × 1280/375: no errors, no overflow, roots OK, 0 contrast failures. Rows 69/121 px, as in 0.14.0.

**Decided**
- The disclosure arrow copies the DS select arrow. The cost: a local rule to remove if the DS adds a disclosure control.

## 2026-10-27 — DS v0.14.0: breadcrumbs, tables, summary list, skip link

**Done**
- Updated `explorer/assets/gov2/gov2.css` to DS tag v0.14.0. The fonts are the same as in v0.13.0.
  The DS changelog has no **Breaking** item between 0.13.0 and 0.14.0.
- Replaced three local components with DS classes and deleted their local rules:
  - `.crumbs` → `.g2-breadcrumbs` (`nav > ol`, `aria-current="page"` on the current item). One helper,
    `breadcrumbs(label, steps)`, builds the state tree, family and record-dialog trails.
  - the list and tree tables → `.g2-table`, with `scope="col"` and an accessible name.
  - the record `dl` → `.g2-summary-list`, with one `div` for each row.
- Added `.g2-skip-link` to `#main` (`tabindex="-1"`). A click handler moves the focus, so the hash does not change.

**Measured** (headless Chrome, 5 views × light/dark × 1280/375)
- No errors, no overflow, `reachableRoots` OK, font Inter, no other hosts, 0 contrast failures in the first screen.
- List row: 69 px at 1280 (was 73 with 0.13.0), 121 px at 375 (was 125). The DS table pads 8 × 12 px.
- Breadcrumb steps are 39 px tall. The skip link is 155 × 50 px with the yellow focus; `main` gets no fill.
- The record summary list is two columns at 1280 and stacks at 375. The dialog has no sideways overflow.
- The three tree tables of "Parlamentul" do not scroll sideways. Unit tests: OK.

**Decided**
- Breadcrumb steps are links (`a.g2-link-quiet`), not buttons. The first build used buttons with a local rule;
  g2-ds answered that a breadcrumb step is a link with its own URL, and the DS will not style buttons there.
  `hrefFor(patch, id)` builds each href from the current state (`browseParams`), so a step can be shared,
  reloaded and opened in a new tab. A plain click still runs the in-place action; a modified click follows the href.
  Measured: hrefs `#v=stat`, `#v=stat&n=guvern&k=Cluj`, `#v=fam`, `#k=Cluj&id=A4266669`. A click changes the hash,
  Back restores it, and loading a record href opens that record. Links are 39 px tall.
- The main list table does not use `.g2-table-stacked`: the phone layout already hides the contact column.
- `.lt-wrap` keeps `overflow-x: auto` and is not a `.g2-table-wrap`. No measured table scrolls, and a focusable
  region for each tree table adds a tab stop for each table. Assumed, not measured, for all nodes.

## 2026-10-27 — Alias rows approved

**Done**
- The operator approved the two `proposed` rows (A4193222 full name, A42283735 ADR), relayed by the stiri session.
  Both are now `reviewed` in `curation/aliases.csv`. Tag v0.18.0.

**Decided**
- Courts (A4… vs A47373…): no merge. A bounded check of the two tax IDs in the official register comes first;
  merge only on clear evidence. The check does not block the alias tag.

## 2026-10-27 — Alias fixes after stiri pinned v0.15.0

**Done**
- `curation/aliases.csv`: RAR now points at R11062162 (national body), not G01302 (Alba unit). Added the full
  name of A4193222 (ANAF typo "PLITIE") and ADR for A42283735, both with status `proposed`.
- Backlog: court pairs, Romsilva and IPJ Valcea, "Adr" R11176080, AMR and UNCJR.

**Decided**
- No merge of the A47373... court records: same name and address but a different parent CIF; unverified, and a wrong
  merge hides a body. Cost: stiri keeps 126 ambiguous surfaces until the owner confirms.
- New alias rows use kind `full_name` and status `proposed`; the operator has not reviewed them.

## 2026-10-27 — gov2 design system v0.13.0 adopted in the explorer

**Done**
- `explorer/assets/gov2/`: `gov2.css`, `fonts.css` and `fonts/` from DS tag v0.13.0, unedited
  (`git archive v0.13.0 gov2.css fonts.css fonts`). The old fonts (`explorer/assets/fonts/`, IBM Plex Sans,
  Instrument Sans, JetBrains Mono) are removed.
- `explorer/index.html`: all project CSS in `@layer app`. Local tokens now read `--g2-*`; radius 0; no shadows.
  `<html data-g2-scheme="auto">` uses the DS dark scheme; the local Monokai palette is gone. The county map keeps
  a local 5-class ramp (`--org-map-0`…`5`), with dark values on the same selectors as the DS scheme.
- Header: `.g2-header`, `.g2-ro-corner`, `.g2-wordmark` with `.g2-ro-sweep` (the title keeps an `h1`).
  The three views are a visible `.g2-nav`; "Mai multe" became "Opțiuni" and holds only the three checkboxes.
- Filters moved to a sticky bar below the header (`.org-filterbar`); the header scrolls away. On phones the
  bar is one row (search, Filtre); "Resetează" shows with the open disclosure.
- DS components: `.g2-btn`/`.g2-secondary` for every button, `.g2-input` for search and the link box,
  `.g2-tag` (warning tone) for the row flags, `.g2-tag` for the category in the dialog, `.g2-footer`.
  Selects copy `.g2-input` locally (no DS select yet).
- Footer: sources, "Despre date", "Accesibilitate", source code, gov2.ro. The "Despre date" dialog has an
  "Accesibilitate" section with the two WCAG deviations of the title sweep (DS ADR 0010 wording, in Romanian).
- CLAUDE.md and AGENTS.md carry the DS project block (version 0.13.0, path, prefix `org-`).

**Measured** (headless Chromium 1248; Cluj list filter; light and dark; 1,280 and 375 px)
- Five views × 2 schemes × 2 widths: no page errors, no horizontal overflow, `reachableRoots()` = `expectedRoots()`,
  font Inter, no request to another host.
- Text contrast in the first screen (every visible text node against its computed background, sweep excluded):
  0 below 4.5:1 (3:1 for large text) after the fixes. Before the fixes: the header summary had white on white
  (1.00) in light.
- List row height: 73 px at 1,280 px (was 53), 125 px at 375 px (was 75). Sticky area: 61 px at both widths
  (was 89 px at 1,280 and 111 px at 375), because only the filter bar is sticky now.
- Keyboard focus, 14 tab stops from the top, both schemes: every stop shows the DS treatment (yellow fill with
  ink text on links and buttons, yellow outline on fields and selects).
- `python3 -m unittest discover -s tests`: 37 tests OK.

**Hard**
- App-layer rules beat `gov2.states`, so local colour rules hid the DS focus. The app layer now writes the DS
  focus treatment again, last. A reset `button, select, input { font: inherit; color: inherit }` in `app` also
  overrode `.g2-btn` focus: light text on yellow in dark. It now uses `:where()` and skips `.g2-btn`/`.g2-input`.
- Assumed, not checked: forced colours, 200% zoom, a screen reader. The contrast check covers only the first
  900 px of each view.

**Decided**
- Only the filter bar is sticky. The black header with the wrapping nav is 190 px tall on phones; keeping it
  sticky would cost more than the old 111 px. Cost: the view links scroll away; the footer and the wordmark
  still reach every view.
- The existing local class names stay; new ones use `org-`. Renaming all of them touches the view code with
  no visual gain. Backlog item added.
- No new ds-proposal issues yet: breadcrumbs, table and summary list are already DS #3, #5, #6 (brief 07).
  The other candidates wait for a second project, as the DS promotion rule says.

## 2026-10-27 — Cross-source duplicates and alias master (request of the stiri session)

**Done**
- `same_name_key` ignores the sector, so "X - Sector 3" (ROePAS) merges with "X" (Registrul, ANI). Groups that
  state two different sectors stay separate. A second pass (`merge_same_name(nationwide=True)`) ignores the
  county when one record is in Bucuresti. Survivor: the Bucuresti record, then ROePAS > Registrul > ANI.
- `curation/merges.csv` (`id, kind, target_id, checked_at, evidence`): 3 merges (Frontiera IGPF, ITPF Timisoara,
  MFE = old MIPE) and 1 parent link (IGPR DICE). The build stops on an unknown id.
- All 109 "- Sector N" names lose the suffix (kept in `aliases`); none collides with another record.
- `curation/aliases.csv`: 105 rows. 4 ids were absorbed by merges (G10525, G10074, G10154, G10529) and were
  replaced by their survivors. The build stops when an alias id matches no record.
- Tests: 4 new (sector relaxed, nationwide, suffix collision, curated merge/parent). Determinism check passes.

**Measured**
- Records 25,106 -> 25,081 (-25). Same-name groups 323 -> 342, nationwide 5. No id vanished without a
  `merged_ids`/`roepas_ids` trail (checked against the previous CSV).

**Hard**
- stiri paired R11046889 (ITPF Timisoara) with the IGPF record A4193222. The weak candidate A4250638 (ITPF
  Timisoara) is the true match; merged there.
- G01302 "Registrul Auto Roman" (county Alba) stays separate: the name appears twice in Registrul (G10798 is the
  Bucuresti record that merged), so G01302 is probably a regional unit.

**Decided**
- Curated file for typo and old-name cases: a fuzzy rule would risk wrong merges of distinct bodies; the cost is
  manual rows (see BACKLOG).

## 2026-10-26 — gov2 design system: compatibility report, owner decisions, adoption brief

**Done**
- Compatibility report for DS v0.8.0 sent to the DS session `g2-ds`. The DS recorded it in its
  `docs/compat-analysis.md`. Read only: no project file changed for the report.
- DS proposals opened: dark colour scheme (gov2-ro/gov2ro-design-system#1), tricolour title (#2).
- Brief `docs/briefs/ds-adoption.md`: owner decisions, the filled-in adoption prompt, work items, acceptance.

**Measured**
- Live page = `gh-pages:index.html` = `main:explorer/index.html` (same SHA-1). Served by GitHub Pages;
  Cloudflare is DNS only. One worktree.
- Project CSS: one inline `<style>`, no `@layer`, 0 `--g2-`/`.g2-` names. Unlayered rules outrank every DS
  layer, the DS focus included.
- Tricolour contrast: #e0a800 on white 2.15:1, DS #fcd116 on white 1.47:1, DS #002b7f on #0b0c0c 1.54:1.
  The title sweep fails WCAG 1.4.3 for part of each cycle.
- DS tags on GitHub: up to v0.6.0. v0.7.0 and v0.8.0 are local only.

**Decided**
- Owner: DS fonts and DS sizes, with no local exception. This reverses the compact list of the styling round:
  rows get taller (baseline about 53 px at 1,280 px).
- Owner: keep dark mode; the DS prepares a shared scheme (#1). Until then, local `--g2-*` overrides in `@layer app`.
- Owner: the tricolour title goes; the DS decides on a shared treatment (#2). It conflicts with the DS rule
  "tricolour is never text".
- Owner: the title sweep keeps looping with no pause control. This is a deliberate deviation from WCAG 2.2.2
  (level A): the animation is slow and small. `prefers-reduced-motion` stays the only stop. Recorded on DS #2.
- Owner: approved the DS dark scheme (DS #1). A local DS tag is enough for adoption; GitHub tags lag on purpose.
- DS answer: dark scheme = DS ADR 0009 (opt-in, `data-g2-scheme="auto"`); title = DS ADR 0010, sweep on the text
  with two recorded deviations (WCAG 2.2.2, 1.4.3), so org needs an accessibility statement. DS order: brief 03
  (local fonts), 05 (dark), 06 (sweep). Every project installs the DS local fonts. The brief follows these.
- Wait for a DS release with ADR 0005 (self-hosted fonts). With the Google Fonts `@import`, the page makes
  third-party requests again. Cost of not waiting: we undo the no-third-party rule of the styling round.

## 2026-10-26 — Styling round: civtech look, compact list

**Done**
- `explorer/index.html` uses the civtech.gov2.ro tokens: white/ink palette, blue accent, 5 px radius, and the
  Monokai dark palette. Fonts (IBM Plex Sans, Instrument Sans, JetBrains Mono; SIL OFL 1.1) are copied from
  gov2-ro/awesome-civtech-ro `site/fonts/` to `explorer/assets/fonts/`. The title carries civtech's tricolour sweep
  (static under `prefers-reduced-motion`).
- The "Surse" column is gone from the list and from the tree tables. Source badges stay in the record dialog and
  the source filter. Flags ("posibil duplicat", "potrivire neclară") sit after the name. The ANI count shows in the
  meta line only when the list is sorted by declarations.
- List rows: no box, hairlines, mono column heads, contact in two lines (site; email · phone). Tree tables show the
  category as plain text, not a chip.
- Phones (≤ 760 px) keep the one-column table: name, kind and location; the contact column stays hidden.

**Measured**
- Headless Chromium screenshots, Cluj filter (73 records), 1,280 px: about 53 px per row, before about 76 px.
- No horizontal overflow at 1,280 px and 390 px. `reachableRoots()` = `expectedRoots()`. No page errors.

**Decided**
- Card view postponed (owner). A phone card layout without the location line was built, shown, and removed before
  the commit; it is in the backlog.
- Fonts are self-hosted, not from Google Fonts: the page keeps no third-party requests. Cost: 150 KB of woff2.

## 2026-10-26 — Filtered-out subordinates stay reachable in "Structura statului"

**Done**
- A filtered tree node ends with a link that reveals its hidden subordinates, dimmed, under the same family bundles.
  The revealed records open their own hidden subordinates the same way. Virtual nodes (Guvernul, county UAT
  lists) get the same link; "Fără corespondent ANAF" does not, because it holds thousands of records.
- A record with subordinates always expands under a filter, also when none of them match.

**Hard**
- The owner's report showed MAE at 0 / 4: the live data predated the curated websites (`3c4136e`). Locally MAE is
  4 / 4. The underlying problem was real elsewhere: MADR 15 / 232, with 217 subordinates hidden and no way to see them.

**Measured**
- MADR with the default filter: 15 matching; the link reveals 217 more (48 rows and 5 family bundles at the first
  level). `reachableRoots()` = `expectedRoots()`; `descendantVisibility()`: 8 checked, 0 failures.

**Decided**
- Keep "are site" on by default and reveal on request, instead of switching the filter off in the state view.
  Switching it off per view makes the same URL filter differ between views; the reveal keeps the filter meaning
  and the counts ("15 / 232") unchanged.

## 2026-10-26 — Explorer live at https://org.gov2.ro

**Done**
- First publish with `scripts/publish_pages.sh` to `gh-pages`. The owner made the repo public, added the Cloudflare
  record, verified `gov2.ro` for the org and enforced HTTPS.

**Hard**
- The `gov2-ro` org is on the Free plan, so Pages needed a public repo. The repo was private.
- Cloudflare flags the DNS-only record as exposing an origin IP. Ignored: the target is GitHub's public Pages hosts,
  and the GitHub certificate needs DNS only.

**Measured**
- Certificate: Let's Encrypt for `org.gov2.ro`, valid to 2027-01-23. HTTP redirects (301) to HTTPS.
- `rows.json`: 6.06 MB, 1.22 MB with gzip. Site: 10 MB, 100 files.
- Live page in headless Chrome: Cluj profile loads with 58 labels; `reachableRoots()` = `expectedRoots()`.

**Decided**
- Keep the record as DNS only. A proxied record needs SSL mode "Full", and it can block GitHub's certificate renewal.

## 2026-10-26 — Curated websites for central bodies

**Done**
- New tracked input `curation/websites.csv` (`cif, website, checked_at, evidence`). `consolidate.py` applies it to
  ANAF records after linking (`load_curated_websites`, `apply_curated_websites`). New CSV column `website_source`.
- 121 websites for central bodies that had none: 37 of the 64 `STATE_MEMBERS` and 84 of their direct children
  seated in București (agencies, authorities, offices, national institutes; not hospitals, schools, territorial
  units or academy research institutes). The selection script and the checks live in gov2-ro/stiri `data/central-2/`.
- Two tests (`CuratedWebsites`); 33 tests pass. `tests/determinism.sh` passes.

**Measured**
- Websites usable for stiri: 2,180 → 2,301 (`website_source`: 2,180 roepas, 121 curation). Rows: 25,106 (unchanged).
- Compared with the build before the change, only `website`/`website_url` differ, on 121 rows, plus the new column.
- Evidence: one GET per website with TLS verification on. 17 sites have a TLS fault, a bot wall, a timeout or a
  maintenance page (for example insse.ro, cnsas.ro, orniss.ro, curteadeconturi.ro); they keep their https URL
  and the fault is in `evidence`.

**Decided**
- A separate websites file now, instead of waiting for the general overrides spec. Cost: one later migration of
  121 rows into `overrides.csv`. The CIF key is stable across ANAF releases, so the file needs no id mapping.
- A curated website replaces a ROePAS one. ROePAS websites of central bodies are free text and sometimes wrong.
  This round replaced none.
- A section of a parent's site (UFIP on edu.ro, ITA on sri.ro) is not recorded as the body's website.

## 2026-10-26 — Landing cleanup, text tabs for types, labelled county maps

**Done**
- Landing: removed section headings and notes, the "largest types" row, and the duplicate state directory.
  One inline row of state branches stays, without Neclasificate and Fără corespondent ANAF.
- Type categories are text tabs (no borders or backgrounds). A click opens the category's types under the row;
  a second click closes them. The open tab survives a return to Acasă.
- The header counter shows only the active count. The full "N din M înregistrări" text is in its tooltip.
- County profile: the map sits in a right column (max 420 px, sticky under the header), the locality tree on the left.
  On phones the map comes between the header and the tree.
- New `scripts/build_uat_maps.py` (stdlib) splits the LAU polygon file into `explorer/assets/gis/uat/<COD>.json`, with
  SIRUTA, ANAF-style name, display label and a label point (polylabel). It replaces `ro-uats3_polygon-topo.json`.
- The UAT map shows names: seat, municipii and sectors, towns, then communes by count and size. Labels that overlap
  a placed label are left out; their names stay in the tooltip. București now has a sector map.

**Hard**
- The LAU file capitalizes the letter after a diacritic ("MăGura", "șTefan"). The script repairs the case.

**Measured**
- Old shapes: about 6.6 points per UAT (20,907 points). New: about 49 per UAT (156,403 points), 3.0 MB in 42 files,
  63–105 KB per county.
- `explorer.mapJoin()`: ANAF UAT roots 3,209 → 3,225 of 3,228; locality labels 3,276 → 3,289 of 3,302.
  One label is lost: Bihor "Abramut" (absent from the LAU file).
- Suceava shows 60 of 114 labels. No horizontal overflow at 320, 390, 900 and 1,440 px.
  `reachableRoots()` = `expectedRoots()`; no console errors; `git diff --check` passes.

**Decided**
- One state row instead of two. The owner asked for both inline; they had the same links.
- Per-county GeoJSON with 4-decimal coordinates instead of one national TopoJSON. A profile loads one county
  (about 70 KB), and the files need no topology encoder. The cost is duplicated shared borders (about 3 MB in total).
- Publish to GitHub Pages (https://org.gov2.ro) from this machine with `scripts/publish_pages.sh`: an orphan
  `gh-pages` commit, force-pushed on each publish. CI cannot rebuild the data, because the inputs stay out of git.
  The rejected alternative (tracked data + an Actions deploy workflow) adds about 6 MB to `main` per regeneration
  and still depends on this machine for the data.

## 2026-10-26 — Compact landing types, title-row menu, and flat government focus

**Done**
- Kept “Tipuri de instituții” and removed the duplicate “Tip → instituții” landing section.
- Type categories start closed on Acasă and in the separate family view.
- Moved both view links into “Mai multe”. The menu now shares the title row with the crest.
- The government display shows SGG, each ministry, and Organe de specialitate as peers.
- Ministry breadcrumbs skip the Ministere heading. Saved `n=ministere` links still work.
- Updated the navigation brief, state display spec, and backlog.

**Hard**
- Browser checks must close the menu before using the reset button. The title-row menu overlays the filter row.
- Website filters still hide branches without matches. The full government peer count uses `web=0`.

**Measured**
- Full government focus: SGG plus 16 ministry rows and one specialty group. Scope: 7,906 unique records.
- Browser checks pass for focus, filtered leaf records, saved ministry links, direct records, menu filters, and history.
- Five views fit at 320, 390, 768, 901, 1,024, and 1,440 pixels. The menu stays on the title row at each width.
- Both colour schemes have no page or console errors. JavaScript syntax and `git diff --check` pass.
- State integrity: 3,296 reachable roots = 3,296 expected roots. All eight attached descendant checks pass.

**Decided**
- Flatten the government display in the page. Metadata keeps Ministere, so counts and saved links retain their scope.
  The alternative requires data regeneration for a display change.
- Keep the compact type grid. Only the final choice between the two state presentations remains open.

## 2026-10-26 — Restore the previous landing sections alongside the new directories

**Done**
- Restored the previous overview, largest-type shortcuts, and compact type grid from the committed page.
- Kept the new state and type directories below those sections. Kept one county map after both layouts.
- Removed the introductory title and instruction. Moved the single “are site” checkbox into “Mai multe”.
- Both layouts share the active filters. Their links open focused groups or single-record details.
- Added the final landing composition decision to the backlog. Updated the navigation brief.

**Hard**
- The first refactor replaced the previous sections. The owner clarified that both layouts must remain for comparison.
- The restored overview overflowed at 320 pixels: document width was 349 pixels. Wrapping long links removed the overflow.

**Measured**
- Browser checks pass for the restored links, new directories, website menu, focus, records, refresh, and browser Back.
- Five views fit at 320, 390, 768, 901, 1,024, and 1,440 pixels. Both colour schemes have no console or page errors.
- State integrity remains 3,296 reachable and expected roots. All eight attached descendant checks pass.
- JavaScript syntax and `git diff --check` pass. Desktop and phone screenshots remain under `/tmp`.

**Decided**
- Preserve both landing compositions until the owner chooses. The cost is temporary duplication and a longer page.
- Keep one website checkbox in the menu. This avoids two controls for the same filter and keeps Acasă free of the search bar.

## 2026-10-26 — Landing navigation and focused institution types

**Done**
- Checked the latest commits and local data. The current snapshot has 25,106 records and 2,180 website URLs.
- Linked the supplied crest and title to `#`. Moved Listă and the two review filters into “Mai multe”.
- Removed the county tab. County profiles remain available through the map and existing links.
- Added state and type directories to Acasă. Groups open focused views; single results open their details.
- Added family breadcrumbs and county groups for large families. Ungrouped records retain a route through their category.
- Enabled “are site” by default. Explicit `web=0` links retain all records after refresh.
- Hid the search and filter bar on Acasă, following the owner's additional request. Result views show it.
- Fixed the favicon paths for hosting under `/explorer/`. Manifest icons use relative paths too.
- Recorded the current navigation rules in `docs/briefs/explorer-landing-refactor.md`.

**Measured**
- Unit tests: 31 pass. JavaScript syntax and `git diff --check` pass.
- Chrome checks: five views at 320, 390, 768, 901, 1,024, and 1,440 pixels. No document overflow.
- Checked menu bounds, both colour schemes, and desktop and phone screenshots. No page or console errors.
- Checked state focus, family focus, direct records, singleton shortcuts, refresh, Back, filters, and county profiles.
- State integrity: 3,296 reachable roots = 3,296 expected roots. All eight attached descendant checks pass.
- Default families include 1,156 commune records with websites. The full county list sums to 25,106 records.

**Hard**
- Chrome required execution outside the sandbox. Browser scripts and screenshots remain under `/tmp`.
- An initial cleanup removed family totals still used by record dialogs. Restored them before the final browser checks.

**Decided**
- The landing directories and county map respect the website filter. This keeps their counts consistent with the destination.
  The cost: branches without matching websites stay hidden until the visitor clears “are site”.
- Keep a separate website checkbox on Acasă. This preserves access to all records while the search bar stays hidden.
- Family focus uses the existing `v=fam` and `fam` parameters. The cost: family history entries need their own navigation key.
- The review checked local data and navigation. It did not verify the supplied website URLs against live services.

## 2026-10-25 — Fix: București records without a sector grouped by level
**Done** (Opus, a small change while the design moved)
- Owner request: replace "Fără localitate / sector necunoscut" with central-level groups above "Sectoare".
- `explorer/index.html`: `bucLevel` sorts București records without a UAT by name pattern into
  "Nivel central (sediu în București, sector necunoscut)" with 13 kind groups (ministere, agenții naționale,
  autorități, instanțe, companii naționale...), "Nivel București (municipal și servicii deconcentrate)",
  and a remaining "Sector necunoscut". Navigation grouping only; not a legal classification.
- Added the owner's curation request (flag duplicates, other edits) to the backlog with a proposal.

**Measured**
- București 1,248 records without a sector: 746 central (largest: companii 166, federații și asociații 121,
  institute 106), 60 București-level, 442 sector necunoscut (mostly schools and kindergartens).
- t10: group sums equal the county total in all 42 profiles. t11: 8 of 8 checks. No page errors
  (the only console errors are 404s for the untracked `explorer/assets/favicon/`).

**Decided**
- Group in the page, not in `consolidate.py`. *Why:* it is a view of existing fields and needs no schema change.
  The cost: the patterns live in JavaScript, and the CSV does not carry the level.

## 2026-10-25 — Build: București sectors, same-name merges, ANI prefix tier
**Done**
- Owner screenshots showed 12 sector groups, 1,426 București records without a locality, and visible duplicates.
  Opus measured the causes and wrote `docs/briefs/sectors-duplicates.md`; Sonnet built it; Opus reviewed.
- `sector_label` unifies "Sector N" (ROePAS) with "Sectorul N al Municipiului Bucuresti" (ANAF).
  `infer_sectors` takes the sector from a name that states exactly one (`uat_source: "name"`, compact `us`).
- `merge_same_name`: source-only records with the same folded name, county and sector numbers, from different
  sources, each name unique within its source and county, merge. Priority R > G > D; `merged_ids` / `mi`;
  `link.<src> = "same_name"`. The explorer resolves an absorbed id in `#id=` to the survivor.
- ANI `prefix` tier: an ANI name that is a strict prefix of exactly one ANAF name in the county.
- Opus tightened the prefix tier after review: a cut on a word boundary links only when one ANAF name in the
  whole country continues it. Sonnet's version linked generic heads ("SERVICIUL DE UTILITATI PUBLICE" →
  Buftea, "STATIUNEA DE CERCETARE DEZVOLTARE AGRICOLA" → Valu lui Traian). Prefix merges 56 → 26.

**Measured**
- Records 25,450 → 25,106. 328 ids absorbed in 323 groups: registrul+declaratii 283, roepas+registrul 26,
  roepas+declaratii 9, roepas+registrul+declaratii 5. 25 generic/village groups and 5 repeated-name groups skipped.
- 112 sector labels unified; 93 sectors inferred from names; București now has 6 sector groups.
- ANAF records unchanged (13,485, same names, UATs, parents). Ids unique; all references resolve; no absorbed id
  remains a record. 31 unit tests pass; CSV identical under two hash seeds. Browser checks t5–t11 pass.

**Hard**
- The brief excluded all `DECL_LOCAL_KIND` names from the same-name merge, but its own example (street
  administration) is a local kind. Sonnet narrowed the exclusion to village-level kinds (schools, kindergartens,
  libraries, cultural homes, parishes) plus generic heads without a proper noun. Opus accepted the deviation.

**Decided**
- `G10011`-style survivors keep the highest-priority source id, so ROePAS contacts stay on the visible record.
  The cost: absorbed D/G ids now resolve only through `mi`.
- Correction: ANAF `4192545` JUDETUL ILFOV and `4267117` MUNICIPIUL BUCURESTI are not misnamed (dropped item).

## 2026-10-25 — Build: landing page, county map and county profiles
**Done**
- Owner request: landing page, county choropleth, UAT maps per county, localities split by kind. Opus wrote
  `docs/briefs/explorer-landing-maps.md`; Sonnet built it in `explorer/index.html`; Opus reviewed.
- New view `acasa` (empty hash): overview, all families by category, county choropleth with a visible county list.
  `#v=loc&k=<county>` is the county profile: coat of arms, UAT choropleth, groups Reședința de județ / Sectoare /
  Municipii / Orașe / Comune / Altele / Fără localitate. Inline SVG, inline TopoJSON decoder, no dependency.
- Opus changed the map classes to quantiles of distinct values. Before, Brașov's UAT map had 3 classes
  (2, 3, 4–164) because most UATs have 2–4 records; now it has 5.

**Measured**
- Join: 42/42 counties; 3,209 of 3,228 ANAF UAT roots (99.4%; 7 are București sectors without shapes);
  3,276 of 3,308 distinct row locality labels. All 41 seats found. Exact-only name matching gave 96.4%.
- Brașov: seat 164, Municipii 46, Orașe 37, Comune 123, Fără localitate 299 = 669 records.
- Old hashes keep their views. No overflow at 320–1,440 px. 0 console errors. Regression scripts t5–t8 pass.
  With GIS requests blocked, a message replaces the map and the lists still work.

**Decided**
- The owner's request supersedes the v1 rule "no mandatory landing page". The landing page shows the whole
  dataset; a filter or search there opens the list. The cost: the list now writes `#v=list` explicitly.
- Name join with spelling tolerance (î/â as i/a, one edit when unique) instead of SIRUTA: ANAF has no SIRUTA code.
- The `explorer/assets/` files are committed: the page needs them at runtime. They are not pipeline inputs.

## 2026-10-25 — Build: data correctness and dense explorer, version 1
Brief: `docs/briefs/explorer-quality-v1.md`. Opus split the brief into two Sonnet briefs (data, UI) and reviewed both.

**Done — data (`scripts/consolidate.py`, `tests/`)**
- `Linker.link` returns candidates and a new tier `ambiguous`. Exact, canonical, unit and token ties merge only when
  a locality hint or a matching " - suffix" structure singles out one row. Token eligibility (kind, numbers,
  county names) is checked before the best score. Tie tolerance `TIE_EPS = 1e-9`. Thresholds 0.75 / 0.5 unchanged.
- A county name in the source name is identity evidence: a candidate that names only other counties is not eligible.
- New output: `match_candidates` (JSON), `match_candidate_cifs` (CSV), compact `i` and `mc`, known zero `pc`/`po`,
  `metadata.dataset` (generation time; per input path, bytes, SHA-256, mtime, rows; ANI `exported_at`, `capped`).
- Categories: word-bounded `ANCESTOR_HINTS`; `COMPANY_RE` ignores `S A` after single-letter abbreviations;
  a narrow "sanitar veterinar" rule before Sănătate; genitive `municipiului/comunei/orasului` as local authority.
- 20 `unittest` fixtures (`python3 -m unittest discover -s tests`), and `sh tests/determinism.sh` (hash seeds 1 and 2).

**Done — explorer (`explorer/index.html`)**
- Tree: full descendant traversal below attached roots, unique-record scoped counts, member notes in tree and dialog,
  `explorer.descendantVisibility()`.
- Wrapping header; "Filtre" disclosure with an active-filter badge on phones; in-strip tab scrolling.
- Overview "Explorează toate instituțiile" (closed initially): 15 state groups and 8 families with unique counts.
- One search normaliser for query and text. Loading status, Romanian error messages, retry.
- `id` hash parameter, "Copiază linkul", accessible dialog focus. "fără corespondent ANAF" and "de verificat"
  (`review=1`) filters. "Descarcă CSV" with the 17 spec columns. "Despre date" panel.

**Measured** (local inputs, same as the audit)
- Records 25,343 → 25,450 (+107). ANAF records 13,485 in both, with identical ids and parent CIFs.
  Registrul-only 6,043 → 6,076; ANI-only 5,328 → 5,403; ROePAS-only 487 → 486.
- ROePAS: 2 rows re-targeted, 1 newly merged, 0 un-merged. ROePAS 11057765 (`dspilfov.ro`) moves from DSP București
  `4400956` to DSP Ilfov `11445640`. ROePAS 11072883 (`dasbotosani.ro`) moves from DAS Dorohoi `4392462` to DAS
  Botoșani `15305089`. "Primaria Municipiului Mangalia" now merges into MUNICIPIULUI MANGALIA.
- Registrul: 6,632 → 6,599 merged; 56 ambiguous. 59 rows un-merged (identical ANAF names, e.g. CURTEA DE APEL BACAU),
  26 newly merged (e.g. GRADINITA 268, previously shadowed by an incompatible number), 3 re-targeted.
- ANI: merged names 17,429 → 16,990; token tier 2,795 → 2,302; 162 ambiguous standalone records; 401 token links
  re-targeted (e.g. ITM BOTOSANI filed under Vaslui now links in Botoșani).
- 236 records carry `match_candidates`; 2,557 carry `possible_duplicate_of` (was 2,581). Review filter: 2,793.
- Categories: 38 Cultură → Agricultură (the audit counted 32; 6 more come from the matching changes), D S V S A ALBA
  Companii → Agricultură, MUNICIPIULUI MANGALIA Altele → Administrație locală, 1 Sănătate → Agricultură.
- Integrity: ids unique; every parent, duplicate and candidate CIF resolves; CSV identical under two hash seeds.
  2,074 rows carry `pc:0`. Tests: 20 pass.
- Browser (playwright-core, installed Chrome): no document overflow at 320–1,440 px in four views and both schemes.
  Collapsed header 146 px at 390 and 320 px width. Bistrița-Năsăud variants return the same 408 ids.
  Roots 3,296 = 3,296; descendant check 8 of 8. `#v=stat&q=39847338` shows MF → acțiuni generale → DGRFP Brașov.
  Full CSV 25,450 unique ids, 0 mismatches with `rows.json`; focused-MF+query CSV holds only `A39847338`.
  Delayed, HTTP 503 and truncated-JSON loads show status or error + retry; retry adds no duplicate handlers.
  Record hashes (A/R/G/D), unknown id, Back/Forward, Escape, backdrop and copy-link behave as specified.
  Opus re-ran the check scripts after the last UI edit: all pass. Scripts and screenshots stay in the session
  scratchpad, outside the repo.

**Hard**
- `prep` collapses "CONSILIUL LOCAL X - SERVICIUL APA" and "COMUNA X" onto one key. Strict tie rules alone turned 104
  correct commune merges ambiguous; the " - suffix" structure rule restores them.
- Exact-name duplicates in ANAF (courts, tribunals) have no distinguishing evidence in the sources. They now stay
  unresolved and lose Registrul/ANI data they received before by first-row choice.
- Ports 8765 and 8791 were in use; the browser checks used a small Node static server.

**Decided**
- Prefer unresolved over wrong. *Why:* a wrong merge moves contacts to another institution, and no count reveals it.
  The cost: 236 records need review and some court records lost ANI/Registrul data.
- Multiple weak candidates set `match_candidates` and leave `possible_duplicate_of` empty (spec §1).
- The CSV formula guard applies to all text cells, including phone numbers that start with `+` (96 cells).
  Logged as a follow-up rather than special-cased now.

## 2026-10-25 — Handoff: implementation spec and brief
**Done**
- Prepared `docs/specs/explorer-quality-v1.md` and `docs/briefs/explorer-quality-v1.md` for another implementation session.
- Defined a bounded release from the confirmed audit defects and the owner's information-density preference.
  Added matching examples, schema fields, URL behavior, CSV selection rules and browser acceptance scenarios.
- Included a compact optional overview using existing groups and families. It does not introduce a new classification system.
- Defined phone header limits and required widths as new acceptance targets. They are not measurements of implemented behavior.
- Added the handoff entry to the backlog and a copyable implementation prompt to the brief.

**Hard**
- The earlier files held research and backlog items. They did not specify the new implementation end to end.
- Source inputs and India screenshots are ignored by Git. A fresh clone/worktree needs those files copied separately.
- Historical ANI identity and detailed ownership/accountability modeling need further design or evidence.

**Decided**
- Keep cross-source reconciliation, ownership research, inferred parents and full standards mapping as deferred work.
  The cost of including them now is an open-ended implementation with unresolved data assumptions.
- Explicitly permit the additive schema changes required by this release. Preserve the accepted constitutional mapping.
- Keep application code and data unchanged during handoff preparation. Implementation and acceptance remain the next session's work.

## 2026-10-25 — Research follow-up: information density and India screenshots
**Done**
- Read all three owner-provided screenshots in `tmp/india.gov.in-directory/`.
  They show the web-directory overview, branch/ministry browsing, and a separate public-utilities overview.
- Recorded the owner's correction: GOV.UK's layout has too little information density for this explorer.
- India's overview makes several routes visible together. Its public-utilities view uses familiar institution types.
  Both layouts use large tiles. The branch view also shows dropdown/View controls and nested scroll areas.

**Hard**
- Screenshots establish visible layout, labels and controls. They do not establish keyboard or mobile behavior.

**Decided**
- Narrow the UK reference to grouping, relationship wording and stable organisation identity. Do not copy its sparse layout.
- Recommend compact overview navigation with counts and direct links into existing results/tree views.
  Keep dense institution rows. An overview must not become a mandatory extra step.
- Keep institutional structure and familiar institution families as complementary routes.
  Do not interpret India's public-utilities categories as evidence of public ownership.
- These are research proposals. No application code or accepted-spec changes.

## 2026-10-25 — Research: foreign organisation directories and relevant standards
**Done**
- Reviewed the owner's examples from Moldova, the UK, the EU, New Zealand, Australia and India.
  Used official pages and standards. Inspected desktop/mobile rendering for Moldova, UK, EU and New Zealand.
- UK: searchable groups by body type; related bodies within department groups; stable profiles for closed bodies.
  The public-bodies guidance distinguishes economic and administrative classification.
- Australia: portfolio/type register, documented scope, reusable downloads, and departmental responsibility for maintenance.
  A sample profile lists legal basis, creation date and distinct classifications.
- New Zealand: explains organisation types, uses expandable purpose summaries, and links current and historical datasets.
- EU: separates organisation type and subject filters. Profiles/results include purpose and contact information.
- Moldova: separate pages for subordinate institutions and internal units/staff. The subordinate list also contains
  a duplicate bureau and a `gov.md/ro/null` link. Official publication alone does not ensure data quality.
- India: the portal and IGOD categories provide central/state, branch and district routes into the directory.
- Relevant specifications: EU CPOV for public-organisation descriptions; W3C ORG for organisations, units and history;
  PROV-O for provenance; DCAT-AP for dataset descriptions; COFOG for functional mapping; WCAG 2.2 for accessibility.
  These have different scopes. CPOV excludes commercial shareholding/ownership details. ORG needs extensions for
  detailed accountability relationships. COFOG classifies expenditure purposes, not institutional hierarchy.
- Added research proposals to the backlog. No implementation or accepted-spec changes.

**Hard**
- Australia's directory was readable through web retrieval, but Chrome failed with protocol errors/timeouts.
  India's portal returned Access Denied in Chrome. Its structure was available through web retrieval and official IGOD pages.
- No universal directory layout emerged. The standards provide data semantics and accessibility requirements.

**Decided**
- Recommend UK grouping, Australian register discipline, and New Zealand explanations/history as design references.
  This is a recommendation, not acceptance of a new spec. Keep Romanian legal types and constitutional navigation.
- Separate classification dimensions and relationship meanings before expanding automatic hierarchy.
  Keep the current JSON/CSV pipeline; assess a vocabulary mapping before choosing any new export format.

**Sources**
- Moldova: [subordinate institutions](https://gov.md/ro/autoritati-administrative-centrale),
  [internal structure](https://gov.md/ro/structura-interna).
- UK: [organisations](https://www.gov.uk/government/organisations),
  [public bodies guidance](https://www.gov.uk/guidance/public-bodies-reform),
  [organisation-page lifecycle](https://guidance.publishing.service.gov.uk/publish-update-retire-content/organisations-people/organisations/).
- EU: [directory](https://european-union.europa.eu/institutions-law-budget/institutions-and-bodies/search-all-eu-institutions-and-bodies_en).
- New Zealand: [organisations and historical dataset link](https://www.publicservice.govt.nz/system/central-government-organisations).
- Australia: [register](https://www.directory.gov.au/reports/australian-government-organisations-register),
  [body types](https://www.finance.gov.au/government/managing-commonwealth-resources/structure-australian-government-public-sector/types-australian-government-bodies),
  [sample profile](https://www.directory.gov.au/portfolios/agriculture-fisheries-and-forestry/australian-fisheries-management-authority).
- India: [portal directory](https://www.india.gov.in/directory/web-directory), [IGOD categories](https://igod.gov.in/categories).
- Specifications: [CPOV 2.1.1](https://semiceu.github.io/CPOV/releases/2.1.1/), [ORG](https://www.w3.org/TR/vocab-org/),
  [PROV-O](https://www.w3.org/TR/prov-o/), [DCAT-AP 3.0](https://semiceu.github.io/DCAT-AP/releases/3.0.0/),
  [COFOG](https://unstats.un.org/unsd/classifications/cofog/revision), [WCAG 2.2](https://www.w3.org/TR/WCAG22/).

## 2026-10-25 — Audit: explorer UX and data quality
**Done**
- Read the pipeline, explorer, accepted spec and prior measurements. Audited the existing output without rebuilding it.
- Measured 25,343 records, 13,485 distinct CIFs, 2,179 website URLs (8.6%), and 2,581 flagged duplicate candidates (10.2%).
  All record IDs are unique. All output parent and duplicate references resolve.
- Found 344 source-only groups with identical normalized county and name: 694 records in total.
  These are review candidates. Generic names can belong to different institutions.
- Reproduced wrong ROePAS contact assignments in the output: DSP București `4400956` gets `dspilfov.ro`;
  DAS Dorohoi `4392462` gets `dasbotosani.ro`. Both arise from tied token scores.
- Found 32 culture-category records with an ANI agriculture umbrella. The ancestor regex matches `culturii`
  inside `agriculturii`. Confirmed the behavior with an isolated call to `categorize`.
- Browser checks covered four views, seven viewport widths (320–1,440 px), CIF search, source-only records,
  county punctuation, focus, browser back, detail dialogs and delayed data loading. No page errors occurred.
- The root check passes: 3,296 reachable roots = 3,296 expected roots. A separate filtered check fails:
  `#v=stat&q=39847338` reports one match but renders no record. Focusing MF reports no match;
  focusing MF acțiuni generale renders the record. `subtree()` omits deeper descendants of attached roots.
- Measured document width 1,042 px at viewport widths 901 and 1,024 px. Phone sticky headers occupy
  349 px at width 390 and 380 px at width 320 (900 px viewport height).
- Search `Bistrița-Năsăud` returns 26 records; `Bistrita Nasaud` returns 408. Opening details preserves the
  current URL. CNCAN's placement note is in metadata but absent from the dialog.
- The local server sends 5,670,071 bytes of rows JSON before the interface becomes usable. Gzip would reduce
  those bytes to 1,071,305. This measures the local server, not a deployed host.
- All 2,074 known zero procedure counts disappear from compact rows. Both capped ANI exports still have
  10,000 rows. Company family coverage remains 17 of 954 records.
- Added confirmed defects and proposed enhancements to the backlog. Application code and data are unchanged.

**Hard**
- Chrome required execution outside the sandbox. Browser checks used Playwright with installed Google Chrome.
- The audit checked local snapshots and internal consistency. It did not verify live websites, ownership,
  current legal status or the accuracy of every source match.

**Decided**
- Prioritize match precision and source provenance before expanding automatic merges. Wrong matches move contact
  fields onto the wrong institution. Stable row counts do not detect this error.
- Keep source-only names as candidates. Reconcile identities with evidence and preserve unresolved cases.
- Recommend a small UX pass for search, filters, tree visibility, stable links and exports before another visualization.

## 2026-10-25 — Build: "Structura statului" view, version 1
**Done**
- `scripts/consolidate.py`: `STATE_NODES`, `STATE_MEMBERS`, `STATE_ATTACH` (next to `FAMILY_HEADS`) and `state_tree()`.
  `write_explorer_data` writes a `state` block to `metadata.json` (nodes, members with notes, attach rules, the
  3,228 UAT root CIFs, the unclassified CIFs). `rows.json` is unchanged. `report` prints "neclasificate".
- `explorer/index.html`: the tab "Autoritate → subordonate" (`renderAuthTree`) became "Structura statului"
  (`renderStat`). New: virtual nodes, county -> kind (Municipii/Sectoare/Orașe/Comune) -> UAT -> children, county
  split for family groups over 60 (`splitByCounty`), focus + breadcrumb, "matches / total", auto-open for at most
  50 matches, URL hash (`syncHash`, `applyHash`), breadcrumb and family siblings in `showDetail`.
- Measured: stderr summary differs from the baseline only by the new block: 2 roots, IDPSAR `25838704` and
  Registrul Urbaniștilor `17244352`. Metadata is now 47 KB (was ~6 KB). 64 mapped CIFs + 2 attached + 2
  unclassified + 3,228 UAT = 3,296 roots.
- Browser check (headless Chrome through playwright-core): `explorer.reachableRoots()` = 3,296 = rows with a CIF and
  no `p`. A full DOM crawl (all nodes opened, all "more" buttons clicked) counts 31,000 record entries = the sum of
  max(1, number of parents) over 25,343 rows. No console errors in any scenario.

**Hard**
- No browser extension was connected. The checks ran with playwright-core and the installed Chrome.
- The Constitution top layer has single-body entries (CCR, Curtea de Conturi...). Each is a virtual node with
  one member, so the breadcrumb and focus work the same way for all.

**Decided**
- The page cannot tell UATs from other roots without the name rule, so the script writes the `uat` and
  `unclassified` lists to `metadata.json`. *Why:* one copy of the rule. The cost: 30 KB more metadata.
- A county record shows as "Consiliul Județean X" (label only; its table row keeps the ANAF name).
- Virtual nodes stay in normal style under a filter; only record nodes that do not match show dimmed.
- Family siblings in the dialog: same family and same first parent; with no parent, same family and county.
- A record with two parents has its breadcrumb through the first parent in `p`.
- Attached roots (MF acțiuni generale, AMRSP) are added to `subordinates`, so "Subordonate" in the dialog lists them.
- `window.explorer.reachableRoots()` and `expectedRoots()` stay in the page as the console check.

**Review** (Opus, against the brief)
- Accepted. Re-ran `consolidate.py`: the stderr diff against the baseline is only the "neclasificate" block.
  `node --check` on the page script passes.
- Fixed one gap: under a filter, a match below an attached root (MF – acțiuni generale) had no visible path,
  because MF itself neither matched nor had matching children. `renderStat` now adds the attached root as
  context. Not re-checked in a browser.
- Accepted the deviation: virtual nodes are not dimmed. They have no match status of their own; record
  ancestors still are dimmed, as the spec asks.

## 2026-10-25 — Fix: `consolidate.py` output depended on the hash seed
**Done**
- Two runs on the same inputs gave different `institutii.csv` files (4–8 changed rows). The cause: the token
  tier summed IDF weights over a set of strings, and iterated a set of candidate rows whose order follows string
  insertion. Both depend on `PYTHONHASHSEED`. So ties between equal candidates went to a random row.
- `Linker.score` now sums in sorted order, and the candidate loop iterates `sorted(cand)`. A tie goes to the
  first ANAF row. Measured: 3 runs with `PYTHONHASHSEED` 1, 2, 3 give identical CSV and stderr.

**Decided**
- A tie goes to the first ANAF row, not to "weak". *Why:* this keeps the fix to two lines and keeps the tiers
  as they are. The cost: a tie still links to an arbitrary row (now a stable one). See the backlog.

**New baseline** (stderr summary): 25,343 records; registrul 6,632 merged / 1,272 weak / 4,771 no candidate;
declaratii 17,429 names merged onto 9,307 records, tokens tier 2,795; 5,328 records of their own (1,228 weak).
Before the fix, one random run gave 25,346 records and 9,327 records with declarations.

## 2026-10-25 — Spec and brief: "Structura statului" view
**Done**
- Measured the parent graph in `institutii.json`. The ANAF parent link is one level deep. There are 3,296
  roots: 73 central bodies, the rest UATs. MEC has 6,036 children, MS 214. 5,657 records have two parents.
  11,861 records have no CIF, and 3,544 of them can get a parent from their family (≥ 90% agreement).
- Wrote `docs/specs/structura-statului.md` and `docs/briefs/structura-statului-v1.md`. Started
  `docs/BACKLOG.md` and this log.

**Hard**
- The top layer (Parlament, Președinție, Guvern…) is not in any source. It must be curated by hand.
- Some placements are disputed (CNCAN, ANL, CNAS, ARACIS, ICR). They carry a note in the mapping.

**Decided** (with the owner)
- The top layer follows the Constitution. *Why:* the Constitution is a citable, stable reference. The cost of
  the alternative: a "who controls it" view needs research per body and changes with each government.
- The new view replaces "Autoritate → subordonate". The new tree contains every node of the old tree.
- Inferred parents wait for phase 2. Version 1 shows only ANAF data.
- Local administration is part of the view. Only this view shows the UAT → subordinates level.
- The mapping lives in `consolidate.py` and is keyed by CIF. `data/` is not in git, and CIFs are stable.
