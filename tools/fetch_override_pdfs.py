#!/usr/bin/env python3
"""Ensure every OCR-override document actually has a PDF to OCR.

## The gap this closes

`ocr_overrides.csv` (rulings D-9, D-12) pins broken-CMap documents to the OCR
path. But `ocr_prepass --scan` builds its inventory by walking `data/raw` for
**PDFs**, and a document retrieved through `txturl` has none. Three of the five
override documents were server-text only, so the override matched nothing, the
inventory never listed them, OCR processed zero of them — and the quality gate
still passed, because a ledger row is what the gate checks.

That is the dangerous shape: **the ruling recorded, the gate satisfied, the
remedy never applied.** A ledger has to be backed by an artifact, so this stage
fetches the PDF for every override document that lacks one, and refuses if any
override cannot be given one rather than proceeding with a silent gap.

Runs before `ocr_scan` in the post-SAP driver. Downloads are text download,
which PREREG §11.3 places after the SAP freeze, so it is gated like the rest.
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "data" / "meta"
RAW = ROOT / "data" / "raw"
OVR = META / "ocr_overrides.csv"
INDEX = META / "frozen_sampling_v2.csv"
UA = "bankspeak-continued/0.1 (research; contact: kapsul.yonetim@gmail.com)"


def pdf_path(row: dict) -> Path:
    return RAW / row["stratum"] / row["year"] / f"{row['id']}.pdf"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="read-only; always allowed")
    ap.add_argument("--i-have-frozen-the-sap", action="store_true")
    a = ap.parse_args(argv)

    if not OVR.exists():
        print("[ovr-pdf] no override ledger; nothing to do")
        return 0
    ids = [r["id"] for r in csv.DictReader(OVR.open(encoding="utf-8"))]
    index = {r["id"]: r for r in csv.DictReader(INDEX.open(encoding="utf-8"))}

    missing, unfixable = [], []
    for i in ids:
        row = index.get(i)
        if row is None:
            continue                      # not in the analysis corpus; not our problem
        if pdf_path(row).exists():
            continue
        (missing if row.get("pdfurl") else unfixable).append(row)

    print(f"[ovr-pdf] {len(ids)} override(s); {len(missing)} need a PDF, "
          f"{len(unfixable)} have no pdfurl")
    if a.list:
        for r in missing:
            print(f"  fetch  {pdf_path(r).relative_to(ROOT)}")
        for r in unfixable:
            print(f"  STUCK  {r['id']} ({r['stratum']}/{r['year']}) — no pdfurl")
        return 0
    if unfixable:
        sys.exit(f"[ovr-pdf] REFUSING: {len(unfixable)} override(s) have no "
                 "pdfurl, so their ruling cannot be applied. A ledger row with "
                 "no reachable artifact is a ruling in name only — re-rule them "
                 "(exclude) rather than leaving the gate satisfied by nothing.")
    if not missing:
        print("[ovr-pdf] every override document already has its PDF")
        return 0
    if not a.i_have_frozen_the_sap:
        sys.exit("[ovr-pdf] REFUSING: fetching is text download, which PREREG "
                 "§11.3 places after the SAP freeze. Use --list to inspect.")

    for r in missing:
        dest = pdf_path(r)
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", "180",
                        "-o", str(dest), r["pdfurl"]], check=False)
        ok = dest.exists() and dest.read_bytes()[:5] == b"%PDF-"
        print(f"  {'ok  ' if ok else 'FAIL'} {dest.relative_to(ROOT)}")
        if not ok:
            dest.unlink(missing_ok=True)
            sys.exit(f"[ovr-pdf] {r['id']}: no usable PDF at its pdfurl; "
                     "the D-9/D-12 remedy cannot be applied — re-rule it")
    print(f"[ovr-pdf] fetched {len(missing)}; ocr_scan will now list them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
