# Activity log

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
