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
    {"company": "Dell Technologies", "group": "big", "type": "workday", "host": "dell.wd1.myworkdayjobs.com",
     "tenant": "dell", "site": ["External"], "queries": Q_EARLY, "require_topic": True},
    {"company": "Broadcom / VMware", "group": "big", "type": "workday", "host": "broadcom.wd1.myworkdayjobs.com",
     "tenant": "broadcom", "site": ["External_Career"], "queries": Q_EARLY},  # unverified site
    {"company": "NetApp", "group": "big", "type": "workday", "host": "netapp.wd1.myworkdayjobs.com",  # unverified
     "tenant": "netapp", "site": ["NetAppCareers", "External"], "queries": Q_EARLY},
    {"company": "Akamai", "group": "big", "type": "workday", "host": "akamai.wd1.myworkdayjobs.com",  # unverified
     "tenant": "akamai", "site": ["akamai_careers", "External"], "queries": Q_EARLY},
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
    {"company": "SAP", "group": "big", "type": "link_scan", "require_topic": True,  # unverified page layout
     "url": "https://jobs.sap.com/search/?q={q}&locale=en_US", "href": r"/job/",
     "queries": ["graduate cloud", "intern cloud", "devops intern", "PhD", "trainee"]},
    {"company": "Spotify", "group": "big", "type": "lever", "slug": ["spotify"]},
    {"company": "Adyen", "group": "big", "type": "greenhouse", "slug": ["adyen"]},
    {"company": "Databricks", "group": "big", "type": "greenhouse", "slug": ["databricks"]},
    {"company": "Snowflake", "group": "big", "type": "phenom",
     "url": ["https://careers.snowflake.com/us/en/search-results?keywords=intern"]},
    {"company": "MongoDB", "group": "big", "type": "greenhouse", "slug": ["mongodb"]},
    {"company": "Mistral AI", "group": "big", "type": "lever", "slug": ["mistral"]},
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
    {"company": "DigitalOcean", "group": "cloud", "type": "ats_any",  # unverified
     "candidates": _any(("greenhouse", "digitaloceanllc"), ("ashby", "digitalocean"), ("lever", "digitalocean"))},
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
    {"company": "Ericsson", "group": "telco", "type": "eightfold", "host": ["jobs.ericsson.com"], "domain": "ericsson.com",
     "queries": ["graduate", "intern", "trainee", "thesis", "PhD", "young professional"]},
    {"company": "Nokia", "group": "telco", "type": "oracle_hcm", "host": "fa-evmr-saasfaprod1.fa.ocs.oraclecloud.com",
     "site": "CX_1", "public_url": "https://jobs.nokia.com/en/sites/CX_1/job/{id}",
     "queries": ["trainee", "intern", "graduate", "thesis", "PhD"]},
    {"company": "Vodafone", "group": "telco", "type": "eightfold",  # unverified
     "host": ["jobs.vodafone.com", "vodafone.eightfold.ai"], "domain": "vodafone.com",
     "queries": ["graduate", "intern", "discover graduate", "trainee"]},
    {"company": "Keysight", "group": "telco", "type": "workday", "host": "keysight.wd5.myworkdayjobs.com",  # unverified
     "tenant": "keysight", "site": ["Keysight", "External"], "queries": Q_EARLY},
    {"company": "Amdocs", "group": "telco", "type": "workday", "host": "amdocs.wd3.myworkdayjobs.com",  # unverified
     "tenant": "amdocs", "site": ["Amdocs", "External"], "queries": Q_EARLY},
    {"company": "Ciena", "group": "telco", "type": "workday", "host": "ciena.wd5.myworkdayjobs.com",  # unverified
     "tenant": "ciena", "site": ["Careers", "External"], "queries": Q_EARLY},
    {"company": "Liberty Global", "group": "telco", "type": "workday", "host": "libertyglobal.wd3.myworkdayjobs.com",  # unverified
     "tenant": "libertyglobal", "site": ["LibertyGlobal", "External"], "queries": Q_EARLY},
    {"company": "Deutsche Telekom", "group": "telco", "type": "page_scan",  # unverified
     "url": ["https://www.telekom.com/en/careers/jobsearch?searchTerm=trainee",
             "https://www.telekom.com/en/careers/jobsearch?searchTerm=intern"]},
    {"company": "Swisscom", "group": "telco", "type": "page_scan",  # unverified
     "url": ["https://www.swisscom.ch/en/about/career/young-talents.html"]},
    {"company": "Accelleran (O-RAN)", "group": "telco", "type": "page_scan",  # unverified
     "url": ["https://www.accelleran.com/careers/", "https://accelleran.com/careers"]},

    # ------------------------------------------------------------- Green / climate-tech / energy
    {"company": "Electricity Maps", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("workable", "electricitymaps"), ("lever", "electricitymaps"), ("greenhouse", "electricitymaps"))
     + [{"type": "page_scan", "url": ["https://www.electricitymaps.com/careers"]}]},
    {"company": "Watershed", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "watershed"), ("greenhouse", "watershedclimate"))},
    {"company": "Greenly", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("lever", "greenly"), ("ashby", "greenly"), ("workable", "greenly"))},
    {"company": "Sweep", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "sweep"), ("lever", "sweep"))},
    {"company": "Kayrros", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("lever", "kayrros"), ("ashby", "kayrros"), ("greenhouse", "kayrros"))},
    {"company": "Sylvera", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "sylvera"), ("greenhouse", "sylvera"))},
    {"company": "Octopus Energy / Kraken", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("ashby", "kraken"), ("ashby", "octopusenergy"), ("greenhouse", "octopusenergy"))},
    {"company": "Climeworks", "group": "green", "type": "ats_any",  # unverified
     "candidates": _any(("greenhouse", "climeworks"), ("lever", "climeworks"))},

    # ------------------------------------------------------------- Research labs & institutes
    {"company": "Inria", "group": "research", "type": "link_scan", "require_topic": True, "default_region": "europe",
     "default_location": "France",
     "url": ["https://jobs.inria.fr/public/classic/en/offres"], "href": r"/offres/\d{4}-\d+"},
    {"company": "imec", "group": "research", "type": "link_scan", "require_topic": True,  # unverified (may be JS-only)
     "default_location": "Leuven, Belgium",
     "url": ["https://www.imec-int.com/work-at-imec/job-opportunities/phd-at-imec",
             "https://www.imec-int.com/en/work-at-imec/master-thesis-internship"],
     "href": r"/work-at-imec/job-opportunities/[a-z0-9-]{12,}$"},
    {"company": "CNRS", "group": "research", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "France",
     "url": ["https://emploi.cnrs.fr/Offres.aspx"], "href": r"/Offres/(Doctorant|CDD|Stage)"},
    {"company": "Fraunhofer", "group": "research", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "Germany",
     "url": "https://jobs.fraunhofer.de/search/?q={q}&locale=en_US", "href": r"/job/",
     "queries": ["cloud", "5G", "6G", "edge computing", "network", "energy efficiency computing", "PhD"]},
    {"company": "CWI Amsterdam", "group": "research", "type": "page_scan", "default_location": "Amsterdam, Netherlands",
     "url": ["https://www.cwi.nl/en/jobs/vacancies/"]},
    {"company": "IMDEA Networks", "group": "research", "type": "page_scan", "default_location": "Madrid, Spain",  # unverified
     "url": ["https://networks.imdea.org/job-offers/", "https://networks.imdea.org/work-with-us/"]},
    {"company": "i2CAT", "group": "research", "type": "page_scan", "default_location": "Barcelona, Spain",  # unverified
     "url": ["https://i2cat.net/work-with-us/", "https://i2cat.net/careers/"]},
    {"company": "CTTC", "group": "research", "type": "page_scan", "default_location": "Castelldefels, Spain",  # unverified
     "url": ["https://www.cttc.cat/jobs/", "https://www.cttc.cat/job-offers/"]},
    {"company": "EURECOM", "group": "research", "type": "page_scan", "default_location": "Sophia Antipolis, France",  # unverified
     "url": ["https://www.eurecom.fr/en/jobs", "https://www.eurecom.fr/en/eurecom-careers"]},
    {"company": "INESC TEC", "group": "research", "type": "page_scan", "default_location": "Porto, Portugal",  # unverified
     "url": ["https://www.inesctec.pt/en/opportunities", "https://www.inesctec.pt/en/jobs"]},
    {"company": "Instituto de Telecomunicações", "group": "research", "type": "page_scan",  # unverified
     "default_location": "Portugal", "url": ["https://www.it.pt/Jobs", "https://www.it.pt/Opportunities"]},
    {"company": "CINECA", "group": "research", "type": "page_scan", "default_location": "Bologna, Italy",  # unverified
     "url": ["https://www.cineca.it/lavora-con-noi"]},

    # ------------------------------------------------------------- PhD / research job portals
    {"company": "EURAXESS", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified page layout
     "url": "https://euraxess.ec.europa.eu/jobs/search?keywords={q}", "href": r"^(https://euraxess\.ec\.europa\.eu)?/jobs/\d+$",
     "queries": ["cloud computing", "edge computing", "kubernetes", "5G", "6G", "telecommunications network",
                 "energy efficient computing", "green computing", "distributed systems", "network orchestration",
                 "backscatter", "serverless", "DevOps"]},
    {"company": "AcademicTransfer (NL)", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "Netherlands",
     "url": "https://www.academictransfer.com/en/jobs/?q={q}", "href": r"/en/jobs/\d+",
     "queries": ["cloud", "edge computing", "5G", "6G", "energy efficient computing", "distributed systems"]},
    {"company": "Academic Positions", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified
     "url": "https://academicpositions.com/find-jobs?search={q}", "href": r"/ad/",
     "queries": ["cloud computing", "edge computing", "6G", "green computing", "distributed systems"]},
    {"company": "FindAPhD", "group": "portal", "type": "link_scan", "require_topic": True, "kind_hint": "phd",  # unverified
     "url": "https://www.findaphd.com/phds/?Keywords={q}", "href": r"/phds/project/",
     "queries": ["cloud computing", "edge computing", "6G", "green computing", "kubernetes", "network energy efficiency"]},
    {"company": "jobs.ac.uk", "group": "portal", "type": "link_scan", "require_topic": True,  # unverified
     "default_location": "United Kingdom",
     "url": "https://www.jobs.ac.uk/search/?keywords={q}", "href": r"^/job/",
     "queries": ["PhD cloud computing", "PhD edge computing", "PhD 6G", "research assistant cloud", "graduate devops"]},

    # ------------------------------------------------------------- Post-graduate programmes
    {"company": "VIE (Business France)", "group": "programme", "type": "vie", "kind_hint": "graduate",  # experimental
     "queries": ["cloud", "devops", "réseaux", "télécom", "infrastructure", "data center", "énergie informatique"],
     "max_details": 0},
]
