#!/usr/bin/env python3
"""Inventory the Annual-Report family by component, and run the two corpora
a reviewer asked for: main narrative volume only, and the full report family.

The objection this answers: the assembled fiscal-year unit is not the same
publication across the span. Fiscal 2020 and 2021 are three-document units of
217,404 and 184,775 tokens; 2022, 2023 and 2024 are single documents of 44,574,
43,795 and 29,028. If financial statements and lending appendixes left the bound
volume after 2021, the endpoint decline could be a packaging regime change rather
than a change in the Bank's prose — and the manuscript printed no per-year
document or token count anywhere for a reader to notice.

Component type is read from the title, which is what the World Bank's own
catalogue exposes. Two prespecified corpora follow:

  MAIN     the narrative volume only, every year — the like-for-like series
  FAMILY   every component the facet returned, every year — the widest reading

Neither is "correct". The point is that a result which survives both is a result
about the Bank's language, and one that does not is a result about packaging.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FEATURE = "temporal_per1k"
EARLY, LATE = (1946, 1965), (2020, 2024)
OUT = ROOT / "data" / "analysis" / "ar_component_inventory.json"

# Ordered: the first pattern that matches wins. Anything unmatched is narrative,
# because the main volume is the one whose title carries no component suffix.
COMPONENTS = [
    ("financial statements", re.compile(
        r"financial statement|management'?s? discussion", re.I)),
    ("appendixes / organizational info", re.compile(
        r"organizational information|lending data appendix|appendixes", re.I)),
    ("executive summary", re.compile(r"executive summary", re.I)),
    ("lending tables", re.compile(
        r"commitments, disbursements|lending to borrowers|by theme and sector", re.I)),
]


def component(title: str) -> str:
    t = " ".join(title.split())
    for name, rx in COMPONENTS:
        if rx.search(t):
            return name
    return "narrative volume"


def era(feat, ids, years):
    """feat is id -> row, so iterate the rows. Passing the dict to a loop that
    expected a list gave 'string indices must be integers'."""
    per = defaultdict(lambda: [0.0, 0.0])
    for r in feat.values():
        if r["id"] not in ids:
            continue
        tok = float(r["tokens"] or 0)
        if tok <= 0:
            continue
        per[int(r["year"])][0] += float(r[FEATURE] or 0) * tok
        per[int(r["year"])][1] += tok
    rates = {y: a[0] / a[1] for y, a in per.items() if a[1] > 0}

    def m(lo, hi, weighted):
        """Equal-year mean, or a token-weighted one.

        The manuscript's -42.5% is the equal-year mean, and it never said so.
        Which weighting is used matters more here than anywhere else in the
        paper, because the late window is not a balanced set of years: fiscal
        2020 and 2021 carry three components and about 200,000 tokens each,
        2022-24 carry one and 29,000-45,000. Equal-year weighting gives the
        three thin single-volume years the same say as the two fat ones;
        token weighting gives them a seventh of it. A reviewer asked for both
        and both belong in print.
        """
        ys = [y for y in rates if lo <= y <= hi and y in years]
        if not ys:
            return float("nan")
        if not weighted:
            return sum(rates[y] for y in ys) / len(ys)
        num = sum(rates[y] * per[y][1] for y in ys)
        den = sum(per[y][1] for y in ys)
        return num / den if den else float("nan")

    out = {}
    for tag, w in (("equal_year", False), ("token_weighted", True)):
        a, b = m(*EARLY, w), m(*LATE, w)
        out[tag] = {"early": a, "late": b,
                    "pct": (100 * (b / a - 1) if a else float("nan"))}
    return out, rates


def main() -> int:
    led = list(csv.DictReader(
        (ROOT / "data/meta/ar_assembly_log.csv").open(encoding="utf-8")))
    feat = {r["id"]: r for r in csv.DictReader(
        (ROOT / "data/features/classic.csv").open(encoding="utf-8"))
        if r["stratum"] == "annual_report"}
    asm = list(csv.DictReader(
        (ROOT / "data/features/ar_fy_features.csv").open(encoding="utf-8")))
    years = {int(r["year"]) for r in asm}
    assembled = set()
    for r in asm:
        assembled.update(x for x in r["doc_ids"].split(";") if x)

    # The family is every World-Bank-own record the facet returned: what the
    # assembler kept, plus what it dropped only for a metadata-key collision.
    family = {r["id"] for r in led
              if (r["decision"] == "include" or r["rule"] == "duplicate_repnb_volnb")
              and r["id"] in feat}
    comp = {i: component(next(r for r in led if r["id"] == i)["display_title"])
            for i in family}
    main_only = {i for i in family if comp[i] == "narrative volume"}

    print(f"{'component':36s} {'files':>6s} {'tokens':>10s}")
    tot = defaultdict(lambda: [0, 0])
    for i in family:
        tot[comp[i]][0] += 1
        tot[comp[i]][1] += int(float(feat[i]["tokens"] or 0))
    for k, (n, t) in sorted(tot.items(), key=lambda kv: -kv[1][1]):
        print(f"  {k:34s} {n:6d} {t:10,d}")

    print(f"\n{'corpus':32s} {'weighting':>15s} {'1946-65':>8s} "
          f"{'2020-24':>8s} {'change':>9s}")
    res = {}
    for label, ids in (("as assembled (frozen)", assembled),
                       ("MAIN narrative volume only", main_only),
                       ("FAMILY, every component", family)):
        both, rates = era(feat, ids, years)
        res[label] = dict(both, n_files=len(ids),
                          # the frozen headline is the equal-year figure
                          early=both["equal_year"]["early"],
                          late=both["equal_year"]["late"],
                          pct=both["equal_year"]["pct"])
        for tag in ("equal_year", "token_weighted"):
            e = both[tag]
            print(f"  {label:30s} {tag:>15s} {e['early']:8.2f} "
                  f"{e['late']:8.2f} {e['pct']:+8.1f}%")

    print(f"\n{'fiscal year':>12s}  {'components in the family':<44s} {'tokens':>9s}")
    per_year = {}
    for y in sorted({int(feat[i]["year"]) for i in family}):
        if y < 2015:
            continue
        here = [i for i in family if int(feat[i]["year"]) == y]
        names = sorted({comp[i] for i in here})
        tk = sum(int(float(feat[i]["tokens"] or 0)) for i in here)
        per_year[y] = {"n": len(here), "components": names, "tokens": tk}
        print(f"  FY{y:>8}  {', '.join(n[:18] for n in names):<44s} {tk:9,d}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"by_component": {k: {"files": v[0], "tokens": v[1]}
                                                for k, v in tot.items()},
                               "corpora": res, "per_year_from_2015": per_year},
                              indent=1), encoding="utf-8")
    print(f"\n[inventory] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
