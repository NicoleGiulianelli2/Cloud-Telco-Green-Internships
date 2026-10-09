import json
import hashlib
import logging
import os
import sys
import time
import traceback
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from .sources import SOURCES
from .fetchers import FETCHERS, fetch_detail
from .classify import (CLASSIFIER_VERSION, CORE_TOPICS, kind_of, topics_of, desc_topics, eligibility, region_of)

log = logging.getLogger("run")
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
JOBS_PATH = os.path.join(DATA_DIR, "jobs.json")
STATUS_PATH = os.path.join(DATA_DIR, "status.json")
OFFTOPIC_PATH = os.path.join(DATA_DIR, "offtopic.json")   # ids dropped by require_topic, so they aren't re-downloaded

MAX_DETAILS_PER_SOURCE = int(os.environ.get("MAX_DETAILS", "80"))
DETAIL_WORKERS = 8


def _id(url):
    return hashlib.sha1(url.encode()).hexdigest()[:12]


def _load_prev():
    try:
        with open(JOBS_PATH) as f:
            return {j["id"]: j for j in json.load(f).get("jobs", [])}
    except Exception:  # noqa: BLE001
        return {}


def _run_source(cfg):
    """Fetch one source and apply the title-level filter. Returns (status, [(job, raw)])."""
    t0 = time.time()
    status = {"company": cfg["company"], "group": cfg["group"], "type": cfg["type"],
              "ok": False, "raw": 0, "kept": 0, "note": "", "error": ""}
    out = []
    try:
        raw, note = FETCHERS[cfg["type"]](cfg)
        status["note"] = note
        status["raw"] = len(raw)
        seen = set()
        for r in raw:
            if not r.get("url") or not r.get("title") or r["url"] in seen:
                continue
            kind = kind_of(r["title"], r.get("extra", ""), cfg.get("kind_hint"))
            if not kind:
                continue
            seen.add(r["url"])
            company = cfg["company"]
            if r.get("company_override"):
                company = f"{cfg['company']} · {r['company_override']}"
            out.append(({
                "id": _id(r["url"]),
                "company": company,
                "group": cfg["group"],
                "title": r["title"][:220],
                "location": (r.get("location") or cfg.get("default_location") or "")[:140],
                "url": r["url"],
                "posted": r.get("posted") or None,
                "kind": kind,
                "tags": topics_of(f"{r['title']} {r.get('extra', '') if cfg['type'] != 'link_scan' else ''}"),
                "via": cfg["type"],
            }, r))
        status["ok"] = True
    except Exception as e:  # noqa: BLE001
        status["error"] = f"{type(e).__name__}: {str(e)[:300]}"
        log.warning("%s failed: %s", cfg["company"], status["error"])
        log.debug(traceback.format_exc())
    status["seconds"] = round(time.time() - t0, 1)
    return status, out


def _enrich(job, raw, prev):
    """Description-based fields: eligibility (graduates / students / unknown) and extra topics."""
    p = prev.get(job["id"])
    if p and p.get("v") == CLASSIFIER_VERSION and p.get("elig_why") != "description not available":
        for k in ("elig", "elig_why", "dtags", "desc_len"):
            job[k] = p.get(k)
        if not job["location"] and p.get("location"):
            job["location"] = p["location"]
        return job, False
    desc = raw.get("desc") or ""
    fetched = False
    if len(desc) < 200 and raw.get("_allow_fetch"):
        try:
            desc = fetch_detail(raw) or desc
            fetched = True
        except Exception as e:  # noqa: BLE001
            log.info("detail failed for %s: %s", job["url"], e)
    job["elig"], job["elig_why"] = eligibility(job["kind"], job["title"], desc, job["location"])
    job["elig_why"] = (job["elig_why"] or "")[:200]
    job["dtags"] = desc_topics(desc, job["tags"])
    job["desc_len"] = len(desc)
    return job, fetched


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    prev = _load_prev()
    try:
        with open(OFFTOPIC_PATH) as f:
            offtopic = json.load(f)
    except Exception:  # noqa: BLE001
        offtopic = {}

    only = os.environ.get("ONLY")  # comma-separated company names, for debugging
    sources = [s for s in SOURCES if not only or s["company"] in only.split(",")]
    cfg_by_name = {s["company"]: s for s in sources}

    statuses, pairs = [], []
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(_run_source, s): s for s in sources}
        for fut in as_completed(futs):
            status, out = fut.result()
            statuses.append(status)
            # cap the number of description downloads per source (cached ones don't count)
            budget = cfg_by_name[status["company"]].get("max_details", MAX_DETAILS_PER_SOURCE)
            for job, raw in out:
                if job["id"] in offtopic:
                    offtopic[job["id"]] = today
                    continue
                cached = job["id"] in prev and prev[job["id"]].get("v") == CLASSIFIER_VERSION
                raw["_allow_fetch"] = (not cached) and budget > 0
                if raw["_allow_fetch"] and len(raw.get("desc") or "") < 200:
                    budget -= 1
                pairs.append((job, raw))

    log.info("enriching %d postings", len(pairs))
    all_jobs, n_fetched = {}, 0
    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as ex:
        for job, fetched in ex.map(lambda jr: _enrich(jr[0], jr[1], prev), pairs):
            n_fetched += fetched
            cfg = cfg_by_name.get(job["company"].split(" · ")[0], {})
            if cfg.get("require_topic") and not (set(job["tags"]) | set(job.get("dtags") or [])) & CORE_TOPICS:
                if job.get("desc_len"):   # judged with its description: no need to look again
                    offtopic[job["id"]] = today
                continue
            job["region"], job["country"] = region_of(job["location"])
            if not job["region"] and cfg.get("default_region"):
                job["region"] = cfg["default_region"]
            p = prev.get(job["id"])
            job["first_seen"] = p["first_seen"] if p else today
            job["last_seen"] = today
            job["v"] = CLASSIFIER_VERSION
            all_jobs[job["id"]] = job
    log.info("descriptions downloaded: %d", n_fetched)

    for s in statuses:
        s["kept"] = sum(1 for j in all_jobs.values() if j["company"].split(" · ")[0] == s["company"])

    # Keep postings from sources that FAILED today (don't drop data because of a transient error).
    failed = {s["company"] for s in statuses if not s["ok"]}
    for jid, j in prev.items():
        if j["company"].split(" · ")[0] in failed and jid not in all_jobs:
            all_jobs[jid] = j

    statuses.sort(key=lambda s: (s["ok"], s["company"]))
    jobs_list = sorted(all_jobs.values(), key=lambda j: (j["first_seen"], j["company"], j["title"]), reverse=True)

    with open(JOBS_PATH, "w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "count": len(jobs_list), "jobs": jobs_list}, f, indent=1, ensure_ascii=False)
    # forget off-topic ids not seen for 30 days
    cutoff = datetime.fromtimestamp(time.time() - 30 * 86400, timezone.utc).strftime("%Y-%m-%d")
    with open(OFFTOPIC_PATH, "w") as f:
        json.dump({k: v for k, v in offtopic.items() if v >= cutoff}, f)
    with open(STATUS_PATH, "w") as f:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "sources": statuses}, f, indent=1, ensure_ascii=False)

    ok = sum(1 for s in statuses if s["ok"])
    print(f"\n=== {ok}/{len(statuses)} sources ok, {len(jobs_list)} postings ===")
    for s in statuses:
        flag = "OK " if s["ok"] else "ERR"
        print(f"{flag} {s['company']:<34} {s['type']:<14} raw={s['raw']:<5} kept={s['kept']:<4} {s['note']} {s['error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
