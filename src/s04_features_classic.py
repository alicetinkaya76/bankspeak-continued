"""s04 — classic Bankspeak feature set per document (D4).
Internal replication rule: before any 2013+ claim, the 1946-2012 Annual Report series
from this script must qualitatively reproduce Moretti-Pestre's published trajectories."""
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
from utils import ROOT, load_config
from textstats import compute_classic

def doc_index(cfg) -> dict[str, dict]:
    frozen = ROOT / "data" / "meta" / f"frozen_sampling_v{cfg['sampling_version']}.csv"
    if not frozen.exists():
        sys.exit(f"[s04] {frozen} not found — run s01/s02/s03 first.")
    with open(frozen, newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    idx = doc_index(cfg)
    out = ROOT / "data" / "features" / "classic.csv"
    rows = []
    for txt in sorted((ROOT / "data" / "text").rglob("*.txt")):
        meta = idx.get(txt.stem)
        if meta is None:
            continue
        feats = compute_classic(txt.read_text(encoding="utf-8"),
                                cfg["markers"]["mgmt_lexicon"])
        rows.append({"id": txt.stem, "stratum": meta["stratum"],
                     "year": meta["year"], **feats})
    rows.sort(key=lambda r: (r["stratum"], r["year"], r["id"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["id", "stratum", "year"])
        w.writeheader(); w.writerows(rows)
    print(f"[s04] wrote {out} ({len(rows)} docs)")

if __name__ == "__main__":
    main()
