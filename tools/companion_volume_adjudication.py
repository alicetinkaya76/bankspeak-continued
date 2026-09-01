#!/usr/bin/env python3
"""Adjudicate the "duplicate" Annual-Report volumes by title, not by metadata key.

`src/s10_assemble_ar.py` excludes a record when its (repnb, volnb) key has
already been seen. That rule is content-blind, and an external review found what
it costs: of the five files it excluded, **three are not duplicates at all**.

  2008  46256/17   same title as the kept record          -> a real duplicate
  2011  64440/1    same title as the kept record          -> a real duplicate
  2023 185130/1    "... Organizational Information and Lending Data Appendixes"
  2023 185130/1    "... IBRD and IDA Management Discussion & Analysis and
                    Financial Statements"
  2024 194209/1    "... Executive Summary"

The last three are companion products of the same report family, sharing a
metadata key with the main volume and carrying different text. They are 42,404,
94,717 and 6,358 tokens. Excluding them removes 137,121 tokens from fiscal 2023
alone, against the 43,795 that were kept — and fiscal 2023 is one of the three
years carrying the headline decline.

This does not touch the frozen assembly. It quantifies the error and reports the
corrected series beside the frozen one, which is this project's standing practice
for a defect found after a freeze.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURE = "temporal_per1k"
EARLY, LATE = (1946, 1965), (2020, 2024)
OUT = ROOT / "data" / "analysis" / "companion_volume_adjudication.json"


def load():
    led = list(csv.DictReader(
        (ROOT / "data/meta/ar_assembly_log.csv").open(encoding="utf-8")))
    feat = [r for r in csv.DictReader(
        (ROOT / "data/features/classic.csv").open(encoding="utf-8"))
        if r["stratum"] == "annual_report"]
    asm = list(csv.DictReader(
        (ROOT / "data/features/ar_fy_features.csv").open(encoding="utf-8")))
    assembled = set()
    for r in asm:
        assembled.update(x for x in r["doc_ids"].split(";") if x)
    return led, feat, assembled, {int(r["year"]) for r in asm}


def adjudicate(led) -> tuple[list, list]:
    """Split the excluded-as-duplicate set into真 duplicates and companions.

    A record is a true duplicate only if some KEPT record with the same key has
    the same title. Title identity is a weak test — two files could share a title
    and differ — but it is strictly stronger than the key alone, and it is the
    test the frozen rule should have applied.
    """
    kept = defaultdict(set)
    for r in led:
        if r["decision"] == "include":
            kept[(r["repnb"], r["volnb"])].add(" ".join(r["display_title"].split()))
    real, companion = [], []
    for r in led:
        if r["rule"] != "duplicate_repnb_volnb":
            continue
        t = " ".join(r["display_title"].split())
        (real if t in kept[(r["repnb"], r["volnb"])] else companion).append(r)
    return real, companion


def era(feat, ids, years):
    per = defaultdict(lambda: [0.0, 0.0])
    for r in feat:
        if r["id"] not in ids:
            continue
        tok = float(r["tokens"] or 0)
        if tok <= 0:
            continue
        per[int(r["year"])][0] += float(r[FEATURE] or 0) * tok
        per[int(r["year"])][1] += tok
    rates = {y: a[0] / a[1] for y, a in per.items() if a[1] > 0}

    def m(lo, hi):
        v = [rates[y] for y in rates if lo <= y <= hi and y in years]
        return sum(v) / len(v) if v else float("nan")
    a, b = m(*EARLY), m(*LATE)
    return a, b, 100 * (b / a - 1)


def main() -> int:
    led, feat, assembled, years = load()
    real, companion = adjudicate(led)
    ids = {r["id"] for r in companion}

    print(f"excluded as duplicate_repnb_volnb: {len(real) + len(companion)}")
    print(f"  same title as a kept record — a real duplicate : {len(real)}")
    print(f"  different title — a COMPANION, wrongly excluded: {len(companion)}\n")
    for r in companion:
        print(f"   {r['year']}  {r['id']:>9}  {r['display_title'][:66]}")

    a0, b0, p0 = era(feat, assembled, years)
    a1, b1, p1 = era(feat, assembled | ids, years)
    print(f"\n{'series':44s} {'1946-65':>8s} {'2020-24':>8s} {'change':>9s}")
    print(f"{'as assembled (frozen)':44s} {a0:8.2f} {b0:8.2f} {p0:+8.1f}%")
    print(f"{'companions restored':44s} {a1:8.2f} {b1:8.2f} {p1:+8.1f}%")

    per_year = {}
    for y in sorted({int(r["year"]) for r in companion}):
        row = {}
        for lab, s in (("frozen", assembled), ("restored", assembled | ids)):
            num = den = 0.0
            for r in feat:
                if r["id"] in s and int(r["year"]) == y and float(r["tokens"] or 0) > 0:
                    num += float(r[FEATURE]) * float(r["tokens"])
                    den += float(r["tokens"])
            row[lab] = {"rate": num / den, "tokens": int(den)}
        per_year[y] = row
        print(f"  FY{y}  frozen {row['frozen']['rate']:6.2f} "
              f"({row['frozen']['tokens']:>7,} tok)   restored "
              f"{row['restored']['rate']:6.2f} ({row['restored']['tokens']:>7,} tok)")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"n_real_duplicates": len(real), "n_companions": len(companion),
         "companion_ids": sorted(ids),
         "frozen": {"early": a0, "late": b0, "pct": p0},
         "restored": {"early": a1, "late": b1, "pct": p1},
         "per_year": per_year}, indent=1), encoding="utf-8")
    print(f"\n[companions] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
