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
    # Round 18 made the supplement counter read both documents and left the
    # other three reading `paper` only, so "See §17.3, Table 99 and Figure 9"
    # inserted into the supplement still passed clean. The supplement points into
    # the paper's numbering constantly and legitimately, which is exactly why it
    # has to be scanned: a reference there to a section that does not exist is a
    # dangling reference in the published package.
    both = paper + "\n" + supp
    want = {
        "section": collections.Counter(
            m.group(1) for m in re.finditer(EXTERNAL + r"§(\d+(?:\.\d+)?)", both)),
        "table": collections.Counter(
            m.group(1) for m in re.finditer(r"\bTable (\d+[a-z]?)\b", both)),
        "figure": collections.Counter(
            m.group(1) for m in re.finditer(r"\bFigure (\d+)\b", both)),
        # The supplement's own cross references were invisible until round 18:
        # this counter read `paper` only, so a dangling "S6.3" INSIDE the
        # supplement passed every check while the reader following it found
        # nothing. Both documents point into the supplement's numbering, so
        # both have to be scanned.
        "supplement": collections.Counter(
            m.group(1) for m in re.finditer(r"\bS(\d+(?:\.\d+)?)\b", both)),
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
