# Landing navigation refactor

Owner request: 2026-10-26. Implemented; browser validation is recorded in the activity log.

This brief replaces the landing navigation rules in [explorer-landing-maps.md](explorer-landing-maps.md).
The data schema and the constitutional placement rules stay the same.

## Navigation

- The upper-left title links to `#`. It uses `explorer/assets/img/gx00.png`.
- “Mai multe” sits on the title row. There is no separate row of view tabs.
- Its view links are “Structura statului”, “Tip → instituții”, and Listă.
- Its filters are “are site”, “fără corespondent ANAF”, and “de verificat”.
- The county tab is hidden. County profiles remain available through the landing map and existing links.
- The landing page hides the search and filter bar. Result views show the bar.
- “are site” starts checked. Its only checkbox is in “Mai multe”, including on result views.
- Reset and the home link restore the website default. `web=0` preserves an explicit choice to show all records.
- Existing `web=1` links still select institutions with websites.

## Landing content

- Preserve the previous overview, largest-type shortcuts, and compact type grid above the state directory.
- Keep “Tipuri de instituții”. Remove the duplicate “Tip → instituții” section from Acasă.
- Start every type category closed, including in the separate family view.
- Keep both state layouts for comparison until the owner chooses the final composition.
- Remove the introductory title “Explorează instituțiile publice” and its accompanying instruction.
- Show the state directory below the compact type grid. Keep the county map below the directory.
- The restored sections, new directories, and county map use the same active filters.
- A state link opens its focused subtree. A virtual group with one institution skips its wrapper.
- A type link opens a focused peer group with a breadcrumb. Large groups split by county.
- A group with one matching record opens that record's details.
- Records without a common type remain accessible within their category.
- Links preserve the website choice. Direct record links can open records without websites.
- Focus changes support refresh and browser Back. The menu supports Escape and outside clicks.

## Government focus

- Show SGG, each ministry, and “Organe de specialitate” at the same level under Guvernul.
- Skip the “Ministere” heading in this display and in ministry breadcrumbs.
- Retain the metadata membership and the existing `n=ministere` links.
- Apply the existing filters and keep ancestors visible when their descendants match.

## Validation

- Verify directory links, focused groups, singleton records, and the advanced filters.
- Verify empty hashes, `web=0`, legacy view links, record links, refresh, and browser history.
- Verify the root count and the attached descendants with the existing console checks.
- Check five views at 320, 390, 768, 901, 1,024, and 1,440 pixels.
- Capture the landing page on desktop and phone. Check both colour schemes.
- Run the existing unit tests and the JavaScript syntax check.
