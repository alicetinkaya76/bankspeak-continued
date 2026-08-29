#!/usr/bin/env python3
"""Re-fetch the documents whose World Bank server-side text lost word spacing.

## The diagnosis, which inverted on measurement

70 extracted documents carry words glued together — `PROJECTAPPRAISALDOCUMENT`,
`FOROFFICIALUSEONLY` — with mean token length up to 10.9 against a corpus median
of 5.56, and up to 17.3% of tokens at 18+ letters. Whole-word matching, which is
how marker families are counted, misses 40-78% of its hits in them.

The first assumption was that our PDF extraction was at fault. It is not:

    pymupdf     0 of 437 affected   (0.0%)
    server_txt  70 of 2,688         (2.6%)

Every affected document came through `txturl`. The defect is in the World Bank's
own plain-text copies, and our PDF path is clean.

That is an awkward result for D9, which chose `txturl`-first precisely to avoid
extraction noise, on the grounds that such noise "is itself era-correlated (older
PDFs are scans), which would otherwise bias features". The server text carries
its own era-correlated defect — concentrated in 2003-2009, absent from 2010 on,
and 65 of the 70 in `pad`, i.e. the P2 confirmatory panel. D9's premise holds for
scans and fails for spacing.

## The remedy, and why it is clean

D9 already specifies the fallback: `pdfurl` + PyMuPDF. All 70 affected documents
carry a `pdfurl` in the frozen sample, and the PyMuPDF path shows a 0.0% defect
rate. So the fix is to take D9's own second branch for exactly these documents,
which changes no rule and needs no new one.

Re-extraction must be VERIFIED, not assumed: this writes nothing over the
existing text until the re-extracted version measures better on the same
statistic that condemned it.

## Gate

Re-fetching is text download, which PREREG §11.3 places after the SAP freeze, so
this refuses without `--i-have-frozen-the-sap`. `--list` is read-only and always
allowed.
"""
from __future__ import annotations

import argparse
import csv
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT = ROOT / "data" / "text"
RAW = ROOT / "data" / "raw"
# The ANALYSIS index, not the sealed Stage-A one. Two things follow from using
# v2 (2026-08-26): the Stage-B redraw's documents are found at all — 49 of them
# were invisible when this read v1, which is what stopped the first post-SAP run
# — and stray text files left behind by the redraw (55 of them, still on disk
# but no longer sampled) are correctly ignored rather than reported as
# unfixable. A remedy is owed only to documents the analysis will actually read.
FROZEN = ROOT / "data" / "meta" / "frozen_sampling_v2.csv"
LOG = ROOT / "data" / "meta" / "refetch_log.csv"
UA = "bankspeak-continued/0.1 (research; contact: kapsul.yonetim@gmail.com)"

LONG_TOKEN = 18
LONG_SHARE = 0.01          # >1% of tokens at 18+ letters is not normal prose
SIGMA = 3                  # mean token length above median + 3 sd


def spacing_stats(text: str) -> tuple[int, float, float]:
    toks = re.findall(r"[A-Za-z']+", text)
    if not toks:
        return 0, 0.0, 0.0
    return (len(toks), sum(map(len, toks)) / len(toks),
            sum(1 for t in toks if len(t) >= LONG_TOKEN) / len(toks))


def corpus_band(text_root: Path = TEXT) -> tuple[float, float]:
    """The healthy range for mean token length, derived from the corpus itself.

    A re-extraction must LAND here, not merely move downward. Measured
    2026-08-26: accepting on direction alone replaced annual_report/2007/8514626
    with mojibake, because garbage tokens are SHORT — mean length fell 6.07 to
    3.05 and the long-token share to zero, so both one-sided tests passed while
    the text became unreadable. Ten standard deviations below the median is not
    an improvement; it is a different failure.
    """
    lens = []
    for p in text_root.rglob("*.txt"):
        n, mean_len, _ = spacing_stats(p.read_text(encoding="utf-8", errors="replace"))
        if n >= 200:
            lens.append(mean_len)
    med = statistics.median(lens)
    sd = statistics.pstdev(lens)
    return med - SIGMA * sd, med + SIGMA * sd


def find_defective(text_root: Path = TEXT,
                   index: set[str] | None = None) -> list[dict]:
    """Documents whose spacing statistics put them outside the corpus norm.

    ``index`` restricts the result to the analysis corpus. The norm itself is
    computed over EVERY extracted document, so a corpus that grows or shrinks
    does not move the threshold under the documents being judged.
    """
    rows = []
    for p in sorted(text_root.rglob("*.txt")):
        n, mean_len, long_share = spacing_stats(
            p.read_text(encoding="utf-8", errors="replace"))
        if n < 200:
            continue
        rows.append({"id": p.stem, "path": p.relative_to(text_root).as_posix(),
                     "tokens": n, "mean_token_len": round(mean_len, 3),
                     "long_share": round(long_share, 4)})
    if not rows:
        return []
    med = statistics.median(r["mean_token_len"] for r in rows)
    sd = statistics.pstdev(r["mean_token_len"] for r in rows)
    bad = [r for r in rows
           if r["mean_token_len"] > med + SIGMA * sd or r["long_share"] > LONG_SHARE]
    if index is not None:
        bad = [r for r in bad if r["id"] in index]
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="read-only; always allowed")
    ap.add_argument("--i-have-frozen-the-sap", action="store_true")
    ap.add_argument("--text-root", default=str(TEXT))
    a = ap.parse_args(argv)

    frozen = {r["id"]: r for r in csv.DictReader(FROZEN.open(encoding="utf-8"))} \
        if FROZEN.exists() else {}
    bad = find_defective(Path(a.text_root), index=set(frozen) or None)
    with_pdf = [r for r in bad if frozen.get(r["id"], {}).get("pdfurl")]

    print(f"[refetch] {len(bad)} document(s) with lost word spacing in the "
          f"analysis corpus; {len(with_pdf)} carry a pdfurl")
    if a.list or not bad:
        for r in sorted(bad, key=lambda r: -r["mean_token_len"])[:10]:
            print(f"  mean_len {r['mean_token_len']:5.2f}  long {r['long_share']:.3f}"
                  f"  {r['path']}")
        return 0

    if not a.i_have_frozen_the_sap:
        sys.exit("[refetch] REFUSING: re-fetching is text download, which PREREG "
                 "§11.3 places after the SAP freeze. Use --list to inspect.")
    if len(with_pdf) != len(bad):
        sys.exit(f"[refetch] {len(bad) - len(with_pdf)} document(s) have no "
                 "pdfurl; refusing a partial pass rather than silently skipping")

    import fitz
    band_lo, band_hi = corpus_band(Path(a.text_root))
    print(f"[refetch] healthy band for mean token length: "
          f"{band_lo:.2f}–{band_hi:.2f} (derived from the corpus)")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG.exists()
    kept = 0
    with LOG.open("a", newline="", encoding="utf-8") as lf:
        w = csv.writer(lf)
        if new:
            w.writerow(["id", "path", "old_mean_len", "new_mean_len",
                        "old_long_share", "new_long_share", "accepted"])
        for r in with_pdf:
            url = frozen[r["id"]]["pdfurl"]
            dest = RAW / Path(r["path"]).with_suffix(".pdf")
            dest.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(["curl", "-sSL", "-A", UA, "--max-time", "120",
                            "-o", str(dest), url], check=False)
            try:
                with fitz.open(dest) as doc:
                    text = "\n".join(p.get_text() for p in doc)
            except Exception:
                w.writerow([r["id"], r["path"], r["mean_token_len"], "",
                            r["long_share"], "", "unreadable_pdf"])
                continue
            _, mean_len, long_share = spacing_stats(text)
            # Verified, not assumed — and two-sided. The re-extraction must both
            # improve on the statistic that condemned the original AND land
            # inside the corpus's own healthy band; see corpus_band().
            ok = (mean_len < r["mean_token_len"] and long_share < r["long_share"]
                  and band_lo <= mean_len <= band_hi)
            if ok:
                sys.path.insert(0, str(ROOT / "src"))
                from s03_extract_text import clean
                (Path(a.text_root) / r["path"]).write_text(clean(text),
                                                           encoding="utf-8")
                kept += 1
            w.writerow([r["id"], r["path"], r["mean_token_len"], round(mean_len, 3),
                        r["long_share"], round(long_share, 4),
                        "replaced" if ok else ("kept_original_outside_band"
                        if mean_len < r["mean_token_len"]
                        else "kept_original_no_improvement")])
            print(f"  {r['id']}: {r['mean_token_len']:.2f} -> {mean_len:.2f} "
                  f"{'REPLACED' if ok else 'kept original'}")
    print(f"[refetch] replaced {kept} of {len(with_pdf)}; log at {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
