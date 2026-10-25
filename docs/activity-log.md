# Activity log

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
