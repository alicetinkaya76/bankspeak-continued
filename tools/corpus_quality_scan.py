#!/usr/bin/env python3
"""Corpus quality scan: find extracted documents that are not usable English prose.

## Why this exists

`s10_assemble_ar` has a prose-likeness gate, but it applies only to the assembled
Annual Report units. For `icr` and `pad` — the P1 and P2 confirmatory panels —
the only eligibility rule is PREREG §7's "tokens >= 1". A document can therefore
carry 70,000 tokens of unusable text and enter the confirmatory analysis intact.

Scanning the extracted WB corpus on 2026-08-20 found exactly that. Of 3,125
documents with >= 200 tokens (median English stopword share 0.259), five sit
below 0.05, and they fail for **four different reasons**:

  pad/2018/29809040   5,951 tok   mojibake — "ŽĐƵŵĞŶƚŽĨ dŚĞtŽƌůĚĂŶŬ" is
                                  "Document of The World Bank" through a broken
                                  ToUnicode CMap
  annual_report/2007  44,516 tok  mojibake, a different substitution — "GHS8" is
                                  "NOTE", "4RTFF4QX" is "A SUMMARY"
  pad/2005/6336275    29,070 tok  FRENCH — "Traduction non officielle du texte
                                  en anglais", against D11's English-only rule
  icr/2004/5527314    70,526 tok  English cover sheet, French body
  annual_report/2008     429 tok  a genuine lending-data table dump

Three of the five are in the confirmatory strata. Two are language violations
that the API's own `lang_exact: English` filter should have prevented, so the
defect is inherited from WB metadata rather than introduced here.

## What it does NOT do

It does not exclude anything. Every finding is written with its class and its
evidence for a human to rule on, per the project's standing rule that borderline
cases are flagged rather than auto-resolved. Excluding documents after seeing the
corpus is a researcher degree of freedom and belongs in the SAP, not in a tool.

## How the classes are told apart

English and French function-word shares are computed side by side. Real English
prose sits near 0.26; French prose shows a high French share and a low English
one; mojibake matches neither, because its characters are not words in any
language; a table dump matches neither either, but is distinguished by its digit
density and short lines.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "data" / "text"
OUT = ROOT / "data" / "meta" / "corpus_quality_flags.csv"

MIN_TOKENS = 200
EN_LOW = 0.15          # s10's own gate value
SUSPECT = 0.05         # below this, something is definitely wrong
# Calibrated on the three real cases found 2026-08-20, in the manner s10
# calibrated its own gate: the two mojibake documents carry digit fractions
# 0.0024 and 0.0321, the table dump 0.1499. Mean line length does NOT separate
# them (43.1 / 53.1 against 54.7), so the digit fraction is the discriminator
# and 0.10 sits in the observed gap. The classes can still be confused in
# principle -- a broken CMap that maps letters onto digits (2007 renders "A" as
# "4" and "E" as "8") pushes mojibake toward the table signature -- which is
# why both verdicts say "suspected" and go to a human.
TABLE_DIGIT_FRAC = 0.10

EN = frozenset("the of and to in a for on with is by as that at from".split())
FR = frozenset("de la le les des du et en un une pour dans sur par au aux "
               "que qui est ce cette".split())

FIELDS = ["path", "stratum", "year", "id", "tokens", "en_share", "fr_share",
          "digit_frac", "mean_line_len", "verdict", "evidence"]


def classify(text: str) -> dict:
    toks = re.findall(r"[A-Za-z'À-ſ]+", text.lower())
    n = len(toks)
    if n < MIN_TOKENS:
        return {"tokens": n, "verdict": "too_short_to_judge"}
    en = sum(1 for t in toks if t in EN) / n
    fr = sum(1 for t in toks if t in FR) / n
    digits = sum(c.isdigit() for c in text) / max(1, len(text))
    lines = [l for l in text.splitlines() if l.strip()]
    mll = sum(len(l) for l in lines) / max(1, len(lines))

    if en >= EN_LOW:
        verdict, ev = "ok", ""
    elif fr > en and fr >= 0.05:
        verdict = "non_english_suspected"
        ev = f"French function-word share {fr:.3f} exceeds English {en:.3f} (D11)"
    elif en < SUSPECT and digits >= TABLE_DIGIT_FRAC:
        verdict = "table_dump_suspected"
        ev = f"digit fraction {digits:.3f}, mean line {mll:.0f} chars"
    elif en < SUSPECT:
        verdict = "mojibake_suspected"
        ev = (f"matches neither English ({en:.3f}) nor French ({fr:.3f}) "
              "function words — likely a broken ToUnicode CMap")
    else:
        verdict = "low_prose_borderline"
        ev = f"English share {en:.3f} below the {EN_LOW} prose gate"
    return {"tokens": n, "en_share": round(en, 4), "fr_share": round(fr, 4),
            "digit_frac": round(digits, 4), "mean_line_len": round(mll, 1),
            "verdict": verdict, "evidence": ev}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--text-root", default=str(TEXT))
    a = ap.parse_args(argv)
    root = Path(a.text_root)

    rows, counts = [], {}
    for p in sorted(root.rglob("*.txt")):
        rel = p.relative_to(root)
        r = classify(p.read_text(encoding="utf-8", errors="replace"))
        parts = rel.parts
        row = {"path": rel.as_posix(), "stratum": parts[0],
               "year": parts[1] if len(parts) > 2 else "", "id": p.stem,
               **{k: r.get(k, "") for k in FIELDS if k in r}}
        rows.append(row)
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in FIELDS})

    print(f"[quality] {len(rows)} extracted document(s)")
    for v in sorted(counts, key=lambda k: -counts[k]):
        print(f"  {v:24s} {counts[v]:5d}")
    flagged = [r for r in rows
               if r["verdict"] not in ("ok", "too_short_to_judge")]
    if flagged:
        print("\n[quality] flagged for human ruling — nothing excluded:")
        for r in sorted(flagged, key=lambda r: r.get("en_share", 1)):
            print(f"  {r['verdict']:22s} {r['stratum']:14s} {r['path']}")
            print(f"      {r['evidence']}")
    print(f"\n[quality] wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
