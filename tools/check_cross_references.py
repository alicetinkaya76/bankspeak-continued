#!/usr/bin/env python3
"""Refuse if the manuscript points at a section, table, figure or supplement
that does not exist.

Sixteen rounds have moved, split, renumbered and deleted material. A cross
reference that survived a renumbering is invisible to every other check in this
repository and to any reader who does not follow it.

One subtlety, and it is the whole reason this is a tool rather than a grep:
`§11.5` in this manuscript means the PREREGISTRATION's §11.5, not the paper's.
A naive pattern reports three false dangling references on that alone, and a
checker whose output is mostly false positives is one nobody runs twice.
Qualified references — anything preceded by PREREG, SAP or a supplement marker —
are counted as external and left alone.
"""
from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
SUPP = ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md"

# A section reference belongs to another document when one of these precedes it.
EXTERNAL = r"(?<!PREREG )(?<!SAP )(?<!PREREG§)(?<!plan )"


def main() -> int:
    paper = PAPER.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8") if SUPP.exists() else ""

    have = {
        "section": ({m.group(1) for m in re.finditer(r"^## (\d+)\.", paper, re.M)}
                    | {m.group(1) for m in re.finditer(r"^### (\d+\.\d+)", paper, re.M)}),
        "table": {m.group(1) for m in re.finditer(r"\*\*Table (\d+[a-z]?) —", paper)},
        "figure": {m.group(1) for m in re.finditer(r"\*\*Figure (\d+)\*\* —", paper)},
        "supplement": ({m.group(1) for m in re.finditer(r"^## S(\d+)\.", supp, re.M)}
                       | {m.group(1) for m in re.finditer(r"^### S(\d+\.\d+)", supp, re.M)}),
    }
    want = {
        "section": collections.Counter(
            m.group(1) for m in re.finditer(EXTERNAL + r"§(\d+(?:\.\d+)?)", paper)),
        "table": collections.Counter(
            m.group(1) for m in re.finditer(r"\bTable (\d+[a-z]?)\b", paper)),
        "figure": collections.Counter(
            m.group(1) for m in re.finditer(r"\bFigure (\d+)\b", paper)),
        # The supplement's own cross references were invisible until round 18:
        # this counter read `paper` only, so a dangling "S6.3" INSIDE the
        # supplement passed every check while the reader following it found
        # nothing. Both documents point into the supplement's numbering, so
        # both have to be scanned.
        "supplement": collections.Counter(
            m.group(1) for m in re.finditer(r"\bS(\d+(?:\.\d+)?)\b",
                                           paper + "\n" + supp)),
    }

    bad = []
    for kind, counts in want.items():
        for n, c in sorted(counts.items()):
            if n not in have[kind]:
                bad.append(f"{kind} {n}: referenced {c}x, never defined")
        print(f"  {kind:11s} defined {len(have[kind]):2d}, referenced {len(counts):2d}")
    if bad:
        print("\n[xref] REFUSING: dangling references")
        for b in bad:
            print("   ", b)
        return 1
    print("\n[xref] every internal reference resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
