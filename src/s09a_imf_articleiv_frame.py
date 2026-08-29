"""IMF Article IV frame builder (PREREG v0.5 Appendix B; round-6 blocker 5).

Deterministic pipeline (fixture-tested here): listing rows -> normalized,
parsed, flagged, revision-resolved, ISO3-mapped frame + full audit trail.
The LIVE capture layer targets the imf.org SPROLL listing
(imf.org/en/Publications/SPROLLs/Article-iv-staff-reports) and eLibrary issue
pages; it refuses to run without --i-am-in-stage-b, logs every request, and
must archive raw HTML — live parsing is a Stage-B obligation, the frozen
decision logic is everything below.
"""
from __future__ import annotations
import re as _re
import argparse, calendar, csv, datetime as _dt, hashlib, json, re, time, unicodedata
from pathlib import Path
import pandas as pd
import yaml

GENRE = "article_iv"
INSTITUTION = "imf"

SEED_ALIASES = {  # extended at Stage-B via config/imf_country_aliases.yaml
 "afghanistan":"AFG","albania":"ALB","algeria":"DZA","argentina":"ARG","armenia":"ARM",
 "australia":"AUS","austria":"AUT","bangladesh":"BGD","belgium":"BEL","brazil":"BRA",
 "canada":"CAN","chile":"CHL","people's republic of china":"CHN","china":"CHN",
 "colombia":"COL","democratic republic of the congo":"COD","republic of congo":"COG",
 "republic of the congo":"COG","costa rica":"CRI","cote d'ivoire":"CIV",
 "côte d'ivoire":"CIV","denmark":"DNK","arab republic of egypt":"EGY","egypt":"EGY",
 "ethiopia":"ETH","finland":"FIN","france":"FRA","georgia":"GEO","germany":"DEU",
 "ghana":"GHA","greece":"GRC","india":"IND","indonesia":"IDN",
 "islamic republic of iran":"IRN","ireland":"IRL","israel":"ISR","italy":"ITA",
 "japan":"JPN","jordan":"JOR","kenya":"KEN","republic of korea":"KOR","korea":"KOR",
 "mexico":"MEX","morocco":"MAR","nepal":"NPL","netherlands":"NLD","new zealand":"NZL",
 "nigeria":"NGA","norway":"NOR","pakistan":"PAK","peru":"PER","philippines":"PHL",
 "poland":"POL","portugal":"PRT","romania":"ROU","russian federation":"RUS",
 "saudi arabia":"SAU","senegal":"SEN","south africa":"ZAF","spain":"ESP",
 "sri lanka":"LKA","sweden":"SWE","switzerland":"CHE","thailand":"THA","the gambia":"GMB",
 "tunisia":"TUN","turkiye":"TUR","türkiye":"TUR","turkey":"TUR","uganda":"UGA",
 "ukraine":"UKR","united kingdom":"GBR","united states":"USA","vietnam":"VNM",
 "zambia":"ZMB","zimbabwe":"ZWE",
 "trinidad and tobago":"TTO","bosnia and herzegovina":"BIH",
 "antigua and barbuda":"ATG","sao tome and principe":"STP",
 "são tomé and príncipe":"STP","st. kitts and nevis":"KNA",
 "saint kitts and nevis":"KNA","st. vincent and the grenadines":"VCT",
 "saint vincent and the grenadines":"VCT",
}
REGIONAL_TOKENS = ["currency union","monetary union","monetary community","euro area",
                   "eastern caribbean","cemac","waemu","eccu","common policies",
                   " and "]
PROGRAM_TOKENS = ["review under","arrangement","extended credit","stand-by",
                  "extended fund facility","policy coordination instrument",
                  "flexible credit line"]

def _field(v, default: str) -> str:
    """NaN-safe field read: pandas to_dict('records') yields float('nan') for
    missing values in mixed frames — .get defaults never fire on those."""
    if v is None or (isinstance(v, float) and v != v) or str(v).strip() == "":
        return default
    return str(v)

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s))
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).strip()

def load_aliases(root: Path) -> dict:
    f = root / "config" / "imf_country_aliases.yaml"
    extra = yaml.safe_load(f.read_text()) if f.exists() else {}
    m = dict(SEED_ALIASES); m.update({norm(k).lower(): v for k, v in (extra or {}).items()})
    return m

def parse_report_no(text: str):
    m = re.search(r"No\.?\s*(\d{2,4})\s*/\s*(\d+)", text)
    if not m:
        return None
    yy, num = m.group(1), int(m.group(2))
    year4 = int(yy) if len(yy) == 4 else (1900 + int(yy) if int(yy) >= 50 else 2000 + int(yy))
    return f"CR{year4}-{num:03d}"

def classify_row(row: dict, aliases: dict, cutoff: str, y_lo: int, y_hi: int) -> dict:
    title = norm(row.get("title", ""))
    tl = title.lower()
    out = {"institution": INSTITUTION, "genre": GENRE, "title": title,
           "url": row.get("url", ""), "pub_date": str(row.get("pub_date", ""))[:10],
           "language": norm(_field(row.get("language"), "English")),
           "report_no": parse_report_no(title + " " + str(row.get("report_no", ""))),
           "combined_with_program": any(t in tl for t in PROGRAM_TOKENS),
           "fssa_cotitled": "financial system stability" in tl}
    out["year"] = int(out["pub_date"][:4]) if out["pub_date"][:4].isdigit() else None
    def rej(reason):
        out["status"] = reason; return out
    if "selected issues" in tl:                 # specific exclusion first,
        return rej("excluded_selected_issues")  # so the audit label is precise
    if "article iv consultation" not in tl:
        return rej("excluded_not_article_iv")
    if out["language"].lower() != "english":
        return rej("excluded_language")
    pre = tl.split(":", 1)[0] if ":" in tl else ""
    if not pre:
        return rej("excluded_no_country_prefix")
    iso = aliases.get(pre.strip())     # alias FIRST (round-7 'Trinidad and
    if iso is None:                    # Tobago' class beats ' and ' token)
        if any(t in pre for t in REGIONAL_TOKENS):
            return rej("excluded_regional_multicountry")
        return rej("unmapped_country")
    out["country_iso3"] = iso
    if out["report_no"] is None:
        return rej("excluded_no_report_number")
    if out["pub_date"] > cutoff:                # frame-defining boundary first
        return rej("excluded_after_cutoff")
    if out["year"] is None or not (y_lo <= out["year"] <= y_hi):
        return rej("excluded_year_window")
    out["status"] = "included"
    return out

def resolve_revisions(df: pd.DataFrame) -> pd.DataFrame:
    """One unit per report_no: latest pub_date; tie -> corrig/revised title;
    final tie -> lexicographically smallest url. Deterministic sort+tail,
    no tuple-apply (pandas-version-proof)."""
    d = df.copy()
    d["_rev"] = d["title"].str.lower().str.contains("corrig|revised").astype(int)
    d = d.sort_values(["report_no", "pub_date", "_rev", "url"],
                      ascending=[True, True, True, False], kind="mergesort")
    keep = d.groupby("report_no", sort=False).tail(1).drop(columns="_rev")
    superseded = d.loc[~d.index.isin(keep.index)].drop(columns="_rev").copy()
    superseded["status"] = "superseded_revision"
    return keep, superseded

def build_frame(listing: pd.DataFrame, cutoff: str = "2025-12-31",
                y_lo: int = 1994, y_hi: int = 2025,
                root: Path = Path(".")) -> tuple[pd.DataFrame, pd.DataFrame]:
    aliases = load_aliases(root)
    rows = [classify_row(r, aliases, cutoff, y_lo, y_hi)
            for r in listing.to_dict("records")]
    audit = pd.DataFrame(rows)
    inc = audit[audit["status"] == "included"].copy()
    if len(inc):
        inc, sup = resolve_revisions(inc)
        if len(sup):
            audit = pd.concat([audit[audit["status"] != "included"], inc, sup],
                              ignore_index=True)
    frame_cols = ["institution", "genre", "year", "id", "country_iso3",
                  "title", "pub_date", "url", "combined_with_program",
                  "fssa_cotitled"]
    if len(inc):
        frame = inc.rename(columns={"report_no": "id"})[frame_cols] \
                   .sort_values(["year", "id"]).reset_index(drop=True)
    else:                                  # zero included rows: stay well-typed
        frame = pd.DataFrame(columns=frame_cols)
    return frame, audit.sort_values(["status", "pub_date"]).reset_index(drop=True)

SPROLL_URL = ("https://www.imf.org/en/Publications/SPROLLs/"
              "Article-iv-staff-reports")
_SPROLL_ROW_RE = re.compile(
    r'<a[^>]+href="(?P<url>[^"]+)"[^>]*>(?P<title>[^<]{15,300})</a>'
    r'.{0,400}?(?P<date>[A-Z][a-z]+ \d{1,2}, \d{4})', re.S)


def parse_sproll_html(html: str) -> list[dict]:
    """Tolerant extractor for SPROLL listing rows under the DOCUMENTED
    structural assumption (round-7): each report row is an anchor whose text
    is the report title, followed within 400 characters by a
    'Month D, YYYY' publication date. The markup-specific pattern is
    verified against the live page at Stage-B (s00-style probe) BEFORE the
    frame snapshot; any divergence is logged and the pattern amended in the
    Stage-B SAP addendum — never silently."""
    rows = []
    for m in _SPROLL_ROW_RE.finditer(html):
        title = norm(re.sub(r"\s+", " ", m.group("title")))
        try:
            d = _dt.datetime.strptime(m.group("date"), "%B %d, %Y").date()
        except ValueError:
            continue
        rows.append({"title": title, "url": m.group("url"),
                     "pub_date": d.isoformat()})
    return rows


# Round-9 positive-terminal contract: a zero-row page is a legal terminal
# page ONLY when it positively matches a documented empty-listing marker,
# contains no anchors, and matches no documented interstitial marker. The
# marker sets are frozen here; the Stage-B capture protocol re-verifies them
# against the live page before any reliance (PREREG C20).
from html.parser import HTMLParser


class _AnchorSniffer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.found = True

    def handle_startendtag(self, tag, attrs):
        if tag == "a":
            self.found = True


def page_has_anchor(text: str) -> bool:
    """Round-11 (C30): anchor detection is STRUCTURAL — an HTML parser
    walks the tags, so <a>, <a/>, <a\nhref=...> are all anchors. The
    typographic regex is kept as a second net; a parser failure counts as
    anchor-bearing (fail-closed)."""
    if _re.search(r"<a[\s>/]", text.lower()):
        return True
    try:
        sn = _AnchorSniffer()
        sn.feed(text)
        sn.close()
        return sn.found
    except Exception:
        return True


TERMINAL_MARKERS = ("no results",)
INTERSTITIAL_MARKERS = ("captcha", "unavailable", "maintenance",
                        "access denied", "forbidden", "rate limit",
                        "temporarily", "error")


def fetch_live_sproll(session, out_raw: Path, log_csv: Path,
                      base_url: str = SPROLL_URL, sleep: float = 1.0,
                      max_pages: int = 400, timeout: int = 60) -> pd.DataFrame:
    """Paginated LIVE capture with per-page raw-HTML archiving
    (sproll_page_%04d.html), a request log (utc, page, url, status, bytes,
    rows_parsed, sha256, raw_file) and a page-count log line (round-6/7
    obligation). Stops at the first page yielding zero parsed rows.
    Stage-B only — main() enforces --i-am-in-stage-b."""
    out_raw.mkdir(parents=True, exist_ok=True)
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    _left = sorted(p.name for p in out_raw.glob("sproll_page_*.html"))
    if _left:                                 # round-10: run-immutable
        raise RuntimeError(f"[s09a] raw directory already holds "
                           f"{len(_left)} page archive(s) (e.g. {_left[0]}) "
                           "— raw archives are write-once; a rerun must "
                           "target a fresh raw directory")
    rows_all, page, terminal = [], 0, False
    _hdr = not log_csv.exists()               # round-10: append-only log
    with open(log_csv, "a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if _hdr:
            w.writerow(["utc", "page", "url", "status", "bytes",
                        "rows_parsed", "sha256", "raw_file"])
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            r = session.get(url, timeout=timeout)
            raw_bytes = getattr(r, "content", None)   # round-11: VERBATIM
            if raw_bytes is None:                     # transport BYTES
                raise RuntimeError("[s09a] transport exposes no raw byte "
                                   "body (.content); live capture requires "
                                   "the VERBATIM server bytes")
            fn = out_raw / f"sproll_page_{page:04d}.html"
            if fn.exists():                   # round-10: write-once
                raise RuntimeError(f"[s09a] {fn.name} already exists — raw "
                                   "archives are write-once")
            fn.write_bytes(raw_bytes)
            try:
                raw = raw_bytes.decode("utf-8", errors="strict")
            except UnicodeDecodeError as e:   # round-11: fail-closed parse
                raise RuntimeError(f"[s09a] page {page} is not valid UTF-8 "
                                   f"({e}); the verbatim bytes are archived "
                                   "in " + fn.name + " — refusing to parse "
                                   "a re-encoded body") from None
            rows = parse_sproll_html(raw)
            w.writerow([_dt.datetime.now(_dt.timezone.utc)
                        .isoformat(timespec="seconds"), page, url,
                        getattr(r, "status_code", None), len(raw_bytes), len(rows),
                        hashlib.sha256(raw_bytes).hexdigest(), fn.name])
            print(f"[s09a] page {page}: {len(rows)} rows")
            # round-8 fail-closed guards -----------------------------------
            if getattr(r, "status_code", None) != 200:
                raise RuntimeError(f"[s09a] page {page}: HTTP "
                                   f"{getattr(r, 'status_code', None)} — "
                                   "live capture aborts (error pages are "
                                   "never a terminal page)")
            if len(rows) == 0:
                if page == 1:
                    raise RuntimeError("[s09a] page 1 parsed 0 rows — an "
                                       "empty FIRST page is a capture "
                                       "failure, never a terminal page")
                low = raw.lower()
                if page_has_anchor(raw):          # round-11: structural
                    raise RuntimeError(f"[s09a] page {page}: 0 rows parsed "
                                       "but the page contains anchors — "
                                       "markup drift, CAPTCHA or "
                                       "interstitial; aborting instead of "
                                       "treating as terminal")
                hit = [m for m in INTERSTITIAL_MARKERS if m in low]
                if hit:
                    raise RuntimeError(f"[s09a] page {page}: interstitial "
                                       f"marker(s) {hit} on a zero-row page "
                                       "— access block or maintenance, "
                                       "never a terminal page")
                if not any(m in low for m in TERMINAL_MARKERS):
                    raise RuntimeError(f"[s09a] page {page}: zero rows but "
                                       "no documented empty-listing marker "
                                       "— a terminal page must be "
                                       "POSITIVELY identified (round-9)")
                terminal = True
                break
            rows_all.extend(rows)
            time.sleep(sleep)
    if not terminal:
        raise RuntimeError(f"[s09a] exhausted max_pages={max_pages} without "
                           "reaching a terminal page — aborting")
    print(f"[s09a] page-count: {page}; total listing rows: {len(rows_all)}")
    return pd.DataFrame(rows_all)


# ---------------------------------------------------------------------------
# Stage-B transport amendment A1 (2026-08-19; docs/SAP_ADDENDUM_A1_coveo_
# transport.md). Observed live: the SPROLL page no longer carries listing
# rows in static HTML (client-side rendering, "Loading component" shell) and
# www.imf.org rejects every non-browser TLS client outright (HTTP 403 for
# curl/requests probes, robots.txt included). The listing data is served by
# the site's public Coveo Search API, which answered probes P1-P4
# (diagnostics/20260819_sproll/) with HTTP 200; totalCount == 7451 == the
# count displayed on the rendered page, and stripping the browser-session
# analytics fields left totalCount unchanged (P1 vs P2). fetch_live_coveo
# reproduces the page's own query verbatim (aq/cq/sort/fields), sends no
# session analytics, partitions by @imfdate year to avoid result-depth
# limits, and keeps every round-8/9/10/11 obligation: write-once raw
# archives, append-only request log (now with request-body sha256), non-200
# abort, JSON-decode abort, positive terminal (empty results AND
# firstResult >= partition totalCount), exact per-partition count match, a
# global sum check against the unpartitioned totalCount, and permanentid
# uniqueness. fetch_live_sproll above is retained unmodified as the
# superseded transport; the frozen decision logic (build_frame) is untouched.
COVEO_URL = ("https://imfproduction561s308u.org.coveo.com/rest/search/v2"
             "?organizationId=imfproduction561s308u")
COVEO_AQ = ("((@title*=\"Article-iv-Consultation\" NOT @z95xtemplatename=="
            "(\"Bucket\",\"Media folder\"))) (@imfdate)")
COVEO_CQ = ("((((@imflanguage=ENG (@language=English AND @filetype=PDF)) OR "
            "(@imflanguage=ENG AND @filetype<>PDF)) OR (NOT @filetype AND "
            "@imflanguage=ENG))) ((((@imflanguage=ENG (@language=English AND "
            "@filetype=PDF)) OR (@imflanguage=ENG AND @filetype<>PDF)) OR "
            "(NOT @filetype AND @imflanguage=ENG))) ((@source==\"IMF-ORG\") "
            "OR (@source==(\"IMFORG-ADMINTRIB\",\"IMFORG-AM-VIDEOS\","
            "\"IMFORG-AM-VIDEOS-PREV\",\"IMFORG-FAD\",\"IMFORG-FANDD\","
            "\"IMFORG-MAIN\",\"IMFORG-MAIN-VIDEOS\",\"IMFORG-SELDEC\","
            "\"IMFORG-SM-VIDEOS\",\"IMFORG-SM-VIDEOS-PREV\","
            "\"IMFORG-STAFFPAPERS\")))")
COVEO_FIELDS = ["author", "language", "urihash", "objecttype", "collection",
                "source", "permanentid", "date", "filetype", "parents",
                "ec_price", "ec_name", "ec_description", "ec_brand",
                "ec_category", "ec_item_group_id", "ec_shortdesc",
                "ec_thumbnails", "ec_images", "ec_promo_price",
                "ec_in_stock", "ec_rating", "imfdescription", "imfdate",
                # SAP addendum A2 (2026-08-19): catalog fields. seriesvolumeno
                # carries the IMF Staff Country Reports volume/issue -
                # "Country Report No. 2026/221" - i.e. the report number the
                # preregistered unit rule (Appendix B.4/B.5) is defined on and
                # that Appendix B.1 names as the eLibrary catalog anchor
                # (series 002, volume = year, issue = report number). The
                # remaining three are provenance only: they travel in the
                # listing CSV for auditing and are ignored by the frozen
                # classifier. imflanguage is deliberately NOT mapped onto the
                # listing's `language` column: it is coded "ENG", and the
                # frozen rule tests equality with "English", so mapping it
                # would silently reject every row; the cq filter already
                # restricts the query to English.
                "seriesvolumeno", "imfseries", "imfisocode", "imftype"]


def _coveo_body(first_result: int, n_results: int,
                window: tuple[str, str] | None = None) -> dict:
    """The page's query, verbatim, minus the browser-session fields
    (actionsHistory / analytics / clientId), whose removal is
    population-neutral (probe P1 vs P2: totalCount 7451 == 7451). An optional
    window appends an @imfdate range to `aq`; the window is a transport
    device only - the frame year always comes from the parsed pub_date,
    never from the window."""
    aq = COVEO_AQ if window is None else (
        COVEO_AQ + f" (@imfdate>={window[0]} @imfdate<={window[1]})")
    return {"locale": "en-US", "debug": False, "tab": "default",
            "referrer": "default", "timezone": "Europe/Istanbul",
            "aq": aq, "cq": COVEO_CQ,
            "context": {"applicationExperience": "modern"},
            "fieldsToInclude": COVEO_FIELDS, "searchHub": "Search",
            "sortCriteria": "@imfdate descending",
            "numberOfResults": n_results, "firstResult": first_result}


def _coveo_scalar(v, join: bool = False) -> str:
    """SAP addendum A2: Coveo returns some fields as single-element lists
    (imfisocode -> ['LTU'], imfseries -> ['IMF Staff Country Reports']) and
    others as plain strings (seriesvolumeno). Absent fields come back None.
    Normalize to a string for the listing CSV WITHOUT interpreting the
    content: a missing field becomes the empty string (the frozen classifier
    then finds no report number, which is the correct verdict for an item
    the catalog does not carry as a Staff Country Report), and a multi-entry
    list is preserved verbatim, pipe-joined, so multi-country tagging stays
    visible in the audit trail instead of being silently collapsed."""
    if v is None:
        return ""
    if isinstance(v, (list, tuple)):
        if not v:
            return ""
        if len(v) == 1:
            return str(v[0])
        return "|".join(str(x) for x in v) if join else str(v[0])
    return str(v)


def _imfdate_ms_to_iso(ms) -> str:
    """imfdate is epoch milliseconds at midnight US-Eastern; the UTC date of
    that instant equals the displayed publication date (offset < 24 h)."""
    return _dt.datetime.fromtimestamp(int(ms) / 1000,
                                      tz=_dt.timezone.utc).date().isoformat()


def _child_windows(kind: str, key):
    """SAP addendum A3: the split ladder. A year splits into its months, a
    month into its days; a day is the floor."""
    if kind == "year":
        return [("month", (key, m),
                 (f"{key}/{m:02d}/01",
                  f"{key}/{m:02d}/{calendar.monthrange(key, m)[1]:02d}"))
                for m in range(1, 13)]
    if kind == "month":
        y, m = key
        return [("day", (y, m, d),
                 (f"{y}/{m:02d}/{d:02d}", f"{y}/{m:02d}/{d:02d}"))
                for d in range(1, calendar.monthrange(y, m)[1] + 1)]
    return []


def fetch_live_coveo(session, out_raw: Path, log_csv: Path, cfg: dict,
                     sleep: float | None = None,
                     page_size: int | None = None,
                     year_lo: int | None = None,
                     year_hi: int | None = None,
                     timeout: int = 60) -> pd.DataFrame:
    """LIVE Article IV listing capture via the site's Coveo Search API
    (SAP addendum A1, catalog fields A2, window recursion A3). Stage-B only -
    main() enforces --i-am-in-stage-b.

    A3 (2026-08-19): offset pagination is GONE. The A1/A2 design walked each
    year with firstResult steps, which assumes the server's result order is
    stable across requests; the live index is not stable under ties in
    @imfdate, and the second live run aborted on a duplicate permanentid
    WITHIN one year (2002, pages 66/67) - the guard did its job, but the
    design invited the fault. Every request now asks for a date window and
    is accepted only if it returns the window ENTIRE
    (len(results) == totalCount, firstResult always 0). A truncated window is
    never paginated: it is split (year -> months -> days) and each child is
    captured the same way, with the children's totals required to sum to the
    parent's. An item can therefore no longer be duplicated or skipped by a
    reordering between two requests, because no two requests ever cover the
    same window."""
    ccfg = cfg.get("imf_coveo")
    if not ccfg or not ccfg.get("api_key"):
        raise SystemExit("[s09a] config imf_coveo.api_key missing - the "
                         "Coveo transport (SAP addendum A1) is not "
                         "configured; refusing to capture")
    url = ccfg.get("search_url", COVEO_URL)
    sleep = float(ccfg.get("sleep_seconds", 1.0)) if sleep is None else sleep
    page_size = (int(ccfg.get("page_size", 1000))
                 if page_size is None else page_size)
    year_lo = int(ccfg.get("year_lo", 1946)) if year_lo is None else year_lo
    year_hi = int(ccfg.get("year_hi", 2026)) if year_hi is None else year_hi
    headers = {"authorization": f"Bearer {ccfg['api_key']}",
               "content-type": "application/json",
               "user-agent": ("Mozilla/5.0 (compatible; bankspeak-continued"
                              f"/0.1; +mailto:{cfg['contact_email']})")}
    out_raw.mkdir(parents=True, exist_ok=True)
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    _left = sorted(p.name for p in list(out_raw.glob("coveo_page_*.json"))
                   + list(out_raw.glob("sproll_page_*.html")))
    if _left:                                 # round-10: run-immutable
        raise RuntimeError(f"[s09a] raw directory already holds "
                           f"{len(_left)} page archive(s) (e.g. {_left[0]}) "
                           "- raw archives are write-once; a rerun must "
                           "target a fresh raw directory")
    page_no = 0
    _hdr = not log_csv.exists()               # round-10: append-only log
    lf = open(log_csv, "a", newline="", encoding="utf-8")
    w = csv.writer(lf)
    if _hdr:
        w.writerow(["utc", "page", "url", "window", "status", "bytes",
                    "req_body_sha256", "results", "total_count",
                    "resp_sha256", "raw_file"])

    def post_window(window, label: str) -> dict:
        nonlocal page_no
        body = _coveo_body(0, page_size, window)
        body_bytes = json.dumps(body, separators=(",", ":"),
                                ensure_ascii=False).encode("utf-8")
        r = session.post(url, data=body_bytes, headers=headers,
                         timeout=timeout)
        raw_bytes = getattr(r, "content", None)   # round-11: VERBATIM BYTES
        if raw_bytes is None:
            raise RuntimeError("[s09a] transport exposes no raw byte body "
                               "(.content); live capture requires the "
                               "VERBATIM server bytes")
        fn = out_raw / f"coveo_page_{page_no:04d}.json"
        if fn.exists():                       # round-10: write-once
            raise RuntimeError(f"[s09a] {fn.name} already exists - raw "
                               "archives are write-once")
        fn.write_bytes(raw_bytes)
        status = getattr(r, "status_code", None)

        def log_row(results, total):
            w.writerow([_dt.datetime.now(_dt.timezone.utc)
                        .isoformat(timespec="seconds"), page_no, url, label,
                        status, len(raw_bytes),
                        hashlib.sha256(body_bytes).hexdigest(), results,
                        total, hashlib.sha256(raw_bytes).hexdigest(),
                        fn.name])
            lf.flush()
        if status != 200:                     # round-8: never terminal
            log_row(-1, -1)
            raise RuntimeError(f"[s09a] coveo page {page_no} ({label}): "
                               f"HTTP {status} - live capture aborts (error "
                               "pages are never a terminal page)")
        try:
            obj = json.loads(raw_bytes.decode("utf-8", errors="strict"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            log_row(-1, -1)                   # round-11: fail-closed parse
            raise RuntimeError(f"[s09a] coveo page {page_no} ({label}) is "
                               f"not valid UTF-8 JSON ({e}); the verbatim "
                               f"bytes are archived in {fn.name} - refusing "
                               "to parse a re-encoded or partial body"
                               ) from None
        total, results = obj.get("totalCount"), obj.get("results")
        if not isinstance(total, int) or not isinstance(results, list):
            log_row(-1, -1)
            raise RuntimeError(f"[s09a] coveo page {page_no} ({label}): "
                               "response lacks integer totalCount / list "
                               "results - schema drift, aborting")
        log_row(len(results), total)
        print(f"[s09a] coveo page {page_no} [{label}]: {len(results)} rows "
              f"(totalCount={total})")
        page_no += 1
        return obj

    rows_all, seen_ids = [], {}

    def take(results, label):
        for res in results:
            raw = res.get("raw") or {}
            pid = raw.get("permanentid")
            if not pid:
                raise RuntimeError(f"[s09a] {label}: result without "
                                   "permanentid - cannot guarantee "
                                   "uniqueness, aborting")
            if pid in seen_ids:
                raise RuntimeError(f"[s09a] duplicate permanentid {pid} "
                                   f"({seen_ids[pid]} and {label}) - "
                                   "windows are not disjoint, aborting")
            seen_ids[pid] = label
            imfdate = raw.get("imfdate")
            if imfdate is None:               # aq requires (@imfdate)
                raise RuntimeError(f"[s09a] {label}: result without imfdate "
                                   "despite the (@imfdate) filter - schema "
                                   "drift, aborting")
            rows_all.append(
                {"title": norm(re.sub(r"\s+", " ",
                                      str(res.get("title", "")))),
                 "url": res.get("clickUri", ""),
                 "pub_date": _imfdate_ms_to_iso(imfdate),
                 # A2: raw catalog string, unparsed - the frozen
                 # parse_report_no is the only interpreter
                 "report_no": _coveo_scalar(raw.get("seriesvolumeno")),
                 # provenance only; the frozen classifier reads none of these
                 "src_imfisocode": _coveo_scalar(raw.get("imfisocode"),
                                                 join=True),
                 "src_imfseries": _coveo_scalar(raw.get("imfseries"),
                                                join=True),
                 "src_imftype": _coveo_scalar(raw.get("imftype"))})

    def capture(kind, key, window) -> int:
        """Capture one window whole, or split it. Returns its totalCount."""
        label = f"{kind} {key}"
        obj = post_window(window, label)
        total, results = obj["totalCount"], obj["results"]
        time.sleep(sleep)
        if len(results) > total:
            raise RuntimeError(f"[s09a] {label}: {len(results)} results > "
                               f"totalCount {total} - incoherent response, "
                               "aborting")
        if total == 0:
            return 0
        if len(results) == total:             # A3: window returned ENTIRE
            take(results, label)
            return total
        children = _child_windows(kind, key)
        if not children:                      # day floor
            raise RuntimeError(f"[s09a] {label}: {total} items exceed what "
                               f"one request returns ({len(results)}) and a "
                               "single day cannot be split further; raise "
                               "imf_coveo.page_size and rerun in a fresh "
                               "directory")
        child_sum = 0
        for ckind, ckey, cwin in children:
            child_sum += capture(ckind, ckey, cwin)
        if child_sum != total:                # A3: split integrity
            raise RuntimeError(f"[s09a] {label}: children sum to "
                               f"{child_sum} but the window reports {total} "
                               "- the live index changed during capture or "
                               "the windows are not exhaustive; aborting "
                               "(rerun in a fresh directory)")
        return total

    try:
        # measurement request: the unpartitioned population size. Its single
        # result is NOT collected, so it cannot double-count.
        global_total = post_window(None, "global")["totalCount"]
        time.sleep(sleep)
        window_sum = 0
        for year in range(year_lo, year_hi + 1):
            window_sum += capture("year", year,
                                  (f"{year}/01/01", f"{year}/12/31"))
        if window_sum != global_total:        # A1: exhaustive/disjoint
            raise RuntimeError(f"[s09a] window sum {window_sum} != "
                               f"unpartitioned totalCount {global_total} - "
                               "the year windows do not cover the "
                               "population, aborting")
        if len(rows_all) != global_total:
            raise RuntimeError(f"[s09a] collected {len(rows_all)} rows != "
                               f"totalCount {global_total} - aborting")
    finally:
        lf.close()
    print(f"[s09a] coveo capture complete: requests={page_no}; "
          f"listed={global_total}; collected={len(rows_all)}")
    return pd.DataFrame(rows_all)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing",
                    help="captured metadata CSV (title,url,pub_date"
                         "[,language,report_no]); omit for LIVE SPROLL "
                         "capture (Stage-B only)")
    ap.add_argument("--config", default="config/config.yaml")
    ap.add_argument("--out-listing",
                    default="data/meta/imf_articleiv_listing.csv",
                    help="live mode: where the captured listing CSV is "
                         "archived before frame construction")
    ap.add_argument("--out-frame", required=True)
    ap.add_argument("--out-audit", required=True)
    ap.add_argument("--cutoff", default="2025-12-31")
    ap.add_argument("--year-lo", type=int, default=1994)
    ap.add_argument("--year-hi", type=int, default=2025)
    ap.add_argument("--i-am-in-stage-b", action="store_true",
                    help="required for any LIVE capture; this build stage only "
                         "consumes an already-captured listing CSV")
    a = ap.parse_args()
    if a.listing:
        listing = pd.read_csv(a.listing)
    else:
        if not a.i_am_in_stage_b:
            raise SystemExit("[s09a] REFUSING live SPROLL capture without "
                             "--i-am-in-stage-b (PREREG SS11: metadata "
                             "acquisition is a Stage-B act).")
        from utils import load_config, session_for
        cfg = load_config(a.config)
        raw_dir = Path("data/meta/imf_articleiv_raw")
        listing = fetch_live_coveo(session_for(cfg), raw_dir,
                                   raw_dir / "request_log.csv", cfg)
        Path(a.out_listing).parent.mkdir(parents=True, exist_ok=True)
        listing.to_csv(a.out_listing, index=False)
        print(f"[s09a] captured listing archived -> {a.out_listing}")
    frame, audit = build_frame(listing, a.cutoff, a.year_lo, a.year_hi)
    Path(a.out_frame).parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(a.out_frame, index=False); audit.to_csv(a.out_audit, index=False)
    print(f"[s09a] frame={len(frame)} included; audit rows={len(audit)}; "
          f"statuses={audit['status'].value_counts().to_dict()}")

if __name__ == "__main__":
    main()
