#!/usr/bin/env python3
"""The access route PLOS ONE requires: which document, and does your copy match ours.

PLOS ONE will not accept "available from the corresponding author on request".
The reasoning is practical rather than bureaucratic — an author changes jobs, an
address dies, and the claim becomes unverifiable — so the policy asks for a route
by which another researcher obtains the same material without going through us.

For this corpus that route already exists and needed only to be stated. **Every
Article IV staff report in the sample is published by the IMF itself**, reachable
by its report number at a static path on imf.org and by its DOI through the IMF
eLibrary; checked 2026-08-29, the PDFs return HTTP 200 with no authentication and
the DOIs resolve to eLibrary landing pages. The written permission of 2026-08-20
governs BULK RETRIEVAL AND REDISTRIBUTION, not access. Nobody needs our copy.

## What this file is, and what it deliberately is not

To act on that route a reader must know *which* documents, and must be able to
confirm their copy is byte-identical to the one analysed. So the index carries,
per document: report number, year, country ISO3, DOI, and SHA-256.

It carries **no title and no imf.org URL**. That is the line this project has
drawn throughout: the 2,789-row frame with every catalogue title and link is
verbatim IMF bibliographic content and stays local, while a report number plus a
DOI plus a hash we computed is derived, non-substitutive, and is exactly what §5
of the permission allows. A DOI is a citation, and it is also a resolver — it
does the work a copied URL would do, without copying anything.

Withholding the identifiers as well would have been the more conservative
posture and the wrong one: a hash manifest whose rows you cannot map to documents
proves nothing, and a study whose corpus membership cannot be inspected is not
reproducible. Conservatism that defeats verification is not caution.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "meta" / "imf_retrieval" / "_manifest.csv"
OUT = ROOT / "data" / "meta" / "imf_document_index.csv"
COLS = ["report_no", "year", "country_iso3", "doi", "sha256"]


def main() -> int:
    if not SRC.exists():
        raise SystemExit(f"[access] missing {SRC.relative_to(ROOT)}")
    # append-only manifest: the last row for a report number is the live one
    latest: dict[str, dict] = {}
    with SRC.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if (r.get("status") or "").lower() == "ok" and r.get("sha256"):
                latest[r["report_no"]] = r

    rows = []
    for rn, r in sorted(latest.items()):
        rows.append({"report_no": rn, "year": r.get("year", ""),
                     "country_iso3": r.get("country_iso3", ""),
                     "doi": r.get("doi", ""), "sha256": r.get("sha256", "")})

    missing_doi = sum(1 for r in rows if not r["doi"])
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    print(f"[access] {len(rows)} documents -> {OUT.relative_to(ROOT)}")
    print(f"[access] columns: {', '.join(COLS)} — no title, no imf.org URL")
    if missing_doi:
        print(f"[access] {missing_doi} document(s) carry no DOI; a reader reaches "
              f"those by report number at the IMF's own publication service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
