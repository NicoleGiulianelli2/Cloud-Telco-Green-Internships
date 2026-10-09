# Cloud · DevOps · Telco · Green computing — Internship & PhD Tracker

A small tracker that fetches early-career postings from ~80 companies, labs, PhD portals and graduate
programmes every morning and publishes them as a filterable table on GitHub Pages.

Topics: **DevOps**, **cloud & infrastructure**, **telco** (5G/6G, RAN, networking), **green / energy-aware computing**
(plus ML and research as optional filters).

The main difference from a plain internship list is the **"Graduates?" column**: it tells whether a posting can be
taken by someone who has *already graduated* (an extra-curricular internship, a graduate programme, a PhD), or whether
it requires current enrolment at a university (curricular internship: "currently enrolled", "returning to school",
*convention de stage*, *Pflichtpraktikum*, *tirocinio curriculare*, master thesis…).

Adapted from [MicheleArmillotta/Cybersec-Research-Internships](https://github.com/MicheleArmillotta/Cybersec-Research-Internships)
(same architecture, fetchers and GitHub Actions setup).

## Publish it (first time, ~5 minutes)

1. Create a new **public** repository on GitHub (e.g. `Cloud-Telco-Green-Internships`) and push this folder:
   ```
   git init && git add . && git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/<you>/Cloud-Telco-Green-Internships.git
   git push -u origin main
   ```
2. **Settings → Pages**: Source = *Deploy from a branch*, Branch = `main`, folder = `/docs`.
3. **Actions** tab: enable workflows if asked, open *Update postings* and click **Run workflow**. The first run takes
   10–20 minutes because it downloads every job description once; later runs reuse the cached results.
4. The site is at `https://<you>.github.io/Cloud-Telco-Green-Internships/`. It then refreshes every day at 06:00 UTC.

## How it works

```
GitHub Actions (cron) -> python -m scraper -> docs/data/*.json -> git commit -> GitHub Pages
```

- `scraper/sources.py` — companies / labs / portals and which backend to use (Greenhouse, Lever, Ashby, Workable,
  Workday, SmartRecruiters, Eightfold, Oracle HCM, Phenom, a generic `page_scan`, a `link_scan` for job portals such as
  Inria, EURAXESS, FindAPhD, and an experimental `vie` fetcher for VIE offers).
- `scraper/fetchers.py` — one fetcher per backend, plus `fetch_detail()` that downloads a job description.
- `scraper/classify.py` — the keyword rules:
  - **kind**: internship · graduate programme / trainee / VIE · PhD · research engineer / predoc · junior job.
    Senior, staff, manager, postdoc and professor posts are dropped.
  - **topics**: devops · cloud · telco · green · ml · research (from the title; dashed tags = found only in the description).
  - **eligibility**: `graduates` / `students` / `unknown`, with the matched phrase shown on hover.
    PhD, graduate-programme and research-engineer posts count as open to graduates. In France a *stage* legally needs a
    *convention de stage* from a school, so French stages without an explicit "graduates welcome" are marked `students`.
  - **region**: Europe / remote / outside Europe, with the country when it can be recognised.
- `scraper/run.py` — runs the sources in parallel, keeps only early-career titles, downloads descriptions for the new
  ones (max 80 per source per run, cached afterwards in `jobs.json`), merges with the previous data to keep
  `first_seen`, and keeps old postings from sources that failed today.

## Known limitations

- Rules are keyword based, so expect some wrong labels: always open the posting before applying.
- Sources marked `# unverified` in `sources.py` are best guesses (ATS slug or page layout). If one is wrong, the
  *Source status* panel on the site shows the error. Fix the slug/URL or delete the entry.
- JavaScript-only career sites (ESA, JRC, imec, most telecom operators) can't be scraped with plain HTTP requests;
  they are linked in the *Check by hand* section of the page instead.
- `.github/workflows/probe.yml` runs any shell command on a GitHub runner and pushes the output to the `probe` branch:
  handy to see what a broken source actually returns (e.g. `curl -s https://... | head -c 5000`).

## Run locally

```
pip install -r requirements.txt
python -m scraper                          # all sources
ONLY="Inria,Canonical" python -m scraper   # a subset, for debugging
MAX_DETAILS=0 python -m scraper            # skip description downloads (fast, eligibility mostly "unclear")
```

## Customising

- **Add a company**: append an entry to `scraper/sources.py`. For Greenhouse/Lever/Ashby only the board slug is needed;
  if you don't know the ATS, use `ats_any` with several candidates.
- **Keep ML-only postings** from large boards (Inria, Bosch, portals): add `"ml"` to `CORE_TOPICS` in `classify.py`.
- **Change keywords**: edit the pattern lists in `classify.py` and bump `CLASSIFIER_VERSION` so cached postings are
  re-classified on the next run.
