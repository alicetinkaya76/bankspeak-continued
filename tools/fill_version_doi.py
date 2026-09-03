#!/usr/bin/env python3
"""Fill the version DOI of the code release into every document that cites it.

Usage:  python tools/fill_version_doi.py 10.5281/zenodo.NNNNNNNN [--tag v1.3.0]

The manuscript, the cover letter, the data-availability statement and the
checklist carry the bracket "[VERSION DOI ...]" until the release is archived.
Zenodo mints the DOI when the GitHub tag is pushed (every release so far was
archived that way: the deposited file is named owner/repo-vX.Y.Z.zip, which is
the integration's naming), so the number is not known until after the push.
This tool is the one place the substitution happens, so that a DOI typed once
cannot disagree with itself across five files.

It refuses a DOI that does not resolve to a Zenodo record whose version matches
the tag, because writing an unverified identifier into a submission is the kind
of drift the guards exist to catch.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "docs" / "PAPER_DRAFT_v2.md",
    ROOT / "docs" / "SUBMISSION_COVER_LETTER.md",
    ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md",
    ROOT / "docs" / "PLOS_SUBMISSION_CHECKLIST.md",
]
BRACKET = re.compile(r"\[VERSION DOI[^\]]*\]")
CONCEPT = "10.5281/zenodo.22152944"


def verify(doi: str, tag: str | None) -> dict:
    rec = doi.rsplit(".", 1)[-1]
    req = urllib.request.Request(f"https://zenodo.org/api/records/{rec}",
                                 headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    if d.get("doi") != doi:
        raise SystemExit(f"[doi] {doi} resolves to record {d.get('doi')}, not itself")
    if d.get("conceptdoi") != CONCEPT:
        raise SystemExit(f"[doi] {doi} is not a version of concept {CONCEPT} "
                         f"(it belongs to {d.get('conceptdoi')})")
    ver = d.get("metadata", {}).get("version")
    if tag and ver != tag:
        raise SystemExit(f"[doi] record version is {ver!r}, expected {tag!r}")
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("doi")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--no-verify", action="store_true")
    a = ap.parse_args()
    if not re.fullmatch(r"10\.5281/zenodo\.\d+", a.doi):
        raise SystemExit(f"[doi] not a Zenodo DOI: {a.doi}")
    if not a.no_verify:
        d = verify(a.doi, a.tag)
        print(f"[doi] verified: {a.doi} = version {d['metadata'].get('version')} "
              f"of {CONCEPT}, published {d['metadata'].get('publication_date')}")
    n_total = 0
    for p in TARGETS:
        if not p.exists():
            print(f"[doi] absent, skipped: {p.relative_to(ROOT)}")
            continue
        s = p.read_text(encoding="utf-8")
        n = len(BRACKET.findall(s))
        if n:
            s = BRACKET.sub(f"`{a.doi}`", s)
            p.write_text(s, encoding="utf-8")
        print(f"[doi] {p.relative_to(ROOT)}: {n} bracket(s) filled")
        n_total += n
    if n_total == 0:
        print("[doi] nothing to fill; the brackets are already gone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
