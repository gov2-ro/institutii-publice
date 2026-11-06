# Draft: message to the author of tipizatul.eu

Status: draft, not sent. The owner approves the text and sends it, or asks an agent to send it.
Channel: not decided. The options are an issue in `iamandiradu/tipizatul.eu` (public) or a private message.
Facts: measured on 2026-11-06, bundle built 2026-08-18. See `docs/activity-log.md`. Check the numbers again before you send.

---

**Subiect: tipizatul.eu și org.gov2.ro: legături între instituții și o hartă nume → CIF**

Salut,

Sunt pax, de la [gov2.ro](https://gov2.ro). Ținem [org.gov2.ro](https://org.gov2.ro), o listă consolidată de instituții publice și companii de stat din România, cu CIF, site, contacte și sursa fiecărui câmp.

Tipizatul.eu ne-a plăcut mult, așa că am pus deja legături către el. Pe pagina unei instituții din org.gov2.ro apare acum „Proceduri și formulare → tipizatul.eu”, de exemplu:
`https://www.tipizatul.eu/proceduri?q=Institutia%20Prefectului%20Judetul%20Br%C4%83ila`

Pentru asta am legat numele de instituții din `procedures.json` de înregistrările noastre. Din cele 688 de nume cu documente, am legat 448, fiecare la un singur CIF. Am lăsat deoparte subunitățile (15 direcții și centre din ministere) și numele fără corespondent sigur. Harta este publică: [`curation/tipizatul.csv`](https://github.com/gov2-ro/institutii-publice/blob/main/curation/tipizatul.csv).

**Ce îți oferim.** Poți folosi harta ca să ai CIF-ul la instituțiile din catalog. Prin CIF ajungi la restul datelor din org.gov2.ro. Dacă găsești o legătură greșită, spune-ne și o corectăm.

**Ce te-am ruga:**

1. **O adresă stabilă pentru o instituție**, de exemplu `/institutie/<CIF>` sau `/proceduri?cif=<CIF>`. Acum legătura depinde de nume, așa că se poate rupe dacă o instituție este redenumită în catalog. Îți trimitem CIF-urile, deci nu trebuie să le cauți.
2. **Licența datelor din `procedures.json`.** Repo-ul are licență MIT pentru cod, dar nu am găsit una pentru date. Deocamdată păstrăm doar numele instituțiilor, ca să construim legătura. Dacă datele se pot refolosi, ne-ar ajuta să știm în ce condiții.

Dacă preferi să nu avem aceste legături sau vrei să arate altfel, spune-ne și le schimbăm.

Îți mulțumim pentru proiect!

pax, [gov2.ro](https://gov2.ro)
