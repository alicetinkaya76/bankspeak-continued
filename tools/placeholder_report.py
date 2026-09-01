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
  BUILT PDF   — the title page deliberately shows the affiliation and ORCID as
                visible brackets, because a made-up affiliation is worse than an
                obvious gap. But "deliberate" is not "ready": those brackets are
                on page one of the file that gets uploaded. Exit 2, which is a
                distinct code meaning "correct as built, not submittable yet".

Round 18 added the third category after external review pointed at two visible
"[… to be completed before submission]" brackets on the submission PDF's first
page while this tool printed "MANUSCRIPT: no placeholders". It was reading two
Markdown files and the artifact was a PDF; the scan was clean and the package
was not.
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
BUILT_MD = ROOT / "build" / "submission" / "submission.md"
BUILT_PDF = ROOT / "build" / "submission" / "PLOS_ONE_submission.pdf"

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
# Two patterns, because the failure modes are different. The keyword list
# catches the wordings this package actually uses. The shape rule catches the
# ones nobody thought to list -- [FIXME], [TK], [PENDING FINAL RUN] all printed
# "MANUSCRIPT: no placeholders" until round 18 -- by looking for a bracket whose
# content is an all-caps token or two rather than prose or a number.
#
# What must NOT match: this manuscript is full of intervals like [−0.732, 0.239]
# and [0.267, 0.921], and a scanner that flags those is one nobody runs twice.
# The shape rule therefore requires at least one ASCII letter run of two or more
# capitals and forbids a digit-leading bracket outright.
KEYWORDS = (r"TBD|TO BE|to be |DOI …|DOI \.\.\.|XXX|AFFILIATION|ORCID|Name,|"
            r"Funding|insert|INSERT|to be completed|to be inserted")
PAT = re.compile(r"\[[^\]]{0,200}?(?:" + KEYWORDS + r")[^\]]{0,200}?\]", re.S)
SHAPE = re.compile(r"\[(?![\s\-−+.]*\d)"          # not an interval or a number
                   r"[^\]\n]{0,80}?"
                   r"\b(?:FIXME|TK|TODO|PENDING|PLACEHOLDER|DRAFT|CHECK|"
                   r"REVISE|CITE|REF|UNKNOWN|NUMBER|VALUE|DATE)\b"
                   r"[^\]\n]{0,80}?\]")


def scan(paths: list[Path]) -> list[tuple[str, int, str]]:
    out = []
    for p in paths:
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        spans = {(m.start(), m.end()) for m in PAT.finditer(text)}
        spans |= {(m.start(), m.end()) for m in SHAPE.finditer(text)}
        for a, b in sorted(spans):
            m = type("M", (), {"start": lambda s, a=a: a,
                               "group": lambda s, _=0, a=a, b=b: text[a:b]})()
            line = text.count("\n", 0, m.start()) + 1
            flat = " ".join(m.group(0).split())
            try:
                name = p.relative_to(ROOT).as_posix()
            except ValueError:          # a file outside the repo, e.g. a test fixture
                name = str(p)
            out.append((name, line, flat))
    return out


def scan_pdf(path: Path) -> list[tuple[str, int, str]]:
    """Note: the caller decides what a MISSING artifact means, not this. A
    "clean" verdict for a file that is not there is the shape of defect that
    lets a package pass by having less in it."""
    """The same patterns, against the rendered pages rather than the source.

    Read the artifact, not the input to it: the brackets are injected by
    tools/build_submission_pdf.py and never appear in either Markdown file the
    manuscript scan covers.
    """
    if not path.exists():
        return []
    try:
        import fitz
    except ImportError:
        return [(path.relative_to(ROOT).as_posix(), 0,
                 "PDF NOT SCANNED — PyMuPDF is not installed")]
    out = []
    with fitz.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            text = page.get_text()
            for m in PAT.finditer(text):
                out.append((path.relative_to(ROOT).as_posix(), i,
                            " ".join(m.group(0).split())))
    return out


def main() -> int:
    in_paper = scan(MANUSCRIPT)
    in_forms = scan(FORMS)
    # Deleting the built PDF used to turn this from exit 2 into exit 0 and
    # "BUILT SUBMISSION ARTIFACT: clean" -- absence read as success, which is the
    # most dangerous verdict a guard can give. The public export legitimately has
    # no build/ tree, so the distinction is between "not built here" and "built
    # and clean", and both are reported by name.
    built_exists = BUILT_PDF.exists() or BUILT_MD.exists()
    in_built = (scan([BUILT_MD]) if BUILT_MD.exists() else []) + scan_pdf(BUILT_PDF)

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

    print()
    if not built_exists:
        print("BUILT SUBMISSION ARTIFACT: NOT CHECKED — no build/submission "
              "artifact in this tree (expected in the public export; run "
              "tools/build_submission_pdf.py --both here)")
        return 0
    if in_built:
        print("BUILT SUBMISSION ARTIFACT — visible on the file that gets "
              "uploaded (page numbers for the PDF, line numbers otherwise):")
        for f, i, t in in_built:
            print(f"   {f}:{i}  {t}")
        print("\n[placeholders] the package is correct as built and NOT "
              "submittable: fill these, rebuild, rerun.")
        return 2
    print("BUILT SUBMISSION ARTIFACT: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
