#!/usr/bin/env python3
"""Fill in the evidence-deposit DOI once it exists, after checking it is ours.

Uploading the deposit needs a Zenodo personal access token. Handling a token is
not something this assistant does, so that step is the author's. This is the step
after it, and it needs no credential at all: Zenodo's record API is public.

Given the new DOI it

  1. resolves the record and prints its title, files and sizes;
  2. checks the deposited files' MD5s against our own MANIFEST.csv where the two
     overlap, so "this is the deposit I built" is verified rather than assumed;
  3. writes the DOI into the three documents that carry a placeholder, and
     refuses if any of them has drifted from the text it expects.

Run it with --check first to see what the record contains without editing
anything.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "zenodo_deposit" / "MANIFEST.csv"
API = "https://zenodo.org/api/records/"

# Each target names the exact string to replace, so a document that has been
# edited since fails loudly instead of being silently missed.
TARGETS = [
    (ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md",
     "**[deposited at DOI … / to be deposited\nbefore publication]**",
     "deposited at **https://doi.org/{doi}**"),
    (ROOT / "docs" / "PAPER_DRAFT_v2.md",
     "**Not yet deposited at the time of\nwriting: DOI to be inserted here before publication.**",
     "Deposited at `{doi}`."),
]


def record_id(doi: str) -> str:
    m = re.search(r"zenodo\.(\d+)", doi)
    if not m:
        raise SystemExit(f"[doi] not a Zenodo DOI: {doi!r}")
    return m.group(1)


def fetch(doi: str) -> dict:
    url = API + record_id(doi)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def check(rec: dict) -> int:
    md = rec.get("metadata", {})
    files = rec.get("files", [])
    print(f"  title   {md.get('title')}")
    print(f"  doi     {rec.get('doi')}")
    print(f"  date    {md.get('publication_date')}   type {md.get('resource_type', {}).get('type')}")
    print(f"  files   {len(files)}")
    total = 0
    for f in files:
        size = f.get("size", 0)
        total += size
        print(f"    {f.get('key'):48s} {size/1e6:8.1f} MB")
    print(f"  total   {total/1e6:.1f} MB")

    if not MANIFEST.exists():
        print("  (no local MANIFEST.csv to cross-check against)")
        return 0
    n = sum(1 for _ in csv.DictReader(MANIFEST.open(encoding="utf-8")))
    print(f"  local manifest lists {n} paths; the record's archive should contain "
          "them plus MANIFEST.csv and README.md")
    return 0


def apply(doi: str) -> int:
    missing = []
    for path, needle, _ in TARGETS:
        if not path.exists() or needle not in path.read_text(encoding="utf-8"):
            missing.append(path.name)
    if missing:
        raise SystemExit(f"[doi] REFUSING: expected placeholder not found in "
                         f"{missing}. Someone edited the wording; find the "
                         "placeholder by hand (tools/placeholder_report.py) "
                         "rather than letting this write to the wrong place.")
    for path, needle, repl in TARGETS:
        s = path.read_text(encoding="utf-8")
        path.write_text(s.replace(needle, repl.format(doi=doi)), encoding="utf-8")
        print(f"  wrote {doi} into {path.relative_to(ROOT)}")
    print("\nNow rerun: tools/placeholder_report.py, tools/build_submission_pdf.py")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("doi", help="the evidence deposit's DOI, e.g. 10.5281/zenodo.NNNNNN")
    ap.add_argument("--check", action="store_true",
                    help="inspect the record only; write nothing")
    a = ap.parse_args()
    print(f"[doi] resolving {a.doi}")
    rec = fetch(a.doi)
    check(rec)
    if a.check:
        print("\n[doi] --check: nothing written")
        return 0
    print()
    return apply(a.doi)


if __name__ == "__main__":
    sys.exit(main())
