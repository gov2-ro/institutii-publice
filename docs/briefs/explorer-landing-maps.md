# Implementation brief: landing page, county map and county profiles

Status: built and accepted, 2026-10-25 (v0.6.0). Owner request, same day.
Builds on [explorer-quality-v1](explorer-quality-v1.md) (accepted, v0.5.0).

## Owner request

1. In the "Județ → localitate" view, split each county's localities into
   Reședința de județ, Municipii, Orașe and Comune.
2. A landing page. First section: the content of "Explorează toate instituțiile".
   Second section: the list from the "Tip → instituții" tab. Third section: a choropleth map of counties.
3. A county profile with a map of its UATs. Assets: `explorer/assets/gis/` and `explorer/assets/steme-judete/`.

## Decisions (Opus)

- The owner's request supersedes the explorer-quality-v1 rule "no mandatory landing page".
  The landing page is a fifth view, `v=acasa`, tab "Acasă", placed first.
- An empty hash opens `acasa`. A hash with other parameters and no `v` still opens the list.
  Every existing hash keeps its meaning.
- A filter change or a search on the landing page opens the list view with that filter.
  The landing page always describes the entire dataset. It does not show filtered counts.
- The overview moves to the landing page, expanded. Remove the collapsible overview from the other views.
  Keep its reset-and-navigate behaviour for the shortcuts.
- The landing family section reuses the family-view rendering for the top level (family label + count).
  Selecting a family opens the list view filtered by that family, as the overview shortcuts do.
- The county map colours each county by its number of records (unique records, `k`).
  Use a sequential scale with 5 quantile classes and a legend. Label the measure "înregistrări".
  Records are not legal entities. Do not imply per-capita values; the data has no population.
- Selecting a county opens its profile: `v=loc&k=<county>`. The profile is the existing locality view
  scoped to one county, with a header: coat of arms, county name, record count and the UAT map.
- The UAT map colours each UAT by its number of records (`u`). Selecting a UAT filters to that locality.
  Show the number of county records without a locality.
- The county seat is a curated constant in `index.html`, keyed by county (41 seats).
  București has sectors instead: group them as "Sectoare". Ilfov's seat is Buftea.
- Locality kind comes from the UAT name prefix (Municipiul/Oraș/Comuna/Sectorul).
  The seat is removed from "Municipii". Unknown prefixes go to "Altele".
- Draw maps as inline SVG with no dependency. Decode TopoJSON in the page (a small inline decoder).
  Project with an equirectangular projection scaled by cos(latitude).
- Load the GIS files only when a map is first shown. A failed map load shows a short Romanian message.
  The rest of the page must still work.
- Maps are keyboard-operable: each shape is focusable, has an accessible name with its count,
  and responds to Enter. A visible list of counties/UATs with counts remains the non-map route.
- Commit the assets under `explorer/assets/`. They are runtime files of the page, not pipeline inputs.

## Acceptance

- All 42 counties and at least 95% of ANAF UAT roots join to a map shape. Report unmatched names.
- Locality groups in each county: seat first, then Municipii, Orașe, Comune. Counts are unique records.
- `#` opens the landing page. `#v=list`, `#q=x`, `#fam=…`, `#v=loc&k=Brasov` and record hashes behave as before.
- No document overflow at 320–1,440 px. The maps fit their container at all widths.
- No console errors. Root and descendant checks still pass. Both colour schemes have legible map colours.
- Screenshots: landing page (desktop, phone) and one county profile (desktop, phone).
