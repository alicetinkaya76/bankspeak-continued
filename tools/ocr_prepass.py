#!/usr/bin/env python3
"""OCR pre-pass for the scanned era of the IMF corpus — and the calibration that
keeps it from silently manufacturing a result.

## The problem this exists for

D9 already names the danger: "extraction noise is itself era-correlated (older
PDFs are scans), which would otherwise bias features. Fallback extraction is
logged per document so era x extraction-method can be controlled."

In the IMF Article IV corpus that mitigation is **not sufficient**, and the
reason is worth stating precisely. Measured 2026-08-20: 194 of 1,064 documents
carry no text layer, and they are **1999-2004 without exception** — 1999-2003
entirely, 2004 partially, essentially none after. The study's contrast is
pre-2023 against post-2023. So extraction method is not merely correlated with
era, it is **perfectly nested inside the pre-period**: every OCR'd document is a
pre document, and no post document is OCR'd.

A variable collinear with the thing being estimated cannot be controlled for.
Logging the method, as D9 prescribes, records the confound but cannot remove it.
If OCR text differs systematically from native extraction — and it does: character
substitutions, broken hyphenation, mangled tables, lost ligatures — that
difference will appear in every feature as a pre-versus-post shift that has
nothing to do with language.

## What breaks the collinearity

Only one thing: OCR documents that **also** have a native text layer, and measure
the method effect on the same document. That is `--calibrate`. It yields a
per-feature OCR-versus-native delta estimated where era is held fixed, which can
then be subtracted, carried as a sensitivity, or reported as the bound on what
the scanned era can support. Without it the 1999-2004 block should not enter any
comparison at all.

## Modes

  --scan       read-only. Classify every PDF under data/raw as native-text or
               scan, per year, and write the inventory. Computes no features and
               extracts no text; safe before the SAP freeze.
  --calibrate  OCR N documents that HAVE a text layer and report extraction-
               fidelity deltas (token counts, hyphenation, character classes)
               native versus OCR on the same pages. Does NOT compute any study
               outcome.
  --run        OCR the text-layer-less documents and write cleaned text to
               data/text/<same relative path>.txt, which is where s03 would have
               put it — s03 skips outputs that already exist, so this leaves the
               native-text documents to s03 untouched. Logs method
               `ocr_tesseract` per document for the D9 log.

`--calibrate` and `--run` are feature-stage acts and stay unrun until the SAP is
frozen (`docs/DEVIATION_20260820_stageb_retrieval.md` D1).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
TEXT = ROOT / "data" / "text"
META = ROOT / "data" / "meta"

TEXT_LAYER_MIN_CHARS = 100      # per probed page; below this the page is an image
PROBE_PAGES = 5
OCR_DPI = 300
OCR_LANG = "eng"


def _rel(p: Path) -> str:
    """Path for display; falls back to absolute when p is outside ROOT (tests
    redirect these paths to a tmp directory)."""
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def has_text_layer(path: Path) -> tuple[bool, int, int]:
    """(native_text, chars_found, page_count) from the first PROBE_PAGES pages."""
    import fitz
    try:
        with fitz.open(path) as doc:
            n = doc.page_count
            probe = min(PROBE_PAGES, n)
            chars = sum(len(re.sub(r"\s", "", doc.load_page(i).get_text()))
                        for i in range(probe))
    except Exception:
        return False, 0, 0
    return chars >= TEXT_LAYER_MIN_CHARS * max(1, probe), chars, n


def ocr_pdf(path: Path, dpi: int = OCR_DPI, lang: str = OCR_LANG) -> str:
    """Rasterise with PyMuPDF, recognise with tesseract, one page at a time."""
    import fitz
    out = []
    with tempfile.TemporaryDirectory() as td:
        with fitz.open(path) as doc:
            for i in range(doc.page_count):
                png = Path(td) / f"p{i:04d}.png"
                pix = doc.load_page(i).get_pixmap(dpi=dpi)
                pix.save(str(png))
                r = subprocess.run(
                    ["tesseract", str(png), "stdout", "-l", lang, "--psm", "1"],
                    capture_output=True, text=True)
                out.append(r.stdout)
    return "\n".join(out)


def fidelity(text: str) -> dict:
    """Extraction-fidelity descriptors only. Deliberately NOT study features:
    calibration must not compute an outcome."""
    toks = re.findall(r"[A-Za-z]+", text)
    return {
        "chars": len(text),
        "tokens": len(toks),
        "mean_token_len": round(sum(map(len, toks)) / max(1, len(toks)), 3),
        "hyphen_breaks": len(re.findall(r"-\n", text)),
        "nonascii_frac": round(sum(c > "\x7f" for c in text) / max(1, len(text)), 5),
        "single_char_tokens": sum(1 for t in toks if len(t) == 1),
    }


def iter_pdfs():
    return sorted(p for p in RAW.rglob("*.pdf"))


def cmd_scan(args) -> int:
    rows = []
    for p in iter_pdfs():
        native, chars, pages = has_text_layer(p)
        rel = p.relative_to(RAW)
        rows.append({"path": rel.as_posix(), "id": p.stem,
                     "stratum": rel.parts[0],
                     "year": rel.parts[1] if len(rel.parts) > 2 else "",
                     "native_text": native, "probe_chars": chars, "pages": pages})
    # Ruling D-9: documents whose text layer EXISTS but is garbled (broken
    # ToUnicode CMap) must stay on the OCR path. A plain rescan would classify
    # them native again and silently undo the ruling, so the override ledger is
    # applied after every scan.
    ovr_path = META / "ocr_overrides.csv"
    if ovr_path.exists():
        ovr = {r["id"]: r for r in csv.DictReader(ovr_path.open(encoding="utf-8"))}
        n_ovr = 0
        for row in rows:
            o = ovr.get(row["id"])
            if o is not None and row["native_text"] != (o["native_text"] == "True"):
                row["native_text"] = o["native_text"] == "True"
                n_ovr += 1
        if n_ovr:
            print(f"[ocr] {n_ovr} override(s) applied from {ovr_path.name} (ruling D-9)")

    out = META / "ocr_inventory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    scans = [r for r in rows if not r["native_text"]]
    by_year: dict[str, list[int]] = {}
    for r in rows:
        by_year.setdefault(r["year"], [0, 0])
        by_year[r["year"]][0 if r["native_text"] else 1] += 1
    print(f"[ocr] {len(rows)} PDF(s); {len(scans)} without a text layer "
          f"({100*len(scans)/max(1,len(rows)):.1f}%), "
          f"{sum(r['pages'] for r in scans):,} pages to OCR")
    print(f"[ocr] years containing scans: "
          f"{sorted(y for y,(n,s) in by_year.items() if s)}")
    post = [r for r in scans if r["year"] and int(r["year"]) >= 2023]
    print(f"[ocr] scans in the POST period (>=2023): {len(post)}")
    if not post and scans:
        print("[ocr] COLLINEAR: every scan is a pre-period document. Extraction "
              "method cannot be controlled for against era; --calibrate is the "
              "only way to estimate the method effect.")
    print(f"[ocr] wrote {_rel(out)}")
    return 0


def cmd_calibrate(args) -> int:
    inv = list(csv.DictReader((META / "ocr_inventory.csv").open(encoding="utf-8")))
    native = [r for r in inv if r["native_text"] == "True"]
    picked = native[:: max(1, len(native) // args.n)][: args.n]
    import fitz
    rows = []
    for r in picked:
        p = RAW / r["path"]
        # Like with like: the native text must cover the SAME pages the OCR
        # covers. Measured 2026-08-27, taking native from the first PROBE_PAGES
        # while OCR'ing the whole document made every COUNT metric a page-count
        # ratio rather than a method effect — chars 21x, tokens 25x, hyphen
        # breaks 80x. Only the scale-free ratios were interpretable. Both sides
        # now read the whole document.
        with fitz.open(p) as doc:
            nat = "\n".join(pg.get_text() for pg in doc)
        ocr = ocr_pdf(p)
        fn, fo = fidelity(nat), fidelity(ocr)
        rows.append({"id": r["id"], "year": r["year"], "pages": r["pages"],
                     **{f"native_{k}": v for k, v in fn.items()},
                     **{f"ocr_{k}": v for k, v in fo.items()},
                     # per-1k-token rates: the method effect a count cannot show
                     "native_hyphen_per1k": round(
                         1000 * fn["hyphen_breaks"] / max(1, fn["tokens"]), 3),
                     "ocr_hyphen_per1k": round(
                         1000 * fo["hyphen_breaks"] / max(1, fo["tokens"]), 3),
                     "native_single_char_per1k": round(
                         1000 * fn["single_char_tokens"] / max(1, fn["tokens"]), 3),
                     "ocr_single_char_per1k": round(
                         1000 * fo["single_char_tokens"] / max(1, fo["tokens"]), 3),
                     "token_recovery_ratio": round(
                         fo["tokens"] / max(1, fn["tokens"]), 4)})
        print(f"[ocr] calibrated {r['id']}")
    out = META / "ocr_calibration.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"[ocr] wrote {_rel(out)} ({len(rows)} documents)")
    return 0


def cmd_run(args) -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from s03_extract_text import clean            # the frozen cleaner, reused

    inv = list(csv.DictReader((META / "ocr_inventory.csv").open(encoding="utf-8")))
    todo = [r for r in inv if r["native_text"] != "True"]
    log = META / "ocr_log.csv"
    # D9 requires the extraction method logged PER DOCUMENT so that
    # era x method can be controlled downstream. Writing only to ocr_log.csv
    # satisfied the letter and not the function: s05b_family_counts — which
    # produces the CONFIRMATORY outcome — iterates extraction_log.csv, so 192
    # OCR'd documents (the whole 1999-2004 IMF block) were silently absent from
    # the Tier-1 counts while present in classic.csv and markers.csv, which walk
    # data/text directly. A log nothing downstream reads is not a control.
    ext_log = META / "extraction_log.csv"
    done = 0
    with log.open("a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if log.stat().st_size == 0:
            w.writerow(["id", "path", "method", "pages", "chars", "utc"])
        for r in todo:
            src = RAW / r["path"]
            dest = (TEXT / r["path"]).with_suffix(".txt")
            if dest.exists():
                continue
            text = clean(ocr_pdf(src))
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8")
            w.writerow([r["id"], r["path"], "ocr_tesseract", r["pages"],
                        len(text), args.utc])
            with ext_log.open("a", newline="", encoding="utf-8") as ef:
                csv.writer(ef).writerow([r["id"], r["path"], "ocr_tesseract"])
            done += 1
            print(f"[ocr] {r['path']} -> {len(text):,} chars")
    print(f"[ocr] OCR'd {done} document(s); s03 will skip these outputs")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--scan", action="store_true")
    g.add_argument("--calibrate", action="store_true")
    g.add_argument("--run", action="store_true")
    ap.add_argument("-n", type=int, default=20, help="--calibrate: documents to OCR")
    ap.add_argument("--utc", default="", help="--run: timestamp for the log")
    ap.add_argument("--i-have-frozen-the-sap", action="store_true",
                    help="required by --calibrate and --run: PREREG §11.3 places "
                         "feature processing after the SAP freeze")
    a = ap.parse_args(argv)

    if a.scan:
        return cmd_scan(a)
    if not a.i_have_frozen_the_sap:
        sys.exit("[ocr] REFUSING: --calibrate and --run are feature-stage acts. "
                 "PREREG §11.3 places them after the SAP freeze "
                 "(see docs/DEVIATION_20260820_stageb_retrieval.md D1).")
    if not shutil.which("tesseract"):
        sys.exit("[ocr] tesseract not found on PATH")
    return cmd_calibrate(a) if a.calibrate else cmd_run(a)


if __name__ == "__main__":
    sys.exit(main())
