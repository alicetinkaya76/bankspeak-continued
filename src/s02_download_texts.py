"""s02 — download sampled documents. txturl preferred, pdfurl fallback (D9) — also
on txturl *failure*, not only absence; --no-pdf-fallback gives txt-only passes so
transient txt 403s don't permanently convert docs to PDF extraction. One
inaccessible document must not kill the run: failures are logged to
data/meta/download_failures.csv and skipped. Content is integrity-checked BEFORE
manifest_append. Resumable; append-only SHA256 manifest (D10); polite rate limiting."""
from __future__ import annotations
import argparse, csv, sys, time
from pathlib import Path
import requests
from utils import (ROOT, load_config, session_for, get_with_retry,
                   sha256_file, manifest_ids, manifest_append)

FAILLOG = ROOT / "data" / "meta" / "download_failures.csv"

def content_problem(content: bytes, ext: str) -> str | None:
    """Integrity gate BEFORE manifest_append (append-only manifest must never
    record a corrupt download — pilot lesson, deviation 2026-08-06)."""
    if ext == "txt":
        return None if content.strip() else "empty txt body"
    try:
        import fitz  # PyMuPDF
        with fitz.open(stream=content, filetype="pdf") as doc:
            if doc.page_count < 1:
                return "pdf has 0 pages"
    except Exception as e:  # fitz raises library-specific errors; any -> corrupt
        return f"corrupt pdf: {e}"
    return None

def log_failure(row: dict, error: str) -> None:
    header_needed = not FAILLOG.exists()
    with open(FAILLOG, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "stratum", "year", "txturl",
                                          "pdfurl", "error", "date"])
        if header_needed:
            w.writeheader()
        w.writerow({"id": row["id"], "stratum": row["stratum"], "year": row["year"],
                    "txturl": row["txturl"], "pdfurl": row["pdfurl"],
                    "error": error, "date": time.strftime("%Y-%m-%d")})

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    ap.add_argument("--no-pdf-fallback", action="store_true",
                    help="txt-only pass: skip pdfurl candidates. Run early passes "
                         "with this flag and only the final pass(es) without it, so "
                         "transient txt-endpoint 403s do not permanently convert "
                         "documents to PDF extraction (D9 refinement).")
    args = ap.parse_args()
    cfg = load_config(args.config)
    frozen = ROOT / "data" / "meta" / f"frozen_sampling_v{cfg['sampling_version']}.csv"
    if not frozen.exists():
        sys.exit(f"[s02] {frozen} not found — run s01 first.")
    sess = session_for(cfg)
    done = manifest_ids()
    with open(frozen, newline="", encoding="utf-8") as f:
        rows = sorted(csv.DictReader(f), key=lambda r: (r["stratum"], r["year"], r["id"]))
    n_ok = n_fail = 0
    for r in rows:
        doc_id = r["id"]
        if doc_id in done:
            continue
        pairs = ((r["txturl"], "txt"),) if args.no_pdf_fallback else \
                ((r["txturl"], "txt"), (r["pdfurl"], "pdf"))
        candidates = [(u, e) for u, e in pairs if u]
        if not candidates:
            log_failure(r, "no txturl/pdfurl")
            print(f"[s02] {doc_id}: no txturl/pdfurl — skipped (logged)", file=sys.stderr)
            continue
        last_err = ""
        for url, ext in candidates:
            try:
                resp = get_with_retry(sess, url, {}, cfg)
            except (RuntimeError, requests.RequestException) as e:
                last_err = str(e)
                continue
            problem = content_problem(resp.content, ext)
            if problem:
                last_err = f"{problem}: {url}"
                continue
            out = ROOT / "data" / "raw" / r["stratum"] / r["year"] / f"{doc_id}.{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(resp.content)
            digest = sha256_file(out)
            manifest_append(doc_id, url, out.relative_to(ROOT), digest)
            print(f"[s02] {doc_id} -> {out.name} ({len(resp.content)//1024} KB, {ext})")
            n_ok += 1
            break
        else:
            log_failure(r, last_err)
            n_fail += 1
            print(f"[s02] {doc_id}: all URLs failed — skipped (logged): {last_err}",
                  file=sys.stderr)
    print(f"[s02] done: {n_ok} downloaded, {n_fail} failed "
          f"(failures logged to {FAILLOG.name}; resumable — rerun to fill gaps).")

if __name__ == "__main__":
    main()
