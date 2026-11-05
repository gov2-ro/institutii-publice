# Implementation brief: checks in `publish_pages.sh`

Status: ready for Sonnet, 2026-11-05. Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-05): add the checks. See `docs/pipeline.md`, *Known gaps*.

## Problem

`publish_pages.sh` runs no tests. It does not check that the data comes from the committed code. Nothing checks the live site after a publish.

A comparison of times does not work: the normal flow is build, test, commit, so a commit is often newer than a correct build.

## Design (Opus)

The build records a hash of what made the data. The publish script recomputes the hash from `HEAD` and compares.

## Tasks

1. **Build hash in `consolidate.py`.** Add `dataset.build_hash` to `metadata.json`.
   - The hash is a SHA-256 over `scripts/consolidate.py` and each tracked `curation/*.csv`, in sorted path order, over the path and the content of each file.
   - Put the calculation in one small function with a named test.
   - `institutii.csv` and `rows.json` must not change.
2. **Preflight in `publish_pages.sh`.** It runs in the dry run too. It stops with a message that names the fix, if one of these fails:
   - `python3 -m unittest discover -s tests` fails.
   - `scripts/`, `curation/`, `explorer/` or `data/consolidated/institutii.csv` has uncommitted changes.
   - `dataset.build_hash` is absent, or differs from the hash of the same files at `HEAD`. Use one calculation only: let the script call the Python function, or a small helper that reads the committed files. Do not write the rule twice.
   Keep the existing checks.
3. **Check after the push.** Do this only in a real publish.
   - Poll `https://org.gov2.ro/metadata.json` with `curl` for at most 3 minutes. Compare `dataset.generated_at` with the published value.
   - A match prints a confirmation with the record count from the live `rows.json`.
   - No match prints a warning and exits 0: the push is done, and Pages or Cloudflare can lag.
4. **Docs.** Update `docs/pipeline.md` (*The build stops*, *Known gaps*), `CLAUDE.md` if a command changes, `docs/BACKLOG.md` and `docs/activity-log.md`. Mark `tests/determinism.sh` as still a step for a person: it takes minutes and rebuilds the data.

## Tests

- `test_build_hash_changes_with_input`: a changed curated file or script gives another hash.
- `test_build_hash_is_stable`: the order of the listing and the hash seed do not change the hash.

Add these to `tests/test_consolidate.py`. They use a temporary folder and no inputs.

## Done when

- All tests pass. A rebuild gives an identical `institutii.csv` and `rows.json` (`cmp`).
- `sh scripts/publish_pages.sh --dry-run` passes on a correct state.
- You showed that the dry run stops in each of these cases, and restored the state after each: a failing test, an uncommitted change in `curation/`, a data file built before a committed change. Report the messages.

## Stop and ask

Stop if a step needs a new dependency, or changes a record. Do not run a real publish. Do not push, tag or commit.

## Not in this brief

A CI job. Running `determinism.sh` in the script. A browser check of the live site.
