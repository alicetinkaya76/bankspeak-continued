"""s03 — normalize raw downloads into data/text/. txt files: light clean.
pdf files: PyMuPDF extraction. Extraction method logged per doc (D9: era-correlated
extraction noise must be controllable downstream)."""
from __future__ import annotations
import argparse, csv, re, sys
from pathlib import Path
from utils import ROOT, load_config

def clean(text: str) -> str:
    text = re.sub(r"-\n(?=[a-z])", "", text)          # de-hyphenate linebreaks
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln for ln in text.splitlines()
             if not re.fullmatch(r"\s*(?:page\s*)?\d{1,4}\s*", ln, flags=re.I)]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    load_config(ap.parse_args().config)  # config read kept for path conventions/uniformity
    raw_root = ROOT / "data" / "raw"
    out_root = ROOT / "data" / "text"
    log_path = ROOT / "data" / "meta" / "extraction_log.csv"
    rows = []
    for src in sorted(raw_root.rglob("*.*")):
        if src.suffix not in {".txt", ".pdf"}:
            continue
        rel = src.relative_to(raw_root)
        out = (out_root / rel).with_suffix(".txt")
        if out.exists():
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".txt":
            text, method = src.read_text(encoding="utf-8", errors="replace"), "server_txt"
        else:
            try:
                import fitz  # PyMuPDF
            except ImportError:
                sys.exit("[s03] PyMuPDF missing: pip install -r requirements.txt")
            with fitz.open(src) as doc:
                text = "\n".join(page.get_text() for page in doc)
            method = "pymupdf"
        out.write_text(clean(text), encoding="utf-8")
        rows.append({"id": src.stem, "path": rel.as_posix(), "method": method})
        print(f"[s03] {rel} [{method}]")
    header_needed = not log_path.exists()
    with open(log_path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "path", "method"])
        if header_needed:
            w.writeheader()
        w.writerows(rows)
    print(f"[s03] extracted {len(rows)} new docs; log at {log_path}")

if __name__ == "__main__":
    main()
