# Implementation brief: București sectors and same-name duplicates

Status: built and accepted, 2026-10-25 (v0.7.0). Owner request with three screenshots of the explorer.
Builds on v0.6.0 ([explorer-landing-maps](explorer-landing-maps.md)).

## Observed (Opus, measured on the v0.6.0 output)

- București has 2,501 records. 1,426 have no UAT (835 ANI-only, 591 Registrul-only).
  94 of them name their sector ("ADMINISTRATIA DOMENIULUI PUBLIC SECTOR 1").
- Two labels exist for each sector: "Sectorul N al Municipiului Bucuresti" (ANAF, 963 records) and
  "Sector N" (ROePAS through `uat_of`, 112 records). The explorer shows 12 sector groups instead of 6.
- 391 groups (788 records) of source-only records share the folded name and county. 320 groups are
  Registrul + ANI. Example: `G10011` and `Df6fe173e`, both "ADMINISTRATIA DOMENIULUI PUBLIC SECTOR 1", București.
- ANI holds shortened forms of ANAF names. Example: `D3f6d6468` "AGENTIA NATIONALA A MEDICAMENTULUI SI A
  DISPOZITIVELOR MEDIC" is a prefix of ANAF `41433222`. Today it is only a weak duplicate.
- Correction to the v0.6.0 backlog: ANAF `4192545` JUDETUL ILFOV and `4267117` MUNICIPIUL BUCURESTI are not misnamed.
  Their seats have București sector addresses. The UAT label is the seat's location, not the authority's territory.

## Tasks

1. **One label per sector.** Map "Sector N", "Sectorul N" and similar forms to "Sectorul N al Municipiului Bucuresti"
   in `uat_of` and in any other place that sets `uat`.
2. **Sector from the name.** For a București record without a UAT, set the UAT when the name states exactly one
   sector (`sector N`, `sectorul N`, `sect N`, N = 1–6). Record `uat_source: "name"` in JSON, compact `us: 1`, and a
   CSV column `uat_source`. Do not infer when the name states two different sectors.
   The explorer labels the remaining București records "Municipiul București (sector necunoscut)",
   not "localitate necunoscută".
3. **Same-name source-only records across sources.** Merge two or more source-only records when all these hold:
   - same folded name (after `strip_suffix`) and same county;
   - they come from different sources;
   - the name occurs once in each of those sources in that county;
   - the name is not a local kind (`DECL_LOCAL_KIND`) and is not a family head without a proper noun
     (for example "SCOALA GIMNAZIALA", "PRIMARIA").

   The surviving id follows source priority ROePAS (`R`) > Registrul (`G`) > ANI (`D`).
   It takes the union of sources and fields (contacts from ROePAS, `registrul_nums`, `declaratii_count`).
   Absorbed ids go into `merged_ids` (JSON, compact `mi`, CSV `merged_ids`).
   Set `link.<source> = "same_name"` for each absorbed source.
   Keep `possible_duplicate_of` and `match_candidates` when they agree. Use the union when they differ;
   apply the existing single/multiple candidate rule.
   Leave same-source duplicates (two Registrul rows with the same name) separate.
4. **ANI prefix forms.** Add a link tier `prefix` for an ANI name that is a strict prefix of exactly one ANAF name
   in the county being tried. Require at least 3 non-stopword tokens and numeric compatibility.
   Exclude local kinds. Several ANAF names with that prefix make the result ambiguous, with candidates.
   A merge at this tier counts as a merge, like `tokens`.
5. **Explorer.** Resolve an absorbed id in the `id` hash through `mi`, and open the surviving record.
   Show "Combinat din: …" in the dialog for merged records. Show "sector dedus din nume" for `us`.

## Constraints

- Do not merge into ANAF records through `same_name`. Only source-only records combine.
- Keep tests deterministic. Add fixtures for tasks 1–4, including a generic name that must stay unmerged.
- Compare the stderr summary before and after. Report the counts per task and 10 named examples.
- Re-run the browser checks (`t5`–`t10` in the session scratchpad `ui/`) and the unit tests.
