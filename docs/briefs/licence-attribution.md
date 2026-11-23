# Implementation brief: attribution and licence notices

Status: brief ready (Opus, 2026-11-23).
Owner: Sonnet builds; Opus reviews and commits. Publishing to org.gov2.ro needs the owner's approval.
Input: `docs/reports/source-licences.md`, sections E (proposed texts) and G (owner decisions).

## Owner decisions (2026-11-23)

- Approved: E1 (`sources` block), E2 (`NOTICE`), E3 (*Despre*), E4 (footer), E5 (README and `pipeline.md`), E6 (map notice),
  E7 (a NOTICE link next to the CSV download; no change inside the CSV).
- **Rule:** where two licence texts of one source disagree, apply the strictest text and mention both. Do not ask the publisher.
- **Maps:** CC BY-SA 4.0 applies. Name both texts: the page footer (CC BY-SA 4.0) and the catalogue record (CC BY 4.0, edition
  2025-05-05). E6 already does this. Do the same in *Despre*, `NOTICE` and the `sources` block.
- **posturi.gov.ro:** the terms are unreadable. Name the source, link it, and say "terms not readable on 2026-11-05 and 2026-11-23".
  Do not send the draft. Mark `docs/drafts/licence-posturi-terms-question.md` and `licence-geo-spatial-question.md` as "not sent:
  the owner applied the strictest text instead (2026-11-23)".
- **MF copy date:** give both. `copy_date` is the snapshot `2026-06-11`. Add `version`: "actualizat iulie 2026".
- **Coats of arms:** the owner says they come from Wikipedia / Wikimedia Commons. See task 3.

## Tasks

1. **Texts.** Apply E3, E4, E5 and E6 as written, with the changes above. Keep the Romanian of *Despre* in the style of the page.
   Update the licence column of the *Sources* table in `docs/pipeline.md` (ANAF list: OGL-ROU-1.0). Fix section 1 and the summary
   table of the report, or add a line that points to section A.
2. **`sources` block and `NOTICE`.**
   - Add `sources` and `licence_note` (E1) to `metadata.json` in `write_explorer_data`. Keep the data in one constant in
     `consolidate.py`, not in the JSON writer. Take `copy_date` from the input metadata where the build has it (`dataset`);
     write a fixed value only where the build has no date. Do not change `rows.json` or `institutii.csv`.
   - Write `NOTICE` at the repo root (E2, with the changes above and the coats-of-arms result). `publish_pages.sh` copies it to
     the root of the site. Link it from *Despre*, the footer, and next to the CSV download.
   - Check that `dataset.build_hash` still works, and that `publish_pages.sh --dry-run` passes after the commit.
3. **Coats of arms.** For each of the 42 files in `explorer/assets/steme-judete/`, find the source file on Wikimedia Commons.
   - Use the Commons API (`action=query&prop=imageinfo&iiprop=url|extmetadata`), at most 1 request per second, with
     the `User-Agent` `institutii-publice-check`. Log the requests in `docs/external-lookups.md`.
   - Match by the county: the Romanian Wikipedia article of the county gives the image in its infobox. Compare the picture.
   - Write `explorer/assets/steme-judete/SOURCES.csv`: `file, commons_file, commons_url, author, licence, licence_url, checked_at`.
   - Strictest reading: our PNG is an adaptation (resized). If the source is CC BY-SA, our file stays CC BY-SA and names the author.
     If the source is public domain (for example `PD-RO-symbol`), say so.
   - Add one credit line to *Despre* and a section to `NOTICE`. The county profile keeps the image. Its `title` names the author and the licence.
   - A file with no certain match: report it, and leave it unchanged. Do not remove an image.
4. **Tests and checks.** Run `python3 -m unittest discover -s tests`, `sh tests/determinism.sh` and the browser check of `docs/pipeline.md`
   (the page *Despre*, one county profile, the footer). Add an activity log entry and close the backlog items.

## Limits

- Do not change the published records or their fields. Only `metadata.json` gets the new keys.
- Do not contact any publisher. Do not publish. Do not commit (Opus reviews and commits).
- Stop and ask if a text of section E conflicts with this brief, or if a Commons licence forbids our use.
