#!/usr/bin/env python3
"""Split the excluded Annual-Report files by WHY they were excluded, and by trend.

§6.1 says the factor of three is document selection, and points at "the 195
excluded files" as one thing. They are not one thing. An external review made the
distinction that matters: removing a duplicate record is data cleaning, while
excluding IFC, MIGA and ICSID volumes is a substantive decision about what counts
as a World Bank Annual Report. A claim resting on a mixed category has not been
demonstrated until the mix is shown.

The classification is not invented here. `src/s10_assemble_ar.py` recorded a rule
per document at assembly time and `data/meta/ar_assembly_log.csv` holds it; this
reads that ledger and reports each class's own trajectory over the assembled
series' own fiscal years.

One reconciliation, because the two files disagree by one document.
`classic.csv` has 329 Annual-Report-facet rows; the assembly ledger has 328 with
text. The difference is 33464456, "IFC Annual Report 2021", which OCR'd to zero
characters — it carries a feature row and no text, so it is in the pool and in no
rate. 329 = 134 assembled + 195 excluded stands.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "analysis" / "ar_exclusion_classes.json"
FEATURE = "temporal_per1k"
EARLY, LATE = (1946, 1965), (2020, 2024)

SIBLING = {"IFC", "MIGA", "ICSID", "ICSID_nonlatin"}
DUPLICATE = {"duplicate_repnb_volnb"}


def klass(rule: str) -> str:
    if rule in SIBLING:
        return "sibling organisation (IFC/MIGA/ICSID)"
    if rule in DUPLICATE:
        return "duplicate volume record"
    return "other logged ruling"


def year_rates(docs) -> dict[int, float]:
    per = defaultdict(lambda: [0.0, 0.0])
    for r in docs:
        tok = float(r["tokens"] or 0)
        if tok <= 0:
            continue
        per[int(r["year"])][0] += float(r[FEATURE] or 0) * tok
        per[int(r["year"])][1] += tok
    return {y: a[0] / a[1] for y, a in per.items() if a[1] > 0}


def era(rates: dict[int, float], allowed: set[int]):
    def m(lo, hi):
        v = [rates[y] for y in rates if lo <= y <= hi and y in allowed]
        return sum(v) / len(v) if v else float("nan")
    a, b = m(*EARLY), m(*LATE)
    return a, b


def main() -> int:
    led = {r["id"]: r for r in csv.DictReader(
        (ROOT / "data/meta/ar_assembly_log.csv").open(encoding="utf-8"))}
    docs = [r for r in csv.DictReader(
        (ROOT / "data/features/classic.csv").open(encoding="utf-8"))
        if r["stratum"] == "annual_report"]
    asm = list(csv.DictReader(
        (ROOT / "data/features/ar_fy_features.csv").open(encoding="utf-8")))
    assembled = set()
    for r in asm:
        assembled.update(x for x in r["doc_ids"].split(";") if x)
    years = {int(r["year"]) for r in asm}

    groups: dict[str, list] = defaultdict(list)
    unledgered = []
    for r in docs:
        if r["id"] in assembled:
            groups["assembled (the Bank's own volumes)"].append(r)
            continue
        e = led.get(r["id"])
        if e is None:
            unledgered.append(r["id"])
            groups["other logged ruling"].append(r)
        else:
            groups[klass(e["rule"])].append(r)

    ASSEMBLED = "assembled (the Bank's own volumes)"
    n_excluded = sum(len(v) for k, v in groups.items() if k != ASSEMBLED)
    print(f"Annual-Report facet: {len(docs)} files, "
          f"{len(groups[ASSEMBLED])} assembled, {n_excluded} excluded\n")
    print(f"{'class':44s} {'files':>6s} {'1946-65':>9s} {'2020-24':>9s} {'change':>9s}")
    out = {"feature": FEATURE, "early": EARLY, "late": LATE, "classes": {}}
    for name in [ASSEMBLED,
                 "sibling organisation (IFC/MIGA/ICSID)",
                 "duplicate volume record", "other logged ruling"]:
        rows = groups.get(name, [])
        if not rows:
            continue
        a, b = era(year_rates(rows), years)
        pct = (100 * (b / a - 1)) if a == a and b == b and a else float("nan")
        show = lambda x: f"{x:9.2f}" if x == x else f"{'—':>9s}"
        print(f"{name:44s} {len(rows):6d} {show(a)} {show(b)} "
              + (f"{pct:+8.1f}%" if pct == pct else f"{'—':>9s}"))
        out["classes"][name] = {"n_files": len(rows), "early": a, "late": b,
                                "pct_change": pct}
    if unledgered:
        print(f"\n  NOTE: {len(unledgered)} file(s) in the feature table with no "
              f"assembly-ledger row: {unledgered}")
        out["unledgered"] = unledgered

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n[classes] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
