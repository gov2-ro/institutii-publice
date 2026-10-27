# Brief: landing v2 and the page "Cum e organizat statul"

For: Sonnet. Spec: [../specs/landing-v2-organizare.md](../specs/landing-v2-organizare.md). Read the spec first,
then `CLAUDE.md` (explorer, DS rules) and the DS `COMPONENTS.md` (Fields, Tile, Buttons).
The owner accepted all five recommendations of spec section 4 (2026-10-27). Build them as written.

## Tasks
1. **`explorer/index.html`, landing (`renderHome`)**
   - Add the sections of spec section 2 in that order: search, "Unde locuiești?", "De ce ai nevoie?",
     "Cum e organizat statul", then the type tabs and the county map of today.
   - The landing search writes to the same `S.q` as the result search, and opens the list view.
     Do not add a second search state.
   - Add the constants `HOME_TASKS` (tile title, icon id, family labels) and `HOME_BRANCHES` (card title,
     icon id, sentence, state node ids, select source). Put them next to `HOME_HIDDEN`.
   - Resolve family labels at render time. Skip an absent label. Log the absent labels once with
     `console.warn('[org] HOME_TASKS: absent family', label)`.
   - Build links with `browseHref` and `browseLink`, as the current landing code does, so that the website
     choice and the filters carry over.
   - Keep the county in `localStorage` key `org-home-county`. Wrap every read and write in try/catch.
   - Add one SVG `<symbol>` sprite for the icons (about 16). Line style, 24 × 24, `currentColor`.
   - Styles in `@layer app`, class prefix `org-`. Use `.g2-tile`, `.g2-input`, `.g2-field`, `.g2-btn`.
2. **`explorer/organizare.html`** (new)
   - Same `<head>` layers, fonts, `data-g2-scheme="auto"`, header and footer as `index.html`.
   - The content of spec section 3.1, in Romanian, under the rules of section 3.2.
   - The diagram as HTML and CSS: a grid of groups on desktop, one column on phones. One colour token per group,
     defined for both schemes. Do not show the relationship by colour only: add a text label or a line style.
   - Every box links into `index.html` with a hash. Check each hash opens a non-empty view.
   - Add the link to the menu of `index.html` and under the cards of landing section 4.
3. **Sources.** Find the legislatie.just.ro link for Legea 304/2022. Open the OUG 109/2011 link and check its
   title. For each article that the text cites, open the article and check that it says what the text says.
   If a claim has no checked source, remove the claim and list it in the activity log.

## Do not
- Do not change `consolidate.py`, `metadata.json` or `rows.json`. All data that the spec needs is already there.
- Do not edit `explorer/assets/gov2/`.
- Do not add a dependency or a build step.

## Acceptance checks
- `python3 -m unittest discover -s tests` passes. The JavaScript syntax check passes.
- `explorer.reachableRoots()` equals `explorer.expectedRoots()`.
- Each `HOME_TASKS` and `HOME_BRANCHES` link opens a non-empty view on today's data. Report the absent labels.
- With county Cluj chosen, every tile link carries `k=Cluj`. After "Șterge", no link carries `k`.
- With `localStorage` blocked, the landing page renders and works.
- Empty hash, `web=0`, legacy view links, record links, refresh and Back work as before.
- Check the landing page and `organizare.html` at 320, 390, 768, 1,024 and 1,440 px, in both schemes.
  No horizontal scroll. Touch targets are at least 44 px. Report the landing height at 390 px (before and after).
- Keyboard: every select, button and tile link is reachable with Tab and has a visible focus.
- Screenshots of both pages, desktop and phone, for the owner.

## Report
- What you measured and what you assumed.
- The activity-log entry and the backlog items, as `CLAUDE.md` asks. Do not publish; the owner reviews first.
