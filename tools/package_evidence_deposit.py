#!/usr/bin/env python3
"""Package the evidence deposit as one archive plus its Zenodo metadata.

The GitHub–Zenodo webhook archives the git repository on every release, and it
does that half by itself. It cannot do this half: the evidence deposit is 48 MB
of data that is deliberately NOT in git — the project's own "git carries the
decision, Zenodo carries the evidence" split, which is also what keeps the leak
guard meaningful, since a guard that never sees the data cannot be tested by it.

So the deposit is a separate Zenodo record and its upload is manual. This makes
the manual step as small as it can be: one file to drag in and one block of
metadata to paste, rather than 780 files and a form filled from memory.

It does NOT upload. Uploading needs a Zenodo personal access token, which is a
credential, and credentials are the author's to handle.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEPOSIT = ROOT / "zenodo_deposit"
OUT_ZIP = ROOT / "build" / "zenodo_evidence_deposit.zip"
OUT_META = ROOT / "build" / "zenodo_evidence_metadata.json"

# The companion code archive this deposit is a supplement TO. It must be the
# release that actually contains the reported results. Round 20 found v1.2.0
# baked in here and in the built metadata, which is the release the manuscript
# says must not be cited for them -- so the deposit was declaring itself a
# supplement to the wrong archive. The concept DOI is used until the new
# version DOI exists; it always resolves to the latest version, so it is wrong
# in a way that self-corrects rather than a way that misdirects.
CONCEPT_DOI = "10.5281/zenodo.22152944"
CODE_DOI = os.environ.get("BANKSPEAK_CODE_VERSION_DOI", CONCEPT_DOI)
SAP_DOI = "10.5281/zenodo.22098259"
OSF_DOI = "10.17605/OSF.IO/5C9J8"

DESCRIPTION = """<p><b>Evidence deposit for <i>Reconstructing Bankspeak</i></b>: the
artifacts behind an independent reconstruction of Moretti and Pestre's <i>Bankspeak</i>
(2015) from primary World Bank documents, and a preregistered test of whether
post-2022 vocabulary associated with large language models shows a World Bank
discontinuity against an IMF Article IV comparator. <b>The confirmatory result is
negative</b>: no panel satisfies the preregistered decision rule.</p>

<p>The companion code archive is {code}; this record carries the evidence it was
run on. Unpack <code>payload/data</code> as <code>data/</code> in a checkout of
that archive and <code>python tools/make_paper_tables.py</code> reproduces all
seven manuscript tables byte-for-byte, and
<code>python tools/make_paper_figures.py</code> all four figures.</p>

<p><b>Deposited:</b> write-once World Bank API captures with their request logs,
frozen sampling frames, retrieval and exclusion ledgers, quality-control
summaries, the OCR inventory and calibration, document- and year-level counts
with token denominators, feature-family counts, the confirmatory panel cells,
both validation batteries, the governing family verdict, the power curves, and
the post-hoc dispersion and block-origin studies.</p>

<p><b>Not deposited, and hashed instead:</b> everything IMF. The 1,064 Article IV
staff reports are held under a written permission that forbids redistributing
documents or extracted text and permits derived non-substitutive outputs
including SHA-256 hashes. <code>MANIFEST.csv</code> lists every IMF-derived file
by path and SHA-256 with disposition <code>hash_only_not_deposited</code>, so a
researcher who lawfully obtains the same documents can verify byte identity
before rerunning anything.</p>

<p>One file ships redacted. The frozen sampling frame carries
<code>display_title</code> and <code>pdfurl</code> for the IMF rows, verbatim
titles and imf.org document URLs, so those columns are dropped, for every row
rather than only the IMF ones, because no generator reads them and a
whole-column rule cannot leak through a misclassified row. The unredacted
original is listed by SHA-256 so nothing becomes unverifiable.</p>

<p>Stage-A preregistration: {osf}. Stage-B statistical analysis plan, externally
timestamped before any reported outcome was computed: {sap}.</p>""".format(
    code=CODE_DOI, osf=OSF_DOI, sap=SAP_DOI)


def main() -> int:
    # Stage, then zip -- always both, in that order, from one command.
    #
    # This used to zip whatever zenodo_deposit/ already held and tell the
    # caller to run the staging step first. Round 20 extended the staging
    # list by eighteen analysis outputs, re-ran only this file, and shipped a
    # deposit that carried none of them: the inputs to S10.3-S10.9 and Tables
    # 3c-5d were on the list and not in the zip. A second external review
    # found it by opening the zip. A build with two steps and no check between
    # them is a build that can be half-run, so the staging step is now called
    # here and the zip is verified against the list before it is reported.
    # The staging script adds files and never removes them, so a file dropped
    # from its list survived from an earlier run, unlisted in MANIFEST.csv, and
    # went into the zip. Rebuild the payload from nothing every time.
    import shutil
    if (DEPOSIT / "payload").exists():
        shutil.rmtree(DEPOSIT / "payload")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "prepare_zenodo_deposit.py"),
                        "--out", str(DEPOSIT), "--copy"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("[package] staging failed; nothing zipped")
    if not (DEPOSIT / "MANIFEST.csv").exists():
        raise SystemExit("[package] staging wrote no MANIFEST.csv")
    OUT_ZIP.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(f for f in DEPOSIT.rglob("*") if f.is_file())
    with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for f in files:
            z.write(f, f.relative_to(DEPOSIT.parent).as_posix())
    raw = sum(f.stat().st_size for f in files)
    print(f"[package] {len(files)} files, {raw/1e6:.1f} MB -> "
          f"{OUT_ZIP.relative_to(ROOT)} ({OUT_ZIP.stat().st_size/1e6:.1f} MB)")

    # Every deposit-list file that exists in the repo must be in the zip.
    sys.path.insert(0, str(ROOT / "tools"))
    from prepare_zenodo_deposit import INCLUDE_FILES as _LIST          # noqa: E402
    with zipfile.ZipFile(OUT_ZIP) as z:
        names = set(z.namelist())
    missing = [rel for rel in _LIST
               if (ROOT / rel).exists()
               and not any(n.endswith("/" + rel) or n.endswith("/" + rel.replace("data/", "payload/data/", 1))
                           for n in names)]
    if missing:
        for rel in missing:
            print(f"    missing from zip: {rel}")
        raise SystemExit(f"[package] REFUSING: {len(missing)} listed file(s) are "
                         "not in the zip; the staging step did not pick them up")
    # ... and nothing in the zip may be absent from the manifest: an unlisted
    # file is one nobody hashed, which is how the stale README travelled.
    import csv
    with zipfile.ZipFile(OUT_ZIP) as z:
        payload_entries = {n.split("/payload/", 1)[1] for n in z.namelist()
                           if "/payload/" in n and not n.endswith("/")}
    with (DEPOSIT / "MANIFEST.csv").open(encoding="utf-8") as fh:
        listed = {r["path"] for r in csv.DictReader(fh)
                  if r["disposition"].startswith("deposited")}
    extras = sorted(payload_entries - listed)
    if extras:
        for rel in extras[:10]:
            print(f"    in zip, not in manifest: {rel}")
        raise SystemExit(f"[package] REFUSING: {len(extras)} zip entr(y/ies) are "
                         "not in MANIFEST.csv")
    print(f"[package] zip and manifest agree: {len(payload_entries)} payload files")
    print(f"[package] every listed file present in the zip "
          f"({sum(1 for rel in _LIST if (ROOT / rel).exists())} checked)")

    meta = {
        "title": "Bankspeak, Continued — Stage-B evidence deposit",
        "upload_type": "dataset",
        "description": DESCRIPTION,
        "creators": [{"name": "Çetinkaya, Ali"}],
        "keywords": ["computational humanities", "corpus linguistics",
                     "institutional discourse", "preregistration", "null result",
                     "interrupted time series", "World Bank",
                     "large language models", "reproducibility"],
        "related_identifiers": [
            {"identifier": CODE_DOI, "relation": "isSupplementTo", "scheme": "doi"},
            {"identifier": SAP_DOI, "relation": "isSupplementTo", "scheme": "doi"},
            {"identifier": OSF_DOI, "relation": "isSupplementTo", "scheme": "doi"},
        ],
        "language": "eng",
        "license": "cc-by-4.0",
        "notes": ("No World Bank or IMF document text is included. World Bank "
                  "content is public disclosure under the Access to Information "
                  "Policy. The IMF corpus is held under a permission forbidding "
                  "redistribution and appears only as SHA-256 hashes in "
                  "MANIFEST.csv."),
    }
    OUT_META.write_text(json.dumps(meta, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    print(f"[package] metadata -> {OUT_META.relative_to(ROOT)}")
    print("\nUpload by hand at https://zenodo.org/uploads/new — this tool does not,\n"
          "because that needs a personal access token and tokens are yours.\n"
          "Afterwards the new DOI replaces the placeholder in:\n"
          "  docs/PAPER_DRAFT_v2.md §9, docs/SUBMISSION_DATA_AVAILABILITY.md,\n"
          "  docs/SUBMISSION_COVER_LETTER.md   (tools/placeholder_report.py lists them)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
