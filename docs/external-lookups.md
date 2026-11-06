# External lookups and downloads

This log lists every call to a public service and every dataset download for this project.
The owner reads this log. Add a row in the same change as the work that made the call.

Rule (owner, 2026-11-05): read-only, within the published limits of the service, only CUIs of public bodies, no personal data.

| Date | Service | What was sent or fetched | Volume | Result | Note |
|---|---|---|---|---|---|
| 2026-11-04 | ANAF `PlatitorTvaRest/v9/tva` | The CUIs of `seap-pairs.csv` | 1 request, 29 CUIs | 28 found | `data/seap/anaf-lookup-pairs.json` |
| 2026-11-04 | ANAF `PlatitorTvaRest/v9/tva` | The CUIs of the `S` records | 28 requests, 2,747 CUIs, one every 1.5 s | 2,728 found | `data/lookup-survey/anaf-s.json`. Some `S` records are companies. ANAF states no terms on re-use. |
| 2026-11-04 | static.anaf.ro | ANAF service documentation `doc_WS_V9.txt` | 1 file | Saved | `data/lookup-survey/anaf-doc-v9.txt` |
| 2026-11-04 | data.gov.ro CKAN API | Search and package metadata | Metadata only | Saved | `data/lookup-survey/ckan-*.json`, `pkg-*.json` |
| 2026-11-04 | data.gov.ro | `OD_FIRME`, `OD_STARE_FIRMA` | About 788 MB, unplanned | Cut to samples, full copies deleted | The server ignored the Range header. This broke the "no full download" rule of the survey. |
| 2026-11-04 | Web pages | Pricing, terms and API documents of openapi.ro, termene.ro, listafirme.eu, demoanaf.ro, recom.onrc.ro, sicap.ai, e-licitatie.ro; web search | Page reads | See the backlog, *Verified limits* | No record data was sent. Several pages returned 403. |
| 2026-11-05 | data.gov.ro | ONRC `OD_FIRME`, `OD_STARE_FIRMA`, `N_STARE_FIRMA` of 2026-10-19 | 787,967,023 bytes, 3 files | To geana, sizes equal the metadata | `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-onrc-firme-2026-10-19/`, `SHA256SUMS` there. Natural persons appear only as `PF`/`II` company rows in this file. |
| 2026-11-05 | data.gov.ro | Finance Ministry dataset, stream samples of 3 files | 5 MB each | `data/lookup-survey/mf-sample/` | The sample holds natural persons. It stays local and out of git. |
| 2026-11-05 | data.gov.ro | ANFP list 2025 | 147,431 bytes | `data/lookup-survey/mf-sample/` | CC-BY-4.0 |
| 2026-11-05 | data.gov.ro | Finance Ministry dataset, 2 July files | 874,608,750 bytes | To geana, sizes equal the metadata | `/Volumes/geana/NAS-devbox/gov2/data.gov.ro-mf-platitori-2026-07/`, `SHA256SUMS` there. 818,693 natural-person rows stay on geana only. |
| 2026-11-05 | roepas.ro | Terms and conditions, GDPR page, home page, `robots.txt`, first 100,000 characters of the sitemap | 4 pages and 1 partial sitemap | Terms forbid scraping and mass copying | Read for licence terms. See `docs/reports/source-licences.md`, section 2. |
| 2026-11-05 | posturi.gov.ro | Home page, `/despre/`, `robots.txt`; `oc.gov.ro/termeni-si-conditii-2/` (terms link) | 3 pages; 3 requests to oc.gov.ro | No licence found; oc.gov.ro answered HTTP 500 | Section 5 of the report. |
| 2026-11-05 | anaf.ro, static.anaf.ro, extranet.anaf.mfinante.gov.ro | Extranet page of the list, `/reinnoire/` (site terms), `static.anaf.ro` copyright page, API terms PDF, OGL PDF | 4 pages, 2 PDFs (235 KB and 11 KB) | Source-named reproduction (2009 notice); OGL on one ANAF site | `www.anaf.ro` home returned "acces interzis" and was not worked around. Section 1. |
| 2026-11-05 | integritate.eu, declaratii.integritate.eu, monitorul.ai | Home page, "Condiții legale", "Condiții de utilizare" of ANI; portal page shell; `monitorul.ai/integritate`, `robots.txt` | 6 pages | ANI: reproduction with the source. No licence on the portal or on monitorul.ai | Section 4. |
| 2026-11-05 | e-guvernare.ro | `Registrul-National-al-Institutiilor-Publice-din-Romania.pdf` (headers and file), home page | 1 PDF of 1,230,806 bytes; 2 home page requests | No terms. The home page gave no text | Read for the publisher; the PDF is of 2020. Section 3. |
| 2026-11-05 | geo-spatial.org, github.com/akaleeroy, lists.openstreetmap.org | Download page of administrative boundaries, home page, a mirror README, a mailing list post | 5 pages | Source ANCPI; footer CC BY-SA 4.0 | Section 6. |
| 2026-11-05 | data.gov.ro | Licence page `/pages/licence` and the OGL-ROU-1.0 PDF | 3 pages, 1 PDF (11 KB) | OGL-ROU-1.0 text read | Section 7. |
| 2026-11-05 | legislatie.just.ro | Legea 179/2022 and Legea 109/2007 (printable texts) | 2 pages | Legea 179/2022 read in full | Section 7. |
| 2026-11-05 | Web search | Queries on ANAF terms, OGL-ROU-1.0, ANI terms, Legea 179/2022, the Registrul, geo-spatial.org | 9 queries | Pointers only | Results used as leads. The report marks as secondary every claim that rests on a search summary only. |
| 2026-11-05 | roepas.ro, legislatie.just.ro | Opus check of the ROePAS terms and of Legea 179/2022 | 2 pages | Quotes of the report confirmed | Read through a summary tool. No record data sent. |
| 2026-11-06 | data.gov.ro, declaratii.integritate.eu, posturi.gov.ro, geo-spatial.org, monitorul.ai | Status check of the links for *Despre* | 9 page requests | All HTTP 200 | No record data sent. Client name `institutii-publice-check`. |
| 2026-11-06 | GitHub, tipizatul.eu | Public repo `iamandiradu/tipizatul.eu` (tree, `procedures.json`, sitemap, code); live home, `/proceduri`, `/procedures.json` | About 25 MB, 10 files; 4 live requests | Saved to a session scratchpad only, not to the project | MIT licence covers the code. No data licence found. No record data sent. |
| 2026-11-06 | transparenta.eu | `/entities/<CUI>` for 10 CUIs of public bodies (one S record) and 1 invalid CUI; `/terms`, `/about`, `robots.txt`, sitemap | About 16 requests, 1 per second for the sample | 9 titles with the name; `Entity <CUI>` for 1 S company and the invalid CUI | Link check only. The automatic text search of `/terms` found no licence term. |
| 2026-11-06 | mfinante.gov.ro, e-licitatie.ro, edirect, opencorporates.com, listafirme.ro, termene.ro, stiri.gov2.ro, roepas.ro | One request per site; the CUI 4305857 to mfinante, listafirme, termene | 13 requests | listafirme and termene: 403. `edirect.gov.ro`: timeout. mfinante: connection reset on the second request | Link check only. |
| 2026-11-06 | Web search | SICAP authority profile URL; transparenta.eu terms | 1 query | No usable result | |
| 2026-11-06 | transparenta.eu | Terms page (`/terms`), read through a summary tool | 1 page | No text on links or automated access. Open data follows the licence of the source. | No record data sent. |
