#!/usr/bin/env python3
"""Publish the evidence deposit the way this project publishes everything:
a public GitHub repository, a release, and Zenodo's GitHub integration.

No Zenodo token, no Zenodo API. The author's method is a GitHub release on a
repository that Zenodo's webhook watches; Zenodo archives the release zipball
and mints a version DOI under the record's concept DOI. The code archive has
been minted that way three times. The evidence deposit is a separate record,
so it needs a repository of its own, and this tool builds and maintains it.

    python tools/publish_evidence_repo.py --stage            # sync + metadata, no git
    python tools/publish_evidence_repo.py --push v1.0.0      # commit, push main, push tag
    python tools/publish_evidence_repo.py --release v1.0.0   # gh release create

The release is the step that triggers Zenodo, and it only works AFTER the
repository has been switched on at https://zenodo.org/account/settings/github/
in a browser, once, by the account owner. That is why it is a separate flag:
a release cut before the switch mints nothing and cannot be re-delivered.

What goes in: exactly the staged tree that tools/prepare_zenodo_deposit.py
--copy writes (MANIFEST.csv, README.md, payload/), which is already the
licence-filtered form -- IMF documents hashed and not copied, titles and URLs
dropped, the frame's identifiers kept because the data-availability statement
promises them. Plus .zenodo.json, LICENSE.md and .gitattributes written here.
The staged tree is re-checked with the mirror's content scanner for anything
other than identifier lists before a single byte is committed.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "zenodo_deposit"
REPO_DIR = ROOT.parent / "bankspeak-evidence-deposit"
OWNER, NAME = "alicetinkaya76", "bankspeak-evidence-deposit"
CODE_DOI = os.environ.get("BANKSPEAK_CODE_VERSION_DOI", "10.5281/zenodo.22272212")
SAP_DOI, OSF_DOI = "10.5281/zenodo.22098259", "10.17605/OSF.IO/5C9J8"

sys.path.insert(0, str(ROOT / "tools"))
from package_evidence_deposit import DESCRIPTION            # noqa: E402

ZENODO = {
    "title": "Bankspeak, Continued: Stage-B evidence deposit",
    "upload_type": "dataset",
    "description": DESCRIPTION,
    "creators": [{"name": "Çetinkaya, Ali", "orcid": "0000-0002-7747-6854",
                  "affiliation": "Selçuk University"}],
    "access_right": "open",
    # World Bank API captures under the Bank's terms, the author's derived
    # outputs under CC BY 4.0: a mixed record, which the author files as
    # other-open by convention.
    "license": "other-open",
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
}

LICENSE_MD = """# Licence

This record mixes two kinds of material and they carry different terms.

**World Bank API captures** (`payload/data/meta/wb_*_raw/` and the request logs
beside them) are the World Bank's own metadata, retrieved from its Documents
and Reports service and reproduced here unchanged as a write-once record of
what was retrieved. They remain under the World Bank's terms of use for that
service and are not relicensed by this deposit.

**Everything else** (sampling frames, retrieval and exclusion ledgers,
quality-control summaries, derived counts, features, panel cells, validation
batteries, calibration outputs and the manifest) was produced by the author and
is released under Creative Commons Attribution 4.0 (CC BY 4.0).

**Nothing from the IMF is included.** The 1,064 IMF Article IV staff reports
analysed in the study are held under a written permission that forbids
redistributing the documents or extracted text. They are listed in
`MANIFEST.csv` by path and SHA-256 with disposition `hash_only_not_deposited`,
and identified in `payload/data/meta/imf_document_index.csv` by report number,
year, country, DOI and hash, with no title and no URL.
"""

GITATTRIBUTES = "* text=auto eol=lf\n*.csv text eol=lf\n*.json text eol=lf\n*.md text eol=lf\n"


def scan_stage() -> None:
    """Refuse on anything but identifier lists, using the mirror's scanner."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bp", ROOT / "tools" / "build_public_repo.py")
    bp = importlib.util.module_from_spec(spec)
    sys.modules["bp"] = bp
    spec.loader.exec_module(bp)
    bad = {}
    for f in STAGE.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(STAGE).as_posix()
        for hit in bp.scan(f, rel) or []:
            # identifier counts over the mirror's cap are the frame; anything
            # else (a URL, a title) is a refusal
            if "report number" in hit or "report no + DOI" in hit or "DOI prefix" in hit:
                continue
            bad.setdefault(rel, []).append(hit)
    if bad:
        for k, v in bad.items():
            print(f"    {k}: {v}")
        raise SystemExit(f"[evidence-repo] REFUSING: {len(bad)} staged file(s) carry "
                         "IMF content other than catalogue identifiers")
    print("[evidence-repo] stage scan: identifiers only; no URL, no title, no text")


def stage() -> None:
    if not (STAGE / "MANIFEST.csv").exists():
        raise SystemExit("[evidence-repo] run tools/package_evidence_deposit.py first")
    scan_stage()
    REPO_DIR.mkdir(exist_ok=True)
    for item in ("MANIFEST.csv", "README.md", "payload"):
        src, dst = STAGE / item, REPO_DIR / item
        if dst.is_dir():
            shutil.rmtree(dst)
        elif dst.exists():
            dst.unlink()
        (shutil.copytree if src.is_dir() else shutil.copy2)(src, dst)
    (REPO_DIR / ".zenodo.json").write_text(
        json.dumps(ZENODO, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (REPO_DIR / "LICENSE.md").write_text(LICENSE_MD, encoding="utf-8")
    (REPO_DIR / ".gitattributes").write_text(GITATTRIBUTES, encoding="utf-8")
    n = sum(1 for f in REPO_DIR.rglob("*") if f.is_file() and ".git" not in f.parts)
    print(f"[evidence-repo] staged {n} files in {REPO_DIR}")


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO_DIR, capture_output=True,
                          text=True, check=check)


def push(tag: str) -> None:
    if not (REPO_DIR / ".git").exists():
        git("init", "-b", "main")
        git("remote", "add", "origin", f"git@github.com:{OWNER}/{NAME}.git")
    git("add", "-A")
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        git("commit", "-q", "-m", f"Evidence deposit {tag}: companion to code release {CODE_DOI}")
    git("tag", "-f", "-a", tag, "-m", f"Evidence deposit {tag}")
    print(git("push", "origin", "main").stderr.strip().splitlines()[-1:] or ["pushed main"])
    print(git("push", "-f", "origin", tag).stderr.strip().splitlines()[-1:] or [f"pushed {tag}"])


def release(tag: str) -> None:
    notes = (f"Stage-B evidence deposit for *Reconstructing Bankspeak*, companion to "
             f"code release {CODE_DOI}. See README.md and LICENSE.md.")
    r = subprocess.run(["gh", "release", "create", tag, "--repo", f"{OWNER}/{NAME}",
                        "--title", f"{tag}: Stage-B evidence deposit", "--notes", notes],
                       capture_output=True, text=True)
    print((r.stdout or r.stderr).strip())
    if r.returncode:
        raise SystemExit(r.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--push", metavar="TAG")
    ap.add_argument("--release", metavar="TAG")
    a = ap.parse_args()
    if a.stage or a.push:
        stage()
    if a.push:
        push(a.push)
    if a.release:
        release(a.release)
    if not (a.stage or a.push or a.release):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
