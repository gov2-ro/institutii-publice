# Brief: "Structura statului" view, version 1

For: Sonnet. Spec: [../specs/structura-statului.md](../specs/structura-statului.md). Read the spec first, and
read `CLAUDE.md` for the data flow and the compact row schema.

## Tasks
1. **`scripts/consolidate.py`**
   - Add `STATE_TREE`: the virtual nodes and the CIF mapping of the spec, each entry with an optional `note`.
     Put it next to `FAMILY_HEADS`.
   - In `write_explorer_data`, add a `state` key to `metadata.json`: the virtual nodes (id, label, parent,
     note) and the assignment of each mapped CIF to a node. Also add the attach-under rules (MF – acțiuni
     generale under MF; AMRSP under Municipiul București). `rows.json` does not change.
   - In `report`, print the number and the names of central roots in "Neclasificate".
2. **`explorer/index.html`**
   - Replace the tab "Autoritate → subordonate" (`data-view="auth"`, `renderAuthTree`) with "Structura
     statului" (`data-view="stat"`). Reuse `branch`, `renderRecords`, `bundleItems` and `leafTable`.
   - Build the local-administration branch in the page: county → county record → UATs (municipii, orașe,
     comune) → children. București: the municipality, then the sectors.
   - Split a family group with more than 60 members by county.
   - Add focus on a node, with a breadcrumb.
   - Add the breadcrumb and the family siblings to the detail dialog (`showDetail`).
   - Show "matches / total" on each node when a filter is active. When a filter leaves at most 50 matches,
     open the path to each match.
   - Keep the view, the focused node and the filters in the URL hash. Restore them on load and on `hashchange`.

## Acceptance checks
- Run `uv run scripts/consolidate.py`. Compare the stderr summary with the summary before the change. The
  counts must be the same, plus the new "Neclasificate" line. That line must list exactly 2 roots (IDPSAR,
  Registrul Urbaniștilor) on today's data.
- In the browser, every one of the 3,296 ANAF roots is reachable in the new view. Count it in the console:
  the number of distinct root CIFs rendered (or reachable) equals the number of rows with `f` and no `p`.
- MEC → Liceu tehnologic opens as county groups, not as one table.
- The filter "Cluj" + "Sănătate" shows the DSP Cluj under *Guvernul › Ministere › Ministerul Sănătății*,
  with dimmed ancestors.
- Opening `#v=stat&n=4266456` shows the Ministerul Sănătății in focus, with the breadcrumb.
- The other three views behave as before.

## Rules
- No new dependencies, no build step (`CLAUDE.md`).
- Stop and ask if a step would change the spec. Examples: a different top layer, or moving a body to another
  node. Disputed placements stay as the spec gives them.
- Report what you measured and what you assumed. Add an entry to `docs/activity-log.md`. Flip the backlog items
  of this brief to `[x]`.
