#!/usr/bin/env python3
"""What actually produces the 43%-versus-14% contrast, step by step.

The manuscript says the same archive gives a 43% or a 14% decline in temporal
anchoring "depending only on whether Annual Report volumes are assembled into
fiscal-year units". The third-eye review of 2026-08-29 objected that the two
series differ in more than one operation, so a one-factor label is not supported.
That objection is correct, and this module settles it by measuring each factor
instead of arguing about it.

## The three operations that differ

1. **File inclusion.** The document-level pool holds 329 Annual-Report-facet
   files. Only 134 of them enter the assembled series: sibling-organisation
   volumes (IFC, MIGA, ICSID) and duplicate volumes are excluded by logged
   ruling. Those excluded files are dense in dates.
2. **Unit definition.** The 134 surviving files are concatenated into 76
   fiscal-year units. This is the operation the manuscript names.
3. **Weighting.** A mean over fiscal-year rates weights each year equally; a
   token-weighted mean weights each year by its size, and recent volumes are far
   larger.

## How the decomposition works

Each step is applied to the *previous* step's output, so the contribution of a
step is the change it alone produces. Every stage is measured over the SAME
fiscal-year windows, because comparing each series over its own available years
is what manufactured an apparent sign reversal in an earlier draft.

The honest headline this produces is "corpus-construction and aggregation choices
jointly change the estimated decline by roughly a factor of three", with the
per-step shares stated. Not "unit definition alone".
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "analysis" / "rq1_decomposition.json"
FEATURE = "temporal_per1k"
EARLY, LATE = (1946, 1965), (2020, 2026)


def load():
    with (ROOT / "data/features/ar_fy_features.csv").open(encoding="utf-8") as fh:
        asm = list(csv.DictReader(fh))
    with (ROOT / "data/features/classic.csv").open(encoding="utf-8") as fh:
        docs = [r for r in csv.DictReader(fh) if r["stratum"] == "annual_report"]
    assembled_ids = set()
    for r in asm:
        assembled_ids.update(x for x in r["doc_ids"].split(";") if x)
    return asm, docs, assembled_ids


def year_rates(docs, weighted: bool):
    """Collapse documents to one rate per year."""
    per = defaultdict(lambda: [0.0, 0.0, 0])
    for r in docs:
        y = int(r["year"])
        tok = float(r["tokens"] or 0)
        if tok <= 0:
            continue
        v = float(r[FEATURE] or 0)
        a = per[y]
        a[0] += v * tok if weighted else v
        a[1] += tok
        a[2] += 1
    return {y: (a[0] / a[1] if weighted else a[0] / a[2]) for y, a in per.items()}


def era_change(rates, years_allowed):
    """Unweighted mean of per-year rates in each era, restricted to given years."""
    def m(lo, hi):
        v = [rates[y] for y in rates if lo <= y <= hi and y in years_allowed]
        return sum(v) / len(v) if v else float("nan")
    a, b = m(*EARLY), m(*LATE)
    return a, b, 100 * (b / a - 1)


def main() -> int:
    asm, docs, assembled_ids = load()
    asm_years = {int(r["year"]) for r in asm}
    asm_rates = {int(r["year"]): float(r[FEATURE]) for r in asm}

    kept = [r for r in docs if r["id"] in assembled_ids]
    steps = []

    def add(label, rates, note):
        a, b, pct = era_change(rates, asm_years)
        steps.append({"step": label, "early_mean": a, "late_mean": b,
                      "pct_change": pct, "note": note})
        print(f"  {label:52s} {a:6.2f} -> {b:6.2f}   {pct:+6.1f}%")

    print(f"RQ1 decomposition — {FEATURE}, era means over the assembled series' "
          f"own fiscal years\n")
    print(f"  document pool {len(docs)}, of which {len(kept)} enter the "
          f"assembled series ({len(asm)} fiscal-year units)\n")

    add("1. all pool documents, token-weighted", year_rates(docs, True),
        "the document-level figure the manuscript quotes")
    add("2. + restrict to files that enter assembly", year_rates(kept, True),
        "isolates FILE INCLUSION (siblings, duplicates, exclusions)")
    add("3. + concatenate into fiscal-year units", asm_rates,
        "isolates UNIT DEFINITION — the step the manuscript names")
    # step 3 output is already one value per year; weighting differs only in how
    # eras are averaged, which era_change already does unweighted. Show the
    # token-weighted era average of the SAME assembled units for step 4.
    tok = {int(r["year"]): float(r["tokens"]) for r in asm}

    def wmean(lo, hi):
        ys = [y for y in asm_rates if lo <= y <= hi]
        t = sum(tok[y] for y in ys)
        return sum(asm_rates[y] * tok[y] for y in ys) / t if t else float("nan")
    a, b = wmean(*EARLY), wmean(*LATE)
    pct = 100 * (b / a - 1)
    steps.append({"step": "4. + weight eras by tokens instead of by year",
                  "early_mean": a, "late_mean": b, "pct_change": pct,
                  "note": "isolates WEIGHTING across eras"})
    print(f"  {'4. + weight eras by tokens instead of by year':52s} "
          f"{a:6.2f} -> {b:6.2f}   {pct:+6.1f}%")

    print("\n  contribution of each step, in percentage points of the change:")
    for i in range(1, len(steps)):
        d = steps[i]["pct_change"] - steps[i - 1]["pct_change"]
        print(f"    {steps[i]['step'][:48]:50s} {d:+6.1f} pp")

    span = steps[0]["pct_change"], steps[2]["pct_change"]
    print(f"\n  document-level {span[0]:+.1f}% vs assembled {span[1]:+.1f}% "
          f"— a factor of {abs(span[1]/span[0]):.2f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"feature": FEATURE, "eras": [EARLY, LATE],
                               "n_pool": len(docs), "n_assembled_files": len(kept),
                               "n_units": len(asm), "steps": steps},
                              indent=1), encoding="utf-8")
    print(f"\n[rq1] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
