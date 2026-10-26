# Implementation brief: adopt the gov2 design system (DS)

Status: brief ready, 2026-10-26. Blocked until the owner announces a DS release.
Inputs: the compatibility report in the DS repo (`docs/compat-analysis.md`, section org.gov2.ro), and the DS
answer of 2026-10-26 (activity log).

## Owner decisions (2026-10-26)

- **Fonts:** use the DS fonts (Inter, Fragment Mono). No local exception. Remove IBM Plex Sans, Instrument Sans
  and JetBrains Mono from `explorer/assets/fonts/`.
- **Text and control sizes:** use the DS type scale and control sizes. No local compact variant.
- **Dark mode:** keep it. The DS has none yet; the owner approved a shared dark scheme
  ([DS #1](https://github.com/gov2-ro/gov2ro-design-system/issues/1)). If the release has it, use it.
- **Tricolour title:** the local sweep goes. The owner requested a shared title treatment
  ([DS #2](https://github.com/gov2-ro/gov2ro-design-system/issues/2)). Until it exists, use `.g2-wordmark` and
  `.g2-ro-corner`. The owner accepts a WCAG 2.2.2 deviation for the sweep: it loops with no pause control,
  because it is slow and small. Do not report it as a checklist failure.

## Preconditions

- The owner announced the release `vX.Y.Z`. A local tag in `~/devbox/gov2/gov2ro-design-system` is enough:
  the owner develops the DS locally and pushes now and then (owner, 2026-10-26).
- Prefer a release that includes ADR 0005 (self-hosted DS fonts, no Google Fonts `@import`). With the `@import`,
  the page makes third-party requests again; the 2026-10-26 styling round removed them on purpose.
  If the release still has the `@import`, stop and ask the owner.

## Prompt for the Sonnet session

Fill in `X.Y.Z`. Keep the rest.

````text
Adopt the gov2 design system (DS) in this project, at version X.Y.Z.
The DS is at ~/devbox/gov2/gov2ro-design-system. Read docs/briefs/ds-adoption.md in this project first.

1. In the DS, read docs/project-block.md, COMPONENTS.md, GUIDELINES.md, CHANGELOG.md,
   the section for this project in docs/compat-analysis.md, and the section
   "Known transition issues" in docs/connect-a-project.md.
2. Add the block from docs/project-block.md to AGENTS.md and CLAUDE.md in this project.
   Values: version X.Y.Z; gov2.css path explorer/assets/gov2.css; project styles in the inline
   <style> of explorer/index.html; prefix org-. Keep the rest of the block as it is.
3. Copy gov2.css from the DS tag vX.Y.Z into explorer/assets/gov2.css:
   git -C ~/devbox/gov2/gov2ro-design-system show vX.Y.Z:gov2.css > explorer/assets/gov2.css
   If the release has self-hosted font files, copy them as the DS documents. Do not edit the copies.
4. Apply the owner decisions in docs/briefs/ds-adoption.md: DS fonts, DS sizes, dark mode kept as
   --g2-* overrides in @layer app (link DS issue #1), tricolour title removed (link DS issue #2).
5. Use a DS component where one fits. Where the DS has no component, build a local version
   with the class prefix org- and open a ds-proposal issue, as the block says.
6. Make a screenshot of each view: #, #v=list, #v=stat, #v=fam, #v=loc&k=CJ, and the record dialog.
   Take each in light and dark, at 1280 px and 375 px. Check each against "Review a page"
   in GUIDELINES.md. Measure the contrast in the browser, not only in the tokens.
7. Follow the process of this project for the backlog, the activity log, commits and tags.
   Do not run scripts/publish_pages.sh. The owner publishes after the review.
8. Send a short summary to the DS session (ListAgents, then SendMessage to g2-ds): the version,
   the issues that you opened, the checklist items that fail, and the problems that you found.
````

## Work items (from the compatibility report)

- Link `assets/gov2.css` before the inline style. Put the inline style in `@layer app`.
- Remove the local `:focus-visible` rule. Test focus on `.seg`, `.cat-tab`, list rows, map regions and dialogs.
- Replace the local tokens with `--g2-*` (RGB channels). Radius 0. No decorative shadows.
  Keep the map ramp (`--m0`…`--m5`) local; rename it with the `org-` prefix.
- Header: `.g2-header`, `.g2-wordmark`, `.g2-ro-corner`. Keep the sticky header and the `--top-h` measurement.
- Add a `.g2-footer`. Content: source repo, data generation time, licence. Ask the owner if unsure.
- Buttons and fields: `.g2-btn`, `.g2-btn.g2-secondary`, `.g2-input`. Flags: `.g2-tag` with `data-tone=warning`.
- Links: use the DS link roles (`.g2-link-quiet`, `.g2-chip`) where GUIDELINES.md permits no underline.
- Local components with the `org-` prefix: choropleth and legend, multi-select filter, filter bar, tree, tabs,
  breadcrumbs, data table, source badges, record dialog. Breadcrumbs and data tables meet the DS promotion rule
  (stiri and org); open a ds-proposal issue for each.

## Acceptance

- `explorer.reachableRoots()` equals `explorer.expectedRoots()`. No page errors. No horizontal overflow at 375 px.
- No third-party request on load (check the network panel), unless the owner accepted the `@import`.
- Every text pair on its real surface meets 4.5:1 (3:1 for large text), in light and dark.
- `python3 -m unittest discover -s tests` passes.
- Measured row height and filter-area height are in the activity log. The DS sizes make the list less dense
  than the 2026-10-26 baseline (about 53 px per row at 1,280 px); record the new value.
