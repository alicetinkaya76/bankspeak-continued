"""B7 [BUILD]: branch-specific cells template for mde_sim --cells-template.

Builds a year,docs,tokens CSV from a frame (s09a/s09b output): per-year
document counts x a tokens-per-document projection. For the P0 branch the
frozen projection is the pooled WB ICR+PAD mean tokens/doc (PREREG v0.5 SS8),
supplied either directly (--tokens-per-doc) or derived from a features CSV
with a 'tokens' column (--icr-pad-features)."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd


def build_template(frame: pd.DataFrame, tokens_per_doc: float) -> pd.DataFrame:
    if tokens_per_doc <= 0:
        raise ValueError("tokens_per_doc must be > 0")
    t = (frame.groupby("year").size().rename("docs").reset_index()
         .sort_values("year").reset_index(drop=True))
    t["tokens"] = t["docs"] * float(tokens_per_doc)
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frame", required=True)
    ap.add_argument("--out", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--tokens-per-doc", type=float)
    g.add_argument("--icr-pad-features",
                   help="CSV with a 'tokens' column; the pooled mean is used")
    a = ap.parse_args()
    tpd = (a.tokens_per_doc if a.tokens_per_doc
           else float(pd.read_csv(a.icr_pad_features)["tokens"].mean()))
    t = build_template(pd.read_csv(a.frame), tpd)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(a.out, index=False)
    print(f"[template] {len(t)} years -> {a.out} (tokens/doc = {tpd:.1f})")


if __name__ == "__main__":
    main()
