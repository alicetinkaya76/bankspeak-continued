#!/usr/bin/env python3
"""Refuse if the review kit no longer matches the repository it was cut from.

`third_eye_kit/` is gitignored, so `git status` cannot see it drift, and it did:
an external reading found the kit's copy of the manuscript, the submission PDF
and two rq1 artifacts differing from their repository originals while the bundle
presented itself as a copy of them. A reviewer checking a number against the kit
would have been checking a different document from the one the author was
editing, and nothing anywhere would have said so.

The builder now records a sha256 per staged file. This compares them, which
answers the question without a rebuild — a rebuild is the fix, not the check,
and a check that fixes what it measures cannot report drift.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "third_eye_kit"
SUMS = KIT / "SHA256SUMS.json"


def main() -> int:
    if not KIT.exists():
        print("[kit-fresh] NOT CHECKED — no third_eye_kit/ in this tree")
        return 0
    if not SUMS.exists():
        print("[kit-fresh] REFUSING: the kit carries no SHA256SUMS.json, so its "
              "freshness cannot be established. Rebuild with "
              "tools/build_third_eye_kit.py.")
        return 1

    rec = json.loads(SUMS.read_text(encoding="utf-8"))["files"]
    # The manifest keys are "<subfolder>/<basename>", and the same basename can
    # be staged from two different repository paths, so resolve back through the
    # builder's own INCLUDE list rather than guessing at the original location.
    sys.path.insert(0, str(ROOT / "tools"))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kitbuild", ROOT / "tools" / "build_third_eye_kit.py")
    kb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb)
    origin = {f"{sub}/{f.name}": f for f, sub, _why in kb.staged_files()}

    stale, missing, unrecorded = [], [], []
    for key, want in sorted(rec.items()):
        src = origin.get(key)
        if src is None:
            unrecorded.append(key)
            continue
        if not src.exists():
            missing.append(key)
            continue
        got = hashlib.sha256(src.read_bytes()).hexdigest()
        if got != want:
            stale.append(key)

    for key in sorted(origin):
        if key not in rec:
            unrecorded.append(key)

    print(f"  staged files recorded  {len(rec)}")
    print(f"  stale against the repo {len(stale)}")
    print(f"  source now missing     {len(missing)}")
    print(f"  not in the record      {len(set(unrecorded))}")

    if stale or missing or unrecorded:
        print("\n[kit-fresh] REFUSING: the kit does not match the repository")
        for k in stale[:12]:
            print(f"    stale: {k}")
        for k in missing[:6]:
            print(f"    source gone: {k}")
        for k in sorted(set(unrecorded))[:6]:
            print(f"    unrecorded: {k}")
        print("    rebuild with tools/build_third_eye_kit.py")
        return 1
    print("\n[kit-fresh] the kit is a current copy of the repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
