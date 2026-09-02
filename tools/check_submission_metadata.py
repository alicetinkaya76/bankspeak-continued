#!/usr/bin/env python3
"""Refuse if the submission documents disagree about the paper's own metadata.

Round 18 retitled the paper and left five documents behind: the checklist, the
cover letter and the public README still carried "an Unconfirmed Post-2022
Break"; the checklist reported a 16-page supplement that is 17, a 300-word
abstract that is 298, an archived version whose test count predates the round,
and called the study a replication where the manuscript says "reconstruction,
not replication" in as many words. check_stated_counts covered none of it,
because it was written around figures, references and kit files.

The fix is not another list of typed numbers. Everything below is DERIVED from
the manuscript or measured from the artifact, and every document that repeats it
is compared against that source. A number nobody can regenerate is a number that
will be wrong eventually, and the same is true of a title.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
SUPP = ROOT / "docs" / "PAPER_SUPPLEMENT_v1.md"
BUILD = ROOT / "build" / "submission"
# Every document that restates the paper's identity. A file absent from the
# tree is reported as unchecked, never as agreeing.
ECHOES = {
    "checklist": ROOT / "docs" / "PLOS_SUBMISSION_CHECKLIST.md",
    "cover letter": ROOT / "docs" / "SUBMISSION_COVER_LETTER.md",
    "data availability": ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md",
    "DAS author note": ROOT / "docs" / "SUBMISSION_DAS_AUTHOR_NOTE.md",
    "supplement": SUPP,
    "public README": ROOT.parent / "bankspeak-public" / "README.md",
    "kit manifest": ROOT / "third_eye_kit" / "MANIFEST.md",
}


def canonical() -> dict:
    """The paper is the source. Nothing here is typed twice."""
    paper = PAPER.read_text(encoding="utf-8")
    title = paper.splitlines()[0].lstrip("# ").strip()
    m = re.search(r"^## Abstract\s*\n(.*?)(?=\n## )", paper, re.S | re.M)
    abstract = m.group(1).strip() if m else ""
    meta = {"title": title, "abstract_words": len(abstract.split())}
    for name, path in (("submission_pages", "PLOS_ONE_submission.pdf"),
                       ("supplement_pages", "PLOS_ONE_supplement.pdf")):
        f = BUILD / path
        meta[name] = _pages(f) if f.exists() else None
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q",
                            "--collect-only"], cwd=ROOT, capture_output=True,
                           text=True, timeout=300)
        mm = re.search(r"(\d+) tests? collected", r.stdout)
        meta["tests_collected"] = int(mm.group(1)) if mm else None
    except Exception:
        meta["tests_collected"] = None
    return meta


def _pages(f: Path):
    try:
        import fitz
        return fitz.open(f).page_count
    except Exception:
        return None


def main() -> int:
    meta = canonical()
    bad, unchecked = [], []
    print(f"  title              {meta['title'][:64]}…")
    print(f"  abstract words     {meta['abstract_words']}")
    print(f"  submission pages   {meta['submission_pages']}")
    print(f"  supplement pages   {meta['supplement_pages']}")
    print(f"  tests collected    {meta['tests_collected']}")

    # The distinctive tail of the title, which is the part that was retitled and
    # the part every stale copy got wrong.
    # Prose wraps, and an author reaching for a dash may reach for any of them.
    # Comparing raw substrings made the guard fire on a document that agreed
    # with the paper and differed only in a line break and an en dash.
    def norm(t: str) -> str:
        t = re.sub(r"[\u2010-\u2015\u2212]", "-", t)
        return " ".join(t.split()).lower()

    tail = meta["title"].split(",")[-1].strip()
    tail_n = norm(tail)
    stale = re.compile(r"unconfirmed post-2022 break")

    for label, path in ECHOES.items():
        if not path.exists():
            unchecked.append(label)
            continue
        text = norm(path.read_text(encoding="utf-8", errors="replace"))
        if stale.search(text):
            bad.append(f"{label} still carries the pre-retitle name "
                       f"(\"Unconfirmed Post-2022 Break\"); the paper says "
                       f"\"{tail}\"")
        # A document that quotes the title at all must quote the current one.
        if "reconstructing bankspeak" in text and tail_n not in text:
            bad.append(f"{label} quotes the title but not its current tail "
                       f"(\"{tail}\")")

    ck = ECHOES["checklist"]
    if ck.exists():
        t = ck.read_text(encoding="utf-8")
        for pat, want, what in (
            (r"`PLOS_ONE_supplement\.pdf` at (\d+) pages", meta["supplement_pages"],
             "supplement page count"),
            (r"\| Abstract \| \"not exceed 300 words\" \| (\d+) \|", meta["abstract_words"],
             "abstract word count"),
        ):
            m = re.search(pat, t)
            if m and want is not None and int(m.group(1)) != want:
                bad.append(f"checklist says {what} {m.group(1)}; it is {want}")
        # The manuscript is explicit that this is not a replication.
        if re.search(r"This paper \*\*is\*\* a replication", t):
            bad.append("the checklist calls the study a replication; the "
                       "manuscript says \"a reconstruction, not a replication\"")
    # The archived release must be the one that carries these results, and an
    # absent claim must not read as a satisfied one -- the first version of this
    # check looked for a stale sentence and passed silently once the sentence
    # was reworded, which is the same "absence is success" defect it was written
    # to catch elsewhere.
    paper_t = PAPER.read_text(encoding="utf-8")
    if "[VERSION DOI" in paper_t:
        bad.append("the manuscript's version DOI is unfilled: the archived "
                   "release does not yet contain these results. Cut a release, "
                   "let Zenodo mint the version DOI, and fill it in the "
                   "manuscript, the checklist and the cover letter")
    elif not re.search(r"version DOI `10\.5281/zenodo\.\d+`", paper_t):
        bad.append("the manuscript names no version DOI at all; a concept DOI "
                   "alone does not pin the content a reviewer sees")

    cl = ECHOES["cover letter"]
    if cl.exists():
        n = len(cl.read_text(encoding="utf-8").split())
        print(f"  cover letter words {n}")
        if n > 550:
            bad.append(f"the cover letter is {n} words; PLOS ONE asks for one "
                       "page, which is about 450-500")

    if unchecked:
        print(f"\n  NOT CHECKED (absent here): {', '.join(sorted(unchecked))}")
    if bad:
        print("\n[metadata] REFUSING: the submission documents disagree")
        for b in sorted(set(bad)):
            print("   ", b)
        return 1
    print("\n[metadata] every document agrees with the manuscript")
    return 0


if __name__ == "__main__":
    sys.exit(main())
