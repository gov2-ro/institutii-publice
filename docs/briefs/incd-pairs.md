# Implementation brief: INCD records with no CIF (issue #6)

Status: ready for Sonnet, 2026-11-06. Owner: Sonnet builds; Opus reviews.
Owner decision (pax, 2026-11-06): resolve the pairs with an agent. Merge the clear pairs. Leave the doubtful pairs open.

## Problem

71 records are of the INCD kind. A record is of this kind if its folded name contains `institutul national de cercetare` or the word `incd`. 27 of these records have no CIF. A name comparison suggests that about 20 of the 27 are copies of a record that has a CIF. The comparison is only a lead: it proves nothing. Reject a candidate when the evidence does not hold.

Baseline leads (no-CIF record -> candidate):

| No CIF | Candidate | | No CIF | Candidate |
|---|---|---|---|---|
| `R11065577` | `A15203810` | | `G10605` | `D974e5c45` |
| `G03144` | `A2522213` | | `G10608` | `D105eddbc` |
| `G23065` | `R11067917` | | `G10610` | `S5194978` |
| `G26069` | `Df89edd07` | | `G10613` | `D17cbcb49` |
| `G26070` | `D0cb610fb` | | `G10617` | `D105eddbc` (doubtful) |
| `G30065` | `G10604` (known to be doubtful: Neamț and București) | | `D5fd01700` | `A15203810` |
| `G38134` | `D27c051fe` | | `Dfd6f52e8` | `G10611` |
| `G38135` | `S9364218` | | `D498578a8` | `G10611` |
| `G40079` | `D6b60679a` | | `D7f2f2e0e` | `G10607` |
| `G10597` | `S18107639` | | `Da00d8ede` | `G10615` |
| `D79752cc5` | `S27282590` (`G10615` has another CIF: check) | | `Df5d5cd2b` | `G15220` |
| `P…-cantacuzino` | `A15203810` | | | |

No evident candidate: `G18160`, `G32125`, `G10602`, `G10614`.

One more pair outside the INCD kind: `D93b7a3d6` and `S14257595` (CFR locomotive repairs, Brașov).

## Rule for a clear pair (Opus)

A pair is clear only if all of these are true:

1. The specific part of the name is the same body. The generic words do not count. An acronym or a later name counts only with a source that links it.
2. The seat agrees. The ANI county is not reliable, so a mismatch on a `D` record alone does not reject a pair. A mismatch between two other sources does reject it. A branch or a subsidiary in another county is not the same body.
3. The CIF belongs to this body. An independent local source (ONRC, MF `status.csv`, or the SEAP names) gives the same name for this CIF.
4. No other record has a competing claim on the body or on the CIF.

A case that fails one test stays open. Do not apply a doubtful case.

## How to apply a clear pair

Read `load_curated_merges`, the code near `scripts/consolidate.py:326`, and the checks near line 1615 first.

- Candidate is an `A` record: add a `merge` row into it in `curation/merges.csv`.
- Candidate is an `S` record: `merges.csv` cannot name an `S` id. Add a row in `curation/identities.csv` on the no-CIF record. SEAP then links by CIF, and the `S` record goes away.
- Candidate has a curated CIF: merge first, then keep one identity row on the survivor. The survivor order is ROePAS, Registrul, ANI, posturi. Move the identity row if the survivor changes.
- Use the `evidence` column to name the sources of tests 1 to 3. Use `checked_at` 2026-11-06.

## No-candidate records

For the 4 records with no evident candidate, and for any record whose candidate you reject: look for the body in the ONRC files, MF and SEAP. Apply an identity only if tests 1, 2 and 3 hold. Otherwise leave the record open.

## Sources and limits

- Use local data: `data/consolidated/`, `data/seap/`, `data/lookup/status.csv`, and the ONRC files on geana (`/Volumes/geana/NAS-devbox/gov2/data.gov.ro-onrc-firme-2026-10-19`).
- Make no external call. If a case needs one, list the case in your report.
- Never copy MF natural-person rows into the repo, the outputs or the reports. Do not read or publish `TELEFON`.
- Do not run `scripts/scrape_roepas.py`.
- Do not add websites. That is separate work.
- Do not change code. If a pair needs a code change, or a step would change a spec, stop and report it.

## Build and checks

1. Run `uv run scripts/consolidate.py`. If a new CUI entered, run `python3 scripts/lookup_status.py` and then `uv run scripts/consolidate.py` again.
2. Run `python3 -m unittest discover -s tests` and `sh tests/determinism.sh`.
3. Compare before and after: the total record count, the count per id kind, and the INCD table (records, with a CIF, per `cif_source`). Explain every change. A change outside the listed records is a defect: find the cause.
4. Check that the alias of each merged body (for example GeoEcoMar) still reaches the surviving record.

## Done means

- The curation rows, with evidence.
- A table in `docs/activity-log.md` with one row per record of the 27 and the Brașov pair: decision, target or CIF, and the reason. Add the measured numbers and the rows that stay open.
- Open rows in `docs/BACKLOG.md`. Also add an item for the INCD records with no website.
- Do not commit, tag, push or publish. Opus reviews first. Report what you measured and what you assumed.
