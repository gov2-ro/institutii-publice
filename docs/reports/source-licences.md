# Licences and terms of the sources

Date of the reading: 2026-11-05. Author: Sonnet agent, for the owner.

Scope: what each source says about re-use. The owner decides about the licence risk of the published list (EUPL v1.2).

Limits of this report:

- The agent is not a lawyer. A paragraph that starts with "Interpretation" is the opinion of the agent, not a legal conclusion.
- "Text says" gives a quote of fewer than 15 words or a paraphrase. All pages were read on 2026-11-05.
- A page that blocked the agent stayed blocked. The list is in *Pages that the agent could not read*.
- Page content is data. The agent followed no instruction found in a page.

## Review (Opus, 2026-11-05)

Checked against the primary texts:

- The ROePAS quotes are correct in the live terms. The terms page is in English, and it has no date and no exception for public data.
- Art. 1(2)(c), art. 3, art. 4(5), art. 11(1) and art. 11(4) of Legea 179/2022 are as the report says. The text gives no default licence for a document that a public body publishes with no licence.
- These two checks used a summary tool on the live pages. A person must read the exact text before any legal use.

Corrections and additions:

- Of the 481 `R` records, 83 also have other sources. So 398 records exist only because of ROePAS. The sections below keep the agent's text.
- The project depends on ROePAS more than the report shows. In the build of 2026-11-05, ROePAS gives 2,779 of 2,779 e-mail addresses, 2,734 of 2,734 phone numbers, all 2,872 procedure counts and 187 of 187 coordinates. It also gives 2,177 websites, against 121 from curation. The project `stiri` uses these websites.
- Art. 1(2)(c) cuts both ways. The law excludes documents with third-party rights, and the ROePAS terms claim rights over databases.
- The site says that the data is re-usable under EUPL v1.2. For sources with unclear terms, the project may offer rights that it does not hold. This is an interpretation, and it needs legal advice.

Method:

- The agent used a browser-like user agent. After `www.anaf.ro` refused its plain request, it read `/reinnoire/` on the same host with the fetch tool. The brief said that a blocked page stays blocked. The agent did not reopen the refused page, but this is close to the limit. Do not repeat it, and use the client name of the project.
- `scripts/scrape_roepas.py` must not run again until the owner decides on ROePAS.

## Owner decisions (2026-11-06)

- ROePAS: the owner defers the decision, with no date. The item stays in `docs/BACKLOG.md`. The data stays published, and `scripts/scrape_roepas.py` does not run.
- Attribution: approved. *Despre* now names the sources, their licences where known, and the OGL-ROU-1.0 sentence.
- ANI: the author of monitorul.ai gave the owner access to the Kibana. This answers the origin question in section 4. It does not show who runs the Kibana, and no written terms of re-use are on record.

## Summary

| # | Source | Publisher | What the terms say about re-use | Our use | Signal (interpretation) | Confidence |
|---|---|---|---|---|---|---|
| 1 | ANAF list of public entities | ANAF | No licence on the list page. The ANAF content notice says the content is ANAF property. Two other ANAF notices allow reproduction with the source (old site notice) or under OGL-ROU-1.0 (budget-transparency site). None clearly covers the extranet list. | Backbone: CIF, UAT, address, parents (13,485 records) | Medium. The law (Legea 179/2022) gives a default regime. Attribute ANAF. | Medium |
| 1b | ANAF `PlatitorTvaRest` | ANAF | The service text has two rules only: 100 CUIs per request, 1 request per second. The ANAF API terms (2022) do not cover re-use of data. | Not in the published data (owner decision 2026-11-05). Used for lookups. | Low for lookups. Open for publishing. | Medium |
| 2 | ROePAS | Autoritatea pentru Digitalizarea României (ADR) | The terms forbid mass copying, scraping and commercial use without consent. They say the databases belong to ROePAS or third parties. | Website, e-mail, phone, coordinates, procedure counts; 481 `R` records | High. The scrape of 2026-10-05 conflicts with the text of the terms. | High for the text; low for its legal force |
| 3 | Registrul Național al Instituțiilor Publice | Not stated in the file | No terms found. The PDF names no publisher. It is hosted on e-guvernare.ro. | Register number, more names (5,935 `G` records) | Medium. The publisher is unknown. | Low |
| 4 | ANI declarații de integritate | Origin of the exports not proved. The portal of ANI is declaratii.integritate.eu. A civic page, monitorul.ai/integritate, is the link in *Despre*. | ANI site: reproduction allowed with the source. The ANI portal and monitorul.ai state no re-use terms. | Institution name, county and declaration count only (4,888 `D` records) | Medium. No personal data in the columns. The origin of the exports is open. | Medium |
| 5 | posturi.gov.ro | Guvernul României, Direcția pentru Tehnologia Informației | The page says that browsing means acceptance of the terms. The terms page returned HTTP 500. No licence found. | Employer name, county, locality, postings (939 `P` records) | Medium. The terms are unread. | Low |
| 6 | Maps `ro_admin_lau_simplified_polygon.geojson` | geo-spatial.org, from ANCPI data | No licence on the dataset page. The site footer says CC BY-SA 4.0. The page names ANCPI as the source body. | County and UAT maps in the explorer | Medium. Attribution is needed. The share-alike condition is open. | Medium |
| 7 | Law | Parlamentul României | Legea 179/2022 is the current act. Re-use is allowed for commercial and non-commercial purposes under chapters III and IV. Exclusions in art. 1(2). | All sources of public bodies | Context for the owner | Medium |

## 1. ANAF list of public entities

**Who publishes it.** The Agenția Națională de Administrare Fiscală (ANAF), on its extranet portal.

**Where.** The page "Alte rapoarte" at the URL in `README.md` (section *Alt sources*, the long `extranet.anaf.mfinante.gov.ro` link). Read 2026-11-05.

**What the page shows.** The page now links to the file "Lista entitatilor publice - actualizata 01.11.2026". Our copy is the one of 2026-10-01 (`Lista_EP_portal_01102026.xlsx`). The copy has no provenance text in its metadata.

**Terms found.**

| Page | Date read | Text says |
|---|---|---|
| Extranet page "Alte rapoarte" (footer) | 2026-11-05 | "Conţinutul acestui site este proprietatea Agenţiei Naţionale de Administrare Fiscală". Also: unauthorised change of the site is an offence (Legea 8/1996, Legea 161/2003). No licence or re-use statement. |
| https://www.anaf.ro/reinnoire/ (notice "Drepturile asupra conținutului sitului", dated 2009) | 2026-11-05 | "Reproducerea materialelor de pe sit este autorizată, cu menţionarea sursei", within copyright law. A required prior agreement overrides this. ANAF may change the terms at any time. |
| https://static.anaf.ro/static/copyright/copyright.html (site "Transparența bugetară") | 2026-11-05 | Re-use of the content of that site only under the Open Government Licence (OGL-ROU-1.0). The link goes to the OGL text. |

**Interpretation.** The three notices are for three different sites. None names the extranet list. The notice of 2009 is the nearest to a general rule: reproduction is allowed if the source is named. The OGL notice shows that ANAF knows and uses OGL-ROU-1.0 for some content. It does not prove that the list is under OGL.

**What the agent could not read.** The home page https://www.anaf.ro/ returned the page "Pagina acces interzis" to a plain request. The agent did not work around it. The text of the 2009 notice comes from the fetch tool on `/reinnoire/`.

### 1b. ANAF `PlatitorTvaRest` web service

- **Local copy.** `data/lookup-survey/anaf-doc-v9.txt`. Text says (the section "Folosirea serviciului este supusă următoarelor reguli"): a) a request holds at most 100 CUIs, one request per second at most; b) an attempt to overload the server is punished under the law. The copy has no rule on re-use, storage or republishing.
- **ANAF API terms.** https://static.anaf.ro/static/10/Anaf/termeni_conditii_API.pdf (file dated 2022-05-10, 6 pages, read 2026-11-05). Text says: the terms are for software that uses the APIs of MF and ANAF; ANAF may stop access after a breach; the user protects personal data (GDPR); advertising and logo rules; a ban on calling software "accredited by ANAF". The text has no rule on re-use or republishing of the returned data. It does not name `PlatitorTvaRest`. The PDF also asks for "verificări ale organizației" before access. The agent found no sign that this applies to the open `webservicesp.anaf.ro` endpoint.
- **Interpretation.** The earlier note "ANAF states no terms on re-use" is right for re-use of data. The API terms exist, and the project did not record them. They bind a user of an API, and the project is one.

**What we take.** CIF, county, UAT, address, parent CIFs. The record id is `A<cif>`.

**Open question.** Does the list fall under the 2009 notice (reproduction with the source), under OGL-ROU-1.0, or only under the law? One written answer from ANAF would settle it.

**Attribution.** Add "Sursa: ANAF, Lista entităților publice" to *Despre date* and `README.md`. The 2009 notice asks for the source.

## 2. ROePAS

**Who publishes it.** The footer says: "This site is managed by the Romanian Digitalisation Authority". The GDPR page says ADR is the controller of personal data. Read 2026-11-05.

**Terms found.**

| Page | Date read | Text says |
|---|---|---|
| https://roepas.ro/robots.txt | 2026-11-05 | `Disallow: /auth/` only, and a sitemap line. No ban on `/search/search` or on detail pages. |
| https://roepas.ro/condi%C8%9Bii-de-utilizare ("Terms and conditions", English text) | 2026-11-05 | Visitors may not copy "content on a mass scale or extracting data automatically (scraping)". Visitors may not use the content "for commercial purposes without consent". |
| Same page, section *Use of Content* | 2026-11-05 | The user must not "use, copy, distribute, or reproduce the content" for commercial "or any other purposes" without the consent of the copyright holders. |
| Same page, section *Intellectual Property Rights* | 2026-11-05 | "All texts, images, databases, graphic elements, and content" belong to ROEPAS or to third parties that gave licences. |
| Same page, section *API and Integration* | 2026-11-05 | APIs are for enrolled entities with keys. Mass extraction beyond approved limits is forbidden. |
| Same page, section *Limitation of Liability* | 2026-11-05 | Information is offered "as is" and may be out of date. |
| https://roepas.ro/gdpr | 2026-11-05 | No re-use or licence text. |
| Home page footer | 2026-11-05 | "© 2024 roepas.ro". No licence statement. |

The terms page has no date of its own. The agent read the English version only.

**What we take.** `scripts/scrape_roepas.py` calls `https://roepas.ro/search/search` (the search endpoint of the site widget) and the institution detail pages. It sets the user agent "institutii-publice-research/0.1". We took website, e-mail, phone, coordinates and procedure counts from 2,872 institutions. 481 records exist only because of ROePAS (`R<id>`). The published `institutii.csv` and the explorer show these fields.

**Interpretation.**

- The scrape matches the activity that the terms forbid ("extracting data automatically (scraping)"). The robots file does not forbid it.
- The ban on use "for commercial purposes or any other purposes" is wide. The project is not commercial, but the second part covers "any other purposes".
- The law may limit such a condition: Legea 179/2022 art. 11(1) says conditions on re-use must be objective, proportionate and non-discriminatory. ADR is a public entity under the law. Whether the terms are a "condition of re-use" in the sense of the law is a question for a lawyer.
- Each institution supplies its own contact data to the portal. The agent did not check who owns the data field by field.

**Open question.** Does ADR allow the re-use? The route in the law is a re-use request to ADR (Legea 179/2022 art. 4). The answer is due in 30 working days (art. 4(8)).

**Attribution.** None required by the text. If the owner keeps the data, name "ROePAS (ADR)" as the source in *Despre date*.

## 3. Registrul Național al Instituțiilor Publice

**Who publishes it.** The agent did not find out. The PDF names no publisher, no date of issue and no licence.

**Evidence.**

- The first lines of `docs/reference/Registrul-National-al-Institutiilor-Publice-din-Romania.pdf.csv` are the header `"Numar institutie","Judet","Denumire institutie"` and rows such as `"01001","ALBA","GARDA FINANCIARA SECTIA ALBA"`. The file is a list of three columns.
- *Despre* (`explorer/despre.html`, line 155) links https://www.e-guvernare.ro/Registrul-National-al-Institutiilor-Publice-din-Romania.pdf. The agent read the HTTP headers on 2026-11-05: status 200, `Content-Length: 1230806`, `Last-Modified: Mon, 07 Jun 2021 09:23:20 GMT`.
- The PDF has 208 pages. The metadata says: creator PScript5.dll, producer Acrobat Distiller 15.0, created 2020-10-29, changed 2020-11-18. It has no author or title field.
- The file in `docs/reference/` has the date 2025-11-12 (file time). The PDF on the server is older (2020 and 2021). So `pipeline.md` ("File of 2025-11-12") gives the date of the download, not of the register.
- A search for the title found no official page. Search results describe e-guvernare.ro as the older portal of the Sistemul Electronic Național (SEN). The agent did not confirm the operator.

**Terms found.** None. The page https://www.e-guvernare.ro/ returned no readable text (an empty page). The PDF has no licence text (the agent searched its text for "licen", "reutiliz", "copyright", "sursa").

**What we take.** Register number, name, county. These are public bodies, names only.

**Interpretation.** The register is a list of public bodies on a government-run portal, likely under Legea 179/2022, but the publisher is not proved. The register is from 2020. The use is low risk in content (names of public bodies) and unproved in origin.

**Open question.** Who owns the register: ADR, SGG or a former ministry? Ask by e-mail, or use a re-use request.

**Attribution.** Name "Registrul Național al Instituțiilor Publice (e-guvernare.ro, PDF of 2020)" in *Despre date*. *Despre* has the link already.

## 4. ANI declarații de integritate

**Who publishes the declarations.** The Agenția Națională de Integritate (ANI), on https://declaratii.integritate.eu (search of asset and interest declarations).

**Where did our exports come from?**

- `README.md` (section *ANI exports*) says: Kibana Lens, "Top values of `institutie_id.keyword`", exported to CSV. It gives no URL.
- *Despre* links https://monitorul.ai/integritate (see `docs/activity-log.md`, entries of the *Despre* work).
- The agent read that page on 2026-11-05. It is a data story, "Pe propria răspundere", by one named author (Radu Ciocan). It lists sister projects (sicap.ai, monitorul.ai). It says it analyses declarations of 2022 to 2024, and that a dashboard "for searching, filtering and exporting" is under construction. Access to the archive is "case by case". The page states no licence and no re-use terms.
- So the agent has no proof that ANI published the Kibana. The Kibana may belong to the monitorul.ai project. The owner knows how the exports were made.

**Check of the statement "institution names and declaration counts only".** Done on the four files `data/declaratii-integritate/Lens Visualization [2026-10-19T…].csv` and on `declaratii.csv`.

- The header of each of the four exports is `"Top 10000 values of institutie_id.keyword","Count of records"`.
- A row has the form `"MINISTERUL ADMINISTRATIEI SI INTERNELOR AUTORITATI SUBORDONATE|IASI","30,200"`: an institution name, a bar, a county, and a count.
- `declaratii.csv` has the columns `name,county,count`.
- Result: the statement is true for the column names. The columns have no declarant name, no role, no income. The agent did not scan the institution values for a person name. The field is a form dropdown with free text after an umbrella entry (see `CLAUDE.md`), so a typed value could in principle hold a name. This is not checked.

**Terms found.**

| Page | Date read | Text says |
|---|---|---|
| https://integritate.eu/conditii-legale-2/ | 2026-11-05 | "© 2024 Agenția Națională de Integritate". "Reproducerea materialelor de pe site este autorizată, cu menţionarea sursei", within copyright law. A required prior agreement overrides it. |
| https://integritate.eu/conditii-de-utilizare-2/ | 2026-11-05 | Terms of use: cookies, acceptance, disclaimers. No re-use rule. A document on the site is not always the official text. |
| https://declaratii.integritate.eu/ | 2026-11-05 | The page is an Angular shell with the title "Declaratii de avere si interese". No terms in the shell. The agent did not read the application pages. |
| https://monitorul.ai/integritate | 2026-11-05 | See above. No licence. |

**Other risk signal.** Search results from news sites (g4media, informat.ro, digi24, 2025) say that a decision of the Curtea Constituțională changed the publication of declarations, and that ANI limited access to the archive of 2008 to 2022. The agent did not read the decision or the news pages. The status is open.

**What we take.** The institution name, the county and the count, to create `D` records and to show a declaration count. No declarant data.

**Interpretation.** The counts are aggregate figures and the names are names of institutions. The data protection risk looks low. The re-use risk depends on who made the Kibana and on its terms, which the agent could not find.

**Open question.** Which service gave the exports, and under which access conditions? Keep a note of this in `README.md`.

**Attribution.** Name "ANI, declaratii.integritate.eu" as the source of the data and "monitorul.ai" if the exports came from there.

## 5. posturi.gov.ro

**Who runs it.** The footer says: "Guvernul României, Direcția pentru Tehnologia Informației", Palatul Victoria, Bucharest. E-mail posturi@gov.ro. Copyright line: "Copyright © 2026 Posturi.gov.ro". Read 2026-11-05 on https://posturi.gov.ro/ and https://posturi.gov.ro/despre/.

**Terms found.**

| Page | Date read | Text says |
|---|---|---|
| https://posturi.gov.ro/ and `/despre/` (footer) | 2026-11-05 | "Continuarea navigării implică acceptarea termenilor şi condiţiilor." No terms text on the site. |
| http://oc.gov.ro/termeni-si-conditii-2/ (the terms link in `/despre/`) | 2026-11-05 | HTTP 500 with a plain request (also on `https://oc.gov.ro/`). Not read. |
| https://posturi.gov.ro/robots.txt | 2026-11-05 | `Disallow: /wp-admin/` only. |

No licence or re-use statement was found. The site cites H.G. 1.336/2022 as the legal basis of the portal.

**What we take.** From the owner's own scrape (the posturi repo): employer name, county, locality, number of postings. The list of employers also holds public bodies' names only.

**Interpretation.** The terms are unread. The data are names of public employers. The content of the postings (job text) is not used.

**Open question.** Read the terms at oc.gov.ro when the site works again, or ask posturi@gov.ro.

**Attribution.** Name "posturi.gov.ro (Guvernul României)" in *Despre date*.

## 6. Maps

**File.** `docs/reference/gis/ro_admin_lau_simplified_polygon.geojson` (6,989,645 bytes). The explorer files in `explorer/assets/gis/` come from it (`scripts/build_uat_maps.py`).

**Evidence of the origin (file metadata only).**

- The macOS attribute `kMDItemWhereFroms` of the file holds `https://geo-spatial.org/`. The quarantine attribute names the browser Brave and the time 2025-11-03 20:18 UTC.
- The same file, with the same size, lies in the owner's other project at `/Users/pax/devbox/GIS/api-places-search/data/cities/polygon/` (modified 2025-11-03) and has the same attribute. This agrees with the backlog note ("copied from `GIS/api-places-search`").
- The file has 3,186 features. The property names are `natCode`, `name`, `natLevName`, `countyId`, `countyCode`, `countyMn`, `county`, `regionId`, `regionCode`, `region`, `version`. Every feature has `version` = `2025-03-26`. The level names are Comuna (2,862), Oras (216), Municipiu (102 in two kinds) and "Sectoarele municipiului Bucuresti" (6).
- The page http://geo-spatial.org/descarcare/date/administrative-boundaries/ (read 2026-11-05) lists the layer `ro_admin_lau_simplified_polygon`, "UAT, România", with the variants polygon, line, simplified polygon, simplified line. The layer code equals our file name. The page says the current version reflects the administrative organisation of Romania in 2025.

**Terms found.**

| Page | Date read | Text says |
|---|---|---|
| http://geo-spatial.org/descarcare/date/administrative-boundaries/ | 2026-11-05 | Source for all datasets: ANCPI. "procesat de comunitatea geo-spatial.org pe baza datelor publice furnizate de Agenția Națională de Cadastru și Publicitate Imobiliară". No licence on the dataset entries. |
| http://geo-spatial.org/descarcare/ (footer) | 2026-11-05 | "Copyright © 2006 - 2026 geo-spatial.org și autorii. CC BY-SA 4.0". The page does not say that the footer covers the datasets. The page notes that the data migration from the old platform is still in progress. |
| Secondary: Wikimedia Commons file notices (search result) | 2026-11-05 | Say that the ANCPI geometry is under the Open Government Licence and the geo-spatial.org conversion under the same licence. The agent did not open the notices. This is old (about 2012) and secondary. |

**Not proved.** The agent cannot prove that the 2025-03-26 file in our folder is the same release as the web page today, because the file has no checksum. The name, the layer code and the file origin agree.

**Interpretation.**

- The origin is very likely geo-spatial.org, from ANCPI data.
- The only licence text found is the footer, CC BY-SA 4.0. If it covers the dataset, then an adaptation (our per-county files) needs attribution and the same licence (share-alike). The project is under EUPL v1.2. The agent did not verify whether EUPL v1.2 and CC BY-SA 4.0 are compatible for this case. The agent recalls that the EUPL appendix lists CC BY-SA 3.0, not 4.0, but this is unchecked.
- The ANCPI data are public data of a public body. Legea 179/2022 may apply to the ANCPI source (open geodata: see the annex of the law, "date geospațiale"). The agent did not check the annex.

**Open question.** Which licence does the geo-spatial.org catalogue (https://services.geo-spatial.org/geonetwork) give for this layer? The agent did not read it.

**Attribution.** "Limite administrative: ANCPI, procesat de geo-spatial.org (CC BY-SA 4.0)". Put it in *Despre date* and in a `NOTICE`-style line near `explorer/assets/gis/`. This records the backlog item "Confirm the origin and licence of …".

## 7. Law on the re-use of public-sector information

**Current act.** LEGE nr. 179 din 9 iunie 2022 privind datele deschise și reutilizarea informațiilor din sectorul public, Monitorul Oficial nr. 577 din 14 iunie 2022. Read on legislatie.just.ro (printable version, https://legislatie.just.ro/Public/FormaPrintabila/00000G1COH3DP6U0ANW3K9EH58HMCYV7, and https://legislatie.just.ro/Public/DetaliiDocument/256414 as listed) on 2026-11-05. The final lines say that the law "transpune Directiva (UE) 2019/1.024".

**Old act.** Legea 109/2007 privind reutilizarea informațiilor din instituțiile publice. The consolidated text on legislatie.just.ro stops at 2015-12-06 (https://legislatie.just.ro/Public/FormaPrintabila/00000G2U65EZ0OT1IZ41RJAZQBIH28HN). Art. 18(6) of Legea 179/2022 says that requests filed before the entry into force are solved under Legea 109/2007. Art. 18(5) repeals "orice prevederi contrare". The agent found no article that names Legea 109/2007 as repealed. The agent did not find the date of entry into force in the text. It did not check later amendments. Note: a "Legea 109 din 22-05-2025" on open data exists, but it is a law of the Republic of Moldova. It is not relevant.

**Text says (articles read).**

| Article | Content |
|---|---|
| 1(1) | The law covers documents that public entities and public enterprises created in their own activity. |
| 2 k) | "entitate publică" includes authorities and institutions of the public sector, UATs and bodies governed by public law. |
| 2 aa) | "Reutilizare" is the use of documents of public bodies, commercial or not, for a purpose other than the original public task. |
| 3 | The documents are re-usable for commercial or non-commercial purposes under chapters III and IV. |
| 4 | Any person may ask any public entity for re-use. The entity answers in 30 working days (50 at most). If no licence is needed, the entity uses a published standard licence. |
| 8(3) | Public entities are encouraged to publish by the principle "open by design and by default". |
| 9(1) | "Reutilizarea documentelor este gratuită". Only marginal costs may be recovered. |
| 11(1) | "Reutilizarea documentelor nu este supusă unor condiții", unless the conditions are objective, proportionate, non-discriminatory and justified by a general-interest aim. |
| 11(4) | Recommended open licences at the entry into force: CC BY 4.0 and CC0. |
| 1(2) | Exclusions: c) documents where third parties hold intellectual property rights; d) sensitive or special-regime data; f) documents with restricted access; g) logos, coats of arms and emblems; h) personal data that the law makes incompatible with re-use; j) cultural institutions other than libraries, museums and archives; k) pre-university schools and universities (other than research data); l) other documents of research bodies. Art. 1(2)(a): documents outside the public task of the entity. |
| 1(4) | The law does not affect the data protection laws (GDPR, Legea 506/2004). |
| 5 | Complaint route: first to ADR, then to the administrative court. |

**Interpretation (not a legal conclusion).**

- When a public body states no licence, the law gives no automatic licence text that the agent could find. Art. 3 and art. 11(1) say that the documents are re-usable and that conditions must be justified. Art. 4(5) says that a standard licence is used when a request is granted. This reads as a default of re-use, but the agent found no article that gives a default licence for documents published without one.
- The law covers "documents" of public bodies. A list that ANAF keeps for its own task is likely a document. A private service is not covered. A site that mixes content of third parties (ROePAS) is a mix.
- The exclusions of art. 1(2) matter for: coats of arms and logos (the county coats of arms in `explorer/assets/steme-judete/` are an exclusion under 1(2)(g), and the agent did not check their origin), personal data, and third-party rights.
- Licence and database right: Legea 8/1996 (copyright and related rights, including the right of the maker of a database). The agent did not read it. The text of OGL-ROU-1.0 refers to it.

### data.gov.ro and OGL-ROU-1.0

- Page https://data.gov.ro/pages/licence (title "Licența deschisă - data.gov.ro", read 2026-11-05): the portal integrated "Licența pentru o Guvernare Deschisă - OGL ROU 1.0" (issued 2014 by SGG). Datasets published earlier under it stay under it. The recommended licence is CC BY 4.0 (since July 2020, updated June 2022). CC0 is also named.
- Text of OGL-ROU-1.0: https://data.gov.ro/base/images/logoinst/OGL-ROU-1.0.pdf. The same file, with the same MD5, is at https://static.anaf.ro/static/copyright/OGLROU10_14032016.pdf. The agent read it on 2026-11-05.
  - Allowed: copy, publish, distribute, adapt, and use commercially or not.
  - Conditions: name the source with the text of the licensor; if the licensor gives none, show "Conține informații publice în baza Licenței pentru Guvernare Deschisă v1.0". Do not suggest an official status or a privileged relation with a public entity. Do not distort the information. Do not infringe personal data rights.
  - Exceptions (part D): personal data; information not published under the access or re-use laws or without the mention of this licence; logos and emblems of public bodies (unless inside a document or database); military insignia; third-party rights.
  - The text includes the right "să extragă și/sau să reutilizeze părți substanțiale" of a database.
- **Side finding.** The pipeline table says that SEAP has OGL-ROU-1.0 on 6 datasets. The OGL asks for the attribution sentence above. The agent found no such sentence in `README.md` or `explorer/despre.html`. The agent did not check `explorer/index.html`.

## Pages that the agent could not read

| Page | Result |
|---|---|
| https://www.anaf.ro/ | Plain request: "Pagina acces interzis". Fetch tool: empty. Not worked around. |
| http://oc.gov.ro/termeni-si-conditii-2/ and https://oc.gov.ro/ | HTTP 500. |
| https://www.e-guvernare.ro/ and https://e-guvernare.ro/ | No readable text. |
| https://declaratii.integritate.eu/ (application pages) | Only the page shell was read. |
| https://natlex.ilo.org/… | HTTP 403 (not needed). |
| https://roepas.ro/ro/conditiile-de-utilizare and a first URL with another spelling of "ț" | HTTP 404. The correct URL came from the footer link. |
| https://interoperable-europe.ec.europa.eu/… (EUPL text) | The page has no licence body. The EUPL compatibility list was not checked. |
| https://services.geo-spatial.org/geonetwork | Not opened. |
| Wikimedia Commons notices of the county maps | Seen only in a search summary. |
| Romanian version of the ROePAS terms | Not read. |
| Later amendments of Legea 179/2022 | Not checked. |

## Notes on the method

- Most pages were read with the fetch tool or with one plain `curl` request of a single page. Both used a browser-like user agent.
- Four documents were downloaded, each once: the ANAF API terms PDF (235 KB), the OGL text from data.gov.ro and from ANAF (11 KB each), and the Registrul PDF (1.2 MB, 208 pages). The agent read the Registrul PDF for its metadata and its first page, and searched its text for licence words. The owner may count this download against the rule "no bulk fetch".
- The fetch tool read the first 100,000 characters (about 0.5 MB in full) of the sitemap of roepas.ro, to look for a terms page. The sitemap lists service pages only.
- No record data or CUI was sent to any service. No form was filled.

## What the owner must decide

1. **ROePAS (highest signal).** The terms forbid scraping and mass copying. The options:
   - a) Ask ADR for written permission, or file a re-use request under art. 4 of Legea 179/2022. Keep the data until the answer.
   - b) Remove the ROePAS-only fields (website, e-mail, phone, coordinates, procedure counts) and the 481 `R` records from the published files.
   - c) Keep the data and accept the risk. The text of art. 11(1) of the law may help, but the agent cannot say.
   - Either way, ask a lawyer whether the clause on "extracting data automatically" binds a visitor who only reads public pages.
2. **ANAF list.** Decide whether to ask ANAF to state the licence of the list. Until then, treat the 2009 notice (reproduction with the source) as the working rule, and attribute ANAF.
3. **Registrul Național.** Decide who to ask about the publisher. The register is of 2020.
4. **ANI.** Record in `README.md` which service gave the Kibana exports and under which access conditions. Decide whether the access "case by case" of monitorul.ai allows the owner to republish aggregate counts.
5. **posturi.gov.ro.** Decide whether to ask posturi@gov.ro for the terms, or to wait for oc.gov.ro to work.
6. **Maps.** Decide how to treat CC BY-SA 4.0 (share-alike) for the per-county files, or find the licence of the layer in the geo-spatial.org catalogue. Decide whether to give the explorer map files a separate licence line.
7. **Attribution.** Approve one attribution block for *Despre date* with these lines: ANAF, ROePAS (if kept), Registrul Național, ANI, posturi.gov.ro, geo-spatial.org with ANCPI, and the OGL-ROU-1.0 sentence for the SEAP datasets under that licence.
8. **Licence column.** Replace "Not recorded" in the table *Sources* of `docs/pipeline.md` with the findings of this report after the owner decides.
9. **Legal advice.** Decide whether to pay for a short legal opinion on three points: the ROePAS clause, the share-alike of the maps, and the default regime of Legea 179/2022 for documents with no stated licence.
