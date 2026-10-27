# Courts with two CIFs: register check, 2026-10-27

## Request
The stiri session asked whether the ANAF records A4… (parent 4265841, Ministerul Justiției) and A47373…
(parent 4340587, Înalta Curte de Casație și Justiție) are one body. The owner approved a bounded check.

## Method
- Source: ANAF public VAT register, `PlatitorTvaRest/v9/tva`, date 2026-10-27.
- Budget: 1 request per CIF, 4 requests, no retry needed. No other ANAF call.
- Sample: Curtea de Apel București (17019105, 47373006) and Tribunalul București (4340633, 47373014).

## Result
| CIF | Name | Address | Postcode | Phone | Registered | Fiscal organ | Active |
|---|---|---|---|---|---|---|---|
| 17019105 | CURTEA DE APEL BUCURESTI | Sector 4, Spl. Independenței 5 | 50091 | 3321060 | 2004-12-09 | Adm. Sector 4 | yes |
| 47373006 | CURTEA DE APEL BUCURESTI | same | 50091 | 3321060 | 2022-12-26 | Adm. Sector 4 | yes |
| 4340633 | TRIBUNALUL BUCURESTI | Sector 4, Str. Gh. Danielopol 2-4 | 40095 | 3373300 | 1993-07-20 | Adm. Sector 4 | yes |
| 47373014 | TRIBUNALUL BUCURESTI | same | 40095 | 3373300 | 2022-12-26 | Adm. Sector 4 | yes |

In each pair, name, address, postcode, phone and fiscal organ are equal. Both CIFs are active. The 47373… CIF
was created on 2022-12-26, and its "stare înregistrare" text repeats the original registration date (MODIFICARE
… din data 09.12.2004 / 20.07.1993).

## Reading
- Measured: the register shows one court identity under two active CIFs.
- Assumed, not shown by the register: the second CIF is the 2022 re-registration of the court under the ÎCCJ budget.
  The parents differ in the same way (MJ 111 children, ÎCCJ 57 children), which fits that reading.
- The register does not say that the two CIFs are one legal body.

## Decision
No merge. Cost of the alternative: one record has one CIF and a parent list from the ANAF file. A merge would drop
one CIF and one parent link for 29 pairs (pairs with an A47373… CIF and the same name and county) and the state tree would lose the ÎCCJ branch. Neither CIF has children
of its own (0 records name them as parent).
Next step for the owner: choose a model, for example a `same_body_cif` link kept on both records. Until then stiri
can treat A47373… as the same court as its A4… partner.

## Operator decision (2026-10-27, relayed by the stiri session) and the build
For the 29 pairs, the A4… record and its A47373… partner are the same body. No merge; both tax IDs stay.
- `curation/same_body.csv` lists the 29 pairs with the evidence. The pairs are the A47373… records that share name
  and county with one A4… record. Courts of different cities never link; a Court of Appeal and a Tribunal of one city
  never link (different names).
- `institutii.csv` has a new last column `same_body_as`: on the A47373… record, the id of its A4… partner. The A4…
  record is canonical. All other records leave it empty.
- Register-checked: 2 of the 29 pairs (Curtea de Apel București, Tribunalul București). The other 27 rest on the
  same name and county in the ANAF list and on the operator decision.
- Not linked: 8 A47373… records have no A4… partner under the same name and county (Tribunalul Iași, Vaslui, Brăila,
  Vrancea, Maramureș, Caraș-Severin, Gorj, Ilfov). Their partner names differ or are missing; a manual check is open
  in the backlog.
