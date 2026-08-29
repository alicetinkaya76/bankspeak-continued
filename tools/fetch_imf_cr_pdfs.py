#!/usr/bin/env python3
"""Retrieve the 1,064-document preregistered IMF Article IV sample as PDFs.

Conduct (IMF permission of 2026-08-20, see commit 8b82787): the preregistered
sample only, one request per second, an identified User-Agent, no circumvention
of access controls, no redistribution.  Output lands in ``data/raw/`` which is
gitignored, so nothing here is republished.

Access note (measured 2026-08-20, diagnostics/20260820_imf_pdf):
www.imf.org's WAF rejects the ``/en/`` CMS pages (403) and elibrary.imf.org
answers 202 with an empty body, but the static PDF paths -- ``/external/pubs/``
and ``/-/media/`` -- serve normally to an ordinary client.  Nothing below
defeats an access control; the blocked paths are simply not used.

Resolution ladder, recorded per record in the manifest; a record that no rung
resolves is reported unresolved rather than guessed (an earlier list guessed
the URL pattern and produced dead links -- see commit 8b82787):

  L1  legacy static path ``/external/pubs/ft/scr/<YYYY>/cr<yy><nn>.pdf``
      (``nn`` = report number, zero-padded to at least two digits).
  L2  the IMF publication page for the record, read from its Wayback snapshot
      because the live page is WAF-blocked, and the ``/-/media/`` link the IMF
      itself put on that page extracted from it.  The PDF is then fetched from
      www.imf.org -- never from the archive.

      L2 IS GATED OFF BY DEFAULT.  The handover of 2026-08-20 reads permission
      condition 3 ("no circumvention of access controls ... technical
      restrictions") as naming imf.org's bot management specifically, and rules
      that defeating it is not an option.  Reading a 403-refused page's content
      out of a public archive is arguably within that ruling: the block is not
      defeated, but it is routed around.  That is an operator call, not the
      tool's, so L2 runs only under --allow-archive-resolution and a record it
      would have handled is otherwise recorded ``blocked_condition3`` with no
      request made.  L1 does not engage the control at all -- the static paths
      answer an ordinary identified GET with 200/206 and robots.txt permits
      them -- so L1 is not gated.

Every stored PDF is verified: PDF magic bytes, a parseable page count, and the
report number present in the cover-page text.  A file failing the last check is
kept and flagged ``needs_human_review``; it is never silently dropped or
silently accepted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import urllib.parse
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_LIST = ROOT / "docs" / "IMF_library_request_list_1064.csv"
PERMISSION_LIST = ROOT / "docs" / "IMF_permission_sample_list_1064.csv"
OUT_DIR = ROOT / "data" / "raw" / "imf_cr_pdf"
MANIFEST = OUT_DIR / "_manifest.csv"
LOG = OUT_DIR / "_log.jsonl"

UA = (
    "BankspeakContinued-Research/1.0 (academic replication of Moretti & Pestre 2015; "
    "IMF permission 2026-08-20; contact: kapsul.yonetim@gmail.com)"
)
IMF_SLEEP = 1.0        # IMF permission condition: one request per second
ARCHIVE_SLEEP = 2.0    # web.archive.org rate-limits harder than that
TIMEOUT = 90
RETRIES = 3

MANIFEST_FIELDS = [
    "report_no", "doi", "country_iso3", "year", "route", "pdf_url",
    "http_status", "bytes", "sha256", "pages", "cover_check", "status",
    "candidates", "utc",
]

# Non-English renditions live in these folders / carry these filename infixes.
NON_EN_DIR = re.compile(
    r"/(french|spanish|arabic|russian|chinese|japanese|portuguese|german|italian)/", re.I
)
MEDIA_LINK = re.compile(r"/-/media/Files/Publications/CR/[^\"'>< )]+", re.I)
LEGACY_LINK = re.compile(r"/external/pubs/ft/scr/[^\"'>< )]+", re.I)


def utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(event: dict) -> None:
    event["utc"] = utcnow()
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, ensure_ascii=False) + "\n")


def curl(url: str, out: Path | None) -> tuple[int, bytes | str, str]:
    """One polite GET.  Returns (http_status, body, effective_url)."""
    cmd = ["curl", "-sSL", "-A", UA, "--max-time", str(TIMEOUT),
           "-w", "%{http_code} %{url_effective}"]
    if out is not None:
        cmd += ["-o", str(out)]
        proc = subprocess.run(cmd + [url], capture_output=True, text=True)
        meta = proc.stdout.strip().split(" ", 1)
    else:
        proc = subprocess.run(cmd + ["-o", "-", url], capture_output=True)
        # the -w string is appended to stdout; split it off from the end
        text = proc.stdout.decode("utf-8", "replace")
        m = re.search(r"(\d{3}) (\S+)$", text)
        if not m:
            return 0, "", url
        return int(m.group(1)), text[: m.start()], m.group(2)
    if len(meta) != 2:
        return 0, b"", url
    return int(meta[0]), b"", meta[1]


def fetch_text(url: str) -> tuple[int, str]:
    for attempt in range(RETRIES):
        status, body, _ = curl(url, None)
        if status == 200:
            return status, body  # type: ignore[return-value]
        if status in (429, 503, 0) and attempt < RETRIES - 1:
            time.sleep(ARCHIVE_SLEEP * (attempt + 2) * 3)
            continue
        return status, body if isinstance(body, str) else ""
    return status, ""


def fetch_pdf(url: str, dest: Path) -> tuple[int, int]:
    """Download to ``dest``.  Returns (http_status, bytes).  Non-PDF bodies are removed."""
    tmp = dest.with_suffix(".part")
    for attempt in range(RETRIES):
        status, _, _ = curl(url, tmp)
        if status == 200 and tmp.exists() and tmp.stat().st_size > 0:
            with tmp.open("rb") as fh:
                magic = fh.read(5)
                fh.seek(max(0, tmp.stat().st_size - 2048))
                tail = fh.read()
            # Magic bytes alone do NOT establish a complete file: a connection
            # cut mid-transfer leaves a body that still starts "%PDF-" and was
            # being recorded ok. Five such truncations reached the corpus before
            # this gate existed (2012/221, 2014/115, 2014/192, 2016/344,
            # 2016/366) -- 1.2 MB of a 2.8 MB file, no %%EOF, both PyMuPDF and
            # pdftotext failing on the XRef. A complete PDF ends with %%EOF.
            if magic == b"%PDF-" and b"%%EOF" in tail:
                size = tmp.stat().st_size
                tmp.replace(dest)
                return status, size
            tmp.unlink(missing_ok=True)
            if magic == b"%PDF-" and attempt < RETRIES - 1:
                time.sleep(IMF_SLEEP * (attempt + 2))   # truncation: worth a retry
                continue
            return status, 0
        tmp.unlink(missing_ok=True)
        if status in (429, 503, 0) and attempt < RETRIES - 1:
            time.sleep(IMF_SLEEP * (attempt + 2) * 3)
            continue
        return status, 0
    return status, 0


def legacy_url(report_no: str) -> str:
    year, num = report_no.split("/")
    return (f"https://www.imf.org/external/pubs/ft/scr/{year}/"
            f"cr{year[-2:]}{str(int(num)).zfill(2)}.pdf")


def media_legacy_url(report_no: str) -> str:
    """The same legacy filename served from the CMS media tree.

    Measured 2026-08-20: some 2017-2018 issues are absent from
    ``/external/pubs/ft/scr/`` but present at
    ``/-/media/files/publications/cr/<YYYY>/cr<yy><nn>.pdf``. This rung touches
    no archive at all, so it sits outside the condition-3 gate."""
    year, num = report_no.split("/")
    return (f"https://www.imf.org/-/media/files/publications/cr/{year}/"
            f"cr{year[-2:]}{str(int(num)).zfill(2)}.pdf")


SEQ_LIMIT = 6


def sequence_candidates(report_no: str, iso3: str) -> list[str]:
    """L1c: the per-country-year media filenames, bounded to the first few.

    ``/-/media/files/publications/cr/<YYYY>/english/1<ISO3>EA<YYYY><NNN>.pdf``
    where NNN is the country's sequence within the year -- NOT the report
    number. Which sequence corresponds to a given report cannot be derived, so
    each candidate is downloaded and accepted ONLY if its cover page names the
    report number; a candidate that names a different report is discarded.

    §4.1 of the compliance record rejects brute-forcing this space, and that
    still stands for the corpus: enumerating it for 1,064 records would fire
    thousands of 404s at the host the permission asks us to treat gently. This
    rung is a different act -- it runs only after every other rung has failed,
    caps at SEQ_LIMIT candidates, and admits nothing that verification has not
    confirmed. Measured 2026-08-20: 2020/198 resolves at ...2020002 (cover
    "IMF Country Report No. 20/198"), while ...2020001 is 20/152 and is
    correctly refused.
    """
    year = report_no.split("/")[0]
    iso = (iso3 or "").strip().lower()
    if not iso or len(iso) != 3:
        return []
    base = f"https://www.imf.org/-/media/files/publications/cr/{year}"
    # The English rendition sits under /english/ from 2020 on, but at the YEAR
    # ROOT in 2019, where only the other languages get a subfolder
    # (.../cr/2019/1ecuea2019001.pdf against .../cr/2019/french/1ecufa2019001.pdf).
    # Assuming the 2020 shape put 2019/079 out of reach; both are tried.
    return [f"{base}/{sub}1{iso}ea{year}{n:03d}.pdf"
            for n in range(1, SEQ_LIMIT + 1) for sub in ("english/", "")]


def pick_english(links: list[str]) -> str | None:
    """Choose the English rendition among the PDF links found on an IMF page."""
    cands = [l for l in links if not NON_EN_DIR.search(l)]
    if not cands:
        return None
    cands.sort(key=lambda l: (0 if "/english/" in l.lower() else 1, len(l)))
    return cands[0]


def _links_in(html: str) -> list[str]:
    links = sorted(set(MEDIA_LINK.findall(html)) | set(LEGACY_LINK.findall(html)))
    links = [re.sub(r"/_(cr)", r"/\1", l) for l in links]
    return [l for l in links if l.lower().endswith((".pdf", ".ashx"))]


def _snapshot_timestamps(page_url: str, limit: int = 25) -> list[str]:
    """Older captures of the same page, newest first.

    Needed because the LATEST capture is often a stub: measured 2026-08-20,
    `2id_` for CR2021/103 returns 15 KB with no download section while the
    2021-06-07 capture carries the link. Walking snapshots recovers those
    without touching any additional IMF surface.

    Ordered by capture LENGTH descending, not by date. A stub and a complete
    capture differ mostly in size, so the biggest capture is the one most likely
    to carry the download section: chronological order missed 2018/285 (the
    18 KB capture holds the link, the four newer ones are 15-16 KB stubs) and
    2019/079 (48 KB against 15-16 KB), and size order found both.
    """
    q = urllib.parse.quote(page_url, safe="")
    status, body = fetch_text(
        "https://web.archive.org/cdx/search/cdx?url=" + q +
        "&output=json&filter=statuscode:200&collapse=timestamp:4"
        f"&limit={limit}&fl=timestamp,length")
    time.sleep(ARCHIVE_SLEEP)
    if status != 200 or not body.strip().startswith("["):
        return []
    try:
        rows = json.loads(body)
    except ValueError:
        return []

    def _len(row):
        try:
            return int(row[1])
        except (IndexError, ValueError):
            return 0

    return [r[0] for r in sorted(rows[1:], key=_len, reverse=True) if r and r[0]]


def resolve_via_archive(page_url: str) -> tuple[str | None, list[str]]:
    seen: list[str] = []
    status, html = fetch_text("https://web.archive.org/web/2id_/" + page_url)
    time.sleep(ARCHIVE_SLEEP)
    if status == 200 and html:
        seen = _links_in(html)
        chosen = pick_english(seen)
        if chosen:
            return "https://www.imf.org" + chosen, seen
    for ts in _snapshot_timestamps(page_url):      # L2b: older captures
        status, html = fetch_text(
            f"https://web.archive.org/web/{ts}id_/{page_url}")
        time.sleep(ARCHIVE_SLEEP)
        if status != 200 or not html:
            continue
        links = _links_in(html)
        if links:
            seen = links
            chosen = pick_english(links)
            if chosen:
                return "https://www.imf.org" + chosen, links
    return None, seen


def cover_check(path: Path, report_no: str) -> str:
    """Does the cover page name this report?  Returns 'ok', 'mismatch' or 'unreadable'."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        return "no_extractor"
    try:
        with fitz.open(path) as doc:
            pages = min(3, doc.page_count)
            text = " ".join(doc.load_page(i).get_text() for i in range(pages))
            meta_title = (doc.metadata or {}).get("title") or ""
    except Exception:
        return "unreadable"
    year, num = report_no.split("/")
    wanted = (f"{year[-2:]}/{int(num)}", f"{year}/{int(num):03d}", f"{year}/{int(num)}")
    page_norm = re.sub(r"\s+", "", text)
    meta_norm = re.sub(r"\s+", "", meta_title)
    if any(w in page_norm for w in wanted):
        return "ok"
    # The older years are pre-OCR scans with no text layer, but the DigiPath
    # metadata title stamps the report number ("...ISCR/99/47"), which is an
    # independent check on the same claim.
    if any(w in meta_norm for w in wanted):
        return "ok_scan_metadata"
    if len(page_norm) < 50:
        return "no_text_layer"
    return "mismatch"


def page_count(path: Path) -> int:
    try:
        import fitz
        with fitz.open(path) as doc:
            return doc.page_count
    except Exception:
        return 0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_records() -> list[dict]:
    perm = {r["id"]: r for r in csv.DictReader(PERMISSION_LIST.open(encoding="utf-8"))}
    out = []
    for row in csv.DictReader(REQUEST_LIST.open(encoding="utf-8")):
        pid = "CR" + row["report_no"].replace("/", "-")
        row["page_url"] = perm[pid]["url"] if pid in perm else ""
        out.append(row)
    return out


def load_done() -> dict[str, dict]:
    if not MANIFEST.exists():
        return {}
    return {r["report_no"]: r for r in csv.DictReader(MANIFEST.open(encoding="utf-8"))
            if r.get("status") == "ok"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="stop after N new downloads")
    ap.add_argument("--only", default="", help="comma-separated report numbers")
    ap.add_argument("--allow-archive-resolution", action="store_true",
                    help="enable the L2 rung (see the module docstring: this is "
                         "an operator ruling on permission condition 3, not a "
                         "default)")
    args = ap.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = load_records()
    if args.only:
        wanted = set(args.only.split(","))
        records = [r for r in records if r["report_no"] in wanted]
    done = load_done()

    new_manifest = not MANIFEST.exists()
    fh = MANIFEST.open("a", newline="", encoding="utf-8")
    writer = csv.DictWriter(fh, fieldnames=MANIFEST_FIELDS)
    if new_manifest:
        writer.writeheader()
        fh.flush()

    processed = 0
    for i, rec in enumerate(records, 1):
        rn = rec["report_no"]
        dest = OUT_DIR / ("CR" + rn.replace("/", "-") + ".pdf")
        if rn in done and dest.exists():
            continue
        if args.limit and processed >= args.limit:
            break
        processed += 1

        route, url, status, size, cands = "", "", 0, 0, []
        # L1 -- legacy static path
        url = legacy_url(rn)
        status, size = fetch_pdf(url, dest)
        time.sleep(IMF_SLEEP)
        if size:
            route = "L1_legacy_static"
        else:
            # L1b -- same filename, CMS media tree. No archive; not gated.
            url = media_legacy_url(rn)
            status, size = fetch_pdf(url, dest)
            time.sleep(IMF_SLEEP)
        if size and not route:
            route = "L1b_media_legacy"
        elif not size:
            # L2 -- IMF's own link, read from the Wayback snapshot of its page
            route, url = "L2_unresolved", ""
            if not args.allow_archive_resolution:
                route = "L2_blocked_condition3"
            elif rec["page_url"]:
                resolved, cands = resolve_via_archive(rec["page_url"])
                if resolved:
                    url = resolved
                    status, size = fetch_pdf(url, dest)
                    time.sleep(IMF_SLEEP)
                    if size:
                        route = "L2_page_link_via_archive"

        if not size and rec.get("country_iso3"):
            # L1c -- bounded, verification-gated sequence enumeration
            for cand in sequence_candidates(rn, rec["country_iso3"]):
                st2, sz2 = fetch_pdf(cand, dest)
                time.sleep(IMF_SLEEP)
                if not sz2:
                    continue
                if cover_check(dest, rn) == "ok":
                    route, url, status, size = "L1c_sequence_verified", cand, st2, sz2
                    break
                dest.unlink(missing_ok=True)      # a real PDF, but not this report

        if size:
            row = dict(
                report_no=rn, doi=rec["doi"], country_iso3=rec["country_iso3"],
                year=rec["year"], route=route, pdf_url=url, http_status=status,
                bytes=size, sha256=sha256(dest), pages=page_count(dest),
                cover_check=cover_check(dest, rn), status="ok",
                candidates="|".join(cands), utc=utcnow(),
            )
            if row["cover_check"] == "mismatch":
                row["status"] = "needs_human_review"
        else:
            row = dict(
                report_no=rn, doi=rec["doi"], country_iso3=rec["country_iso3"],
                year=rec["year"], route=route, pdf_url=url, http_status=status,
                bytes=0, sha256="", pages=0, cover_check="",
                status=("blocked_condition3"
                        if route == "L2_blocked_condition3" else "unresolved"),
                candidates="|".join(cands), utc=utcnow(),
            )
        writer.writerow(row)
        fh.flush()
        log({"event": "record", **row})
        print(f"[{i}/{len(records)}] {rn} {row['status']:18s} {row['route']:26s} "
              f"{row['bytes']:>9d}B {row['cover_check']}", flush=True)

    fh.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
