#!/usr/bin/env python3
"""Upload the evidence deposit to Zenodo, using a token this script never prints.

The GitHub-Zenodo webhook archives the code on every release and needs nobody.
The evidence deposit is a separate record -- 48 MB deliberately outside git -- so
it has to be pushed through Zenodo's API, which needs a personal access token.

**The token is not this script's to create.** Put it in `.env` as

    ZENODO_TOKEN=...

(`.gitignore` now covers `.env`; it did not until this file was written, which is
worth knowing before putting a secret there). Make it at
https://zenodo.org/account/settings/applications/tokens/new with the scopes
`deposit:write` and `deposit:actions`. The token is read, used as a bearer
header, and never echoed, logged or written anywhere.

**It does not publish by default.** A published Zenodo record cannot be deleted,
only superseded, so the last irreversible step stays a deliberate one: this
creates the draft, uploads, sets the metadata, reserves the DOI and prints the
draft URL. `--publish` completes it.

`--sandbox` does the whole thing against sandbox.zenodo.org instead, which mints
throwaway records. Rehearse there first; it costs nothing and the real record
cannot be taken back.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "build" / "zenodo_evidence_deposit.zip"
META = ROOT / "build" / "zenodo_evidence_metadata.json"
LIVE = "https://zenodo.org"
SANDBOX = "https://sandbox.zenodo.org"


def token(sandbox: bool) -> str:
    """Read the token from the environment or .env. Never returned to a log."""
    name = "ZENODO_SANDBOX_TOKEN" if sandbox else "ZENODO_TOKEN"
    tok = os.environ.get(name)
    if not tok:
        env = ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith(f"{name}=") and not line.startswith("#"):
                    tok = line.split("=", 1)[1].strip().strip("'\"")
                    break
    if not tok:
        raise SystemExit(
            f"[zenodo] no {name}. Put it in {ROOT / '.env'} as {name}=... — "
            "this script reads it and never prints it. Create one at "
            f"{'sandbox.zenodo.org' if sandbox else 'zenodo.org'}"
            "/account/settings/applications/tokens/new with scopes "
            "deposit:write and deposit:actions.")
    return tok


def call(url: str, tok: str, method: str = "GET", body: bytes | None = None,
         ctype: str = "application/json") -> dict:
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {tok}")
    if body is not None:
        req.add_header("Content-Type", ctype)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:800]
        # The URL can carry no secret: the token travels in a header, not a query
        # string, precisely so that an error message like this one is safe to show.
        raise SystemExit(f"[zenodo] {method} {url} -> HTTP {e.code}\n{detail}")


def put_file(bucket: str, path: Path, tok: str) -> dict:
    with path.open("rb") as fh:
        req = urllib.request.Request(f"{bucket}/{path.name}", data=fh,
                                     method="PUT")
        req.add_header("Authorization", f"Bearer {tok}")
        req.add_header("Content-Type", "application/octet-stream")
        req.add_header("Content-Length", str(path.stat().st_size))
        try:
            with urllib.request.urlopen(req, timeout=1800) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"[zenodo] upload -> HTTP {e.code}\n"
                             f"{e.read().decode('utf-8', 'replace')[:800]}")


def md5(path: Path) -> str:
    h = hashlib.md5()
    with path.open("rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", action="store_true",
                    help="use sandbox.zenodo.org; records there are throwaway")
    ap.add_argument("--publish", action="store_true",
                    help="publish. IRREVERSIBLE: a published record cannot be "
                         "deleted, only superseded by a new version")
    a = ap.parse_args()

    if not ARCHIVE.exists() or not META.exists():
        raise SystemExit("[zenodo] build them first: "
                         "python tools/package_evidence_deposit.py")
    base = SANDBOX if a.sandbox else LIVE
    tok = token(a.sandbox)
    meta = json.loads(META.read_text(encoding="utf-8"))
    local_md5 = md5(ARCHIVE)
    print(f"[zenodo] target   {base}")
    print(f"[zenodo] archive  {ARCHIVE.name}  "
          f"{ARCHIVE.stat().st_size/1e6:.1f} MB  md5 {local_md5}")

    dep = call(f"{base}/api/deposit/depositions", tok, "POST", b"{}")
    dep_id, bucket = dep["id"], dep["links"]["bucket"]
    print(f"[zenodo] draft    {dep_id}")

    up = put_file(bucket, ARCHIVE, tok)
    remote = (up.get("checksum") or "").replace("md5:", "")
    if remote != local_md5:
        raise SystemExit(f"[zenodo] REFUSING: uploaded checksum {remote} != "
                         f"local {local_md5}. The draft is at {dep_id}; delete "
                         "it and retry rather than publishing a corrupt file.")
    print(f"[zenodo] uploaded and checksum-verified against the local file")

    call(f"{base}/api/deposit/depositions/{dep_id}", tok, "PUT",
         json.dumps({"metadata": meta}).encode("utf-8"))
    print("[zenodo] metadata set")

    rec = call(f"{base}/api/deposit/depositions/{dep_id}", tok)
    doi = rec.get("metadata", {}).get("prereserve_doi", {}).get("doi") or rec.get("doi")
    print(f"[zenodo] reserved DOI  {doi}")
    print(f"[zenodo] draft URL     {base}/uploads/{dep_id}")

    if not a.publish:
        print("\n[zenodo] NOT published. Review the draft, then rerun with "
              "--publish, or press Publish in the browser.\n"
              "         Publishing cannot be undone.")
        return 0

    out = call(f"{base}/api/deposit/depositions/{dep_id}/actions/publish",
               tok, "POST")
    print(f"\n[zenodo] PUBLISHED  doi {out.get('doi')}  {out.get('links', {}).get('record_html')}")
    print(f"[zenodo] next: python tools/record_evidence_doi.py {out.get('doi')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
