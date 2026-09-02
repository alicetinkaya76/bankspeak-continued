#!/usr/bin/env python3
"""Refuse if a count stated in prose disagrees with the filesystem.

An external review found four: the reference-audit footer said 25 entries and 22
DOI resolutions when the audit object held 31 and 28; the kit manifest described
three figures when four exist and an eight-section supplement when it runs to
S10. Each was true when written and none was regenerated afterwards.

Round 18 found three more, all of the same shape and none of them visible to
the first version of this file, whose inputs were fixed to the two manuscript
Markdown files: the submission checklist said 25 pages against a 30-page PDF and
"23 of 25 entries resolved" against 34 entries with 31 resolved, and the kit
manifest said 91 files against 92 in the bundle. So the checklist, the built PDF
and the manifest's own file count are now inputs too.

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
CHECKLIST = ROOT / "docs" / "PLOS_SUBMISSION_CHECKLIST.md"
PDF = ROOT / "build" / "submission" / "PLOS_ONE_submission.pdf"


def pdf_pages(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        import fitz
    except ImportError:
        return None
    with fitz.open(path) as d:
        return d.page_count


def main() -> int:
    paper = PAPER.read_text(encoding="utf-8")
    supp = SUPP.read_text(encoding="utf-8")
    bad = []

    n_fig = len(re.findall(r"\*\*Figure \d+\*\* —", paper))
    n_sup = len(re.findall(r"^## S\d+\.", supp, re.M))

    n_entries = n_doi = None
    if AUDIT.exists():
        a = json.loads(AUDIT.read_text(encoding="utf-8"))
        n_entries = a["n_entries"]
        # "Resolved from Crossref" is a claim about a lookup, and this counted
        # entries that merely carried a doi field -- a DOI that 404s counted as
        # resolved. The audit records a per-entry verdict; use it, and fall back
        # to the field only when no verdict was stored, so an older audit object
        # still checks rather than silently passing.
        def resolved(e):
            v = (e.get("check") or {}).get("verdict")
            if v is None:
                return bool(e.get("doi"))
            return bool(e.get("doi")) and "NOT" not in str(v).upper()
        n_doi = sum(1 for e in a["entries"] if resolved(e))
        # The footer moved out of the manuscript's bibliography and into the
        # submission checklist, because an external review pointed out that a QA
        # note is not a bibliographic entry and that Crossref resolution says
        # nothing about whether a source supports its proposition. The numbers
        # are still guarded; only where they live changed. Both files are read
        # so that the check survives whichever document carries the sentence.
        checklist = ROOT / "docs" / "PLOS_SUBMISSION_CHECKLIST.md"
        hay = paper + "\n" + (checklist.read_text(encoding="utf-8")
                              if checklist.exists() else "")
        m = re.search(r"all (\d+) entries parsed,\s*\n?(\d+) resolved", hay)
        if not m:
            bad.append("the reference-audit footer is missing or reworded in "
                       "both the manuscript and the checklist; its counts can "
                       "no longer be checked")
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

    # --- the checklist's own numbers, against the artifacts they describe ---
    if CHECKLIST.exists():
        cl = CHECKLIST.read_text(encoding="utf-8")
        pages = pdf_pages(PDF)
        if pages is None and PDF.exists():
            bad.append("the submission PDF exists but could not be opened; its "
                       "page count is unchecked")
        m = re.search(r"PLOS_ONE_submission\.pdf`?\s*(?:—|--)\s*(\d+) pages", cl)
        if m and pages is not None:
            if int(m.group(1)) != pages:
                bad.append(f"checklist says the PDF is {m.group(1)} pages; "
                           f"it is {pages}")
            print(f"  PDF pages          stated {m.group(1)}   actual {pages}")
        elif pages is None:
            print("  PDF pages          not checked (no PDF, or PyMuPDF absent)")
        else:
            bad.append("the checklist no longer states a page count in a form "
                       "this can read; it cannot be checked")

        m = re.search(r"\*\*(\d+) of (\d+) entries resolved from Crossref\*\*", cl)
        if m and AUDIT.exists():
            if int(m.group(2)) != n_entries or int(m.group(1)) != n_doi:
                bad.append(f"checklist says {m.group(1)} of {m.group(2)} "
                           f"references resolved; the audit has {n_doi} of "
                           f"{n_entries}")
            print(f"  checklist refs     stated {m.group(1)}/{m.group(2)}   "
                  f"actual {n_doi}/{n_entries}")
        elif AUDIT.exists():
            bad.append("the checklist no longer states a resolved-reference "
                       "count in a form this can read")

    # --- the kit manifest's own file count, against the bundle it describes ---
    # A missing manifest used to drop the check silently and still exit 0.
    # The public export has no kit, so absence is reported by name rather than
    # treated either as success or as failure.
    man = KIT / "MANIFEST.md"
    if not man.exists():
        print("  kit files          NOT CHECKED (no third_eye_kit/ in this tree)")
    if man.exists():
        txt = man.read_text(encoding="utf-8")
        actual = sum(1 for f in KIT.rglob("*") if f.is_file())
        m = re.search(r"^(\d+) files", txt, re.M)
        if m:
            if int(m.group(1)) != actual:
                bad.append(f"kit manifest says {m.group(1)} files; the bundle "
                           f"holds {actual}")
            print(f"  kit files          stated {m.group(1)}   actual {actual}")
        else:
            bad.append("the kit manifest no longer opens with a file count")

    if bad:
        print("\n[counts] REFUSING: stated counts disagree with the filesystem")
        for b in sorted(set(bad)):
            print("   ", b)
        return 1
    print("\n[counts] every stated count matches what is on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
