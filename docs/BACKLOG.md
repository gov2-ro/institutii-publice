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
- [x] Publish the DS adoption. Live since the publish of 2026-11-02, found on 2026-11-05.
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

- [x] Limited preview polish (brief limited-preview): meta tags, logo tile, header, footer, disclaimer, Contact. Built 2026-10-28, not published.

## Explorer: landing v2 and "Cum e organizat statul" (spec: specs/landing-v2-organizare.md)
- [x] Owner: answer the five decisions in spec section 4 (landing search, headings, state row, remembered
      county, separate page). All five accepted, 2026-10-27.
- [x] Build landing v2 and `explorer/organizare.html` ([brief](briefs/landing-v2-organizare.md)). Built 2026-10-27,
      not published; Opus reviews first.
- [x] Landing v2 on a phone: 2,909 px at 390 px with everything collapsed (was 5,970 px). Review round 1, 2026-10-27.
- [x] Tiles and cards ignore the website filter (owner decision 2026-10-27, review round 1).
- [ ] `organizare.html`: claims dropped for lack of a checked source (see the activity log, 2026-10-27, landing v2).
      Open them again when a source is checked: Academia Română and the branch academies as autonomous bodies;
      autonomous authorities "under parliamentary control"; DNA and DIICOT inside the Ministerul Public; "tutela
      administrativă" as a legal term; the Legea 544/2001 guide link.
- [ ] Add a check that every link of `organizare.html` opens a non-empty view (the build has none; this run used a
      Playwright script outside the repo).
- [x] Publish landing v2 and `organizare.html`. Live since the publish of 25592ae, 2026-11-02, found on 2026-11-05.
- [ ] The "Guvernul" and "Ministere" card counts (7,907 and 7,654) include the 6,000 schools funded through the
      Ministerul Educației. Consider a note or a count of direct subordinates only.
- [x] Landing: replace the category tabs with the "Toate tipurile" side box (spec section 2, item 5). Owner request 2026-10-27. Built 2026-10-27 (not published).
- [x] (Done in round 4, spec 2b.3) "Toate tipurile" box: records without a type are invisible there. "Companii de stat" shows 10 of 930 records
      (914 have no family); Altele 182 of 1,235; Agricultură 432 of 936. Add a last row per category,
      "Alte instituții din categorie · N", that opens the list filtered by the category.
- [x] Landing round 4 (spec section 2b): two-column top, jump links, "Domenii" section, page "Despre", GitHub icon,
      map compare by domain and type. Owner request 2026-10-27. Built 2026-10-27 (not published).
- [ ] Collect visitor feedback (owner, 2026-10-27). Options: a "Semnalează o problemă" link on each record (GitHub
      issue with the record id prefilled), a short form, an e-mail address. Decide the channel and who reads it.
- [ ] Map: a "pe hartă" link per need tile ("De ce ai nevoie?"), kept apart from the domain selects (spec 2b.5).
- [ ] Map: counts per 10,000 inhabitants (needs INS population per county; licence and date to record).
- [ ] A family label is cut off: "Centrul național pentru conservarea și promovarea culturii t" (seen in Domenii,
      Cultură). Check `pretty` / the network-family key for truncated tokens.
- [x] (Section removed, 2026-10-28) Despre: the source files show local paths and raw export names ("Lens Visualization [2026-10-19…] 3.csv").
      Show a readable name per source and keep the path in a detail line.
- [ ] Refine the county profiles (`#v=loc&k=<county>`): owner request 2026-10-28, deferred. Scope to agree first.
- [x] Publish the landing v2 work to org.gov2.ro. Done 2026-11-02; the status and SEAP work followed on 2026-11-05.
- [ ] Check the share preview of `og.png` in a share debugger (owner).
- [ ] Later: live counts on `organizare.html` (needs a small counts file, so that the page does not load `rows.json`).

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
- [ ] Short-form alias proposals (stiri, operator request, later): for the main public bodies, rows of kind `acronym` or
      `short_name` ("AJOFM Ilfov", "ISU Maramures", "Prefectura Galati"), status `proposed`, reviewed in batches by the
      operator. Not part of any tag yet. Start from the family heads (`FAMILY_HEADS`) and the county records.
- [x] `aliases_unique` column built 2026-10-27 (5,239 records): aliases whose folded text no other record uses and that
      are not a bare kind of body. 41 rows "Consiliul Judetean X" added to `curation/aliases.csv` as `proposed`;
      the operator must review them (a row becomes `reviewed` on approval).
- [x] A4469183 generic IPJ record: fixed 2026-10-27. The tokens tier let a source name that states county X link to
      an ANAF row of county Y when the ANAF name states no county. An ANAF name without a county now counts as
      its row's county. 16 foreign aliases -> 0 (3 aliases left, all Arges or bare). 67 records changed counts.
- [x] Cross-source duplicates reported by stiri (2026-10-27): sector-relaxed same-name key, nationwide pass for
      Bucuresti bodies, `curation/merges.csv`, sector suffix removed from source-only names. Tag v0.15.0.
- [x] Alias master `curation/aliases.csv` (105 rows from stiri, ids checked against each build).
- [x] Courts check done 2026-10-27 ([report](reports/2026-10-27-courts-cif-check.md)): the register shows the same
      name, address and phone under both CIFs; not merged. Linked 2026-10-27 by `same_body_as` (29 pairs, operator decision).
- [x] 12 more court pairs linked 2026-10-27 (partners found by hand; see `curation/same_body.csv`).
- [x] 15 more A47372... courts linked 2026-10-27 (operator principle: two records of one court). 56 links in all.
- [x] Review list of same-name groups outside courts built 2026-10-27: [report](reports/2026-10-27-same-name-review.md),
      89 groups. Done 2026-10-27: owner rule applied by `merge_loose_names` (87 groups merged).
- [x] stiri non-court ambiguous pairs (Romsilva, salt company, IPJ Valcea): merged by the loose-name rule.
- [-] ADR Vest (Timisoara): dropped by the owner 2026-10-27. No source has it; a hand record would need a new id prefix and a verified CIF.
- [ ] Same-name pairs reported by stiri (2026-10-27), unresolved. Courts have two ANAF records with one name and
      address but different parent CIFs: A17019105 / A47373006 (Curtea de Apel Bucuresti), A4340633 / A47373014
      (Tribunalul Bucuresti), and the same pattern for Dolj, Maramures, Harghita, Timis, Constanta, Valcea. The
      A47373... series has parent 4340587. Check with the owner whether it is a second CIF of the same body before
      any merge. Also D4618737e / G10796 (Romsilva) and IPJ Valcea (D9c68db53, G40002, G40072): the names differ in
      punctuation or spelling, so the same-name rule misses them. 126 ambiguous surfaces in all.
- [ ] R11176080 is named only "Adr" (ROePAS, Str. Italiana 22, Sector 2). Its meaning is unknown. Not the
      Autoritatea pentru Digitalizarea Romaniei (A42283735).
- [x] AMR and UNCJR: records `S11036662` and `S4696968` via SEAP (2026-11-03).
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
- [~] Resolve ANI-only records (state companies) to a CUI with the ONRC open data. (from README) First batch applied 2026-11-05; open: the hand-review list in the SEAP section. 4,274 records have no ONRC match (fuzzy matching is not started).

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

## posturi.gov.ro employers as a source (owner request, 2026-11-02)
- [x] DATA-ORG-01 — posturi employers as a source: [brief](briefs/posturi-employers-source.md). Merged 2026-11-02
      (`a97d412`…`25b0b88`), not published. The export script is `ops/export-employers-for-org.py` in posturi.gov.ro.
      Measured on the posturi export of 2026-10-18: 4,443 of 5,901 employers link (75.3%; 76.5% of postings),
      1,172 `P` records in `posturi-review.csv`, 11 with 10 or more postings. Records 24,981 → 26,153; no old id lost.
- [x] DATA-ORG-03 — name rules for posturi names: [brief](briefs/posturi-name-rules.md). Merged 2026-11-02
      (`5c78f09`…`0742bf7`), not published. Posturi linked 4,443 → 4,661 (79.0%; 81.1% of postings); queue 1,172 → 945,
      6 with 10 or more postings. The linker now reads the reviewed rows of `curation/aliases.csv` (139 + 21 new acronym rows).
      A kindergarten never token-links to a school. 67 tests; determinism passes.
- [x] Issue #6, parts done 2026-11-02: acronym aliases (ROTLD, INCAS, GeoEcoMar, IFIN-HH, INCDFM, ICI, CNAIR, ARACIP, ANMCS),
      alias rows now reach `aliases` for all id kinds, INCDFM and CNAIR duplicates merged.
- [x] Issue #6: curated CIF identities for the INCDs, BNR, RAAPPS and Imprimeria BNR. Built 2026-11-03: `curation/identities.csv`,
      521 rows (512 by an exact-name rule, 9 INCD rows by hand). CNAIR has no row: two project records are candidates
      (`R11040419`, `Dd8f2fa63`); see the SEAP section below.
- [x] Issue #6: absent bodies. Built 2026-11-03: AMR and UNCJR come in via SEAP (the name rule keeps them); Consiliul Fiscal,
      CSAT and Autoritatea de Audit have a `hosted_body` alias on the host body.
- [ ] DATA-ORG-07 — posturi gives the posting county, not the seat, for national bodies. Five ABA bodies cannot link
      (Jiu in Gorj/Mehedinți, Crișuri in Hunedoara, Olt in Sibiu/Harghita, Prut-Bârlad in Galați/Botoșani/Vaslui,
      Buzău-Ialomița in Prahova). Scan the other national bodies. Decide between a national alias scope and a posturi fix.
- [-] "A.B.A." does not fold to "aba", so the ABA alias rows do not catch that spelling. Dropped (Opus, 2026-11-04): see *Verified limits*.
- [ ] DATA-ORG-04 — re-run with a fresh full posturi export from the VPS (`--db` on a full export, not the
      active-only deploy file), then rebuild.
- [ ] DATA-ORG-02 — review `data/consolidated/posturi-review.csv` after DATA-ORG-03 and -04. Decisions go to
      `curation/merges.csv` or `curation/aliases.csv`.
- [ ] DATA-ORG-05 — decide whether linked posturi names become `aliases`. Not now: they carry county suffixes and junk.
- [ ] Check the posturi badge, filter and employer link of the explorer in a browser. The builder checked only the
      script syntax (`node --check`).

## Explorer issues from the 2026-10-28 review (gov2-ro/institutii-publice #1-#5)
- [x] #1 — landing search and example links drop the website filter; `?q=` moves to the hash.
- [x] #2 — the landing county row opens the profile without the website filter.
- [x] #3 — "Caută un tip" uses `norm` and tokens.
- [x] #4 — empty state shows the records hidden by the website filter; the landing counter shows the total.
- [x] #5 — `institutii.csv` is published at the site root; the footer shows the link and the EUPL line. Publish to see it live.
- [-] The footer text "41 de coloane" was hard-coded. Opus dropped the count from the footer instead (2026-11-02).

## SEAP contracting authorities as a source (owner request, 2026-11-02; brief: briefs/seap-authorities-source.md)
- [x] Phase 1: extractor, source `seap`, `S<cui>` records, `curation/identities.csv`, hosted-body aliases. Built 2026-11-03.
      Opus decisions of 2026-11-03 applied (see the activity log): rule accepted, company rule added, state tree fixed.
- [~] Review `data/consolidated/seap-pairs.csv`. Done 2026-11-04: 44 duplicate pairs merged and 41 identities added (same name, one county
      or one Bucuresti sector). Done 2026-11-04, second pass (ANAF web service lookup, see the activity log): 18 identities and 19 merges.
      After the extractor re-run the file had 29 rows (18 `two_records`, 11 `two_seap_rows`); it now has 11 (4 + 7). Rows that stay open:
      - `2865432`, `12269739` (Camin pentru persoane varstnice), `17993499` (Unitatea de asistenta medico-sociala), `24618107`
        (SPCLEP), `34052870` (Serviciul public de salubrizare), `39483628` (Directia de asistenta sociala), `4291700` (APM):
        ANAF puts the seat in a county where no candidate lies. A person or a county-level source must decide.
      - `4515077` (DADR): the ANAF name differs ("DIRECTIA PENTRU AGRICULTURA JUDETEANA CONSTANTA", status RADIERE 2017) while SEAP
        lists 354 rows up to 2026-Q3. G15191 (Constanta) is the likely record, but the name and the dates disagree.
      - `448001922` (Administratia Comerciala Sector 6): the ANAF service does not know the CUI (9 digits, likely a typo).
      - New rows, not decided: `11446310` (Oficiul Judetean de Consultanta Agricola; ANAF name "CAMERA AGRICOLA DOLJ", Dolj; G18183 is
        the only Dolj candidate), `15221670` (Serviciul Public de Administrare a Domeniului Public si Privat; ANAF name is the one of
        Mangalia, Constanta; G15340 is the only Constanta candidate). Both names differ from the ANAF name.
      Lowest confidence among the applied merges: `39466317` (D04a78a2e, Ilfov): ANI often files Bucuresti bodies under Ilfov.
      `14198936`: the identity is on G12310 (Calarasi). D22bd9669 (Arges) stays separate, because the name is generic (Opus review).
- [x] Re-run `scripts/extract_seap.py` when the dump download ends (2021 TIII/TIV, 2024 TIII/TIV and others were missing on 2026-11-03).
      Done 2026-11-04 with `--trust 38e601a9`: 291 resources, 181 read, 1 trusted, 62 `no_size`, 47 `no_header`, 0 `missing`.
      Distinct authority CUIs 17,783 -> 18,077. The cache in `data/seap/cache/` rebuilds `authorities.csv` after the dump is deleted.
- [-] 62 files of 2016-2019 stay unread. Reason: `packages.json` has no size for them (status `no_size`), so a partial download
      cannot be told from a full one; the authorities are old. Owner decision (Opus, 2026-11-03).
- [-] 47 files of 2007-2016 stay unread (4 on 2026-11-03; 43 more files of this kind were downloaded later). Reason: they are `^`-separated with other column names (`AutoritateContractanta`,
      `AutoritateContractantaCUI`) and the authorities are old (status `no_header`). Owner decision (Opus, 2026-11-03).
- [x] Check `explorer.reachableRoots()` against `expectedRoots()` in a browser. Done 2026-11-04 in headless Chrome: 3,296 = 3,296;
      `descendantVisibility()` checked 8, 0 failures; no console error. Before this, the builder had checked only that the root CIFs
      of `rows.json` equal the CIFs placed in `metadata.state` (3,296 both) and the page script syntax (`node --check`).
- [ ] `curation/merges.csv` cannot name an `S<cui>` id (the records are created after the merges). Add it if a merge is needed.
- [x] Defect: `period()` in `scripts/extract_seap.py` gave the wrong period to the files of the dataset "Achizitii publice 2007-2015
      (Contracte)": the title gave 2007 for files of 2008-2016 (among them the 3 files of 2014 T3/T4, `2d1bcb67`, `3d31f7be`, `e32a3d76`).
      Fixed 2026-11-05: a year in the file name wins over the year in the title. Measured: 58 of 291 resources changed, all in that dataset;
      the other 233 keep their period. `first_seen` 2007: 4,935 -> 0 CUIs; `last_seen` 2007: 294 -> 0. Only these two columns differ in
      `authorities.csv`; `institutii.csv` is unchanged. A cache with a stale period is now corrected when the file is there (no full read).
- [ ] Family "Poliția locală" lost Sector 1, 2, 4 and 5 after the merge of the ANI copies of Sector 2 (2026-11-04). The ANI county noise
      had carried these records over the rule of 5 members in 4 counties. Consider `FAMILY_HEADS` for this family.
- [ ] Phase 2: spike on the e-licitatie.ro authority profiles for contacts (access, terms, fields), then a brief.
- [~] ANAF lookup of the `S` records. Run 2026-11-04: 2,747 CUIs in 28 requests; 2,728 found; 809 `RADIERE` or `DIZOLVARE`; 19 not found.
      The output stays in `data/lookup-survey/` (not in git). ANAF states no terms on re-use: the right to republish is open.
- [x] Build status and county of `S` records ([brief](briefs/record-status.md)). Owner decision 2026-11-05: keep defunct records,
      add a status field, hide them by default. Source: MF only. Built 2026-11-05 (Sonnet), awaits review by Opus. 3,406 CUIs looked up:
      2,441 `activ`, 572 `not_found`, 386 `fuzionat`, 1 `in_lichidare`, 0 `radiat`. 386 records hidden by default; 6 SEAP conflicts and 17 county
      disagreements in `status-review.csv`; county filled on 1,585 `S` records. Script `scripts/lookup_status.py`; tests `tests/test_status.py`.
- [x] Check the Finance Ministry dataset (MF, CC-BY-4.0): base source for the status brief, not the only source. See the activity log, 2026-11-05. Yearly dataset with a new name each year; snapshot 2026-06-11.
- [ ] Status rows: the page hides only `radiat` and `fuzionat`. `radiat` is 0 in our data now (MF has 41 `RADIERE` rows, none is ours): the 391 deregistered
      `S` bodies of the ANAF survey are `not_found` and stay visible until the owner accepts ANAF.
- [ ] Status review (Opus): `data/consolidated/status-review.csv` lists 6 SEAP conflicts (5 `fuzionat` `S` records and `G18039`) and 17 county disagreements
      (9 `S`, 8 `D`). Decide whether a SEAP conflict with a fuzionat body (the SEAP rows may belong to the successor, e.g. E-Distributie) should keep the status.
- [ ] 217 `S` records got a county but no UAT: the MF locality is a village, or a spelling that ANAF does not use ("Simleu Silvaniei" / "Simleul Silvaniei").
- [ ] Explorer: the CSV export of the page has no `status` column yet.
- [x] Owner: accept or reject ANAF as a status source for the published data. Decided 2026-11-05: keep ANAF out for now. ANAF states no re-use terms. Until this changes, 391 deregistered `S` bodies stay visible as `not_found`.
- [ ] Check the public-data re-use law, or ask ANAF, about re-use of the ANAF status. If the answer allows it, ask the owner to add ANAF rows to `status.csv`. A message to ANAF needs the owner's approval first.
- [x] Record the licence or the re-use terms of the ANAF list, ROePAS, Registrul and ANI. Done 2026-11-05: `reports/source-licences.md`, summary in `pipeline.md`.
- [ ] Owner, later (deferred by the owner 2026-11-06, no date): decide on ROePAS. Its terms forbid scraping and mass copying, and it gives all e-mail addresses and phone numbers in the list. Options are in `reports/source-licences.md`. The data stays published. Do not run `scrape_roepas.py` again until the owner decides.
- [x] Owner: approve one attribution block for *Despre*, with the ANAF list, Registrul, ANI, posturi.gov.ro, the maps and the OGL-ROU-1.0 sentence for the SEAP datasets under that licence. Approved and added 2026-11-06, also with ONRC and the MF line.
- [x] Owner: say which service gave the ANI Kibana exports. Answered 2026-11-06: the author of monitorul.ai gave the owner access to the Kibana. Recorded in `README.md`.
- [ ] Owner: ask the author of monitorul.ai who runs the Kibana, and whether the project may republish the aggregate counts. No written terms are on record.
- [ ] Check the licence of the map layer in the geo-spatial.org catalogue and its compatibility with EUPL v1.2. Check the origin of the county coats of arms: Legea 179/2022 art. 1(2)(g) excludes coats of arms.
- [ ] Read the posturi.gov.ro terms when `oc.gov.ro` works again.
- [x] Add a preflight to `publish_pages.sh`: run the tests, and stop if the data does not come from the committed code (`dataset.build_hash`). Add a check of the live site after a publish. Built and reviewed 2026-11-05. The live-site check has run only against the current live site, not after a real push. Read its first real output at the next publish.
- [ ] MF `TELEFON`: 1,540 usable numbers for `S` and 7,526 for `A`. Owner, 2026-11-05: do not publish for now. 50% differ from our phones, 1,373 are mobiles, 38 numbers are shared by 3 or more CUIs, so they may be fiscal or personal contacts. Open it again only with a personal-data review.
- [ ] MF `STARE` "MODIFICARE PUBLICI": 2,176 rows are not in our data. About 794 look public by a rough regex. A lead for missing public bodies, after a filter and a review.
- [ ] ANFP list 2025 (CC-BY-4.0, 4,325 rows; name, type, county, locality; no CUI or contacts): consider it for classification.
- [x] ONRC files of 2026-10-19 for the ANI-only records: downloaded to `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-onrc-firme-2026-10-19/`, match measured 2026-11-05.
      Queue: `data/lookup-survey/onrc-review.csv` (not in git).
- [x] Apply the ONRC matches ([brief](briefs/onrc-identities.md)). Built 2026-11-05, reviewed by Opus. Records 28,511 -> 28,308 (-203: 167 `S`, 35 `D`, 1 `P`).
      `curation/identities.csv` 581 -> 826 rows (+245: 3 test rows of task 2, 158 `S` holders `exact_county`, 6 `S` holders `exact_elsewhere`, 78 by the task 4 rule).
      `curation/merges.csv` 81 -> 117 rows (+36: 8 `D` copies of one CUI, 24 `G`, 2 `R`, 1 `P`, 1 `D` holders). Rule (Opus, 2026-11-05) in the activity log.
      Script: `scripts/onrc_candidates.py` (queue `data/consolidated/onrc-review.csv`, not in git); tests: `tests/test_onrc.py`.
      `exact_elsewhere` and `ambiguous` get no rule; only the 9 ids named in the activity log entered.
      Sample limit: 0 wrong in 30 `S` cases cannot rule out a wrong share up to about 10%. The other 141 `S` cases had only a flag scan
      (name key, county, generic name without county), not a read.
- [ ] ONRC hand-review list (Opus decides; none of these is applied). Ids are `D` records unless said.
      Dissolved or insolvent, new identity not set (`exact_county`, 17: 14 not in function, 3 `unknown`): `D0d7368df`, `D0e19aa1c`, `D0f4231e3`, `D164c95a7`,
      `D2ba6cb6e`, `D35351796`, `D3bb87ffc`, `D43679d3d`, `D4a4215c2`, `D863838d3`, `D9a851607`, `Daa718cae`, `De78aca44`, `Deef5259b`
      (not in function); `D5742add0` ROMAERO, `D6fa13d26` CASSTIL, `D7f6e3e64` (`unknown`, insolvency). Also `D03dd09f1`, `D6d256391` (FORMENERG),
      `D8d5b84e1`, `Daa85e87f`, `Db9360acb` (INTERNET SI TEHNOLOGIE S3), `D4b7995b1`, `De33610b1` (SERVICII ENERGETICE OLTENIA) below.
      Form conflicts: `Dd4162cb3` (name SRL, ONRC SA), `Ddbc23bf1` ROMGAZ SA (ONRC: ROMGAZ RA, radiată), `De46bd2ca` SMART SA (ONRC: SMART SRL, radiată);
      with an `S` holder: `D67040b8e` CALORGAL SA (ONRC and `S`: SRL), `Ddf59f970` AMENAJARE EDILITARA S5 S R L (ONRC: SA; `S` name: SRL) and `D566191d2`
      (same CUI 27515874, form agrees; held back with the other).
      Several `D` records on one CUI, no other holder (13 records, 6 CUIs): 14529126 (`D03dd09f1`, `D6d256391`), 14325290 (`D47f94e9f`, `D61e5c56c`),
      2410163 OIL TERMINAL (`D48913daf`, `D4e8f1dbb`, `Df875d65a`, and `Dfba6e431` with no form), 29389861 (`D4b7995b1`, `De33610b1`),
      38189005 (`D8d5b84e1`, `Daa85e87f`, `Db9360acb`), 1350020 CONPET (`D45dd80c7`; the ambiguous `D6d38ad48` has the same name in Giurgiu).
      A merge of the copies, then one identity, is the likely action.
      No company form in the name, so the rule does not apply (6): `D498578a8` (ICPE-CA), `D8b450ebf` (EXIM BANCA ROMANEASCA), `D90ca3d97` (a CFR branch),
      `D9188e2c5` (GRADINITA PITICOT, SRL, radiată: a private body), `Dcc400e15` (CENTRUL DE AFACERI FLANDRA VALCEA), `Dfba6e431`.
      Held back: `Dffbbf1ee` ADMINISTRATIA DOMENIULUI PUBLIC (Bihor; the name has no SA; Bihor has several such bodies; the holder is `Dd0e06565`, ADP Oradea SA).
      Side effect to check: `G02187` changed category from Altele to Companii de stat (the absorbed `Dfe52ae98` had that category; `absorb` takes the new category when the old is Altele).
- [ ] Phase 2: sicap.ai API (`https://api.sicap.ai/v1/openapi/json`) gives `cityAuthority`/`countyAuthority` per authority CIF,
      which fills the county of the `S` records. No contacts. Needs an API key (the owner has none yet) and a check of the
      pricing and terms (re-publishing under EUPL). `https://sicap.ai/mcp` is behind a Vercel checkpoint (429 for scripts).
- [x] Deleted by the owner, 2026-11-05; `packages.json` stays. Delete the dump `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-adr-achizitii-publice-dump` (owner request, 2026-11-03).
      Do it after the download ends and `extract_seap.py` re-ran, and only when the manifest has no `incomplete` or `missing`
      resource that the owner wants. Keep `packages.json`. The cache in `data/seap/cache/` keeps the extracted authorities.
      State on 2026-11-04: the manifest has no `missing` and no `incomplete` resource. The owner still decides about the resources
      that the extractor does not read: 62 `no_size` files (2016-2019, no size in `packages.json`) and 47 `no_header` files (2007-2016,
      `^`-separated). The cache holds nothing for them, so the deletion loses them. The owner accepted that loss on 2026-11-04.
      The `period()` defect is fixed (2026-11-05). Check of 2026-11-05: `extract_seap.py --dump <folder with packages.json only> --out <copy
      of the cache>` gave `authorities.csv` byte-identical to the run with the dump; 182 resources `cached` (181 read + 1 trusted), 109
      `missing` (62 `no_size` + 47 `no_header`); 18,077 CUIs. Ready to delete: the owner deletes the dump files, keeps `packages.json`.
- [ ] Private utilities pass the SEAP company rule by volume (100 rows or more): ENGIE Romania, E-Distributie Dobrogea, and
      similar sector entities. Consider a curated exclusion list or a "utility operator, private" flag.
- [x] `packages.json` resource `38e601a9` has the size and file name of `e40a48ed`. Checked by hand 2026-11-03: the file is a valid
      zip, 72,644 rows, header `Numar notificare`: it is the report "Notificări de atribuire la cumpărarea directă TII 2025".
      The extractor reads it with `--trust 38e601a9`.

- [ ] Record `Px` has the name "—" (source posturi, Alba). It is the first row of the A-Z list. It existed before v0.55.0. Fix the name or exclude the row in the posturi export.

## Verified limits
- openapi.ro cannot feed the published data: its terms forbid redistribution (checked 2026-11-04).
- No free, republishable source of email or website for `S` or `D` records was found on 2026-11-04. ANAF gives a fiscal phone only; ONRC `WEB` is filled in 0.25% of the sampled rows. termene.ro, listafirme.eu, sicap.ai and RECOM could not be verified (403 or no connection).
- data.gov.ro ignores HTTP Range headers. To sample a file, read a stream and stop it (`curl | head -c`).
- The ANAF parent link (ordonator principal de credite) is one level deep. It gives no middle level
  (for example, no ISJ between a school and the ministry). A middle level must come from grouping (family,
  county), not from ANAF.
- "A.B.A." (Administrația Bazinală de Apă) in the posturi names (Opus, 2026-11-04): only 3 posturi names use this spelling, and all three
  name SGA units, so they stay in the posturi review queue. A change in `fold` would alter the folding of every initialism in the dataset.
- The active-only posturi deploy SQLite (`webapp-php/posturi.sqlite`) cannot feed the employer export: 4,807 of 5,901 employers have no posting in it, so no county. Use a full export (2026-11-02, DATA-ORG-01).

- ONRC `exact_elsewhere` and `ambiguous` matches never enter by rule (Opus, 2026-11-05). 13 generic `D` records matched the CUI of one body in another county, and all
  are wrong: 8 "SPITALUL ORASENESC" (`D0f8380d1` Arges, `D2a7aa9d6` Cluj, `D486d4cf3` Bacau, `D9160515f` Vrancea, `D97fb74ec` Satu Mare, `D99649007` Olt,
  `Dd71046bb` Prahova, `Dfba6611a` Brasov) against the Videle hospital (CUI 25040361, record `Da56aef25`), and 5 "ADMINISTRATIA DOMENIULUI PUBLIC" (`D513b336e` Arges, `D751068ae` Cluj,
  `D7577ebdf` Hunedoara, `D892d2100` Ilfov, `Dc2fe7efa` Mures) against ADP Oradea SA (CUI 7997507, record `Dd0e06565`). Do not merge them. In a sample of 30
  `exact_elsewhere` cases, 14 were wrong; the specific names (company names) are right, the generic local names are wrong.

## Later / misc / unfilled
- [ ] create /llms.txt, then let ~/devbox/gov2/gov2.ro know, to update their llms.txt - or submit an issue to [gov2-ro/gov2-alpha-sunrise](https://github.com/gov2-ro/gov2-alpha-sunrise)