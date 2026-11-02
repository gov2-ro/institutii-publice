# Implementation brief: name rules for posturi.gov.ro employers (DATA-ORG-03)

Status: ready for Sonnet, 2026-11-02. Owner decision (pax): "name rules first", then a fresh posturi export, then the
manual review of a smaller queue. Builds on [posturi-employers-source](posturi-employers-source.md) (merged as `25b0b88`).
Owner: Sonnet builds; Opus reviews.

## Observed (measured on `25b0b88`, posturi export of 2026-10-18)

- 4,443 of 5,901 posturi employers link (75.3%): exact 1,932, tokens 1,616, canonical 718, unit 177. 1,172 become
  `P` records in `posturi-review.csv`.
- 19 of the 20 `P` records with the most postings are name variants of an existing record, not missing institutions:
  - a trailing `, județul X` / `, judetul X` (and `, <locality>, județul X`);
  - a leading `U.A.T.` / `UAT`;
  - `spital`/`spitalul`, `complex`/`complexul`, `tg`/`târgu`, `dr.`/`doctor`, `c.f.`/`cf`;
  - acronyms: USAMV, DGASPC, ABA.
- A spike outside the repo, which stripped only the suffix and the `U.A.T.` prefix, moved 96 rows to linked
  (4,443 → 4,539). About 780 `tokens` links became `exact` or `canonical`.
- **False positives:** 24 of 141 `U.A.T. X` rows token-link to `SCOALA GIMNAZIALA X` instead of the commune record.

## Tasks

1. **Strip posturi name noise before linking**, in one function `posturi_clean(name)`, applied only to posturi rows:
   - a trailing `, județul X` / `, jud. X` / `, judetul X`, with an optional `, <locality>` before it;
   - a leading `U.A.T.` / `UAT` (with or without dots). The rest (`Comuna Matca`) then goes through `prep()`, which
     already collapses local authorities to `uat:<locality>`.
   Keep the raw name in the record. The cleaning is for linking only.
2. **Equivalent words.** Extend the token normalisation so that these pairs compare equal for **all sources**:
   `spital`=`spitalul`, `complex`=`complexul`, `tg`=`targu`, `dr`=`doctor`, `c f`/`c.f.`=`cf`.
   - `DECL_ABBREV` holds similar rules for ANI only. Move the shared ones (`tg`) to a common step, so that each rule
     exists once. Keep the ANI-only ones where they are.
   - This changes matching for the old sources. That is intended, but every change must show in the summary diff
     (Verification).
3. **No school for a commune.** A row that `prep()` classes as a local authority (`kind = uat`) must not link through
   `tokens` to a record whose name starts with a school, kindergarten or other local-unit word (the `DECL_LOCAL_KIND`
   pattern). It falls through to `canonical`, or stays unlinked.
4. **Acronym aliases.** Add rows to `curation/aliases.csv` for USAMV Cluj-Napoca, the DGASPC of each county that
   appears in `posturi-review.csv`, and „ABA <river>” (Administrația Bazinală de Apă). Follow the existing column rules
   (`kind=acronym`, a `basis` with evidence, `status=reviewed` only when you checked the ANAF record).
   Check that the linker reads `aliases.csv` for posturi rows. If it does not, report it and stop. Do not wire it
   without a question.
5. **Wrong county.** Do not fix posturi county errors (for example ABA Jiu, which posturi puts in Gorj and ANAF in Dolj).
   List them in the report.

## Verification

- `python3 -m unittest discover -s tests`: add a fixture for each rule. Use the real names from the top-20 table of
  the DATA-ORG-01 report, and the 24 `U.A.T.` → school cases.
- `sh tests/determinism.sh` passes.
- **Summary diff, before and after.** Report:
  - the posturi link rate by tier;
  - the size of `posturi-review.csv` and its count with 10 or more postings;
  - for each **old** source (anaf, roepas, registrul, declaratii), the links that changed. List 20 changed links
    of the old sources, each checked by hand as better, worse or equal. If any is worse, stop and report before you
    commit the data rebuild.
- The 24 `U.A.T.` → school links are gone. Report where each one goes now.

## Not in scope

- The fresh posturi export. The owner runs `ops/export-employers-for-org.py` on the VPS full database later, and
  then rebuilds.
- The manual review of the queue (DATA-ORG-02).
- Publishing, tagging, pushing.
