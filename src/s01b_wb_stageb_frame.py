"""s01b — World Bank Stage-B metadata frame capture (PREREG §7.6).

The `annual_report`, `icr` and `pad` frames inside the sealed package are the
Stage-A capture of 6 August 2026. PREREG §7.6 requires the frame to be captured
and hashed AT THE STAGE-B SNAPSHOT DATE, so the confirmatory P1/P2 panels run on
a frame whose capture date is recorded rather than inherited. This module is
that capture. It adds no decision logic: the rules that decide what a document
IS stay in `s01_fetch_metadata.fetch_stratum_year`, which is already hardened
(rounds 8-12: declared-total drift, an empty page before the total is reached, a
non-string or duplicate id, and a final count differing from the declared total
all RAISE). s01b is transport, archiving and shaping only.

Window (A6 decision, 2026-08-20): **1946-2026**, matching the Stage-A window so
the new frame can be compared like-for-like against `frozen_sampling_v1.csv`.
Calendar-2026 is captured but flagged: PREREG §11.4 excludes it from the
confirmatory frame (Appendix B cutoff: publication date <= 2025-12-31) and
routes 2026 to a prespecified descriptive update off a 2027-01-15 snapshot. The
flag is derived from each record's own `docdt`, which is what §11.4 actually
names -- NOT from the query year, which would silently agree with it and so
verify nothing.

Output is a frame CSV in the `[institution, genre, year, id, ...]` shape
`s09_frame_sampler` requires; sampling stays that module's job, with its
per-cell seeds. Nothing here samples.

Refuses to run without `--i-am-in-stage-b` (PREREG §11: Stage-B is metadata
only). Raw archives are write-once and a rerun must target a fresh directory;
the request log is append-only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib as _h
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import ROOT, load_config, iter_documents  # noqa: E402

INSTITUTION = "wb"
CONFIRMATORY_CUTOFF = "2025-12-31"
LOG_HEADER = ["utc", "genre", "year", "os", "total", "rows_returned",
              "payload_sha256", "raw_file", "params_json"]
FRAME_FIELDS = ["institution", "genre", "year", "id", "docdt", "repnb",
                "display_title", "txturl", "pdfurl", "confirmatory_eligible",
                "docdt_year_matches_cell"]


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def confirmatory_eligible(docdt: str) -> bool:
    """PREREG §11.4: publication date <= 2025-12-31. A record with no parseable
    date is NOT eligible -- an unknown date is never treated as an early one."""
    d = (docdt or "").strip()[:10]
    if len(d) != 10 or d[4] != "-" or d[7] != "-":
        return False
    return d <= CONFIRMATORY_CUTOFF


def fetch_live(cfg: dict, strata: dict, y_lo: int, y_hi: int, raw_dir: Path,
               log_csv: Path | None = None, session=None) -> list[dict]:
    """LIVE capture via the s01 fetch stack, one (genre, year) request series at
    a time. Archives EVERY raw API page verbatim to
    ``raw_dir/{genre}_{year}_os{offset}.json`` and every retried 429/5xx body to
    ``..._attempt{n}_status{code}.json``, both write-once, both logged.

    Returns a flat list of ``{"genre", "year", "record"}`` dicts in capture
    order; shaping into the frame is ``build_frame``'s job so that the capture
    can be replayed from the archive without re-requesting anything.
    """
    from utils import session_for
    from s01_fetch_metadata import fetch_stratum_year

    sess = session if session is not None else session_for(cfg)
    raw_dir.mkdir(parents=True, exist_ok=True)
    leftover = sorted(p.name for p in raw_dir.glob("*.json"))
    if leftover:
        raise RuntimeError(
            f"[s01b] raw directory already holds {len(leftover)} archive(s) "
            f"(e.g. {leftover[0]}) — raw archives are write-once; a rerun must "
            "target a fresh raw directory")

    log_csv = log_csv or (raw_dir / "request_log.csv")
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_csv.exists()
    out: list[dict] = []

    with open(log_csv, "a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if write_header:
            w.writerow(LOG_HEADER)
        for genre in sorted(strata):
            labels = strata[genre]["docty_exact"]
            for year in range(y_lo, y_hi + 1):
                pages: list[int] = []
                attempts = [0]

                def attempt_hook(params, raw_bytes, status, _g=genre, _y=year):
                    if raw_bytes is None:
                        raise RuntimeError(
                            "[s01b] a retried response supplied no raw byte "
                            "body; capture requires the VERBATIM server bytes")
                    attempts[0] += 1
                    os_ = params.get("os", 0)
                    fn = raw_dir / (f"{_g}_{_y}_os{os_}_attempt"
                                    f"{attempts[0]}_status{status}.json")
                    if fn.exists():
                        raise RuntimeError(f"[s01b] {fn.name} already exists — "
                                           "attempt archives are write-once")
                    fn.write_bytes(raw_bytes)
                    w.writerow([_utc(), _g, _y, os_, "", f"attempt:{status}",
                                _h.sha256(raw_bytes).hexdigest(), fn.name,
                                json.dumps(params, sort_keys=True)])

                def hook(params, raw_bytes, _g=genre, _y=year, _pages=pages):
                    if raw_bytes is None:
                        raise RuntimeError(
                            "[s01b] transport supplied no raw byte body; "
                            "capture requires the VERBATIM server bytes")
                    os_ = params.get("os", 0)
                    fn = raw_dir / f"{_g}_{_y}_os{os_}.json"
                    if fn.exists():
                        raise RuntimeError(
                            f"[s01b] {fn.name} already exists — raw archives "
                            "are write-once; a rerun must target a fresh raw "
                            "directory")
                    fn.write_bytes(raw_bytes)
                    try:                       # informational only: the frame's
                        pl = json.loads(raw_bytes)   # data comes from s01's parse
                        docs = pl.get("documents") or {}
                        nrows = len([k for k in docs if k != "facets"])
                        tot = pl.get("total", "")
                    except Exception:
                        nrows, tot = "unparsed", ""
                    w.writerow([_utc(), _g, _y, os_, tot, nrows,
                                _h.sha256(raw_bytes).hexdigest(), fn.name,
                                json.dumps(params, sort_keys=True)])
                    _pages.append(os_)

                recs = fetch_stratum_year(sess, cfg, labels, year,
                                          page_hook=hook,
                                          attempt_hook=attempt_hook)
                for r in recs:
                    out.append({"genre": genre, "year": year, "record": r})
                print(f"[s01b] {genre} {year}: {len(recs)} record(s) over "
                      f"{len(pages)} raw page(s) archived", flush=True)
    return out


def build_frame(captured: list[dict]) -> list[dict]:
    """Shape the capture into `s09_frame_sampler`'s input contract.

    `year` is the CELL year (the query window), because the cell is what the
    per-cell seed and the sampler key on. `confirmatory_eligible` is derived
    independently from the record's own `docdt`, and the two are compared in
    `docdt_year_matches_cell` rather than assumed to agree.
    """
    rows, seen = [], set()
    for item in captured:
        r = item["record"]
        rid = str(r.get("id", "")).strip()
        if not rid:
            raise RuntimeError("[s01b] record with an empty id reached the "
                               "frame builder — schema failure")
        if rid in seen:
            raise RuntimeError(f"[s01b] duplicate document id {rid!r} across "
                               "genres/years — refusing to double-count")
        seen.add(rid)
        docdt = str(r.get("docdt", ""))
        rows.append({
            "institution": INSTITUTION,
            "genre": item["genre"],
            "year": item["year"],
            "id": rid,
            "docdt": docdt,
            "repnb": str(r.get("repnb", "")),
            "display_title": str(r.get("display_title", ""))[:200],
            "txturl": str(r.get("txturl", "")),
            "pdfurl": str(r.get("pdfurl", "")),
            "confirmatory_eligible": confirmatory_eligible(docdt),
            "docdt_year_matches_cell": docdt[:4] == str(item["year"]),
        })
    rows.sort(key=lambda x: (x["genre"], x["year"], x["id"]))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    ap.add_argument("--raw-dir", default=str(ROOT / "data" / "meta" / "wb_p1p2_raw"))
    ap.add_argument("--frame-out",
                    default=str(ROOT / "data" / "meta" / "wb_p1p2_frame.csv"))
    ap.add_argument("--year-lo", type=int, default=None)
    ap.add_argument("--year-hi", type=int, default=None)
    ap.add_argument("--strata", default="",
                    help="comma-separated subset; default is every configured stratum")
    ap.add_argument("--i-am-in-stage-b", action="store_true",
                    help="required: PREREG §11 makes Stage-B metadata-only, so a "
                         "live capture is an explicit act")
    a = ap.parse_args(argv)

    if not a.i_am_in_stage_b:
        sys.exit("[s01b] REFUSING to run without --i-am-in-stage-b "
                 "(PREREG §11: Stage-B is metadata only)")

    cfg = load_config(a.config)
    strata = dict(cfg["strata"])
    if a.strata:
        want = {s.strip() for s in a.strata.split(",") if s.strip()}
        missing = want - set(strata)
        if missing:
            sys.exit(f"[s01b] unknown stratum/strata: {sorted(missing)}")
        strata = {k: v for k, v in strata.items() if k in want}

    y_lo = a.year_lo if a.year_lo is not None else cfg["years"]["start"]
    y_hi = a.year_hi if a.year_hi is not None else cfg["years"]["end"]

    frame_out = Path(a.frame_out)
    if frame_out.exists():
        sys.exit(f"[s01b] REFUSING to overwrite {frame_out} (write-once). "
                 "A recapture must target a fresh path.")

    captured = fetch_live(cfg, strata, y_lo, y_hi, Path(a.raw_dir))
    rows = build_frame(captured)

    frame_out.parent.mkdir(parents=True, exist_ok=True)
    with frame_out.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=FRAME_FIELDS)
        wr.writeheader()
        wr.writerows(rows)

    n_2026 = sum(1 for r in rows if not r["confirmatory_eligible"])
    n_mismatch = sum(1 for r in rows if not r["docdt_year_matches_cell"])
    print(f"[s01b] wrote {frame_out}: {len(rows)} row(s), "
          f"{y_lo}-{y_hi}, strata {sorted(strata)}")
    print(f"[s01b] confirmatory-ineligible (docdt > {CONFIRMATORY_CUTOFF} or "
          f"unparseable): {n_2026}")
    if n_mismatch:
        print(f"[s01b] NOTE: {n_mismatch} record(s) whose docdt year differs "
              f"from their cell year — flagged in the frame, not corrected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
