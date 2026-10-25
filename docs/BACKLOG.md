# Backlog

Statuses: `[ ]` open, `[~]` in progress, `[x]` done, `[-]` dropped (with the reason).

## Implementation handoff
- [x] Data correctness and dense explorer, version 1 (built and accepted 2026-10-25):
      [spec](specs/explorer-quality-v1.md), [implementation brief](briefs/explorer-quality-v1.md).
      Includes conservative matching, confirmed category fixes, tree visibility, dense responsive filters, record links,
      review filters, CSV export, loading feedback, minimal dataset provenance and compact overview navigation.
      This is the bounded next release. The spec lists deferred research and data-enrichment work explicitly.

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

## Explorer: landing page and maps (brief: briefs/explorer-landing-maps.md)
- [x] Landing view `acasa`, county choropleth, county profile with UAT map and seat/municipii/orașe/comune groups.
- [ ] 12 ANAF UAT roots have no map shape (e.g. Orasul Victoria, Orasul Balan, Comuna Saniob; Orasul Stei has null
      geometry). București is one polygon, so sectors have no shape. A SIRUTA join would remove the name matching.
- [-] ANAF UAT root names look wrong for two sector CIFs. Dropped: `4192545` JUDETUL ILFOV and `4267117` MUNICIPIUL
      BUCURESTI are correct. Their seats have București sector addresses; the UAT label is the seat's location.
- [x] București sectors and same-name duplicates (brief: briefs/sectors-duplicates.md).
- [ ] Same-name merge needs no review step yet. 323 groups merged automatically; sample of 14 looked right.
      Add a review list if a wrong merge turns up. Spelling variants ("ADMINISTRATIE" vs "ADMINISTRARE")
      and ANI sub-units ("ANAF … ACTIVITATE ECONOMICA") remain separate, under "de verificat".

## Data quality
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
