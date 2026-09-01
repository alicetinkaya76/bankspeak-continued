#!/usr/bin/env python3
"""Is the Tier-2 register measurable across eight decades, or only after 1965?

An external review objected that a fixed contemporary word list cannot be a
period-neutral instrument against a 1946-65 baseline: a word form existing early
does not mean its institutional sense or its opportunity for use did. The
objection is right in principle, and the review's examples were wrong in fact —
`alignment`, `augment`, `calibrate`, `chatbot`, `corpus`, `digital`,
`hallucination` and `scalable` were named, and only `scalable` is in the list.
So this measures the real thing.

The 35 Tier-2 terms are split by whether the sense the World Bank uses them in
was available in institutional prose before 1965. That is a judgement and it is
made explicitly here rather than left implicit:

  PERIOD-PLAUSIBLE   ordinary English whose institutional sense is stable:
                     accelerate, bold, crucial, foster, robust, strengthen, vital
  MODERN REGISTER    development-and-management vocabulary whose current sense
                     postdates the early window: stakeholder (management, 1980s),
                     sustainable (Brundtland, 1987), governance (the Bank's own
                     1989 usage), empower, leverage as a verb, holistic,
                     transformative, resilience as policy, scalable, unlock,
                     vibrant, landscape as metaphor, innovative, harness

Counts come from the assembled World Bank fiscal-year texts, which are public
disclosure under the Bank's Access to Information Policy. No IMF text is touched.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "data" / "text_assembled" / "annual_report"
OUT = ROOT / "data" / "analysis" / "tier2_period_fairness.json"
EARLY, LATE = (1946, 1965), (2020, 2024)

# Stems, not whole words: "leveraging" does NOT start with "leverage" -- the
# eighth character differs -- so the first version put leverage and leverages in
# the modern set and leveraging in the plausible one, which is incoherent.
MODERN_STEMS = {"stakeholder", "sustainable", "governance", "empower", "leverag",
                "holistic", "transformative", "resilien", "scalable", "unlock",
                "vibrant", "landscape", "innovat", "harness"}


def is_modern(term: str) -> bool:
    return any(term.startswith(s) for s in MODERN_STEMS)


def main() -> int:
    cfg = yaml.safe_load((ROOT / "config" / "config.yaml").read_text())
    tier2 = None
    for v in cfg.values():
        if isinstance(v, dict) and "tier2" in v:
            tier2 = sorted(v["tier2"])
            break
    if not tier2:
        raise SystemExit("[tier2] no tier2 list in config")
    modern = [t for t in tier2 if is_modern(t)]
    plausible = [t for t in tier2 if not is_modern(t)]
    print(f"{len(tier2)} terms: {len(plausible)} period-plausible, "
          f"{len(modern)} modern register\n")
    print(f"  plausible: {', '.join(plausible)}")
    print(f"  modern   : {', '.join(modern)}\n")

    pats = {t: re.compile(rf"\b{re.escape(t)}\b", re.I) for t in tier2}
    per_year = {}
    for f in sorted(TEXT.glob("*.txt")):
        year = int(f.stem)
        txt = f.read_text(encoding="utf-8", errors="replace")
        ntok = len(txt.split())
        if ntok == 0:
            continue
        counts = {t: len(pats[t].findall(txt)) for t in tier2}
        per_year[year] = {"tokens": ntok, "counts": counts}

    def rate(years_dict, terms, lo, hi):
        num = den = 0
        for y, d in years_dict.items():
            if lo <= y <= hi:
                num += sum(d["counts"][t] for t in terms)
                den += d["tokens"]
        return 1000 * num / den if den else float("nan")

    print(f"{'subset':26s} {'1946-65':>9s} {'2020-24':>9s} {'ratio':>8s}")
    res = {"n_terms": len(tier2), "plausible": plausible, "modern": modern,
           "subsets": {}}
    for label, terms in (("all 35 terms", tier2),
                         ("period-plausible only", plausible),
                         ("modern register only", modern)):
        a = rate(per_year, terms, *EARLY)
        b = rate(per_year, terms, *LATE)
        r = b / a if a else float("inf")
        res["subsets"][label] = {"early": a, "late": b, "ratio": r,
                                 "n_terms": len(terms)}
        print(f"  {label:24s} {a:9.3f} {b:9.3f} {r:8.1f}x")

    print("\nterms with ZERO occurrences in 1946-65 (unavailable, not merely rare):")
    never = [t for t in tier2
             if sum(d["counts"][t] for y, d in per_year.items()
                    if EARLY[0] <= y <= EARLY[1]) == 0]
    print("  " + (", ".join(never) if never else "none"))
    res["absent_in_early_window"] = never

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[tier2] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
