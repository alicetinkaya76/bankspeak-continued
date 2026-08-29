#!/usr/bin/env python3
"""List every unfilled field in the submission package, and refuse if one is in
the manuscript.

An external review found a literal bracket — "**[deposited at DOI … / to be
deposited before publication]**" — in a file whose own second line called itself
"Submission-ready. Paste into the journal's Data Availability field." PLOS ONE
screens data availability BEFORE peer review, so that bracket is an editorial
return, and nothing in the repository was watching for it.

Two severities, because they are genuinely different:

  MANUSCRIPT  — a placeholder in the paper itself is a defect now. The paper is
                supposed to be finished prose; there is no later moment when
                someone fills a bracket in §6. Exit non-zero.
  FORM FIELD  — the cover letter's name and ORCID and the deposit DOI are
                legitimately unfilled until the author submits and the deposit
                is minted. Listing them is the point; failing on them would train
                whoever runs this to ignore it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = [ROOT / "docs" / "PAPER_DRAFT_v2.md",
              ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md"]
FORMS = [ROOT / "docs" / "SUBMISSION_COVER_LETTER.md",
         ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md",
         ROOT / "docs" / "SUBMISSION_DAS_AUTHOR_NOTE.md"]

# A bracket holding an instruction, not a citation or an interval. Numbers,
# maths and reference-style brackets are excluded deliberately: the manuscript is
# full of "[−0.732, 0.239]" and none of those is a placeholder.
#
# NOT line-scoped. The two placeholders that mattered most were wrapped across a
# line break — "[deposited at DOI … / to be deposited\nbefore publication]" and
# "[Funding, competing interests, preprint and ethics statements as\napplicable.]"
# — and the first version of this pattern forbade a newline inside the brackets,
# so it found neither. That is the same defect the citation audit shipped and had
# to be repaired for ("De\nFrancesco" read as an uncited entry): a hand-wrapped
# Markdown file has no obligation to keep a construct on one line, and a scanner
# that assumes it will is looking at a different document than the reader is.
PAT = re.compile(r"\[[^\]]{0,200}?(?:TBD|TO BE|to be |DOI …|DOI \.\.\.|XXX|"
                 r"AFFILIATION|ORCID|Name,|Funding|insert|INSERT|"
                 r"to be completed|to be inserted)[^\]]{0,200}?\]", re.S)


def scan(paths: list[Path]) -> list[tuple[str, int, str]]:
    out = []
    for p in paths:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        for m in PAT.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            flat = " ".join(m.group(0).split())
            try:
                name = p.relative_to(ROOT).as_posix()
            except ValueError:          # a file outside the repo, e.g. a test fixture
                name = str(p)
            out.append((name, line, flat))
    return out


def main() -> int:
    in_paper = scan(MANUSCRIPT)
    in_forms = scan(FORMS)

    if in_forms:
        print("FORM FIELDS still to fill before submitting "
              "(expected; fill, do not ignore):")
        for f, i, t in in_forms:
            print(f"   {f}:{i}  {t}")
    else:
        print("FORM FIELDS: none outstanding")

    print()
    if in_paper:
        print("MANUSCRIPT placeholders — these must not ship:")
        for f, i, t in in_paper:
            print(f"   {f}:{i}  {t}")
        return 1
    print("MANUSCRIPT: no placeholders")
    return 0


if __name__ == "__main__":
    sys.exit(main())
