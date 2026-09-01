#!/usr/bin/env python3
"""Refuse if a count stated in prose disagrees with the filesystem.

An external review found four: the reference-audit footer said 25 entries and 22
DOI resolutions when the audit object held 31 and 28; the kit manifest described
three figures when four exist and an eight-section supplement when it runs to
S10. Each was true when written and none was regenerated afterwards.

Every count checked here is derived, never typed. A prose number that cannot be
derived is one that will be wrong eventually.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
SUPP = ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md"
AUDIT = ROOT / "data" / "analysis" / "citation_audit.json"
KIT = ROOT / "third_eye_kit"


def main() -> int:
    paper = PAPER.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8")
    bad = []

    n_fig = len(re.findall(r"\*\*Figure \d+\*\* —", paper))
    n_sup = len(re.findall(r"^## S\d+\.", supp, re.M))

    if AUDIT.exists():
        a = json.loads(AUDIT.read_text(encoding="utf-8"))
        n_entries = a["n_entries"]
        n_doi = sum(1 for e in a["entries"] if e.get("doi"))
        m = re.search(r"all (\d+) entries parsed,\s*\n?(\d+) resolved", paper)
        if not m:
            bad.append("the reference-audit footer is missing or reworded; "
                       "its counts can no longer be checked")
        else:
            if int(m.group(1)) != n_entries:
                bad.append(f"footer says {m.group(1)} entries, the audit has {n_entries}")
            if int(m.group(2)) != n_doi:
                bad.append(f"footer says {m.group(2)} resolved, {n_doi} entries carry a DOI")
        print(f"  citation entries   stated {m.group(1) if m else '?'}   actual {n_entries}")
        print(f"  DOI-bearing        stated {m.group(2) if m else '?'}   actual {n_doi}")

    for label, n, pat in (("figures", n_fig, r"the (\w+) figures, generated"),
                          ("supplement sections", n_sup, r"(\w+)-section supplement")):
        WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                 "seven": 7, "eight": 8, "nine": 9, "ten": 10}
        for src in (paper, supp, (KIT / "MANIFEST.md").read_text(encoding="utf-8")
                    if (KIT / "MANIFEST.md").exists() else ""):
            for mm in re.finditer(pat, src):
                said = WORDS.get(mm.group(1).lower())
                if said is not None and said != n:
                    bad.append(f"{label}: prose says {mm.group(1)} ({said}), "
                               f"there are {n}")
        print(f"  {label:18s} actual {n}")

    if bad:
        print("\n[counts] REFUSING: stated counts disagree with the filesystem")
        for b in sorted(set(bad)):
            print("   ", b)
        return 1
    print("\n[counts] every stated count matches what is on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
