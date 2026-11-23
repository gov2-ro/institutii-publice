# Brief: licence compliance audit at the strictest reading

Status: brief ready (Opus, 2026-11-23). Owner request, 2026-11-23: "we should make sure we abide by the maximal terms of
licenses, for transparenta.eu and other projects we got data from."
Owner: Sonnet audits and proposes; the owner decides; Opus reviews.

## Context

- `docs/reports/source-licences.md` (2026-11-05) lists the terms of each source and nine open owner decisions.
  The owner decided on attribution (2026-11-06). The ROePAS decision is deferred.
- Since then, the project added sources: SEAP (CC-BY-4.0 and OGL-ROU-1.0), Ministerul Finanțelor (CC-BY-4.0),
  ONRC (CC-BY-4.0), tipizatul.eu names (`curation/tipizatul.csv`), and links to transparenta.eu.
- `README.md` says that the data is re-usable under EUPL v1.2. The page *Despre* (`explorer/despre.html`) names the sources.
- The published files are `institutii.csv` (in git), and `metadata.json` and `rows.json` on https://org.gov2.ro.

## Rule

For each source, take the strictest reading of its terms and licence. An obligation counts when any text of the
publisher states it. Where the text is not clear, assume the obligation applies.

## Tasks

1. **Inventory.** One row per source, including the sources used only for links, lookups or matching (ANAF web service,
   ONRC, tipizatul.eu, transparenta.eu, geo-spatial.org maps, county coats of arms, fonts of the DS). Read the current
   text of each licence or terms page again. Log each page in `docs/external-lookups.md`.
2. **Obligations.** For each source, list every obligation: attribution text, licence name and link, "indicate changes",
   share-alike, no endorsement, no misrepresentation, date of the copy, non-commercial, no automated access, notices
   that must stay in exports.
3. **Gaps.** For each obligation, say where the project complies and where it does not, with the file and line. Check at
   least these points:
   - Does the attribution travel with the data files (`institutii.csv`, `metadata.json`, `rows.json`), or only with the page?
   - Does the EUPL v1.2 statement in `README.md` and *Despre* claim rights on third-party data or on CC BY-SA map files?
   - Do the CC-BY sources say what we changed?
   - Does *Despre* say correctly what we take from tipizatul.eu (we store their spelling of institution names)?
   - Are the coats of arms and the fonts under a known licence, with the notice that it needs?
   - Is the posturi.gov.ro terms page readable now?
4. **Proposals.** Write the exact text of each fix (Romanian for the explorer, English for repo docs), and say which file
   it goes in. Propose a `sources` block for `metadata.json` (name, publisher, licence, URL, date of the copy, what we
   changed) and a `NOTICE` file for the repo and for `gh-pages`.
5. **Report.** Add the findings as a new dated section of `docs/reports/source-licences.md`. Add the open owner decisions
   to `docs/BACKLOG.md`. Add an activity log entry.

## Limits

- Do not change `README.md`, `explorer/`, `scripts/` or published data. The owner approves each text first.
- Do not contact any publisher. Prepare a draft message in `docs/drafts/` where a question needs the publisher.
- Do not reopen a page that refused the request. Use the client name `institutii-publice-check`.
- The agent is not a lawyer. Mark each interpretation as such.
