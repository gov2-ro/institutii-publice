# Backlog

Statuses: `[ ]` open, `[~]` in progress, `[x]` done, `[-]` dropped (with the reason).

## Explorer: "Structura statului" (spec: specs/structura-statului.md)
- [x] Version 1: top layer from the Constitution, local administration, focus and breadcrumb, URL hash
      (brief: briefs/structura-statului-v1.md)
- [ ] Phase 2: give a parent to records with no ANAF match, from their family, when ≥ 90% of the family's ANAF
      members share one parent. Measured 2026-10-25: 3,544 of 11,861 records. Show these parents in a
      different style ("atribuit după tip").
- [ ] Later: a treemap or icicle chart of the top two levels, sized by number of institutions.

## Data quality
- [ ] Companii de stat: 937 of 954 are in "(fără tip comun)". 719 of them come only from ANI. Ideas:
      curated group heads (Electrica, CNAIR/DRDP, CFR, Romsilva, Transelectrica, ROMARM, Hidroelectrica);
      local utilities (apă-canal, termie, domeniul public, parcuri industriale, drumuri și poduri) placed
      under their UAT or county; merging the name variants (for example, at least 5 spellings of
      "Electrica Furnizare SFEE Transilvania Sud").
- [ ] Ugly network-family labels in Companii de stat: "Electrica furnizare sa sfee transilvania sud brasov
      afee", "Smart sa sucursala".
- [ ] Wrong categories: "D S V S A ALBA LABORATOR SANITAR VETERINAR" is in Companii de stat (it belongs under
      ANSVSA). "MUNICIPIULUI MANGALIA" is in Altele (the genitive form is not matched). IDPSAR is in Sănătate.
      SRR and SRTV are in "Servicii publice locale și regii".
- [ ] Re-export the two capped ANI county groups (full tail of rare names). (from README)
- [ ] Resolve ANI-only records (state companies) to a CUI with the ONRC open data. (from README)

- [ ] Linker ties: when two ANAF rows get the same best token score, the first row wins. Consider "weak"
      for a tie instead (two equal candidates means the link is ambiguous).

## Verified limits
- The ANAF parent link (ordonator principal de credite) is one level deep. It gives no middle level
  (for example, no ISJ between a school and the ministry). A middle level must come from grouping (family,
  county), not from ANAF.
