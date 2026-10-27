# Spec: landing v2 and the page "Cum e organizat statul"

Status: accepted, 2026-10-27. The owner accepted all five recommendations in section 4. Brief: [../briefs/landing-v2-organizare.md](../briefs/landing-v2-organizare.md).

Owner request (2026-10-27): improve the landing page from the visitor's point of view, with the India web
directory as inspiration. Add a separate page that explains how the Romanian state is organised, like the
New Zealand and Australian diagrams.

References that the owner gave:
- https://www.india.gov.in/directory/web-directory — one card per branch (Ministries, Apex bodies, Judiciary,
  Legislature, States, Districts, Local bodies). Each card has icons, a dropdown and a "View" button.
- https://www.publicservice.govt.nz/system/central-government-organisations — one diagram of the public sector,
  boxes grouped by kind, a colour key for the relationship to ministers.
- https://www.finance.gov.au/government/managing-commonwealth-resources/structure-australian-government-public-sector —
  primary bodies, then secondary structures, then other governance relationships.

## 1. Who comes to the landing page, and what they want

| Visitor | Question | Current landing page | Gap |
|---|---|---|---|
| Citizen | "Which office handles X where I live?" (hospital, school, taxes, ID card, pension) | Branches of state, type tabs, county map | No search. No entry by need. The type tabs use administrative words ("Servicii publice locale și regii"). |
| Citizen | "What is the site of my primărie / school?" | County map → county profile | Works, but needs two clicks and a map. No locality picker. |
| Journalist, researcher | "What sits under ministry X?", "Which state companies exist?" | State branch row | Works. The row of 12 links has no explanation. |
| Developer, gov2 projects | "What data is this, how fresh, how do I download it?" | "Despre date" in the menu | Hidden. |
| Student, any visitor | "How is the state organised?" | Nothing | No explanation of the words "subordonare", "deconcentrat", "autonom". |

The current landing page assumes that the visitor knows the structure of the state. The India directory makes
the same assumption, but each card says what it holds, and the dropdown gives the full list in one control.
Most visitors start from a place or a need. So the new landing page starts with search, place and need, and
puts the structure of the state after them.

## 2. Landing page v2

Order, from the top. Every section uses the active filters, as now (the website default stays).

1. **Search.** A large search field: "Caută o instituție, o localitate sau un CIF". Under it, three example
   links (for example "Spitalul Județean Cluj", "Primăria Iași", a CIF). Enter opens the list view with `q`
   (`leaveHome` already does this). One line under the field shows the total and the sources:
   "24.988 de instituții · surse: ANAF, ROePAS, Registrul Național, ANI · date din <dată>". A link "Despre date"
   ends the line.
2. **"Unde locuiești?"** Two native selects, `.g2-input` in `.g2-field`: county, then locality (filled when a
   county is chosen; the existing `uat` hash key). A button "Arată" opens the county profile
   (`#v=loc&k=<county>`), with `u=<locality>` when a locality is chosen. The select does not navigate by itself.
   The chosen county also scopes the links of section 3. The page keeps the county in `localStorage`
   (try/catch; the page works without it). A link "Șterge" clears it.
3. **"De ce ai nevoie?"** 8–10 tiles (`.g2-tile`), each with a line icon, a title in everyday words and 3–5 type
   links with counts. A type link opens the family view (`#v=fam&fam=<label>`), plus `k=<county>` when a county
   is chosen. The tiles are a constant `HOME_TASKS` of family labels. A label that is absent from the data
   is skipped, and a tile with no label left is hidden. Proposed tiles (labels from `metadata.json` families):
   - Sănătate: Spital județean, Spital municipal, Spital orășenesc, Serviciul de ambulanță județean,
     Direcția de sănătate publică, Casa de asigurări de sănătate.
   - Școli și grădinițe: Grădiniță, Școală gimnazială, Liceu teoretic, Liceu tehnologic, Inspectoratul școlar
     județean, Centrul județean de resurse și asistență educațională.
   - Acte și proprietăți: Direcția județeană de evidența persoanelor, Oficiul de cadastru și publicitate
     imobiliară, Primărie.
   - Taxe: Direcția generală finanțelor publice, Centru financiar.
   - Muncă, pensii și ajutoare: Agenția județeană pentru ocuparea forței de muncă, Inspectoratul teritorial
     de muncă, Casa județeană de pensii, Agenția județeană pentru plăți și inspecție socială, Direcția generală
     de asistență socială și protecția copilului.
   - Siguranță și urgențe: Inspectoratul de poliție, Inspectoratul pentru situatii de urgenta, Inspectoratul de
     jandarmi județean, Poliția locală.
   - Instanțe și parchete: Judecatoria, Tribunalul, Curtea de apel, Parchetul de pe lângă tribunalul.
   - Agricultură, mediu, animale: Agenția de plăți și intervenție pentru agricultură, Direcția pentru agricultură
     județeană, Agenția pentru protecția mediului, Direcția sanitară veterinară și pentru siguranța alimentelor.
   - Cultură și sport: Muzeu, Teatru, Bibliotecă, Direcția județeană pentru cultură, Club sportiv.
   - Consumatori: Oficiul județean pentru protecția consumatorilor.
4. **"Cum e organizat statul"** — the India-style directory. Six cards (`.g2-tile`), each with an icon, a title,
   one sentence on what the card holds, 3–4 direct links with counts, and, where the list is long, one native
   select with a "Vezi" button. The cards reuse the state nodes of `metadata.json` (`state.nodes`); no new data.
   - Puterea legislativă: Parlamentul (node `parlament`). Links: Camera Deputaților, Senatul.
   - Președinția și Guvernul: nodes `presedinte`, `guvern`. Select: the ministries and the organe de specialitate.
   - Justiție: nodes `justitie`, `ccr`. Links: Curtea de apel, Tribunalul, Judecatoria, parchete (families).
   - Autorități autonome și de control: nodes `curtea-conturi`, `avp`, `autonome`, `ces`, `servicii`, `aparare`,
     `academii`. Select: the members of `autonome`.
   - Administrația locală: county select → county profile. Links: Județ, Municipiu, Oraș, Comună (families).
   - Companii și regii de stat: category "Companii de stat", family "Regie autonomă", category "Servicii
     publice locale și regii".
   A link under the cards opens the new page: "Cum funcționează fiecare ramură →".
5. **Tipuri de instituții** — the category tabs of today, unchanged.
6. **Județe** — the county map and the county list of today, unchanged.

Phone (320–390 px): one column. Search, then the county selects, then the tiles in one column. Each tile shows
its title and its first 3 links; a "+ N" link opens the family list. Touch targets stay at least 44 px.

Icons: inline SVG, line style, `stroke="currentColor"`, `aria-hidden="true"`, one `<symbol>` sprite in the page.
The DS has no icon set ("Not in the DS yet"), so the class is `org-icon`. Open a `ds-proposal` issue only when a
second project needs the icons.

## 3. Page "Cum e organizat statul" (`explorer/organizare.html`)

A separate static page, not a view of `index.html`. *Why:* the text is mostly prose; search engines index a
real page; the page loads without the 6 MB `rows.json`. *Cost of the alternative (a view):* live counts and
in-page focus, but a large page for a reader who only wants to read. The page links into the explorer with
hashes (`index.html#v=stat&n=<node>`, `#v=fam&fam=<label>`). Version 1 shows no counts, so no number goes stale.

The page uses `gov2.css`, the same header and footer as `index.html`, and `@layer app` styles with the prefix
`org-`. The header menu of `index.html` and the landing card section link to it.

### 3.1 Content outline (Romanian text, plain language, one idea per paragraph)

1. **Introducere.** The state has three powers, separate and balanced (Constituția, art. 1 alin. 4): legislativă,
   executivă, judecătorească. Some bodies stand outside the three powers (Curtea Constituțională, the autonomous
   authorities). Local administration has its own autonomy.
2. **Diagrama "Statul român".** A dashed frame with groups of boxes, built in HTML and CSS (not an image), so it
   reflows on phones and every box is a link. The groups:
   - *Puterea legislativă:* Parlamentul (Camera Deputaților, Senatul).
   - *Sub controlul Parlamentului:* Curtea de Conturi, Avocatul Poporului, autoritățile administrative autonome
     (for example AEP, Consiliul Concurenței, ANCOM, ANRE), the intelligence services (SRI, SIE).
   - *Puterea executivă — central:* Președintele (Administrația Prezidențială, CSAT); Guvernul (SGG, ministere,
     organe de specialitate subordonate Guvernului sau ministerelor).
   - *Puterea executivă — în teritoriu:* the prefect (represents the Government in the county) and the servicii
     publice deconcentrate (DSP, ITM, AJOFM, ISJ, DGRFP and others).
   - *Autoritatea judecătorească:* ÎCCJ, curți de apel, tribunale, judecătorii; Ministerul Public (parchete,
     DNA, DIICOT); CSM.
   - *Curtea Constituțională* (its own title in the Constitution).
   - *Administrația publică locală:* UAT (județ, municipiu, oraș, comună); consiliul județean and its president;
     consiliul local and the mayor; local public services, subordinate institutions, local regii and companies.
   - *Întreprinderi publice:* regii autonome, companii și societăți naționale, companies with state capital; each
     has an "autoritate publică tutelară".
   - *Instituții cu autonomie proprie:* universities (autonomie universitară), Academia Română and the branch
     academies.
   Each box links to its node or family in the explorer.
3. **Cheia relațiilor** (the key, like the New Zealand key). One line style per relationship, used in the
   diagram, and one paragraph each: *în subordinea* (the parent leads, appoints, funds); *în coordonarea*;
   *sub autoritatea*; *sub control parlamentar*; *autonomie locală* plus the prefect's legality check (tutela
   administrativă); *autoritate publică tutelară* (a ministry or a UAT owns an enterprise); *deconcentrare*
   versus *descentralizare* (Codul administrativ, art. 5 lit. u and x).
4. **Cum circulă banii: ordonatorii de credite.** Principal, secundar, terțiar (Legea 500/2002, art. 21;
   Legea 273/2006 for local budgets). Say plainly that the ANAF parent CIF in this list is the ordonator
   principal, so a link in the explorer means "is funded through", not always "is led by". This explains why
   5,657 schools have two parents (the UAT and the Ministerul Educației).
5. **Ce apare în listă, dar nu face parte din stat.** Professional bodies (colegii, ordine), chambers of commerce,
   parishes: they receive public money or keep a public register, so they are in the ANAF list.
6. **Cum citești exploratorul.** Where each group of the diagram sits in "Structura statului"; why some records
   have no parent (no ANAF match); the "de verificat" filter.
7. **Surse și lecturi.** The list in section 5. A note: we found no official plain-language guide to the whole
   structure; the page fills that gap and cites the law for each claim.

### 3.2 Rules for the text
- Every legal claim cites an article from a source in section 5. Do not cite an article that was not checked.
  Codul administrativ art. 5 does **not** define *subordonare*, *coordonare* or *autoritate* (checked 2026-10-27);
  describe these from their use in the organisation decisions (HG), with one cited example each.
- A disputed placement keeps the note that `STATE_MEMBERS` already carries.
- Simple words first, the legal term after it in italics: "birourile ministerelor din județe (*servicii publice
  deconcentrate*)".

## 4. Owner decisions (2026-10-27: all five recommendations accepted)

1. **Search on the landing page.** The 2026-10-26 refactor made search result-only. Visitors expect a search
   field first. *Recommendation:* show it on the landing page. *Cost:* the landing page is longer by one row.
2. **Section headings on the landing page.** The 2026-10-26 cleanup removed headings and notes. Sections 2–4
   need a short heading each, or the visitor cannot tell a place picker from a type list. *Recommendation:*
   headings, no notes.
3. **The state row of today.** Section 4 replaces the inline row of state branches. *Recommendation:* replace it.
4. **Remembered county.** *Recommendation:* yes, in `localStorage`, with a clear "Șterge" link.
5. **The new page as a separate file.** *Recommendation:* `explorer/organizare.html` (section 3).

## 5. Sources (checked 2026-10-27)

Official texts on legislatie.just.ro (the titles were checked by opening each page):
- Constituția României, republicată — https://legislatie.just.ro/Public/DetaliiDocument/47355
- OUG nr. 57/2019 privind Codul administrativ — https://legislatie.just.ro/Public/DetaliiDocument/215925
  (art. 2: the central authorities; art. 5 lit. u deconcentrare, w instituție publică, x descentralizare,
  kk serviciu public, ll servicii publice deconcentrate)
- Legea nr. 500/2002 privind finanțele publice — https://legislatie.just.ro/Public/DetaliiDocument/37954 (art. 21)
- Legea nr. 273/2006 privind finanțele publice locale — https://legislatie.just.ro/Public/DetaliiDocument/73527
- OUG nr. 109/2011 privind guvernanța corporativă a întreprinderilor publice —
  https://legislatie.just.ro/public/detaliidocument/133685 (from the search index; not opened)
- Legea nr. 304/2022 privind organizarea judiciară (with Legea 303/2022 and 305/2022). No legislatie.just.ro
  link found yet; the brief asks for it.

Searches for a plain-language Romanian guide to the whole structure found none (2026-10-27). They found the
"Ghidul cetățeanului" for Legea 544/2001 (many town halls publish one), academic papers on the prefect and
the tutela administrativă, and press analyses. The page may link the Legea 544/2001 guide in section 6, as
"how to ask an institution for information".
