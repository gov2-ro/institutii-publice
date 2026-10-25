# Implementation brief: data correctness and a dense explorer, version 1

Status: ready for implementation handoff, 2026-10-25.
Spec: [../specs/explorer-quality-v1.md](../specs/explorer-quality-v1.md).

## Read first

1. Read `AGENTS.md` and `CLAUDE.md`.
2. Read this brief and its spec.
3. Read `docs/BACKLOG.md` and the audit/research entries in `docs/activity-log.md`.
4. Read `docs/specs/structura-statului.md` for the existing accepted hierarchy.
5. Inspect the three screenshots in `tmp/india.gov.in-directory/` if they are available.

The screenshots illustrate browsing routes. The owner prefers dense results and rejected the UK layout's low density.
The current state-structure brief describes completed work. Do not implement that old brief again.

## Preflight

- Inspect the working tree. Preserve existing changes, including README, memory files and the owner's AGENTS.md.
- Capture a consolidation baseline before changing matching or category rules.
- Confirm these ignored inputs exist:
  - `docs/reference/Lista_EP_portal_01102026.xlsx`
  - `docs/reference/Registrul-National-al-Institutiilor-Publice-din-Romania.pdf.csv`
  - `data/roepas/institutii.json`
  - `data/declaratii-integritate/Lens Visualization*.csv`
- Use the same checkout where possible. A new clone/worktree does not automatically contain ignored inputs or screenshots.
- If inputs are missing, continue with fixtures and independent UI work. Report the missing full-data validation explicitly.
- Do not rely on audit scripts or browser artifacts under `/tmp`; those files are temporary and not handoff dependencies.

## Implementation order

1. **Matching and classification.** Add regression fixtures, fix arbitrary ties and the confirmed category errors.
   Add candidate evidence to full output, CSV and compact rows. Preserve unresolved source records.
2. **Tree correctness and schema.** Fix recursive descendant visibility, note rendering and scoped counts.
   Add compact record IDs and preserve known zeros. Add minimal dataset provenance.
3. **Dense interaction.** Fix responsive filters, search normalisation, loading/retry and record URL navigation.
   Add uncertainty filtering and selection export.
4. **Discovery.** Add the compact optional overview using the existing state groups and families.
5. **Acceptance.** Run fixture tests, full-data checks and browser scenarios. Record results and screenshots.

Finish the bounded spec. Do not stop after the first visible improvement.
Keep changes reviewable by stage. Follow the repository's commit/tag rules when making commits.

## Likely files

- `scripts/consolidate.py`: linking, category rules, candidates, compact schema, CSV and metadata.
- `explorer/index.html`: layout, traversal, details, filters, URL state, loading and exports.
- `tests/`: small regression fixtures and checks introduced for confirmed failures.
- `docs/BACKLOG.md` and `docs/activity-log.md`: completion status, decisions and measurements.
- `AGENTS.md` / `CLAUDE.md`: keep compact-schema and test commands accurate if changed.

The spec explicitly authorises its additive schema and URL changes.
Do not treat those documented changes as an unexpected schema decision requiring another approval.
Choose routine code organisation and styling details within the spec.
Raise a concrete conflict only if implementation would change a preserved invariant, dependency or deferred scope.

## Acceptance evidence

- Wrong contact transfers to DSP București and DAS Dorohoi are removed or remain unresolved without merging.
- Ambiguous exact/canonical/token candidates never select the first row without distinguishing evidence.
- All eight MF acțiuni generale children remain visible under filtered ancestor paths.
- Existing 3,296-root reachability still passes on the audited inputs.
- Hyphenated and space-separated county queries return identical record IDs.
- No document overflow at the specified widths. Collapsed phone header meets the height limits.
- Record links survive reload and browser navigation, including records without CIFs.
- Filtered CSV includes all selected records, deduplicates identities and preserves zeros.
- Dataset dates and truncation warnings describe evidence without implying verification.
- Desktop/phone screenshots demonstrate dense rows and optional overview navigation.
- Before/after data changes are explained. The backlog and activity log are updated.

## Report back

State what changed and why. Include test commands and outcomes.
Give before/after counts, notable changed links and screenshots of the final interface.
State remaining limitations. Mark only completed backlog items as done.

## Prompt for the implementation session

```text
Implement docs/briefs/explorer-quality-v1.md and its linked specification in this repository.
Read AGENTS.md, CLAUDE.md, docs/BACKLOG.md and docs/activity-log.md first.
The existing state-structure v1 work is complete; preserve its constitutional mapping.
Implement the new brief end to end, starting with matching correctness and regression fixtures.
Keep the static vanilla-JS architecture and dense results. Use India's screenshots for browsing ideas;
do not copy the sparse UK layout or add a mandatory landing page.
The spec authorises its documented schema and URL additions. Make routine choices autonomously.
Preserve unrelated working-tree changes and keep ignored source inputs/screenshots out of commits.
Run the full-data and browser acceptance checks. Explain changed counts and unresolved limitations.
Update the backlog and activity log, then report the implementation and validation evidence.
```
