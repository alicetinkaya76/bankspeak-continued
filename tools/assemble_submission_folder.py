#!/usr/bin/env python3
"""Lay out submission/PLOS/ as the journal's upload form expects it.

One folder, one file per upload slot, named the way PLOS names them, plus a
short index saying which form field each text file feeds. Nothing is edited
here: every file is copied from the build or from docs/, and the folder is
rebuilt from nothing each time so nothing stale survives.

    python tools/assemble_submission_folder.py

Refuses if the guards would refuse: a placeholder in the manuscript, a page
count or DOI that disagrees across documents, or a missing figure file.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "PLOS"
BUILD = ROOT / "build" / "submission"
FIG = ROOT / "docs" / "figures"

ITEMS = [
    # (source, target name in the folder, PLOS slot)
    (BUILD / "PLOS_ONE_submission.pdf", "Manuscript.pdf",
     "Manuscript (PDF for a LaTeX-built manuscript; line numbers, double spacing, page numbers)"),
    (BUILD / "PLOS_ONE_supplement.pdf", "S1_Text.pdf",
     "Supporting Information, S1 Text (caption is at the end of the manuscript)"),
    (FIG / "fig1_composition.tif", "Fig1.tif", "Figure 1 (TIFF, 300 dpi)"),
    (FIG / "fig2_panels.tif", "Fig2.tif", "Figure 2 (TIFF, 300 dpi)"),
    (FIG / "fig3_power.tif", "Fig3.tif", "Figure 3 (TIFF, 300 dpi)"),
    (FIG / "fig4_contrast.tif", "Fig4.tif", "Figure 4 (TIFF, 300 dpi)"),
    (ROOT / "docs" / "SUBMISSION_COVER_LETTER.md", "Cover_Letter.md",
     "Cover letter: paste the body (from 'Dear PLOS ONE Editors') into the form"),
    (ROOT / "docs" / "SUBMISSION_DATA_AVAILABILITY.md", "Data_Availability_Statement.md",
     "Data Availability field: paste from 'This study uses two document collections'"),
    (ROOT / "docs" / "SUBMISSION_FORM_FIELDS.md", "Form_Fields.md",
     "Short title, financial disclosure, competing interests, CRediT, ethics, preprint"),
]

GUARDS = ["placeholder_report.py", "check_submission_metadata.py",
          "check_stated_counts.py", "check_cross_references.py"]


def main() -> int:
    failed = []
    for g in GUARDS:
        r = subprocess.run([sys.executable, str(ROOT / "tools" / g)],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            failed.append((g, (r.stdout or r.stderr).strip().splitlines()[-3:]))
    if failed:
        for g, tail in failed:
            print(f"[submission] {g} refuses:")
            for line in tail:
                print("    " + line)
        raise SystemExit("[submission] not assembled: fix the guards first")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    lines = ["# submission/PLOS", "",
             "Built by `tools/assemble_submission_folder.py`; every guard was green at "
             "build time. One file per upload slot.", "",
             "| file | PLOS slot | sha256 |", "|---|---|---|"]
    for src, name, slot in ITEMS:
        if not src.exists():
            raise SystemExit(f"[submission] missing: {src.relative_to(ROOT)}")
        dst = OUT / name
        shutil.copy2(src, dst)
        digest = hashlib.sha256(dst.read_bytes()).hexdigest()[:16]
        lines.append(f"| `{name}` | {slot} | `{digest}` |")
    lines += ["",
              "Order in the form: manuscript, then figures Fig1 to Fig4, then S1 Text; the "
              "three Markdown files are pasted, not uploaded.", ""]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    n = sum(1 for p in OUT.iterdir() if p.is_file())
    print(f"[submission] {n} files in {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
