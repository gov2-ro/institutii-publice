# Implementation brief: posturi employers with no org record (DATA-ORG-07, DATA-ORG-02)

Status: built by Sonnet and accepted by Opus, 2026-11-23. Request from ciulei (owner pax), see the inbox block at the end of `docs/BACKLOG.md`.
Owner: Sonnet builds; Opus reviews and commits.

## Observed (build 2026-11-06T21:58:17Z, posturi export of 2026-11-02)

- ciulei reports 1,009 posturi slugs (929 records, 1,375 postings) with no org record: `../ciulei/reports/posturi-unmatched.csv`.
- 423 of the 1,009 slugs have a candidate CIF (`possible_duplicate_of` or `match_candidate_cifs`): 406 have one candidate, 17 have more.
- Examples: `Universitatea de Vest` (Timiș) → 4250670, `Pius Brînzeu` → 4663448, `Termoficare Brașov` → 36560173.
- Five ABA bodies do not link because posturi gives the county of the posting, not the seat (DATA-ORG-07).
  The alias rows are scoped to the county of their record, so they do not help.

## Decision (Opus, 2026-11-23): DATA-ORG-07

Give posturi rows the two fallbacks that ANI rows already have in `link_declaratii`. Do not add an alias scope column.
- **Why:** the posting county is a true fact of the posting, so posturi cannot "fix" it. The ANI fallbacks already solve
  the same problem, with tested guards. One mechanism for two sources is cheaper than a new curation column.
- **Cost of the alternative:** an alias scope column changes `curation/aliases.csv`, which other projects read as a master.

## Tasks

1. **Nationwide aliases.** `Linker.anywhere()` reads `nat_exact` and `nat_canon` only. Add the reviewed alias rows to a
   nationwide index, so that `anywhere()` also finds a name that is an alias. The rule "exactly one row" stays.
2. **Fallbacks for posturi.** When a posturi row does not link in its county, try these steps in this order:
   - the Bucharest bodies, tiers `exact` and `canonical` only (tier `national`);
   - `linker.anywhere()` (tier `elsewhere`).
   Use the guards of `link_declaratii`: skip both steps for a local kind (`DECL_LOCAL_KIND`), and skip both steps when the
   county gave `ambiguous`. Do not use the `widespread` rule; posturi has no dropdown labels. Reuse code; do not copy it.
   Check that `TIER_RANK` and the posturi summary know the two tiers.
3. **Review the unmatched rows (DATA-ORG-02).** Work through the rows with a candidate CIF, most postings first. Then take
   the 50 rows without a candidate with the most postings, and search ANAF by name.
   - Accept a candidate only when it is the same body: the same name core and the same county, or a national body.
   - When the posturi name, after `posturi_clean()`, is a real name of the body, add a row to `curation/aliases.csv`:
     kind `short_name` or `full_name`, a `basis` with the evidence, `status` `reviewed`. An alias survives a new posturi export.
   - When the posturi name is not a real name (a typo, a junk suffix), add a `merge` row to `curation/merges.csv` with the
     `P` id. List each such row in the report: a new export can change the `P` id.
   - A subunit (a section, a branch) is not the same body. Leave it open.
   - Leave a doubtful row open, and list it with the reason.
   - Do not add an alias that folds to the name or alias of another record (check `aliases_unique`).
4. **Backlog and log.** Flip DATA-ORG-07 to `[x]` if task 2 links the ABA bodies. Keep DATA-ORG-02 `[~]` and write the
   number of rows that remain. Add an entry to `docs/activity-log.md` with Done / Hard / Decided, and the measured numbers.

## Do not

- Do not change `posturi_clean()`, the tiers of the other sources, or the ciulei block in `docs/BACKLOG.md`.
- Do not commit, tag, push or publish. Opus reviews first.
- Stop and ask if a step changes a spec, `curation/aliases.csv` columns, or the matching of ANI, ROePAS or Registrul.

## Verification

- `python3 -m unittest discover -s tests` passes. Add a test for an alias found by `anywhere()` and for the guard on a local kind.
- `sh tests/determinism.sh` passes.
- Save the stderr summary of `consolidate.py` before and after. Report the diff: posturi links per tier, the posturi
  review count, and any change in ANI, ROePAS, Registrul or SEAP counts (expected: none from task 2; task 1 can change ANI).
- List every posturi row with tier `national` or `elsewhere`: posturi name, posting county, record name, record county.
- Report the counts of task 3: rows accepted as alias, as merge, left open, and the postings they carry.
