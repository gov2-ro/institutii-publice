# Spec: data correctness and a dense explorer, version 1

Status: prepared for implementation handoff, 2026-10-25.
Brief: [../briefs/explorer-quality-v1.md](../briefs/explorer-quality-v1.md).

This spec defines the first release after the UX and data audit.
It preserves the accepted [state-structure spec](structura-statului.md).
The broader comparative-research proposals remain future work.
The additive schema changes below supersede the old brief's restriction against changing compact rows.

## Outcome

Users can find, inspect, share and export institution records with fewer navigation steps.
Unresolved matches remain visible. They do not transfer contacts to an arbitrary institution.
Results remain dense. Overview navigation supports discovery without becoming a mandatory landing page.

## Constraints

- Keep the static page, vanilla JavaScript and existing consolidation pipeline.
- Add no runtime dependencies, framework, build step or database.
- Keep Romanian UI text, existing four views, filters, multi-parent placement and URL compatibility.
- Preserve the curated constitutional mapping and its disputed-placement notes.
- Preserve source-only records. Missing ANAF correspondence does not make a record noise.
- Preserve existing ANI umbrella exclusions and minimum declaration-count rules.
- Keep policy classification separate from claims about legal form, ownership or current legal status.
- Do not scrape or download new source data for this release.
- Do not alter unrelated working-tree changes or commit local source inputs and screenshots.

## Baseline and interpretation

The local audit snapshot contains 25,343 records and 13,485 distinct CIFs.
It has 2,179 website URLs, 2,581 flagged duplicate candidates and 3,296 ANAF roots.
These are record counts, not verified counts of current legal entities.
The activity log records the measurements and source limitations.

Matching corrections may change record counts and source combinations.
Record those changes with explanations. Do not preserve incorrect links to retain the baseline count.
ANAF input identities and parent references must remain intact on unchanged inputs.

## 1. Resolve matches conservatively

Apply ambiguity handling to exact, canonical, unit and token matching.
Several candidates with the same name do not establish a unique identity.
An existing locality hint may resolve a match only when it distinguishes one eligible candidate.
Use locality evidence in token matching too.

Retain discriminating geographic names in identity decisions.
For example, DSP Ilfov and DSP București can both have office addresses in București.
Office county alone cannot distinguish those organisations.

For token matching, check kind and numeric compatibility before selecting the best eligible candidate.
Keep the existing acceptance thresholds unless a separately justified change is needed.
Equal best scores with unresolved identity evidence must not produce a confident merge.
Use a documented numerical tolerance for float equality.
Do not introduce an uncalibrated probability or a new score-margin threshold.

Keep an ambiguous source row as its own record.
Retain candidate links only at the existing weak or merge thresholds; lower overlaps do not establish duplicate candidates.
Retain every tied eligible candidate's CIF, tier and score in optional `match_candidates` output.
Sort candidates deterministically. Preserve their evidence when ANI standalone rows are grouped.
Keep `possible_duplicate_of` for an existing single weak candidate.
Do not assign an arbitrary single duplicate target to a multiple-candidate ambiguity.

The compact explorer row carries candidate CIFs in optional `mc`.
The master CSV exposes them in a documented `match_candidate_cifs` column.
The detail dialog lists candidate names and CIFs with links to their records.
Label these records as unresolved matches. A matching score is not a probability of correctness.

### Required examples

- DSP București, CIF `4400956`, must not receive the Ilfov ROePAS contact fields or website `dspilfov.ro`.
- DAS Dorohoi, CIF `4392462`, must not receive the Botoșani ROePAS website `dasbotosani.ro`.
- Correct targets include DSP Ilfov `11445640` and DAS Botoșani `15305089` when evidence resolves the match.
- If evidence remains insufficient, preserve the source row and its candidates without merging.
- Duplicate generic school names in different UATs must remain distinct.
- An unresolved exact/canonical tie must not silently select the first ANAF row.
- A numbered institution must not lose an eligible match because an incompatible number was examined first.

## 2. Correct the confirmed category errors

Match ancestor classification terms at word boundaries.
`culturii` must not match inside `agriculturii`.
The audited agriculture umbrella contains 32 wrongly assigned culture records.
Use this as a comparison baseline, not a permanent fixture count for all future inputs.

Prevent an internal abbreviation fragment such as `S A` from establishing company status.
`D S V S A ALBA LABORATOR SANITAR VETERINAR` belongs in the agriculture/veterinary category.
Retain valid company-name cases in regression fixtures.

Recognise `MUNICIPIULUI MANGALIA` consistently in local-authority matching and classification.
Keep the county-council versus municipality distinction.
Defer other curated category changes that need new evidence, including IDPSAR, to follow-up work.

## 3. Repair state-tree visibility and counts

Traverse all descendants, including descendants below attached roots.
Deduplicate records by identity within subtree counts.
Preserve appearance under both parents when rendering a record with two ANAF parents.

Search `#v=stat&q=39847338` must reveal DGRFP Brașov under the complete visible ancestor path.
The path includes MF and MF acțiuni generale (`8609468`).
The same record must remain visible when focused on MF (`4221306`).
Exercise all eight children of MF acțiuni generale.
Keep the existing root-reachability check and add a descendant-visibility check.

Render the optional note in each `STATE_MEMBERS` tuple.
Show the note in the detail dialog and wherever its structural placement is presented.
CNCAN `10792013` must expose the note already present in metadata.
Do not resolve disputed placements by changing the curated mapping.

Counts must state their scope.
A focused node shows its matching unique-record count as well as any global count that remains visible.
Virtual-group counts include their descendant records. Record-node subordinate counts exclude the record itself.
Family bundles and virtual nodes are navigation groups, not additional institutions.

## 4. Keep the interface dense and responsive

Keep the results visible on initial load.
Retain compact tables/rows, source badges and access to record details.
Do not replace results with large cards or a mandatory portal landing page.
Borrow UK grouping and relationship wording, not its sparse layout.

On narrow screens, keep search and access to secondary filters visible.
Place secondary filters inside a keyboard-accessible disclosure.
Show an active-filter count when the disclosure is closed.
Keep reset reachable and ensure that the source dropdown fits inside the viewport.

At 390 x 844, the collapsed header must occupy at most 180 CSS pixels.
At 320 x 844, it must occupy at most 200 CSS pixels.
Long tab labels may scroll inside the tab strip. They must not widen the document.
No document-level horizontal scrolling is allowed at the required viewport widths.
Do not remove useful record fields solely to meet a density target; use expansion or details where necessary.

### Optional overview navigation, included in this release

Provide one compact, collapsible overview. Keep it closed initially.
Expose two groups: `Structura statului` and `Tipuri de instituții`.
Use the existing top-level state groups and existing families.
Show at most eight family shortcuts initially, with access to all families through the existing view/filter.
Use text links or small controls with counts. Avoid oversized icons and nested scrolling lists.

Overview counts describe the entire dataset and use unique records.
Label the overview `Explorează toate instituțiile`.
Explain that choosing an overview shortcut resets filters.
A state shortcut clears filters and opens its focused node in the state view.
A family shortcut clears filters, selects that family and opens the list view.
Update URL state through the same navigation mechanism as existing controls.
Overview expansion itself is transient UI state.

This overview does not introduce new legal categories or ownership claims.
India's screenshots in `tmp/india.gov.in-directory/` are visual references, not interaction specifications.

## 5. Make search, loading and details reliable

Normalise diacritics, whitespace, punctuation and hyphen variants consistently for both query and searchable text.
`Bistrița-Năsăud` and `Bistrita Nasaud` must return the same record IDs.
Preserve CIF, website and alias search.

Show a visible, accessible loading state while data loads.
On failure, explain the problem in Romanian and offer retry.
Do not show visitors a Python command.
Handle HTTP and JSON failures without duplicating event handlers or leaving partial interactive controls.

Give every compact row its full record ID in field `i`.
Support an optional `id` hash parameter alongside existing filters, view and focus.
For example: `#v=list&id=A4400956`.
Opening a record preserves the current browsing state and adds its ID to the URL.
Reloading a record URL opens its detail dialog.
Support source-only IDs as well as ANAF IDs.

Browser Back restores the previous record or closes the dialog as appropriate.
Closing a directly loaded dialog removes `id` without navigating away from the explorer.
Closing by button, Escape or backdrop must have consistent URL behavior.
An unknown record ID shows a useful message and preserves the valid browsing state.
Keep all existing hashes without `id` working.
Provide a `Copiază linkul` action with success/failure feedback.
Give the dialog an accessible name and preserve sensible focus on open and close.

Existing source-only IDs remain stable for unchanged inputs.
This release does not promise persistent identity across future ANI county/name corrections.
A durable identity registry is follow-up work.

## 6. Expose uncertainty and export the selection

Add separate filters for records without an ANAF match and records needing duplicate/match review.
Reuse the existing without-ANAF source option if it remains easy to discover.
Review records include existing `possible_duplicate_of` values and multiple-candidate ambiguities.
Persist the review filter in optional hash parameter `review=1`.
Reset and all existing facets must respect this filter.

Offer `Descarcă CSV` for the current selection.
In list, family and locality views, export every matching record, including records beyond the rendered page.
In a focused state view, export the intersection of matching records and the focused subtree.
Export each ID once, even when a record appears under two parents.
Context ancestors that do not match must not enter the export.

Export these columns:
`id`, `name`, `category`, `family`, `county`, `uat`, `cif`, `parent_cifs`, `website_url`,
`email`, `phone`, `sources`, `possible_duplicate_of`, `match_candidate_cifs`, `declaratii_count`,
`procedures_count`, `online_procedures_count`.
Use UTF-8, correct CSV quoting and a documented representation for multi-value cells.
Keep zero distinct from unknown. Treat source text as text when producing spreadsheet-oriented exports.

Preserve known zero values for both procedure fields in compact rows.
The audited full JSON contains 2,074 records with zero procedures; all currently lose that fact in the explorer.
Show an ANI explanation: totals count declarations, not employees or distinct institutions.
Use `înregistrări` for aggregate counts while identity remains unresolved.

## 7. Publish minimal dataset provenance

Add backward-compatible metadata describing the generation time and each input file.
Record relative path, byte size and SHA-256 for each input used.
Surface ANI exports that reach the 10,000-row cap in metadata and a concise dataset-information panel.
Expose source dates only when explicitly supported by the source or its recorded export metadata.
Label date meanings. Generation time and file modification time are not institution-verification dates.
Do not infer active status or website health from a source badge or CIF.

Document the compact schema additions and how to obtain or copy the ignored inputs.
Retain the tracked master CSV and the existing generated-output/symlink arrangement.
Generation timestamps may vary; unchanged inputs must still produce deterministic CSV and matching decisions.

## Validation

Use small, meaningful fixtures for ambiguity, locality, jurisdiction, numeric eligibility and classification.
Exercise deterministic decisions with at least two hash seeds.
Use the standard library test runner unless an existing suitable runner is already available.
Browser checks may use available Playwright/Chrome without adding runtime dependencies.

Check widths 320, 390, 768, 900, 901, 1,024, 1,280 and 1,440 CSS pixels.
Check all four views, source combinations, reset, an empty result and more than 100 matching records.
Check search equivalence by record IDs, not only by result counts.
Check old hashes, record hashes, source-only records, peer navigation, Back, Escape and copy-link feedback.
Check CSV selection against data identities and verify known zero values.
Check loading and retry with deliberately delayed and failed requests.
Check keyboard operation, visible focus and overflow in both colour schemes.

Run consolidation on the local inputs and compare the before/after summary.
Explain changed matches and counts. Check unique output IDs and resolving parent/candidate references.
Re-run the root check and verify all eight filtered attached-root descendant paths.
Capture representative desktop and phone screenshots for review.
Report measured outcomes, assumptions and remaining limits in the activity log.

## Deferred

- Automatic reconciliation of source-only records across sources.
- ONRC identity resolution, ownership research and inferred parents.
- A redesigned legal/function/ownership classification system or new hierarchy facts.
- A complete field-level claim store, durable identity registry and historical entity lifecycle model.
- Full CPOV/ORG conformance, JSON-LD exports and COFOG mappings.
- Live website verification, scraper refresh rules and new ANI exports.
- Purpose-statement enrichment, internal staff directories, maps, treemaps and new visualisations.

Keep these in the backlog. Do not turn them into implicit requirements for this release.
