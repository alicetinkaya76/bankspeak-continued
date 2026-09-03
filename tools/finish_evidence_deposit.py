#!/usr/bin/env python3
"""The last mile for the evidence deposit, as one command.

Run only after the dataset repository has been switched on at
https://zenodo.org/account/settings/github/ (this script checks that the
webhook exists and refuses otherwise, because a release cut before the switch
mints nothing and cannot be re-delivered). Then, in order:

  1. gh release create v1.0.0 on alicetinkaya76/bankspeak-evidence-deposit
     (tools/publish_evidence_repo.py --release), which triggers Zenodo;
  2. poll Zenodo's public records API, no token, until a dataset titled
     "Bankspeak, Continued: Stage-B evidence deposit" by this author exists;
  3. tools/record_evidence_doi.py <DOI>, which fills the last bracket in the
     data-availability statement and wherever else the deposit is cited;
  4. rebuild both PDFs and run the guards.

Nothing here is retried blindly: each step stops the script if it fails, and
the DOI is verified to belong to a record whose creator carries the author's
ORCID before it is written anywhere.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
REPO = "alicetinkaya76/bankspeak-evidence-deposit"
TAG = "v1.0.0"
TITLE = "Bankspeak, Continued: Stage-B evidence deposit"
ORCID = "0000-0002-7747-6854"


def sh(*args: str, check: bool = True) -> str:
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:])
        raise SystemExit(f"[finish] failed: {' '.join(args[:3])}")
    return (r.stdout or r.stderr).strip()


def hook_present() -> bool:
    out = sh("gh", "api", f"repos/{REPO}/hooks", "--jq", "length", check=False)
    return out.isdigit() and int(out) >= 1


def find_record(timeout_s: int = 900) -> str | None:
    q = urllib.parse.quote(f'metadata.title:"{TITLE}"')
    url = f"https://zenodo.org/api/records?q={q}&size=5&sort=mostrecent"
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                d = json.load(r)
            for h in d.get("hits", {}).get("hits", []):
                m = h.get("metadata", {})
                creators = m.get("creators", [])
                if (m.get("title") == TITLE
                        and any(c.get("orcid") == ORCID for c in creators)
                        and (m.get("resource_type", {}).get("type") or m.get("upload_type")) == "dataset"):
                    return h["doi"]
        except Exception:
            pass
        time.sleep(30)
    return None


def main() -> int:
    if not hook_present():
        raise SystemExit("[finish] REFUSING: no webhook on the dataset repository. "
                         "Switch it on at https://zenodo.org/account/settings/github/ "
                         "first; a release cut before that mints nothing.")
    releases = sh("gh", "release", "list", "--repo", REPO, "--limit", "5", check=False)
    if TAG in releases:
        print(f"[finish] release {TAG} already exists; not recreating")
    else:
        print(sh(PY, "tools/publish_evidence_repo.py", "--release", TAG))
    doi = find_record()
    if not doi:
        raise SystemExit("[finish] no Zenodo record appeared within 15 minutes; check the "
                         "hook deliveries (status codes only) and rerun")
    print(f"[finish] minted: {doi}")
    print(sh(PY, "tools/record_evidence_doi.py", doi))
    print(sh(PY, "tools/build_submission_pdf.py", "--both").splitlines()[-1])
    for t in ("placeholder_report.py", "check_submission_metadata.py",
              "check_stated_counts.py", "check_cross_references.py"):
        out = sh(PY, f"tools/{t}", check=False)
        print(f"[finish] {t}: {out.splitlines()[-1] if out else '(no output)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
