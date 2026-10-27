# Backlog

Statuses: `[ ]` open, `[~]` in progress, `[x]` done, `[-]` dropped (with the reason).

## Implementation handoff
- [x] Data correctness and dense explorer, version 1 (built and accepted 2026-10-25):
      [spec](specs/explorer-quality-v1.md), [implementation brief](briefs/explorer-quality-v1.md).
      Includes conservative matching, confirmed category fixes, tree visibility, dense responsive filters, record links,
      review filters, CSV export, loading feedback, minimal dataset provenance and compact overview navigation.
      This is the bounded next release. The spec lists deferred research and data-enrichment work explicitly.
- [x] Adopt the gov2 design system (DS) v0.13.0: [brief](briefs/ds-adoption.md). Built 2026-10-27, not yet
      published (the owner reviews the screenshots first). DS fonts and sizes, DS dark scheme
      (`data-g2-scheme="auto"`), DS title sweep, footer, accessibility statement in "Despre date".
- [ ] Review and publish the DS adoption (owner): screenshots, then `sh scripts/publish_pages.sh`.
- [ ] Rename the remaining local classes to the `org-` prefix (`.tree`, `.multi`, `.seg`, `.src`…).
      New classes already use it. Low risk, but it touches the JS that builds the views.
- [x] Replace the local breadcrumbs, tables and record summary list with DS v0.14.0 (brief 07). Done 2026-10-27
      (DS issues [#3](https://github.com/gov2-ro/gov2ro-design-system/issues/3),
      [#5](https://github.com/gov2-ro/gov2ro-design-system/issues/5),
      [#6](https://github.com/gov2-ro/gov2ro-design-system/issues/6)).
- [ ] Propose to the DS the org components that a second project needs: county choropleth with legend,
      multi-select filter with AND/OR, filter bar with a phone disclosure, collapsible tree, category tabs.
- [ ] Phone list rows are taller with the DS sizes: 121 px at 375 px wide (was 75 px). Consider a phone layout
      that shows fewer lines per row (card view, already deferred above).

## Explorer: "Structura statului" (spec: specs/structura-statului.md)
- [x] Version 1: top layer from the Constitution, local administration, focus and breadcrumb, URL hash
      (brief: briefs/structura-statului-v1.md)
- [ ] Phase 2: give a parent to records with no ANAF match, from their family, when ≥ 90% of the family's ANAF
      members share one parent. Measured 2026-10-25: 3,544 of 11,861 records. Show these parents in a
      different style ("atribuit după tip").
- [ ] Later: a treemap or icicle chart of the top two levels, sized by number of institutions.
- [x] Filtered tree: include all descendants of attached roots in `subtree()`. Search `#v=stat&q=39847338`
      reports one match but shows no record. All eight children of MF acțiuni generale have this path problem.
      The existing root-count check passes. Add a check for descendant visibility under filters.
- [x] Show the notes on `STATE_MEMBERS` in the tree and detail dialog. The page discards the third tuple value.
      CNCAN's disputed-placement note is present in metadata but absent from its dialog.

## Explorer: usability and data presentation
- [x] The default "are site" filter hid most of the state structure: MADR showed 7 of 232 subordinates, with no hint
      that more exist (owner report, 2026-10-26). Each filtered node now ends with "+ arată și N subordonate fără
      site" (or "care nu corespund filtrelor"), which shows the rest dimmed. Records with subordinates always expand.
- [x] Fix filter overflow between the 900 px breakpoint and the grid's minimum width. Measured:
      a 901 px viewport has 1,042 px of document width; a 1,024 px viewport also overflows.
- [x] Reduce the sticky filter area on phones. It occupies 349 px at 390 px width and 380 px at 320 px width.
      Keep search visible. Put secondary filters behind a disclosure.
- [x] Normalize punctuation in search. `Bistrița-Năsăud` returns 26 records; `Bistrita Nasaud` returns 408.
- [x] Add stable record links and a copy-link action. Opening a detail dialog does not change the URL.
      The compact rows omit the record ID, which source-only records need for links.
- [x] Add loading feedback and a retry action. The main area stays blank while JSON loads.
      The current error text gives visitors a developer command.
- [x] Preserve known zero procedure counts in compact rows. There are 2,074 such records in the full JSON;
      none retains `pc` in the explorer. Zero and unknown must stay distinct.
- [x] Offer a filtered CSV download and filters for unresolved records and duplicate candidates.
      Show source dates and explain that ANI totals count declarations, not institutions or employees.

- [x] Styling round (owner request, 2026-10-26): align with civtech.gov2.ro (tokens, self-hosted fonts, dark palette),
      remove the "Surse" column from the list and the tree tables, denser rows.
- [ ] Card view (postponed by the owner, 2026-10-26): a card layout of the list, possibly without the address.
      A first version (phones: name, kind, site; no location line) was built and then removed before the commit.
- [ ] Add a light/dark toggle like civtech's footer control. The page follows only `prefers-color-scheme` now.

## Explorer: landing page and maps (brief: briefs/explorer-landing-maps.md)
- [x] Restore the previous landing sections alongside the new directories. Remove the introduction and move “are site” into “Mai multe”.
- [x] Keep the compact type grid, remove its duplicate, close categories initially, and put view links in the title-row menu.
- [x] Show SGG, ministries, and Organe de specialitate as peers in the Guvern focus.
- [x] Choose whether both the compact state shortcuts and the larger state directory stay. Owner choice 2026-10-26:
      one inline row of state branches, without Neclasificate and Fără corespondent ANAF (they stay in the state view).
- [x] Landing cleanup (owner request, 2026-10-26): no section headings or notes, header counter shows only the active
      count, type categories are text tabs with the types in a panel under the row, no "largest types" row.
- [x] Refactor landing navigation: linked crest, compact menu, website default, state and type focus, and result-only search.
      Owner request: 2026-10-26. Rules: [landing refactor brief](briefs/explorer-landing-refactor.md).
- [x] Landing view `acasa`, county choropleth, county profile with UAT map and seat/municipii/orașe/comune groups.
- [x] 12 ANAF UAT roots have no map shape, and București has no sector shapes. Fixed 2026-10-26: the county map
      reads per-county files from `scripts/build_uat_maps.py` (LAU polygons, 2025-03-26, with sectors).
- [ ] 3 ANAF UAT roots and 13 locality labels still have no map shape (`explorer.mapJoin()`): Berzasca, Simnihaiul
      de Cimpie, Vartoapele, "Stefanesti Stefanesti", "Municipiul Orsova - Mehedinti", Abramut (absent from the
      LAU file). A SIRUTA join would remove the name matching; the map files carry SIRUTA in `s`.
- [ ] Confirm the origin and licence of `ro_admin_lau_simplified_polygon.geojson` (copied from the owner's
      `GIS/api-places-search`). Record it in "Despre date".
- [-] ANAF UAT root names look wrong for two sector CIFs. Dropped: `4192545` JUDETUL ILFOV and `4267117` MUNICIPIUL
      BUCURESTI are correct. Their seats have București sector addresses; the UAT label is the seat's location.
- [x] București sectors and same-name duplicates (brief: briefs/sectors-duplicates.md).
- [ ] Same-name merge needs no review step yet. 323 groups merged automatically; sample of 14 looked right.
      Add a review list if a wrong merge turns up. Spelling variants ("ADMINISTRATIE" vs "ADMINISTRARE")
      and ANI sub-units ("ANAF … ACTIVITATE ECONOMICA") remain separate, under "de verificat".

## Publishing
- [x] Publish the explorer on GitHub Pages at https://org.gov2.ro (owner decision, live 2026-10-26).
      - `scripts/publish_pages.sh` builds the site from the committed `explorer/` of HEAD plus the generated
        `metadata.json` and `rows.json`, and force-pushes it as one orphan commit to `gh-pages`, with `CNAME`.
      - The owner publishes from this machine. CI cannot rebuild the data: the inputs stay out of git by design.
      - Set-up: repo made public (Pages needs a public repo on the Free plan), Cloudflare `CNAME org ->
        gov2-ro.github.io` as DNS only, `gov2.ro` verified for the org, HTTPS enforced.
- [-] Track the explorer data in `explorer/` and deploy with a GitHub Actions workflow. Dropped 2026-10-26: CI
      cannot rebuild the data, so the workflow would only copy files that one machine generated anyway. Tracking
      `rows.json` adds about 6 MB to `main` history per regeneration.

## Curation (owner request, 2026-10-25)
- [x] Curated websites for central bodies (2026-10-26, for gov2-ro/stiri's second central round):
      `curation/websites.csv`, keyed by CIF, applied by `consolidate.py`; provenance in `website_source`.
      121 websites filled: state-tree members and their national-level children in București with no ROePAS website.
- [ ] 7 central bodies still have no website: ASSN (assn.ro parked), Institutul Național de Cercetare pentru Sport,
      ARICE, ARCTIS (predecessor ocats.gov.ro under construction), ICDI Politehnica; UFIP and ITA exist only as
      sections of edu.ro and sri.ro (not recorded: a parent's section is not the body's own website).
- [ ] Fold `curation/websites.csv` into the general overrides file below when that spec exists (`set_website`).
- [ ] A method to flag duplicates and make other manual edits. Proposal, not yet a spec:
      a tracked overrides file (for example `curation/overrides.csv`: `id, action, value, note, author, date`)
      that `consolidate.py` applies last, with actions such as `merge_into`, `not_duplicate_of`, `set_uat`,
      `set_category`, `set_parent`, `hide`. Each applied override is recorded in the record's provenance.
      The static explorer gets a "Semnalează" action in the record dialog that prefills a GitHub issue
      (or copies an override line), because the page has no backend. Needs a spec: id stability across
      re-runs, conflicting overrides, and how a reviewer accepts a flag.
- [ ] București "Nivel central" groups come from name patterns in `explorer/index.html` (`BUC_CENTRAL`).
      442 records stay under "Sector necunoscut" (mostly schools and kindergartens). Overrides could place the rest.

## Data quality
- [x] Cross-source duplicates reported by stiri (2026-10-27): sector-relaxed same-name key, nationwide pass for
      Bucuresti bodies, `curation/merges.csv`, sector suffix removed from source-only names. Tag v0.15.0.
- [x] Alias master `curation/aliases.csv` (105 rows from stiri, ids checked against each build).
- [x] Courts check done 2026-10-27 ([report](reports/2026-10-27-courts-cif-check.md)): the register shows the same
      name, address and phone under both CIFs; not merged. Open: model a "same body, second CIF" link (29 pairs).
- [ ] ADR Vest (Timisoara) has no record in any source. stiri counts 7 mentions. Add a curated record, then alias rows.
- [ ] Same-name pairs reported by stiri (2026-10-27), unresolved. Courts have two ANAF records with one name and
      address but different parent CIFs: A17019105 / A47373006 (Curtea de Apel Bucuresti), A4340633 / A47373014
      (Tribunalul Bucuresti), and the same pattern for Dolj, Maramures, Harghita, Timis, Constanta, Valcea. The
      A47373... series has parent 4340587. Check with the owner whether it is a second CIF of the same body before
      any merge. Also D4618737e / G10796 (Romsilva) and IPJ Valcea (D9c68db53, G40002, G40072): the names differ in
      punctuation or spelling, so the same-name rule misses them. 126 ambiguous surfaces in all.
- [ ] R11176080 is named only "Adr" (ROePAS, Str. Italiana 22, Sector 2). Its meaning is unknown. Not the
      Autoritatea pentru Digitalizarea Romaniei (A42283735).
- [ ] AMR and UNCJR are in no source. Add them as curated records when the owner decides how.
- [ ] More duplicates that differ by an ANAF typo or an old name remain undetected. Review the weak candidates
      (`possible_duplicate_of`) of source-only Bucuresti records and add rows to `curation/merges.csv`.
- [ ] No ANAF or registrul record exists for Inspectoratul General al Jandarmeriei Romane. Only the ANI record
      D81c99b86 carries it (its weak candidate 4453144, IGPR, is wrong). The registrul extraction G14228 is damaged.
- [ ] ANAF-linked ROePAS ids appear in `roepas_ids`, not in `merged_ids`. Consumers must read both to redirect.
- [ ] Companii de stat: 937 of 954 are in "(fără tip comun)". 719 of them come only from ANI. Ideas:
      curated group heads (Electrica, CNAIR/DRDP, CFR, Romsilva, Transelectrica, ROMARM, Hidroelectrica);
      local utilities (apă-canal, termie, domeniul public, parcuri industriale, drumuri și poduri) placed
      under their UAT or county; merging the name variants (for example, at least 5 spellings of
      "Electrica Furnizare SFEE Transilvania Sud").
- [ ] Ugly network-family labels in Companii de stat: "Electrica furnizare sa sfee transilvania sud brasov
      afee", "Smart sa sucursala".
- [x] Wrong categories: "D S V S A ALBA LABORATOR SANITAR VETERINAR" was in Companii de stat (now Agricultură).
      "MUNICIPIULUI MANGALIA" was in Altele (now Administrație locală; the genitive form matches).
- [ ] Wrong categories, needing evidence first: IDPSAR is in Sănătate. SRR and SRTV are in
      "Servicii publice locale și regii".
- [ ] Re-export the two capped ANI county groups (full tail of rare names). (from README)
- [ ] Resolve ANI-only records (state companies) to a CUI with the ONRC open data. (from README)

- [x] Linker ties: when two ANAF rows get the same best token score, the first row wins. Consider "weak"
      for a tie instead (two equal candidates means the link is ambiguous). Confirmed contact errors:
      DSP București `4400956` receives `dspilfov.ro`; DAS Dorohoi `4392462` receives `dasbotosani.ro`.
      Use locality hints in token matching. Keep jurisdiction names as identity evidence.
      Also review ambiguous exact/canonical matches; they select the first candidate too.
- [x] Bound the ancestor category patterns to whole words. `culturii` matches inside `agriculturii` before
      the agriculture rule. Measured: 32 ANI records under an agriculture umbrella have the culture category.
- [~] Reconcile source-only records across sources, with review before merging. v0.7.0 merges exact same-name
      groups across sources (rules in briefs/sectors-duplicates.md); fuzzy variants remain. There are 344 groups
      containing 694 records with the same normalized county and name and no CIF. Example: DGASPC Sector 6
      appears separately in ROePAS, Registrul and ANI. A shared name alone does not prove identity.
- [ ] Retain each source row, match score, candidate alternatives and field choice in the output provenance.
      The current record exposes only the best link tier per source, which can hide mixed match quality.
- [x] Surface input checksums, sizes, file dates and capped ANI exports in `metadata.dataset` and the
      "Despre date" panel. Document how to obtain ignored inputs (CLAUDE.md / AGENTS.md).
- [ ] Add source snapshots and a reproducible release manifest. Add refresh rules to the ROePAS detail cache.
      Keep historical names and organizational units distinct from confirmed current legal entities.
- [ ] Review the 236 records with `match_candidates`. Most are exact-name duplicates in ANAF (two
      "CURTEA DE APEL CRAIOVA", "TRIBUNALUL BUCURESTI" rows with different CIFs and parents). Since v1 they no
      longer receive Registrul/ANI data. A curated CIF choice per name, or an ANAF parent hint, could resolve them.
- [ ] CSV export: the formula guard prefixes `'` to 96 phone numbers that start with `+`. Consider exempting
      `+` followed by digits in the phone column.
- [ ] Header at 768 px is 215 px tall (filters wrap to two lines). No spec limit covers it.

## Comparative research proposals (not an accepted implementation spec)
- [x] Keep high information density in institution results. The owner rejected GOV.UK's sparse layout as a UI reference.
      Borrow its grouping and relationship labels. India's screenshots suggest a compact overview of browsing routes,
      followed by dense results. Avoid a mandatory landing screen, oversized tiles and nested scrolling lists.
- [x] Explore two complementary entry routes: state structure and familiar institution families (schools, hospitals,
      municipalities). Show counts and open the corresponding filtered results or tree directly.
      Navigation groups do not establish legal form or public ownership.
- [ ] Separate policy function, body type, government level, ownership and territorial remit.
      Keep office location separate from the territory served. The EU directory separates type and subject.
      Australia separates portfolio and body classifications. Use Romanian terms with documented definitions.
- [ ] Plan stable organisation profiles with a short purpose statement, typed relationships, source dates,
      contact links and history. Keep closed records at their existing URLs, following GOV.UK's approach.
- [ ] Define relationship types before adding more hierarchy: administrative supervision, ANAF budget authority,
      internal unit, ownership and inferred placement. Record the source and validity dates for each relationship.
      Preserve the accepted constitutional view. Treat these as proposed additions, not new facts about a body.
- [ ] Map public-organisation fields to EU CPOV and organisation/unit concepts to W3C ORG.
      Document Romanian extensions for budget relationships and company ownership. Consider JSON-LD export later.
      Use COFOG as an optional function mapping; it does not define institutional hierarchy.
- [ ] Add a short explanation of public-sector scope and the tree's relationship meanings.
      Keep internal staff/unit structures separate from the directory of institutions. Add a dataset field guide,
      release dates and named source maintainers where known. See the comparative-research activity entry.

## Verified limits
- The ANAF parent link (ordonator principal de credite) is one level deep. It gives no middle level
  (for example, no ISJ between a school and the ministry). A middle level must come from grouping (family,
  county), not from ANAF.
