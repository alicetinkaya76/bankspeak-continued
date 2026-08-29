"""Round-4 parallel item: backfill provenance columns into the WB extraction log
NON-destructively -> data/meta/extraction_log_v2.csv.
Columns added: sampling_version (v1 | v0_pilot_only), run_id, analysis_eligible
(sampled in v1 AND featured AND tokens>0), tokens, nll_eligible (tokens>=100),
branch_panel (blank for legacy WB)."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meta-dir", default="data/meta")
    ap.add_argument("--features", default="data/features/classic.csv")
    ap.add_argument("--run-id", default="wb-v1-2026-08")
    args = ap.parse_args()
    meta = Path(args.meta_dir)
    log = pd.read_csv(meta / "extraction_log.csv")
    frozen = pd.read_csv(meta / "frozen_sampling_v1.csv")
    idcol = "id" if "id" in frozen.columns else frozen.columns[0]
    v1 = set(frozen[idcol])
    cl = pd.read_csv(args.features)[["id", "tokens"]]
    out = log.merge(cl, on="id", how="left")
    out["sampling_version"] = out["id"].map(lambda i: "v1" if i in v1 else "v0_pilot_only")
    out["run_id"] = args.run_id
    out["analysis_eligible"] = ((out["sampling_version"] == "v1")
                                & out["tokens"].notna() & (out["tokens"] > 0))
    out["nll_eligible"] = out["tokens"].fillna(0) >= 100
    out["branch_panel"] = ""
    dest = meta / "extraction_log_v2.csv"
    out.to_csv(dest, index=False)
    n = out["sampling_version"].value_counts().to_dict()
    print(f"[provenance] wrote {dest}: {len(out)} rows, {n}, "
          f"analysis_eligible={int(out['analysis_eligible'].sum())}, "
          f"nll_eligible={int(out['nll_eligible'].sum())}")

if __name__ == "__main__":
    main()
