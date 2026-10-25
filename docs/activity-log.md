# Activity log

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
