"""Deterministic frame -> frozen sample with per-cell seeds + provenance schema
(PREREG v0.3 App. B.7-B.8; round-4 precondition 3). Works for IMF Article IV,
the P0 candidate probes, and any future WB stratum.

Input : a metadata CSV with at least [institution, genre, year, id]; extra
        columns pass through untouched.
Output: a WRITE-ONCE frozen sampling CSV with the provenance columns
        sampling_version, run_id, branch_panel, analysis_eligible (blank until
        download/extraction), sampled_at.
"""
from __future__ import annotations
import argparse, datetime, sys
from pathlib import Path
import pandas as pd
from percell_seed import cell_rng

REQUIRED = ["institution", "genre", "year", "id"]

def sample_frame(meta: pd.DataFrame, cap: int) -> pd.DataFrame:
    for c in REQUIRED:
        if c not in meta.columns:
            raise ValueError(f"metadata missing column {c!r}")
    if meta["id"].duplicated().any():
        raise ValueError("duplicate ids in metadata frame")
    keep = []
    for (inst, genre, year), grp in meta.groupby(["institution", "genre", "year"],
                                                 sort=True):
        ids = sorted(grp["id"].astype(str))
        if len(ids) > cap:
            ids = sorted(cell_rng(str(inst), str(genre), int(year)).sample(ids, cap))
        keep.append(grp[grp["id"].astype(str).isin(ids)])
    return pd.concat(keep, ignore_index=True).sort_values(
        ["institution", "genre", "year", "id"]).reset_index(drop=True)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cap", type=int, default=40)
    ap.add_argument("--sampling-version", required=True, help="e.g. imf_v1")
    ap.add_argument("--run-id", required=True, help="e.g. stageB-2026-09")
    ap.add_argument("--branch-panel", default="", help="e.g. P1 / P2 / P0")
    args = ap.parse_args()
    out = Path(args.out)
    if out.exists():
        sys.exit(f"[s09] REFUSING to overwrite frozen sample {out} (write-once)")
    meta = pd.read_csv(args.metadata)
    smp = sample_frame(meta, args.cap)
    smp["sampling_version"] = args.sampling_version
    smp["run_id"] = args.run_id
    smp["branch_panel"] = args.branch_panel
    smp["analysis_eligible"] = ""     # filled after download/extraction
    smp["sampled_at"] = datetime.date.today().isoformat()
    out.parent.mkdir(parents=True, exist_ok=True)
    smp.to_csv(out, index=False)
    print(f"[s09] wrote {out}: {len(smp)} rows from {len(meta)} candidates "
          f"({meta.groupby(['institution','genre'])['year'].nunique().to_dict()} cell-years)")

if __name__ == "__main__":
    main()
