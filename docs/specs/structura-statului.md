# Spec: "Structura statului" view

Status: accepted, 2026-10-25. Brief: [../briefs/structura-statului-v1.md](../briefs/structura-statului-v1.md).

## Goal
The explorer shows the state as one tree: the branches of power at the top, then the ANAF hierarchy, then
local administration. The view replaces the tab "Autoritate → subordonate".

## What the data gives (measured 2026-10-25, 25,346 records)
- The ANAF parent link is the *ordonator principal de credite*. The link is one level deep: every parent is a
  root, and no record is deeper than 1. There are 3,296 ANAF roots: 73 central bodies, the rest UATs.
- No ANAF record stands for "Parlament", "Guvern" or "Președinție".
- There is no middle level. The 42 DSPs sit flat under the Ministerul Sănătății (214 children). The Ministerul
  Educației has 6,036 children.
- 5,657 records (mostly schools) have two parents: a UAT and the Ministerul Educației.
- 11,861 records have no ANAF match and no parent. About 3,544 of them can get a parent from their family
  (phase 2, see the backlog).

## Decisions
1. **The top layer follows the Constitution** (titles and chapters), not the "who controls it in practice"
   view. A body whose place is disputed gets a short note in the mapping. *Why:* the Constitution is a citable,
   stable reference. The cost of the alternative: a "control" view needs research per body and changes with
   each government.
2. **The new view replaces "Autoritate → subordonate".** The new tree contains every node of the old tree.
3. **Inferred parents (by family) are phase 2.** Version 1 shows only ANAF parents.
4. **Local administration is part of this view** (Județ → UAT → subordinates). Only this view shows the
   UAT → subordinates level.
5. **The mapping is a Python constant in `consolidate.py`** (`STATE_TREE`), keyed by CIF, next to
   `FAMILY_HEADS`. *Why:* CIFs are stable across ANAF releases, and `data/` is not in git. The script writes the
   resulting virtual nodes to `metadata.json`. `rows.json` does not change.
6. **No central root is hidden.** An ANAF root with no mapping that is not a UAT goes to "Neclasificate".
   `consolidate.py` prints the number and the names of these roots. That output is the regression check for a
   new ANAF release.

## Tree
Virtual nodes are in *italics*. A CIF is an ANAF root; its ANAF children hang under it as today.

Display update, 2026-10-26: Guvernul shows SGG, each ministry, and Organe de specialitate at the same level.
The display and ministry breadcrumbs skip Ministere. Metadata retains that group for counts and existing links.

- *Parlamentul* (Titlul III, cap. I)
  - Camera Deputaților `4265795` · Senatul `4284070` · Consiliul Legislativ `7901650` (art. 79)
- *Președintele României* (Titlul III, cap. II)
  - Administrația Prezidențială `4283732`
- *Guvernul* (Titlul III, cap. III; cap. V secț. 1)
  - Secretariatul General al Guvernului `4283422`
  - *Ministere*: MAE `4266863`, MAI `4267095`, MADR `4221187`, MApN `11424532`, MC `4192812`,
    MDLPA `26369185`, MEDAT `24931499`, MEC `13729380`, ME `43507695`, MF `4221306`
    (with "Ministerul Finanțelor – acțiuni generale" `8609468` as a child of MF), MIPE `38918422`,
    MJ `4265841`, MMAP `16335444`, MMFTSS `4266669`, MS `4266456`, MTI `13633330`
  - *Organe de specialitate ale administrației centrale*: ANRSPS `26288978`, ANSVSA `16277408`,
    AAAS `11795573`, ANRP `22464311`, AMEPIP `49199357`, CNCAN `10792013`, ANL `11795581`,
    Secretariatul de Stat pentru Culte `26429279`, SSRMLRC `4266499`
- *Autoritatea judecătorească* (Titlul III, cap. VI)
  - ICCJ `4340587` · Parchetul de pe lângă ICCJ `4364748` · CSM `16973795`
- *Curtea Constituțională* (Titlul V) — `4265850`
- *Curtea de Conturi* (Titlul IV, art. 140) — `4265922`
- *Avocatul Poporului* (Titlul II, cap. IV) — `9766550`
- *Consiliul Economic și Social* (Titlul IV, art. 141) — `10464660`
- *Autorități administrative autonome* (art. 117 alin. 3; under parliamentary control)
  - AEP `16460641`, CNA `4266189`, CNSAS `12932750`, ANI `22838777`, Consiliul Concurenței `8844560`,
    ANRE `11514848`, ANCOM `14751237`, ASF `31588130`, ANSPDCP `18073706`, CNCD `14818035`,
    ANRMSGDC `50306805`, CNSC `20329980`, Consiliul de Monitorizare `36401992`
- *Apărare și siguranță națională* (art. 118–119; CSAT coordinates)
  - SRI `4204291`, SIE `10668016`, STS `4267230`, SPP `4283635`, ORNISS `15085226`
  - Note: MApN and MAI stay under *Guvernul / Ministere*.
- *Servicii publice autonome* (under parliamentary control)
  - SRR `8296093`, SRTV `8468440`, AGERPRES `4266448`, ICR `15726657`
- *Academii și instituții publice autonome*
  - Academia Română `4192472`, AOSR `5091859`, ASSN `33354101`, ARACIS `18476245`, CNAS `11697800`
- *Administrația locală* (Titlul III, cap. V secț. 2)
  - *Județ* (one node per county, alphabetical; București last)
    - the county record ("JUDETUL X") first, as "Consiliul Județean", with its children
    - then the UATs: municipii, then orașe, then comune; each UAT with its children
    - București: Municipiul București `4267117`, then Sectoarele 1–6
  - Autoritatea Municipală de Reglementare a Serviciilor Publice `26246549` is a child of
    Municipiul București.
  - A root is a UAT when its category is "Administrație locală", or when its name starts with
    MUNICIPIUL/ORAS/COMUNA/JUDETUL/SECTORUL/PRIMARIA (this catches "MUNICIPIULUI MANGALIA").
- *Neclasificate* — every other ANAF root. Today: Institutul de Drept Public și Științe Administrative
  `25838704`, Registrul Urbaniștilor `17244352`.
- *Fără corespondent ANAF* — records with no CIF, as in the current view.

Disputed placements, to check against the founding law: CNCAN (Guvern vs. autonomous), ANL (MDLPA
coordination), CNAS (autonomous vs. MS), ARACIS, ICR (parliamentary control vs. MAE). Each entry in
`STATE_TREE` carries a `note` field for this.

## Large nodes
A node with many children stays browsable as follows:
1. Children group by family when the node has more than 12 children (`bundleItems`, as today).
2. A family group with more than 60 members splits by county. Example: MEC → Liceu tehnologic → Cluj.
3. A record with two parents appears under both, as today.

## Explorability (version 1)
- **Focus on a node.** Each node has a "focus" action. The node becomes the root of the view, and a
  breadcrumb (`Statul › Guvernul › Ministerul Sănătății`) leads back up.
- **Breadcrumb in the detail dialog.** The dialog shows the path from the top layer to the record. It also
  shows the siblings of the same family ("alte 41 Direcții de sănătate publică"). Each item opens that record.
- **Filters in the tree.** Filters work as in the current view: matches show normally, and ancestors show as
  dimmed context. Each node shows "matches / total" when a filter is active. When a filter leaves at most 50
  matches, the tree opens the path to each match.
- **State in the URL hash.** The hash holds the view, the focused node and the filters, for example
  `#v=stat&n=4266456&q=spital`. The page restores the state from the hash on load, and the back button works.

## Out of scope (version 1)
- Parents inferred by family (phase 2).
- A treemap or icicle chart of the top levels.
- Placement of state companies under their owner (see the backlog).
