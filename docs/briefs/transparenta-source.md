# Implementation brief: transparenta.eu as a source (new records and parents)

Status: built by Sonnet and accepted by Opus with a fix (fields of `T` records from transparenta.eu, not the ANAF service), 2026-11-23. Owner decisions of 2026-11-23: yes to new records, yes to parents, both by rule.
Owner: Sonnet builds; Opus reviews and commits. Publishing needs the owner's approval.
Background: `briefs/transparenta-candidates.md`, `data/transparenta/candidates.csv`, `data/transparenta/parent-proposals.csv`.

## Decisions (Opus, 2026-11-23)

- transparenta.eu becomes a source of `consolidate.py`, with a rule, not with curation rows. **Why:** each new pull applies the rule
  again with no manual work. **Cost of the alternative:** curation rows go stale after every pull and need a new review.
- The inputs are the cached files of `transparenta_compare.py` (ignored, local), like the posturi and SEAP inputs. A missing file
  skips the source with a warning. `consolidate.py` makes no network call.
- Licence (owner rule: strictest text): the data comes from the ANAF budget execution reports, so OGL-ROU-1.0 applies.
  Attribute "ANAF, via Transparenta.eu". Name the transparenta.eu terms ("open data follows the licence of the source").

## Tasks

1. **Input.** `consolidate.py` reads `data/transparenta/entities-*.jsonl` (the newest), `last-report-*.jsonl` and `anaf-*.json`.
   Record each file in `dataset` of `metadata.json` (path, bytes, SHA-256, mtime, rows), as for the other inputs.
2. **New records (rule = the `add` rule of `transparenta_compare.py`).** A transparenta entity becomes a record `T<cui>` when all hold:
   - no record of ours has the CUI (as `cif` or `cif_tva`);
   - its latest report is in the current year or the year before;
   - the ANAF cache says active, and MF does not say `radiat`, `fuzionat` or `in_lichidare`;
   - at least one parent is a record of ours.
   Fields: name (ANAF name if present, else their name), county, UAT where `uat_of` finds it, address, `cif`, `cif_source` `transparenta`,
   `sources` `transparenta`, parents. Reuse the `add` rule code; do not copy it. Expected now: 11 records.
3. **Parents.** For a record with a CIF and no parent, take the parents of the transparenta entity with that CIF, where the parent is a
   record of ours. Set `parent_source` `transparenta` (CSV column; ANAF parents keep it empty). Do not change a parent that ANAF or
   `curation/merges.csv` (kind `parent`) set. Expected now: about 1,250 records.
4. **Output.**
   - Source bit `transparenta` = 64 in `SRC_BIT`. A record gets `transparenta` in `sources` only when it is a `T` record or takes a parent.
   - Row key `pt` = 1 when the parents come from transparenta.eu. Decode `pt` and the bit in `explorer/index.html`.
   - The record page shows such parents with the note "părinte după transparenta.eu" in the DS style of a secondary note.
   - Add the source to the `SOURCES` block, `NOTICE`, *Despre* and the footer list of sources.
5. **Checks.** Before and after, compare the stderr summary and report: new records, records with a new parent, category changes
   (parents feed `categorize`; list 20 examples), family changes, and any change to the "Structura statului" roots.
   `explorer.reachableRoots()` must equal `explorer.expectedRoots()`. Run the unit tests (add tests for the rule and the
   parent rule), `sh tests/determinism.sh`, and a browser check if a local server is allowed (otherwise say so).
6. **Docs.** `CLAUDE.md` (*Data flow*, row keys), `docs/pipeline.md` (source table, run order), activity log with measured numbers,
   backlog. Mark `briefs/transparenta-candidates.md` items done.

## Limits

- No network call from `consolidate.py`. Do not request `profile`.
- Stop and ask if a parent creates a cycle, moves a record out of a family by more than 50 records, or changes a root of the state tree.
- Do not commit and do not publish.
