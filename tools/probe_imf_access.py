#!/usr/bin/env python3
"""Probe the access route the Data Availability Statement promises, and record it.

A verification pass objected that the manuscript asserts an HTTP 200 recheck on
2026-08-29 with no artifact in the repository to show for it, and that the route
the statement describes — resolve the DOI through the IMF eLibrary — is the one
`docs/IMF_ACCESS_COMPLIANCE_20260820.md` records as sitting behind a silent bot
wall. Both halves of that objection deserve an answer made of evidence rather
than of assurance, which is what this produces.

The probe samples documents from the deposited index, tries each reachable route
in turn, and writes the status codes, content types and byte counts to a dated
artifact. It downloads nothing: HEAD requests only, so no IMF document is
retrieved, stored or redistributed by running it.

If the DOI route does not serve a document, the statement must say so and name
the route that does. A data-availability claim the authors could not themselves
walk is worse than no claim.
"""
from __future__ import annotations

import csv
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "meta" / "imf_document_index.csv"
OUT = ROOT / "data" / "meta" / "imf_access_probe.json"
UA = {"User-Agent": "Mozilla/5.0 (compatible; academic-access-probe)"}
SEED = 42


def static_url(report_no: str) -> str:
    """The legacy static path the retrieval ladder's first rung used."""
    year, num = report_no.split("/")
    return (f"https://www.imf.org/external/pubs/ft/scr/{year}/"
            f"cr{year[-2:]}{str(int(num)).zfill(2)}.pdf")


def probe(url: str) -> dict:
    """Read the first five bytes, because the status code lies here.

    A HEAD-only probe cannot answer this question. When a report is absent the
    IMF site redirects to `/en/errors/404?URL=…`, which returns **HTTP 200 with
    text/html** — so status alone reports success for a 178 KB error page. That
    is exactly the mistake this module exists to stop me repeating: the first
    version of this check reported "200 application/pdf" for documents that were
    not there. Five bytes settle it; nothing more is read, so no document is
    retrieved, stored or redistributed.
    """
    try:
        r = requests.get(url, headers=UA, allow_redirects=True, timeout=30,
                         stream=True)
        magic = r.raw.read(5) if r.status_code == 200 else b""
        r.close()
        return {"url": url, "status": r.status_code,
                "content_type": r.headers.get("Content-Type", ""),
                "is_pdf": magic.startswith(b"%PDF"),
                "final_url": r.url[:160]}
    except Exception as e:                       # a failure is a result
        return {"url": url, "status": None, "is_pdf": False,
                "error": type(e).__name__}


head = probe                                     # call sites keep their name


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    with INDEX.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    rng = random.Random(SEED)
    sample = rng.sample(rows, min(n, len(rows)))

    out = {"probed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "method": "GET, first 5 bytes only; no document retrieved or stored",
           "n_sampled": len(sample), "seed": SEED, "documents": []}

    print(f"Probing {len(sample)} documents, 5-byte magic check, seed {SEED}\n")
    for r in sample:
        rec = {"report_no": r["report_no"], "year": r["year"],
               "static": head(static_url(r["report_no"]))}
        if r.get("doi"):
            rec["doi"] = head(f"https://doi.org/{r['doi']}")
        out["documents"].append(rec)
        st = rec["static"]
        dm = rec.get("doi", {})
        print(f"  {r['report_no']:10s} static {st.get('status')} "
              f"{'PDF' if st.get('is_pdf') else 'not a PDF':10s} | "
              f"doi {dm.get('status','-')} "
              f"{'PDF' if dm.get('is_pdf') else ''}")

    ok_static = sum(1 for d in out["documents"] if d["static"].get("is_pdf"))
    doi_pdf = sum(1 for d in out["documents"] if d.get("doi", {}).get("is_pdf"))
    out["summary"] = {
        "static_serves_pdf": f"{ok_static}/{len(sample)}",
        "doi_serves_pdf": f"{doi_pdf}/{sum(1 for d in out['documents'] if 'doi' in d)}",
    }
    print(f"\n  static path serves a PDF: {ok_static}/{len(sample)}")
    print(f"  DOI resolves to a PDF:    {doi_pdf}/"
          f"{sum(1 for d in out['documents'] if 'doi' in d)}")
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n[probe] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
