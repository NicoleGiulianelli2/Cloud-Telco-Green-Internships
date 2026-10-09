"""Sources to track: DevOps / cloud & infrastructure / telco / green computing, plus PhD and
post-graduate programmes.

group:   big | cloud | telco | green | research | portal | programme
type:    one of scraper.fetchers.FETCHERS
Optional per-source keys:
  require_topic   drop postings whose title AND description match none of the topics
                  (use it for huge or off-topic boards: Bosch, SAP, Inria, portals...)
  kind_hint       kind assigned when the title says nothing (e.g. "phd" for FindAPhD)
  default_location / default_region   used when the posting has no location
  max_details     cap on description downloads per run (default 80)
Fields like slug / site / host accept a list of candidates; the first working one is used.
ats_any tries several backends in order (useful when the ATS is not known for sure).

Entries marked "unverified" are best guesses: if they fail, the Source status panel says so.
"""

# Typical search terms for boards that need a query (Workday, SmartRecruiters, Eightfold, Oracle...)
Q_EARLY = ["intern", "internship", "graduate", "trainee", "PhD"]
Q_INFRA = ["cloud intern", "devops intern", "network intern", "infrastructure intern", "graduate cloud",
           "graduate network", "SRE intern", "PhD"]


def _any(*cands):
    """ats_any candidates helper: _any(("greenhouse", "x"), ("lever", "x"))."""
    return [{"type": t, "slug": s} for t, s in cands]


SOURCES = [
    # ------------------------------------------------------------- Big tech / industry
    {"company": "Google", "group": "big", "type": "google", "require_topic": True,
     "queries": ["cloud intern", "infrastructure intern", "network intern", "site reliability intern",
                 "student researcher", "PhD intern", "graduate"]},
    {"company": "Amazon / AWS", "group": "big", "type": "amazon", "require_topic": True,
     "queries": ["AWS intern", "cloud intern", "network intern", "graduate cloud", "PhD intern", "sustainability intern"]},
    {"company": "IBM", "group": "big", "type": "ibm", "require_topic": True,
     "queries": ["intern cloud", "intern infrastructure", "research intern", "graduate"]},
    {"company": "IBM Research", "group": "big", "type": "page_scan",
     "url": ["https://research.ibm.com/careers", "https://www.zurich.ibm.com/careers/"]},
    {"company": "NVIDIA", "group": "big", "type": "workday", "host": "nvidia.wd5.myworkdayjobs.com", "require_topic": True,
     "tenant": "nvidia", "site": ["NVIDIAExternalCareerSite"], "queries": ["intern", "PhD", "graduate"]},
    {"company": "Intel", "group": "big", "type": "workday", "host": "intel.wd1.myworkdayjobs.com", "require_topic": True,
     "tenant": "intel", "site": ["External"], "queries": ["intern", "graduate", "PhD"]},
    {"company": "Cisco", "group": "big", "type": "workday", "host": "cisco.wd5.myworkdayjobs.com",
     "tenant": "cisco", "site": ["Cisco_Careers"], "queries": Q_EARLY},
    {"company": "Red Hat", "group": "big", "type": "workday", "host": "redhat.wd5.myworkdayjobs.com",
     "tenant": "redhat", "site": ["Jobs", "jobs"], "queries": Q_EARLY},
    {"company": "SUSE", "group": "big", "type": "workday", "host": "suse.wd3.myworkdayjobs.com",  # unverified
     "tenant": "suse", "site": ["Jobsatsuse", "SUSE", "External"], "queries": Q_EARLY},
    {"company": "HPE (incl. Juniper)", "group": "big", "type": "workday", "host": "hpe.wd5.myworkdayjobs.com",
     "tenant": "hpe", "site": ["Jobsathpe", "ACJobSite"], "queries": Q_EARLY},
    {"company": "Broadcom / VMware", "group": "big", "type": "workday", "host": "broadcom.wd1.myworkdayjobs.com",
     "tenant": "broadcom", "site": ["External_Career"], "queries": Q_EARLY},  # unverified site
    {"company": "Equinix", "group": "big", "type": "workday", "host": "equinix.wd1.myworkdayjobs.com",  # unverified
     "tenant": "equinix", "site": ["External"], "queries": Q_EARLY},
    {"company": "Airbus", "group": "big", "type": "workday", "host": "ag.wd3.myworkdayjobs.com",  # unverified
     "tenant": "ag", "site": ["Airbus"], "require_topic": True,
     "queries": ["VIE", "graduate", "cloud", "network", "PhD", "thèse"]},
    {"company": "Thales", "group": "big", "type": "workday", "host": "thales.wd3.myworkdayjobs.com",  # unverified
     "tenant": "thales", "site": ["Careers"], "require_topic": True,
     "queries": ["VIE", "graduate", "cloud", "devops", "5G", "PhD", "thèse"]},
    {"company": "Bosch", "group": "big", "type": "smartrecruiters", "slug": ["BoschGroup"], "require_topic": True,
     "queries": ["cloud intern", "devops", "graduate", "PhD", "network intern", "energy intern"]},
    {"company": "Spotify", "group": "big", "type": "lever", "slug": ["spotify"]},
    {"company": "Adyen", "group": "big", "type": "greenhouse", "slug": ["adyen"]},
    {"company": "Databricks", "group": "big", "type": "greenhouse", "slug": ["databricks"]},
    {"company": "Snowflake", "group": "big", "type": "phenom",
     "url": ["https://careers.snowflake.com/us/en/search-results?keywords=intern"]},
    {"company": "MongoDB", "group": "big", "type": "greenhouse", "slug": ["mongodb"]},
    {"company": "Hugging Face", "group": "big", "type": "workable", "slug": ["huggingface"]},

    # ------------------------------------------------------------- Cloud / DevOps / infra
    {"company": "Canonical", "group": "cloud", "type": "greenhouse", "slug": ["canonical"]},
    {"company": "GitLab", "group": "cloud", "type": "greenhouse", "slug": ["gitlab"]},
    {"company": "Grafana Labs", "group": "cloud", "type": "greenhouse", "slug": ["grafanalabs"]},
    {"company": "Datadog", "group": "cloud", "type": "greenhouse", "slug": ["datadog"]},
    {"company": "Elastic", "group": "cloud", "type": "greenhouse", "slug": ["elastic"]},
    {"company": "Cloudflare", "group": "cloud", "type": "greenhouse", "slug": ["cloudflare"]},
    {"company": "Fastly", "group": "cloud", "type": "greenhouse", "slug": ["fastly"]},
    {"company": "Pure Storage", "group": "cloud", "type": "greenhouse", "slug": ["purestorage"]},
    {"company": "Confluent", "group": "cloud", "type": "ashby", "slug": ["confluent"]},
    {"company": "Vercel", "group": "cloud", "type": "greenhouse", "slug": ["vercel"]},
    {"company": "Tailscale", "group": "cloud", "type": "greenhouse", "slug": ["tailscale"]},
    {"company": "Docker", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "docker"), ("lever", "docker"), ("greenhouse", "dockerinc"))},
    {"company": "Kong", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "kong"), ("greenhouse", "kong"), ("lever", "kong"))},
    {"company": "Chainguard", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "chainguard"), ("greenhouse", "chainguard"))},
    {"company": "Supabase", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "supabase"), ("greenhouse", "supabase"))},
    {"company": "OVHcloud", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": [{"type": "smartrecruiters", "slug": "OVHcloud", "queries": ["intern", "stage", "graduate", "VIE"]},
                    {"type": "page_scan", "url": ["https://careers.ovhcloud.com/"]}]},
    {"company": "Scaleway", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("lever", "scaleway"), ("ashby", "scaleway"), ("greenhouse", "scaleway"))},
    {"company": "CERN (IT / computing)", "group": "programme", "type": "smartrecruiters", "slug": ["CERN"],
     "default_location": "Geneva, Switzerland",
     "queries": ["graduate", "early career", "doctoral", "technical student", "trainee", "fellow", "internship"]},

    # ------------------------------------------------------------- Telco: vendors & operators
    {"company": "Nokia", "group": "telco", "type": "oracle_hcm", "host": "fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com",
     "site": "CX_1", "public_url": "https://jobs.nokia.com/en/sites/CX_1/job/{id}",
     "queries": ["trainee", "intern", "graduate", "thesis", "PhD"]},
    {"company": "Ciena", "group": "telco", "type": "workday", "host": "ciena.wd5.myworkdayjobs.com",  # unverified
     "tenant": "ciena", "site": ["Careers", "External"], "queries": Q_EARLY},
    # ------------------------------------------------------------- Green / climate-tech / energy
    {"company": "Watershed", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "watershed"), ("greenhouse", "watershedclimate"))},
    {"company": "Sweep", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "sweep"), ("lever", "sweep"))},
    {"company": "Sylvera", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "sylvera"), ("greenhouse", "sylvera"))},
    # ------------------------------------------------------------- Research labs & institutes
    {"company": "Inria", "group": "research", "type": "link_scan", "require_topic": True, "default_region": "europe",
     "default_location": "France",
     "url": ["https://jobs.inria.fr/public/classic/en/offres"], "href": r"/offres/\d{4}-\d+"},
    {"company": "Fraunhofer", "group": "research", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "Germany",
     "url": "https://jobs.fraunhofer.de/search/?q={q}&locale=en_US", "href": r"/job/",
     "queries": ["cloud", "5G", "6G", "edge computing", "network", "energy efficiency computing", "PhD"]},
    {"company": "CWI Amsterdam", "group": "research", "type": "page_scan", "default_location": "Amsterdam, Netherlands",
     "url": ["https://www.cwi.nl/en/jobs/vacancies/"]},
    {"company": "IMDEA Networks", "group": "research", "type": "link_scan", "default_location": "Madrid, Spain",
     "require_topic": True,
     "url": ["https://networks.imdea.org/taxonomy_jobs/ingenieria-y-apoyo-a-la-investigacion/",
             "https://networks.imdea.org/jobs/"], "href": r"networks\.imdea\.org/(en/|es/)?job/[a-z0-9-]+/?$"},
    {"company": "CTTC", "group": "research", "type": "link_scan", "default_location": "Castelldefels, Spain",
     "kind_hint": "research", "url": ["https://www.cttc.cat/?p=33435"], "href": r"cttc\.cat/job/[a-z0-9-]+/?$"},
    {"company": "EURECOM", "group": "research", "type": "page_scan", "default_location": "Sophia Antipolis, France",
     "url": ["https://www.eurecom.fr/en/eurecom/job-opportunities/job-opportunities"]},
    # ------------------------------------------------------------- PhD / research job portals
    {"company": "EURAXESS", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified page layout
     "url": "https://euraxess.ec.europa.eu/jobs/search?keywords={q}", "href": r"^(https://euraxess\.ec\.europa\.eu)?/jobs/\d+$",
     "queries": ["cloud computing", "edge computing", "kubernetes", "5G", "6G", "telecommunications network",
                 "energy efficient computing", "green computing", "distributed systems", "network orchestration",
                 "backscatter", "serverless", "DevOps"]},
    {"company": "jobs.ac.uk", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "United Kingdom",
     "url": "https://www.jobs.ac.uk/search/?keywords={q}", "href": r"^/job/",
     "queries": ["PhD cloud computing", "PhD edge computing", "PhD 6G", "research assistant cloud", "graduate devops"]},

    # ------------------------------------------------------------- Post-graduate programmes

]
