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
