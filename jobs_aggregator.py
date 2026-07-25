#!/usr/bin/env python3
"""AI-Engineering job board aggregator.

Pulls "AI engineer"-type roles from a few named companies' OWN public careers'
APIs (free, no key), filters by keywords, merges manual/sponsored listings, and
writes jobs.json for the Ghost page (page-ai-jobs.hbs) to render.

Run:    python3 jobs_aggregator.py
Output: jobs.json (place it in your theme's assets/ folder -> served at /assets/jobs.json)

Sources supported (add companies in COMPANIES below):
  - workday   (e.g. Intel)         - microsoft (Microsoft careers API)
  - greenhouse (board token)       - lever (company slug)

Only stdlib is used (urllib) — no pip installs.
"""

import json, sys, time, urllib.request, urllib.error, datetime

# ---------------------------- CONFIG ----------------------------
COMPANIES = [
    # --- Workday ---
    {"name": "Intel", "source": "workday",
     "host": "intel.wd1.myworkdayjobs.com", "tenant": "intel", "site": "External"},
    {"name": "NVIDIA", "source": "workday",
     "host": "nvidia.wd5.myworkdayjobs.com", "tenant": "nvidia", "site": "NVIDIAExternalCareerSite"},
    {"name": "Salesforce", "source": "workday",
     "host": "salesforce.wd12.myworkdayjobs.com", "tenant": "salesforce", "site": "External_Career_Site"},
    {"name": "Adobe", "source": "workday",
     "host": "adobe.wd5.myworkdayjobs.com", "tenant": "adobe", "site": "external_experienced"},

    # --- Microsoft (own careers API) ---
    {"name": "Microsoft", "source": "microsoft"},

    # --- Greenhouse (board token) ---
    {"name": "Anthropic", "source": "greenhouse", "token": "anthropic"},
    {"name": "xAI", "source": "greenhouse", "token": "xai"},
    {"name": "Databricks", "source": "greenhouse", "token": "databricks"},
    {"name": "Scale AI", "source": "greenhouse", "token": "scaleai"},
    {"name": "CoreWeave", "source": "greenhouse", "token": "coreweave"},
    {"name": "SambaNova", "source": "greenhouse", "token": "sambanovasystems"},

    # --- Ashby (board slug) ---
    {"name": "OpenAI", "source": "ashby", "slug": "openai"},
    {"name": "Perplexity", "source": "ashby", "slug": "perplexity"},
    {"name": "ElevenLabs", "source": "ashby", "slug": "elevenlabs"},
    {"name": "Cursor", "source": "ashby", "slug": "cursor"},
    {"name": "Harvey", "source": "ashby", "slug": "harvey"},

    # NOTE: Meta, Google, Amazon, Apple, Tesla, SpaceX run custom career sites (no standard ATS
    # API), so they aren't fetched automatically. Add specific roles via selected.json (normal
    # list) or sponsored.json (Featured), or write a dedicated adapter later.
]

# A title must contain an AI/ML term AND a role term to count as an "AI engineer" role.
AI_TERMS = ["ai", " ai ", "artificial intelligence", "machine learning", "ml", "deep learning", "llm", "genai", "gpu", "cuda", "inference", "pytorch", "tensorflow", "ml "]
ROLE_TERMS = ["engineer", "engineering", "developer", "scientist", "architect"]

SEARCH_TEXT = "AI engineer"      # server-side pre-filter where supported
MAX_PER_COMPANY = 60
OUT = "jobs.json"
SPONSORED_FILE = "sponsored.json"   # pinned under "Featured" with a badge
SELECTED_FILE = "selected.json"     # hand-picked roles merged into the NORMAL list (subtle "Pick" tag)
# ------------------------------------------------------------

def _get(url, data=None, headers=None):
    hdrs = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    body = json.dumps(data).encode() if data is not None else None
    if body is not None:
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=hdrs)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch_workday(c):
    url = f"https://{c['host']}/wday/cxs/{c['tenant']}/{c['site']}/jobs"
    out, offset = [], 0
    while offset < MAX_PER_COMPANY:
        d = _get(url, data={
            "limit": 20,
            "offset": offset,
            "searchText": SEARCH_TEXT,
            "appliedFacets": {}
        })
        posts = d.get("jobPostings", [])
        if not posts:
            break

        for p in posts:
            out.append({
                "company": c["name"],
                "title": p.get("title", ""),
                "location": p.get("locationsText", ""),
                "url": f"https://{c['host']}/en-US/{c['site']}{p.get('externalPath','')}",
                "source": "workday",
            })

        offset += 20
        if offset >= d.get("total", 0):
            break

    return out


def fetch_microsoft(c):
    url = (
        "https://gcsservices.careers.microsoft.com/search/api/v1/search"
        "?q=AI%20Engineer&l=en_us&pg=1&pgSz=50&o=Relevance"
    )
    d = _get(url)
    jobs = d.get("operationResult", {}).get("result", {}).get("jobs", [])
    out = []
    for j in jobs:
      loc = ""
      props = j.get("properties", {}) if isinstance(j.get("properties"), dict) else {}
      loc = props.get("primaryLocation") or (j.get("location") or "")
      out.append({
          "company": "Microsoft", "title": j.get("title", ""),
          "location": loc,
          "url": f"https://jobs.careers.microsoft.com/global/en/job/{j.get('jobId','')}",
          "source": "microsoft",
      })
    return out


def fetch_greenhouse(c):
    d = _get(f"https://boards-api.greenhouse.io/v1/boards/{c['token']}/jobs")
    return [{
        "company": c["name"], "title": j.get("title", ""),
        "location": (j.get("location") or {}).get("name", ""),
        "url": j.get("absolute_url", ""), "source": "greenhouse"
    } for j in d.get("jobs", [])]


def fetch_lever(c):
    d = _get(f"https://api.lever.co/v0/postings/{c['slug']}?mode=json")
    return [{
        "company": c["name"], "title": j.get("text", ""),
        "location": (j.get("categories") or {}).get("location", ""),
        "url": j.get("hostedUrl", ""), "source": "lever"
    } for j in d]


def fetch_ashby(c):
    d = _get(f"https://api.ashbyhq.com/posting-api/job-board/{c['slug']}?includeCompensation=false")
    return [{
        "company": c["name"], "title": j.get("title", ""),
        "location": j.get("location", ""),
        "url": j.get("jobUrl", ""), "source": "ashby"
    } for j in d.get("jobs", [])]


ADAPTERS = {
    "workday": fetch_workday,
    "microsoft": fetch_microsoft,
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
}


def is_ai_engineer(title):
    t = " " + title.lower() + " "
    return any(a in t for a in AI_TERMS) and any(r in t for r in ROLE_TERMS)


DOMAIN_RULES = [
    ("compiler", "Compiler"),
    ("kernel", "Kernel"),
    ("cuda", "Kernel"),
    ("performance", "Performance"),
    ("optimization", "Performance"),
    ("perf", "Performance"),
    ("inference", "Inference"),
    ("serving", "Inference"),
    ("deploy", "Inference"),
    ("research", "Research"),
    ("scientist", "Research"),
    ("framework", "Frameworks"), ("library", "Frameworks"), ("runtime", "Frameworks"),
("systems", "Systems"), ("infrastructure", "Systems"), ("infra", "Systems")]

_COUNTRY_MAP = {"US": "USA", "U.S.": "USA", "USA": "USA", "PRC": "China", "UK": "UK",
                "United States": "USA", "United Kingdom": "UK"}

# substring (lowercased) -> country. Countries first, then major hub cities, so the filter
# dropdown stays clean across sources that order location as "Country, City" or "City, Country".
_COUNTRY_HINTS = [
    ("united states", "USA"), ("usa", "USA"), (" us,", "USA"), ("u.s.", "USA"),
    ("united kingdom", "UK"), (" uk,", "UK"), ("ireland", "Ireland"), ("germany", "Germany"),
    ("switzerland", "Switzerland"), ("france", "France"), ("japan", "Japan"), ("india", "India"),
    ("china", "China"), ("prc", "China"), ("canada", "Canada"), ("israel", "Israel"),
    ("singapore", "Singapore"), ("australia", "Australia"), ("poland", "Poland"), ("brazil", "Brazil"),

    # hub cities -> country
    ("san francisco", "USA"), ("new york", "USA"), ("seattle", "USA"), ("redmond", "USA"),
    ("boston", "USA"), ("washington", "USA"), ("menlo park", "USA"), ("santa clara", "USA"),
    ("austin", "USA"), ("mountain view", "USA"), ("bellevue", "USA"), ("san jose", "USA"),
    ("palo alto", "USA"), ("sunnyvale", "USA"), ("st. louis", "USA"), ("chicago", "USA"),
    ("los angeles", "USA"), ("dublin", "Ireland"), ("london", "UK"), ("munich", "Germany"),
    ("berlin", "Germany"), ("\u00fcrich", "Switzerland"), ("zurich", "Switzerland"),
    ("paris", "France"), ("tokyo", "Japan"), ("bengalore", "India"), ("bengaluru", "India"),
    ("hyderabad", "India"), ("shanghai", "China"), ("beijing", "China"), ("toronto", "Canada"),
    ("vancouver", "Canada"), ("tel aviv", "Israel"), ("sydney", "Australia"),
    ("seoul", "South Korea"), ("madrid", "Spain"), ("barcelona", "Spain"),
    ("\u00e3o paulo", "Brazil"), ("amsterdam", "Netherlands"), ("stockholm", "Sweden"),
    ("locations", "Multiple"),  # Workday's "N Locations" placeholder
]

# Ordered: first match wins. Seniority keywords checked most-senior-first so e.g.
# "Senior Staff Engineer" -> Staff+ and "Senior Principal" -> Principal.
LEVEL_RULES = [("intern", "Intern"),
               ("principal", "Principal"), ("distinguished", "Principal"), ("fellow", "Principal"),
               ("staff", "Staff"),
               ("director", "Manager"), ("head of", "Manager"), (" vp", "Manager"), ("manager", "Manager"),
               ("senior", "Senior"), ("sr.", "Senior"), (" sr ", "Senior"),
               ("lead", "Lead"),
               ("new grad", "Junior"), ("new graduate", "Junior"), ("early career", "Junior"),
               ("associate", "Junior"), ("junior", "Junior"), (" jr", "Junior")]

def domain_of(title):
    t = title.lower()
    for kw, dom in DOMAIN_RULES:
        if kw in t:
            return dom
    return "AI Engineering"


def level_of(title):
    t = " " + title.lower() + " "
    for kw, lvl in LEVEL_RULES:
        if kw in t:
            return lvl
    return "Mid"


def country_of(location):
    if not location:
        return "Other"
    low = location.lower()
    if "remote" in low:
        return "Remote"
    for hint, country in _COUNTRY_HINTS:
        if hint in low:
            return country
    first = location.split(",")[0].strip()
    return _COUNTRY_MAP.get(first, first if 0 < len(first) <= 24 else "Other")


def classify(row):
    row["domain"] = domain_of(row.get("title", ""))
    row["country"] = country_of(row.get("location", ""))
    row["level"] = level_of(row.get("title", ""))
    return row


def _load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return []


def main():
    aggregated, seen = [], set()
    ok_companies = 0
    for c in COMPANIES:
        fn = ADAPTERS.get(c["source"])
        if not fn:
            print(f"[skip] unknown source for {c['name']}", file=sys.stderr)
            continue
        try:
            rows = fn(c)
            kept = [classify(r) for r in rows if is_ai_engineer(r["title"])]
            for r in kept:
                key = (r["company"], r["title"], r["location"])
                if key in seen:
                    continue
                seen.add(key)
                aggregated.append(r)
            ok_companies += 1
            print(f"[ok] {c['name']}: {len(kept)} AI roles (of {len(rows)} fetched)")
        except Exception as e:
            # failing source never breaks the board
            print(f"[warn] {c['name']} ({c['source']}) failed: {e}", file=sys.stderr)

    # Hand-picked roles -> merged into the NORMAL list (filterable/interleaved), flagged "pick".
    for r in _load_json(SELECTED_FILE):
        classify(r)
        r["pick"] = True
        key = (r.get("company"), r.get("title"), r.get("location"))
        if key not in seen:
            seen.add(key)
            aggregated.append(r)

    sponsored = _load_json(SPONSORED_FILE)

    aggregated.sort(key=lambda r: (r["company"], r["title"]))
    out = {
        "updated": datetime.date.today().isoformat(),
        "sponsored": sponsored,
        "jobs": aggregated
    }

    with open(OUT, "w") as f:
        json.dump(out, f, indent=2)

    print(
        f"\nFetched from {ok_companies}/{len(COMPANIES)} companies. "
        f"Wrote {OUT}: {len(aggregated)} roles + {len(sponsored)} sponsored. "
        f"Copy it to your theme's assets/ (served at /assets/jobs.json)."
    )


if __name__ == "__main__":
    main()