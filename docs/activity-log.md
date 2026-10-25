# Activity log

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
