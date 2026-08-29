#!/usr/bin/env python3
"""Count how each of the 1,064 comparator documents was actually retrieved.

The manuscript and the data-availability statement both printed "710 came from
static paths, 354 through a public web archive, and five through media or
sequence paths." Those sum to 1,069, five more than the corpus.

710 is the number of ROWS in the retrieval manifest carrying the static route,
and the manifest is an attempt log: 1,120 rows for 1,064 documents, because 42
report numbers were retried. Five documents downloaded incompletely, were
withdrawn, and were fetched again on the same static route, so they each own two
static rows. Counting rows counted them twice.

(The coincidence that 705 + 4 + 1 also equals 710 is what let the wrong number
look like a plausible total for as long as it did. It is not the derivation: the
five media and sequence documents pair with unresolved archive attempts, not
with static ones.)

Documents, not attempts, is the count a reader needs, because the claim being
made is a partition of the corpus.
"""
from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "meta" / "imf_retrieval" / "_manifest.csv"
INDEX = ROOT / "data" / "meta" / "imf_document_index.csv"
OUT = ROOT / "data" / "analysis" / "retrieval_route_tally.json"

SUCCESS = ["L1_legacy_static", "L1b_media_legacy", "L1c_sequence_verified",
           "L2_page_link_via_archive"]
LABEL = {"L1_legacy_static": "static path",
         "L1b_media_legacy": "media tree",
         "L1c_sequence_verified": "verification-gated sequence",
         "L2_page_link_via_archive": "public web archive"}


def main() -> int:
    if not MANIFEST.exists():
        raise SystemExit(f"[routes] needs {MANIFEST.relative_to(ROOT)} "
                         "(restricted; present only in the author's tree)")
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    per_doc: dict[str, str] = {}
    for r in rows:
        if r["route"] in SUCCESS:
            # First success wins; a document has at most one successful rung by
            # construction, and the ladder is tried in order.
            per_doc.setdefault(r["report_no"], r["route"])

    tally = collections.Counter(per_doc.values())
    total = sum(tally.values())
    n_index = sum(1 for _ in csv.DictReader(INDEX.open(encoding="utf-8")))
    if total != n_index:
        raise SystemExit(f"[routes] REFUSING: routes cover {total} documents but "
                         f"the published index lists {n_index}")

    row_counts = collections.Counter(r["route"] for r in rows)
    print(f"attempt rows {len(rows)}, documents {len(per_doc)}\n")
    print(f"{'route':32s} {'documents':>10s} {'rows':>7s}")
    for k in SUCCESS:
        print(f"{LABEL[k]:32s} {tally[k]:10d} {row_counts[k]:7d}")
    print(f"{'TOTAL':32s} {total:10d}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"attempt_rows": len(rows), "documents": total,
         "by_route_documents": {LABEL[k]: tally[k] for k in SUCCESS},
         "by_route_rows": {LABEL[k]: row_counts[k] for k in SUCCESS}},
        indent=1), encoding="utf-8")
    print(f"\n[routes] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
