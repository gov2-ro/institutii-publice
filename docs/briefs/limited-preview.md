# Brief: limited preview polish

For: Sonnet. Owner request 2026-10-27: the owner will show the site to a limited circle.
Pages: `explorer/index.html`, `explorer/organizare.html`, `explorer/despre.html`. Keep the DS rules of `CLAUDE.md`.

Opus already made the image assets (do not regenerate them):
- `explorer/assets/favicon/*` regenerated from `g2-0.png` (96, 180, 192, 512, ICO 16/32/48). `favicon.svg` is deleted:
  remove its `<link>` on all pages. The manifest icons use `purpose: any`.
- Header logo: `explorer/assets/img/g2-0-64.png` (64 × 64, transparent, black outline).
- Social image: `explorer/assets/img/og.png` (1,200 × 630).

## Tasks (all three pages unless stated)
1. **Open Graph and Twitter meta.** `og:title`, `og:description`, `og:type=website`, `og:url` (absolute, per page:
   https://org.gov2.ro/, …/organizare.html, …/despre.html), `og:image=https://org.gov2.ro/assets/img/og.png` with width,
   height and `og:image:alt`, `og:locale=ro_RO`, `og:site_name=org.gov2.ro`, `twitter:card=summary_large_image`, and a
   `<meta name="description">` where it is missing. Descriptions in Romanian, at most about 160 characters.
2. **Logo.** Replace `gx00.png` with `g2-0-64.png` in the header. The outline is black and the header is dark: put the
   image on a light rounded tile (local `org-` rule, DS tokens), so it is visible in both schemes.
3. **Header.**
   - Remove the nav links "Structura statului", "Domenii" and "Listă" from the header. The views stay.
   - The counter shows the active count and the total: for example "2.299 din 24.981". Keep `role="status"`.
   - Remove the border around the "Opțiuni" summary. Keep a visible focus and a 44 px target.
4. **Landing.**
   - Remove the two lines under the search: the examples stay; the "24.981 de instituții · surse … · Despre" line goes.
   - "Sari la:" links are bold: Domenii · Structura statului · Lista completă. "Lista completă" is the last
     one and opens the list view (`#v=list`, as the old nav link).
5. **Footer.** One row, vertically centred (the text, "un proiect gov2.ro" and the GitHub icon share one centre line).
   Add the view links: Structura statului · Domenii · Lista completă · Cum e organizat statul · Despre. From
   `organizare.html` and `despre.html` they point to `index.html#v=…`. Phones may wrap; no horizontal scroll.
6. **Disclaimer.** A dismissable notice at the top of every page: "Acesta nu este un proiect oficial al Guvernului
   României." Use the DS notice bar (`COMPONENTS.md`, "Notice bar"). A close button with `aria-label="Închide"`.
   The dismissal is kept in `localStorage` key `org-disclaimer-closed` (try/catch; without storage it shows again on
   the next load). The notice must not cover content and must not move focus on load.
7. **Despre.**
   - For "Declarații de integritate ANI", add the source link https://monitorul.ai/integritate.
   - Add a section "Contact": problems and suggestions as GitHub issues
     (https://github.com/gov2-ro/institutii-publice/issues), or e-mail to cancelarie@gov2.ro (a `mailto:` link).

## Checks
- JS syntax on the three pages; 44 unit tests; roots check.
- No horizontal scroll at 320, 390, 768, 1,024 and 1,440 px, both schemes. Targets ≥ 44 px.
- The meta tags parse: print the `og:*` and `twitter:*` values of each page from the served HTML.
- The disclaimer: shows, closes, stays closed after reload, shows again with storage blocked, Tab reaches the close button.
- Legacy hashes work (`#v=stat`, `#v=fam`, `#v=list`, `#v=loc&k=Cluj`, `#id=…`).
- Screenshots with suffix `-r7`: landing 1440 light and dark (top with the disclaimer), landing 390 light, footer 1440
  light and dark, despre 1440 light (Contact section visible).

Commit (Sonnet co-author line), no tag, no publish. Add the activity-log entry.
