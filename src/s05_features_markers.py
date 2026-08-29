"""s05 — Tier-1 / Tier-2 lexical marker rates per document (D5).
Tier split separates 'more Bankspeak' (T2) from candidate LLM fingerprint (T1)."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
from utils import ROOT, load_config
from textstats import compute_markers
from s04_features_classic import doc_index

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    idx = doc_index(cfg)
    rows = []
    for txt in sorted((ROOT / "data" / "text").rglob("*.txt")):
        meta = idx.get(txt.stem)
        if meta is None:
            continue
        feats = compute_markers(txt.read_text(encoding="utf-8"),
                                cfg["markers"]["tier1"], cfg["markers"]["tier2"])
        rows.append({"id": txt.stem, "stratum": meta["stratum"],
                     "year": meta["year"], **feats})
    rows.sort(key=lambda r: (r["stratum"], r["year"], r["id"]))
    out = ROOT / "data" / "features" / "markers.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["id", "stratum", "year"])
        w.writeheader(); w.writerows(rows)
    print(f"[s05] wrote {out} ({len(rows)} docs)")

if __name__ == "__main__":
    main()
