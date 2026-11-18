# Fetch notes

How to reach each source from a Claude Code cloud session: which URL patterns work, how to
parse them, which ones block plain requests, and the traps learned the hard way.

Runs **edit this file in place** when a route changes (put the date on the change). It is
shared knowledge: if you improve a row for a public board, it helps everyone who uses the
template.

The board rows below were verified from a cloud session in Germany between October and
November 2026. Treat any row older than a few weeks as "probably still right, check it".

---

## General rules

- **Plain `curl` with a desktop User-Agent** reaches most boards. Use `curl -sL --compressed`
  by default: some servers redirect and some gzip unconditionally.
- **Headless Chromium + Playwright is usually pre-installed** in the cloud environment
  (`require('playwright')`, `chromium.launch()` with no options; binary at
  `/opt/pw-browsers/chromium`). Use it for pages that render client-side or 403 plain
  requests. It does **not** beat Cloudflare/WAF challenges or 429 rate limits.
- **429 is rate limiting, not blocking.** Space requests out or try another hour.
  **403 with a tiny body** is usually a bot block; try the browser once, then record it.
- **A proxy error is not a site error.** `CONNECT tunnel failed, response 502` or
  `net::ERR_TUNNEL_CONNECTION_FAILED` means the environment's network policy refused the
  host. Note it and tell the user which host to allow; no fetch method will get through.
- **Pages that say "no vacancies" or show no rows usually mean no vacancies**, not a fetch
  failure. Record the body size: a sudden drop is the early warning that a route broke.

## Verification rules

1. **A posting can be live on a board and closed at the employer.** Always open the
   employer's own *detail* page, never its index. If it says closed, fetch a neighbouring id
   to confirm the status is per-job and not a site-wide fault.
2. **Dedup on URL, board id, title and employer, all four.** Re-posts come back with a new
   board id; employers lose punctuation ("W&S" → "WS"); job titles swap word order.
   `tools/seen.py` handles the common cases. Grep `seen/index.csv` by hand for anything
   it flags as REVIEW.
3. **Board dates lie in both directions.** Aggregators refresh old ads with a new date, and
   some carry an expiry that is just "posted + 30 days". Prefer the employer's own date.
4. **Index-page counts hide turnover.** A board whose row count is unchanged may still have
   new rows: old ads stay up for months while new ones arrive. Diff by id, not by count.
5. **Some ads are empty shells** (title, place, contact, no text). Report them as leads to
   phone, and say so; don't guess requirements.

## Language notes for German-speaking boards

German titles come in many spellings; treat these as the same title and don't search each:

- **Gender notation:** `(m/w/d)` · `(w/m/d)` · `(d/m/w)` · `(m/f/d)` · `(all genders)` ·
  `(a*)` · `(gn)` · `*in` · `:in` · `_in` · `/-in` · Binnen-I (`DesignerIn`) · plain masculine.
- **Compounds:** written together, hyphenated or spaced (`Produktdesigner` /
  `Produkt-Designer` / `Produkt Designer`).
- **Inverted word order:** `Computational Design Specialist` ↔ `Specialist Computational Design`.
- **Experience wording.** Multi-year: *mehrjährige / langjährige / fundierte
  Berufserfahrung*, *mind. 3 Jahre*, *eigenverantwortliche Projektleitung*. Entry-friendly:
  *erste Berufserfahrung*, *idealerweise*, *Berufseinsteiger\*in*, *Quereinsteiger\*in*.
  Watch sentences that put a multi-year demand and an "or willingness to learn" alternative
  together: report them, quoting both clauses.
- **Trade-qualification ads** (*Ausbildung / Meister / Techniker oder vergleichbare
  Qualifikation*) often accept an equivalent degree. Report with the equivalence clause quoted.

---

## Machine-readable routes

### National and general boards

| Source | Route | Parse / notes |
|---|---|---|
| **Arbeitsagentur Jobbörse** (DE) | `arbeitsagentur.de/jobsuche/suche?angebotsart=1&was=<stem>&veroeffentlichtseit=7&sort=veroeffdatum&page=<1..6>` | `<script id="ng-state">` JSON → `suchergebnis.ergebnisliste[]`: `stellenangebotsTitel`, `firma`, `referenznummer`, `datumErsteVeroeffentlichung`, `stellenlokationen[0].adresse.{ort,region}`; total in `suchergebnis.maxErgebnisse`. Detail: `/jobsuche/jobdetail/<ref>` → `jobdetail.stellenangebotsBeschreibung`. **`ersteVeroeffentlichungsdatum` on the detail is often null: take the date from the search row.** The detail JSON also carries `quereinstiegGeeignet`, `festgehalt`, `vertragsdauer`, `arbeitszeitVollzeit` (contract type and pay without a second fetch). ~130 stems ≈ 4 min at 6 threads. Weekend volumes are mostly agency bulk-posting. Re-posts get a new Referenznummer: dedup on title + employer too |
| **StepStone** (DE) | `stepstone.de/jobs/<stem>?sort=2&ag=age_3` (+`&page=2`) | regex `stellenangebote--([^"/]*?)--(\d{6,9})-inline\.html`. Build the title/employer key from the slug and dedup **before** fetching details. Detail page JSON-LD `JobPosting` has `datePosted` / `validThrough`; **`validThrough` is always posted + 30 days, not a deadline.** **An ad id more than ~100k below the day's highest id is a refreshed old ad**, whatever `datePosted` says. Stems with a dot (`three.js`) 404: use `webgl`. Records can splice one ad's title onto another's body: read the body |
| **jobs.ch** (CH) | `jobs.ch/en/vacancies/?term=<kw>` | The page's `application/ld+json` is a `CollectionPage` → `ItemList` → `ItemListElement` → `JobPosting`. **Walk the JSON recursively for `@type == "JobPosting"`**; a top-level-only parser returns zero rows on a healthy page. Has `title`, `hiringOrganization`, `addressLocality`, `datePosted`, `url` |
| **jobs.ac.uk** (UK academic) | Playwright: `https://www.jobs.ac.uk/search/?keywords=<terms>&sort=date` | **Use the browser**: plain fetches ignore the keyword. Rows render server-side; each ad page has Placed On, Closes, Salary, Contract Type and full text in `document.body.innerText`. URLs are `/job/<ref>/<slug>`; the ref is the dedup key. ~20 cuts ≈ 4 min. Search role words, not tool names (`Rhino`, `Grasshopper` return zero). Most results are unrelated PhD studentships. UK posts need right-to-work: flag sponsorship |
| **holzjob.eu** (DACH timber) | `holzjob.eu/sitemap.xml` → `/company/<co>/job/<id>-<slug>` | Diff **row by row on id**; the total count barely moves. Ad pages show **"Online seit: dd.mm.yyyy"** at the bottom (it is a dated board). Some ads have no text |
| **EURAXESS, AcademicTransfer (NL), findaphd** | | Accept a keyword URL but **silently ignore it** and return a generic list. Don't trust results; reach them via web search or the browser |
| **Indeed** | | 401/403 to curl and WAF-blocked in the browser |
| **academicpositions.com** | | 403 |

### Design, creative and cultural boards

| Source | Route | Parse / notes |
|---|---|---|
| **Berlin Design Network** | `https://www.berlin-design-network.org/jobs` (**`www.` required**) | Server-rendered table: position / contract / discipline / organisation / language / publication date / location. A seniority tag makes the junior filter free |
| **dasauge** (DE) | `dasauge.de/jobs/` | Board answers 200; ad URLs `dasauge.de/jobs/<6-hex>-<slug>`. **Keyword cuts `dasauge.de/jobs/q:<term>` have been 403 to curl and to the browser (WAF challenge) since 15.11.2026.** `/jobs/feed` is empty. Mostly graphic/marketing roles in late 2026 |
| **museumsbund.de** (DE museums) | `museumsbund.de/stellenangebote/` | Exhibition, technical and workshop posts that design boards don't carry |
| **McNeel / Rhino forum: Jobs** | `discourse.mcneel.com/c/jobs-portfolios/l/latest.json` (**needs `curl -L`**) | `topic_list.topics[]`; body at `/t/<slug>.json`. Topic ids increase strictly: keep a high-water mark |
| **three.js forum: Jobs** | `discourse.threejs.org/c/jobs/9.json` | Same Discourse shape. Dedup on topic id and slug |
| **fablabs.io** | `fablabs.io/jobs` (HTML) | `/api/0/jobs` 404s. No dates and mostly stale: a lead list |
| **Parametric Architecture jobs** | `parametric-architecture.com/jobs/` → each post's JSON-LD `datePublished` | **An archive, not a board**: most posts are 2020–2023. Check monthly; read the date first |
| Creative City Berlin, getbaito, Core77/Coroflot, creativeapplications.net | | Blocked (403/429), browser included, as of 11.2026. Coroflot opens in the browser but is US-only |

### Universities and research institutes (DACH, NL, Nordics, UK, ES)

| Source | Route | Parse / notes |
|---|---|---|
| **ETH Zurich** | `jobs.ethz.ch/` (one page, all rows) | regex `href="(/job/view/[^"]+)"[^>]*aria-label="([^"]+)"`. A closed ad redirects to the list. Turns over fast: read titles, don't compare counts. `www.ethz.ch/job/view/` links 404 |
| **TU Delft** | `careers.tudelft.nl/sitemap.xml` (**no `www.`**: it 502s) | `<loc>` entries containing `/job/`. `lastmod` is the same on every entry: **diff on job id** |
| **TU Berlin** | `jobs.tu-berlin.de/stellenausschreibungen.atom` | Clean Atom feed with `<updated>`. Titles are generic ("Wiss. Mitarbeiter\*in"): the subject is only on `/stellenausschreibungen/<id>`. Diff on ids |
| **TU Graz** | `personal.tugraz.at/api/erec/public/job-postings` | Clean JSON: `job_title`, `organisational_unit`, `application_deadline`, `id` |
| **TUM** | `portal.mytum.de/jobs/wissenschaftler/` | 200 to curl again since 15.11.2026 (was 403). `?start=10` pagination 404s: page 1 only |
| **Universität Stuttgart** | `careers.uni-stuttgart.de/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=0&locale=en_US` | SuccessFactors `href="/job/<slug>/<id>/"`. Thin; institute news pages (e.g. `icd.uni-stuttgart.de/news/`) carry more |
| **Bauhaus-Universität Weimar** | `uni-weimar.de/de/universitaet/aktuell/stellenausschreibungen/` (`curl -L`, it 307s) | Parse page text: faculty, title, `Bewerbungsschluss` in plain blocks |
| **UdK Berlin** | `udk-berlin.de/universitaet/stellenausschreibungen/aktuelle-jobs/` | `/service/stellenangebote/` 404s |
| **weißensee kunsthochschule** | `kh-berlin.de/hochschule/stellenangebote` | No rows = no vacancies |
| **Burg Giebichenstein Halle** | `burg-halle.de/institution/stellenausschreibungen/` | Ads at `/artikel/a/<slug>` |
| **HfG Karlsruhe** | `hfg-karlsruhe.de/aktuelles/offene-stellen` | No rows = no vacancies |
| **Hochschule Anhalt** | **`hs-anhalt.de/stellenangebote`** (short path; the long one resets the connection) | Grouped lists, each with `Nr.`, Bewerbungsfrist and pay grade in plain text |
| **Hochschule Bielefeld** | `hsbi.de/karriere/stellenangebote` | Grouped with counts. Ad PDFs `/jobs/download?jobid=<n>` 404 once closed: a cheap closed-check |
| **HCU Hamburg** | `hcu-hamburg.de/universitaet/stellenausschreibungen` | Full text and Bewerbungsschluss in page body |
| **FHNW incl. HGK Basel** | `apply.refline.ch/655298/search.html` | Table: Stelle / Hochschule / Arbeitsort; detail `…/<job>/pub/<n>/index.html` |
| **ZHdK** | `apply.refline.ch/788531/search.html` | Has a **Bewerbungsfrist column**. Bodies under ~2 KB mean the route broke |
| **HSLU** | `hslu-jobs.ch` | Server-rendered text, not a table |
| **Royal Danish Academy (CITA)** | `kglakademi.dk/en/vacancies` → `candidate.hr-manager.net/ApplicationInit.aspx?cid=5001&ProjectId=<n>&DepartmentId=7810&MediaId=5` | `<title>` is the job title; deadline in body. The index's date column is misaligned: trust the ad |
| **DTU** | `efzu.fa.em2.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList&finder=findReqs;siteNumber=CX_1,limit=200,sortBy=POSTING_DATES_DESC` | `items[0].requisitionList[]` → `Title`, `PostedDate`, `Id`. **`expand=requisitionList` is required.** The detail REST route 400s: use the browser for details |
| **Aalto** | POST `aalto.wd3.myworkdayjobs.com/wday/cxs/aalto/aalto/jobs` body `{"appliedFacets":{},"limit":20,"offset":0}` | `jobPostings[]`; `limit` max 20, page with `offset` |
| **KTH** | `kth.se/lediga-jobb?l=en` | `href="/lediga-jobb/<id>?l=en"` |
| **IAAC Barcelona** | `iaac.net/about/work-with-us/` | Table with Posted on + full text + deadline. "Open" status is unreliable: check the deadline |
| **Fraunhofer** | `jobs.fraunhofer.de/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=0` | SuccessFactors rows |
| **Matters of Activity (HU Berlin)** | `matters-of-activity.de/en/jobs/` (trailing slash required) | States plainly when there are no vacancies |
| **Design Academy Eindhoven** | browser: `designacademy.nl/page/6123/jobs` → list at `welcome.designacademy.nl/vacaturebeschrijvingen/vacatures-outsite` | 403 to curl. "No data to be shown" = no vacancies. DAE takes no open applications |
| Chalmers · TU Wien `jobs.tuwien.ac.at` · AA `aaschool.ac.uk/about/work-at-the-aa` · UCL/Bartlett · HFBK Hamburg | | No readable rows (client-side, blocked, or no vacancy page) as of 11.2026 |

### Companies and studios (selection)

| Source | Route | Notes |
|---|---|---|
| **Ottobock** | `jobs.ottobock.com/search/?q=&sortColumn=referencedate&sortDirection=desc&startrow=0` | SuccessFactors. **`startrow` steps in 25.** `/en/jobs` is an empty shell |
| **MX3D** | `mx3d.com/about/careers/` (`--compressed`) | Ads at `mx3d.com/vacancie/<slug>/` (sic) |
| **ATELIER BRÜCKNER** | `atelier-brueckner.com/de/jobs` | Ads at `/de/jobs/<slug>` |
| **Studio Olafur Eliasson** | `olafureliasson.net/jobs` | Says plainly when there are none |
| **WHITEvoid** / **KINETIC LIGHTS** | `whitevoid.com/jobs` · `kinetic-lights.com/jobs/` | PDFs; upload month in `wp-content/uploads/<yyyy>/<mm>/` is the only date. Kinetic Lights titles are only in the link's `aria-label` |
| **BigRep** | `bigrep.jobs.personio.de/?language=en` | The Personio XML is empty; this renders |
| **Combeenation** · **Expivi** | `combeenation.com/karriere/` · `expivi.com/company/careers/` | Configurator companies |
| **Blumer-Lehmann** | | Rows render client-side; it posts to jobs.ch, StepStone, Indeed and holzjob.eu, so cover it there |
| `jobs.bam.de` | | Refused by the cloud proxy (502 tunnel). Read BAM ads from Arbeitsagentur (no deadline there) |

Studio and company careers paths that 404'd or blocked in 11.2026 (check monthly at most,
or approach directly): Studio RAP, The New Raw, Design-to-Production, Noumena, Maffeis,
Format Engineers, Octatube, seele, Lufthansa Technik, raumlaborberlin, Random International,
Field.io, Bühnenservice Berlin, Ai Build, Hyperion Robotics, Speckle, Roomle, Xolo, YOU MAWO,
Vectary, Spline, 3Shape, Museumstechnik, Duncan McCauley, nTop, Formlabs, trinckle (on and
off), cadwork; 403: Nagami, ROK, Tylko, HEXR; 429: Zellerfeld; 502: WASP.

---

## Changelog

<!-- Runs add one line per change: date, source, what changed. -->

- 2026-11-18: file created from the notes of an earlier deployment.
