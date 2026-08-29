#!/usr/bin/env python3
"""Quality gate (ruling D-10): no unruled hard defect may reach the features.

Runs after the quality scan inside the post-SAP driver. It reads the fresh
flags, the analysis index (`frozen_sampling_v2.csv`) and the ruling ledgers, and
**exits nonzero** if any document in the analysis index carries a hard-class
flag (`non_english_suspected`, `mojibake_suspected`, `table_dump_suspected`)
that no recorded ruling covers. The driver stops there; the flag gets a dated
ruling; the run resumes. That is D-10's letter: "any new flag gets a dated
ruling before the analysis proceeds."

`low_prose_borderline` warns but does not stop — D-10 ruled the class kept
(genuine prose diluted by tables), and a re-run after the D-7 refetch is
expected to lift the spacing-caused ones out of the band.

Rulings recognised: `d8_exclusions.csv` (language, D-8/D-11),
`ocr_overrides.csv` (broken CMaps, D-9/D-12 — after OCR these should scan clean,
so a persistent flag on them is itself worth seeing), and `d13_kept.csv`
(material ruled not-a-defect, D-13). A ruling is a row in a ledger, so the gate
cannot be satisfied by prose alone.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "meta"
HARD = {"non_english_suspected", "mojibake_suspected", "table_dump_suspected"}


def load_ids(path: Path, col: str = "id") -> set[str]:
    if not path.exists():
        return set()
    return {r[col] for r in csv.DictReader(path.open(encoding="utf-8"))}


def main() -> int:
    index = load_ids(META / "frozen_sampling_v2.csv")
    ruled = (load_ids(META / "d8_exclusions.csv")        # D-8, D-11 language
             | load_ids(META / "ocr_overrides.csv")      # D-9, D-12 broken CMaps
             | load_ids(META / "d13_kept.csv"))          # D-13 ruled not-a-defect
    flags = list(csv.DictReader(
        (META / "corpus_quality_flags.csv").open(encoding="utf-8")))

    unruled, borderline = [], 0
    for r in flags:
        if r["id"] not in index:
            continue                       # not in the analysis corpus
        if r["verdict"] in HARD and r["id"] not in ruled:
            unruled.append(r)
        elif r["verdict"] == "low_prose_borderline":
            borderline += 1

    print(f"[gate] index {len(index)}, flags {len(flags)}, "
          f"ruled ids {len(ruled)}, borderline kept {borderline}")
    if unruled:
        print(f"[gate] STOPPING: {len(unruled)} hard flag(s) with no recorded ruling:")
        for r in unruled:
            print(f"  {r['verdict']:22s} {r['stratum']:14s} {r['path']}")
            print(f"      {r['evidence']}")
        print("[gate] rule on these (a dated addendum to "
              "docs/DECISIONS_20260820_stageb_close.md), extend the ledgers, "
              "then resume with --from-stage quality_scan")
        return 1
    print("[gate] clean — every hard flag in the analysis corpus has a ruling")
    return 0


if __name__ == "__main__":
    sys.exit(main())
