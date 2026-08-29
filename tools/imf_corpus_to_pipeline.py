#!/usr/bin/env python3
"""Land the retrieved IMF corpus in the pipeline's own layout (A8, part 2).

`tools/fetch_imf_cr_pdfs.py` retrieved the 1,064 documents into a flat working
directory. `s03_extract_text` walks ``data/raw/`` recursively and mirrors each
file's RELATIVE PATH into ``data/text/``, so the layout the files sit in decides
the layout the corpus ends up in. `s02_download_texts` writes
``data/raw/<stratum>/<year>/<id>.<ext>``; this module puts the IMF corpus in the
same shape so `s03` needs no modification and A9's ``data/text/imf_*``
convention comes out on its own:

    data/raw/imf_article_iv/<year>/CR<YYYY>-<NNN>.pdf

``<year>`` is the FROZEN SAMPLE's year column, not the report number's year. The
two differ for some records (frozen row `2002/246` carries year 2004), and the
sampler, the per-cell seed and every downstream cell key use the sample's year.
Taking it from the report number would silently re-bin those documents.

It also emits an s02-shaped CSV. `s02` reads `id`, `stratum`, `year`, `txturl`,
`pdfurl` from a frozen sampling file, and the IMF sample has none of those
columns; the handover's A8 item asks for that adapter. `pdfurl` is filled with
the URL the retrieval actually resolved, taken from the manifest, so the
retrieval is reproducible through the pipeline's own stage rather than only
through the bespoke tool.

Verification is not optional: every file's SHA-256 is re-derived after the move
and checked against the manifest. A mismatch aborts and leaves the file in
place.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "data" / "raw" / "imf_cr_pdf"
DEST_ROOT = ROOT / "data" / "raw" / "imf_article_iv"
PROV_DIR = ROOT / "data" / "meta" / "imf_retrieval"
FROZEN = ROOT / "data" / "meta" / "frozen_sampling_imf_v1.csv"
S02_CSV = ROOT / "data" / "meta" / "frozen_sampling_imf_v1_s02.csv"

STRATUM = "imf_article_iv"
S02_FIELDS = ["id", "stratum", "year", "docdt", "repnb", "display_title",
              "txturl", "pdfurl"]
PROV_FILES = ["_manifest.csv", "_verification.csv", "_log.jsonl"]


def _rel(p: Path) -> str:
    """Path for display; falls back to absolute when p is outside ROOT (tests
    redirect these paths to a tmp directory)."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest() -> dict[str, dict]:
    """Last row per report number; the manifest is append-only."""
    out: dict[str, dict] = {}
    with (SRC_DIR / "_manifest.csv").open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            out[row["report_no"]] = row
    return out


def load_frozen() -> dict[str, dict]:
    with FROZEN.open(encoding="utf-8") as fh:
        return {r["id"]: r for r in csv.DictReader(fh)}


def plan(manifest: dict[str, dict], frozen: dict[str, dict]) -> list[tuple]:
    """(doc_id, source, destination, expected_sha256) for every retrieved file."""
    moves = []
    for report_no, row in sorted(manifest.items()):
        if row.get("status") != "ok":
            continue
        doc_id = "CR" + report_no.replace("/", "-")
        if doc_id not in frozen:
            raise RuntimeError(
                f"[land] {doc_id} is not in the frozen sample — the corpus must "
                "never carry a document outside it (permission condition 1)")
        year = frozen[doc_id]["year"]          # sample year, NOT the report year
        src = SRC_DIR / f"{doc_id}.pdf"
        if not src.exists():
            raise RuntimeError(f"[land] manifest says ok but {src.name} is missing")
        moves.append((doc_id, src, DEST_ROOT / year / f"{doc_id}.pdf",
                      row["sha256"]))
    return moves


def write_s02_csv(manifest: dict[str, dict], frozen: dict[str, dict]) -> int:
    rows = []
    for report_no, row in sorted(manifest.items()):
        doc_id = "CR" + report_no.replace("/", "-")
        f = frozen.get(doc_id)
        if f is None:
            continue
        rows.append({
            "id": doc_id,
            "stratum": STRATUM,
            "year": f["year"],
            "docdt": f.get("pub_date", ""),
            "repnb": report_no,
            "display_title": f.get("title", "")[:200],
            "txturl": "",                       # the IMF serves no plain-text copy
            "pdfurl": row.get("pdf_url", ""),   # the URL the retrieval resolved
        })
    S02_CSV.parent.mkdir(parents=True, exist_ok=True)
    with S02_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=S02_FIELDS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    manifest, frozen = load_manifest(), load_frozen()
    moves = plan(manifest, frozen)
    print(f"[land] {len(moves)} document(s) to place under "
          f"{_rel(DEST_ROOT)}/<year>/")
    if a.dry_run:
        for doc_id, src, dest, _ in moves[:3]:
            print(f"  {src.name} -> {_rel(dest)}")
        print("  ... (dry run, nothing moved)")
        return 0

    moved = 0
    for doc_id, src, dest, expected in moves:
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        got = sha256(dest)
        if got != expected:
            shutil.move(str(dest), str(src))     # put it back, then stop
            raise RuntimeError(
                f"[land] sha256 mismatch after moving {doc_id}: manifest "
                f"{expected[:16]}… but file {got[:16]}… — moved back, aborting")
        moved += 1

    PROV_DIR.mkdir(parents=True, exist_ok=True)
    for name in PROV_FILES:
        s = SRC_DIR / name
        if s.exists() and not (PROV_DIR / name).exists():
            shutil.copy2(s, PROV_DIR / name)

    n = write_s02_csv(manifest, frozen)
    print(f"[land] moved {moved}, verified {moved} by re-derived sha256")
    print(f"[land] provenance copied to {_rel(PROV_DIR)}/")
    print(f"[land] wrote {_rel(S02_CSV)} ({n} rows, s02 column shape)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
