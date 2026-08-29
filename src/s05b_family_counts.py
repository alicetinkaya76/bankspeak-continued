"""Exact integer Tier-1 outputs per document (round-4 precondition 4):
tier1_count, 13 per-family counts, eligible_tokens, eligibility flags.
Reads data/text/ via extraction_log paths; frozen-sample rows only.
-> data/features/family_counts.csv (the go-forward outcome source; s05's
rounded rates stay untouched for legacy artifacts)."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from families import count_families, load_families

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-root", default="data/text")
    ap.add_argument("--meta-dir", default="data/meta")
    ap.add_argument("--out", default="data/features/family_counts.csv")
    # Stage-B (2026-08-26): the frozen-sample index was hardcoded to v1, the
    # SEALED Stage-A sample. Left that way it silently drops every IMF document
    # and most of the Stage-B redraw from the family counts — the same class of
    # error that stopped the refetch stage. The default is unchanged, so a
    # Stage-A rerun reproduces byte-for-byte; the Stage-B driver passes 2.
    ap.add_argument("--sampling-version", default="1",
                    help="index to filter on: frozen_sampling_v<N>.csv")
    args = ap.parse_args()
    fams = load_families()
    print(f"[s05b] families.yaml sha256={fams['_sha256']}")
    meta = Path(args.meta_dir)
    log = pd.read_csv(meta / "extraction_log.csv")
    frozen_path = meta / f"frozen_sampling_v{args.sampling_version}.csv"
    print(f"[s05b] index: {frozen_path.name}")
    frozen = pd.read_csv(frozen_path)
    idcol = "id" if "id" in frozen.columns else frozen.columns[0]
    log = log[log["id"].isin(set(frozen[idcol]))]
    rows, missing = [], 0
    for _, r in log.iterrows():
        p = Path(args.text_root) / r["path"]
        p = p.with_suffix(".txt") if p.suffix != ".txt" else p
        if not p.exists():
            missing += 1
            continue
        rec = count_families(p.read_text(encoding="utf-8", errors="ignore"))
        parts = str(r["path"]).split("/")
        rec.update({"id": r["id"], "stratum": parts[0], "year": int(parts[1]),
                    "method": r.get("method", "")})
        rec["analysis_eligible"] = rec["eligible_tokens"] > 0
        rec["nll_eligible"] = rec["eligible_tokens"] >= 100
        rows.append(rec)
    df = pd.DataFrame(rows)
    lead = ["id", "stratum", "year", "method", "eligible_tokens",
            "tier1_count", "analysis_eligible", "nll_eligible"]
    df = df[lead + [c for c in df.columns if c not in lead]]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    print(f"[s05b] wrote {args.out}: {len(df)} docs "
          f"(missing_text={missing}, zero_token={int((df.eligible_tokens==0).sum())}, "
          f"tier1_total={int(df.tier1_count.sum())})")

if __name__ == "__main__":
    main()
