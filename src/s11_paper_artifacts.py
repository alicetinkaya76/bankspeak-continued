"""s11 — regenerate every paper-facing table and figure from data/ (no hand numbers).
North star: any number that appears in the manuscript must be reproducible by
rerunning this script. Outputs -> data/analysis/paper/.

Tables (CSV + one consolidated markdown):
  T1 corpus composition & coverage per stratum
  T2 ITS at 2023: doc-level strata (from s08 output) + assembled AR series (recomputed)
  T3 power summary (from s07 output) + assembled-AR token gate
Figures (PNG, 150 dpi):
  F1 assembled AR series 1947-2024: six classic features (pamphlet continuation)
  F2 tier1/tier2 per stratum, yearly doc-level means + assembled AR series
Vocabulary discipline: descriptive only ('discontinuity', 'consistent with')."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import pandas as pd
from utils import ROOT, load_config
from s08_its_analysis import fit_its, yearly_series

OUT = ROOT / "data" / "analysis" / "paper"

def t1_corpus(cfg) -> pd.DataFrame:
    frozen = pd.read_csv(ROOT / "data" / "meta" /
                         f"frozen_sampling_v{cfg['sampling_version']}.csv",
                         dtype={"id": str})
    man_ids = {l.split("\t", 1)[0] for l in
               (ROOT / "data" / "meta" / "manifest.tsv").read_text().splitlines() if l}
    classic = pd.read_csv(ROOT / "data" / "features" / "classic.csv", dtype={"id": str})
    toks = classic.groupby("stratum")["tokens"].sum()
    rows = []
    for st, sub in frozen.groupby("stratum"):
        got = sub["id"].isin(man_ids).sum()
        rows.append({"stratum": st, "sampled": len(sub), "downloaded": int(got),
                     "coverage_pct": round(100 * got / len(sub), 1),
                     "residue": int(len(sub) - got),
                     "year_min": int(sub["year"].min()),
                     "year_max": int(sub["year"].max()),
                     "tokens_total": int(toks.get(st, 0))})
    return pd.DataFrame(rows).sort_values("stratum")

def assembled_ar() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "features" / "ar_fy_features.csv")
    df["year"] = df["year"].astype(int)
    df["stratum"] = "annual_report_assembled"
    return df

def fit_level_only(sub: pd.DataFrame, feature: str, break_year: int, lags: int) -> dict:
    """Level-shift-only segmented spec: y = b0 + b1*t + b2*post. With only two
    post-break annual observations (2023-24) a post-break slope is not identified;
    this is the primary AR spec after the third-eye review (2026-08-07)."""
    import statsmodels.api as sm
    sub = sub.dropna(subset=[feature]).sort_values("year")
    if len(sub) < 8:
        return {}
    X = sm.add_constant(pd.DataFrame({
        "t": sub["year"] - sub["year"].min(),
        "post": (sub["year"] >= break_year).astype(int)}))
    res = sm.OLS(sub[feature], X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    return {"n_years": len(sub),
            "n_post": int((sub["year"] >= break_year).sum()),
            "level_shift_b2": round(res.params["post"], 4),
            "p_b2": round(res.pvalues["post"], 4)}

def t2_its(cfg) -> pd.DataFrame:
    doc_level = pd.read_csv(ROOT / "data" / "analysis" / "its_results.csv")
    doc_level.insert(0, "series", "doc_level")
    lags = cfg["its"]["newey_west_lags"]
    break_year = int(cfg["its"]["breakpoint"][:4])
    placebo_years = sorted(int(d[:4]) for d in cfg["its"]["placebo_breakpoints"])
    ar = assembled_ar()
    rows = []
    feats = ["nominal_per100", "acronym_per1k", "and_per100", "temporal_per1k",
             "mean_slen", "mattr500", "mgmt_per1k", "tier1_per1k", "tier2_per1k"]
    for feat in feats:
        fit = fit_its(ar, feat, break_year, lags)
        if not fit:
            continue
        pre_only = ar[ar["year"] < break_year]
        n_sig = sum(1 for py in placebo_years
                    if (pf := fit_its(pre_only, feat, py, lags))
                    and (pf["p_b2"] < 0.05 or pf["p_b3"] < 0.05))
        rows.append({"series": "ar_assembled", "stratum": "annual_report",
                     "feature": feat, "breakpoint": break_year, **fit,
                     "placebo_sig_frac": round(n_sig / len(placebo_years), 2)})
        lo = fit_level_only(ar, feat, break_year, lags)
        n_sig_lo = sum(1 for py in placebo_years
                       if (pf := fit_level_only(pre_only, feat, py, lags))
                       and pf["p_b2"] < 0.05)
        rows.append({"series": "ar_assembled_levelonly", "stratum": "annual_report",
                     "feature": feat, "breakpoint": break_year, **lo,
                     "placebo_sig_frac": round(n_sig_lo / len(placebo_years), 2)})
    return pd.concat([doc_level, pd.DataFrame(rows)], ignore_index=True)

def t3_power(cfg) -> pd.DataFrame:
    raw = pd.read_csv(ROOT / "data" / "analysis" / "power.csv")
    req = int(raw["required_tokens_per_group"].dropna().iloc[0]) \
        if "required_tokens_per_group" in raw.columns \
        and raw["required_tokens_per_group"].notna().any() else 41981
    pw = raw.dropna(subset=["power"]) if "power" in raw.columns else raw.iloc[0:0]
    ar = assembled_ar()
    rows = [{"series": "doc_level", "cells_total": len(pw),
             "cells_below_0.8": int((pw["power"].astype(float) < 0.8).sum()),
             "required_tokens_per_group": req},
            {"series": "ar_assembled", "cells_total": len(ar),
             "cells_below_0.8":
                 int((ar["tokens"] < req).sum()),  # token gate as proxy per D7
             "required_tokens_per_group": req}]
    return pd.DataFrame(rows)

def figures(cfg) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    break_year = int(cfg["its"]["breakpoint"][:4])
    paths = []
    ar = assembled_ar().sort_values("year")
    f1_feats = [("nominal_per100", "Nominalizations /100 tokens"),
                ("and_per100", "'and' /100 tokens"),
                ("temporal_per1k", "Temporal anchors /1k tokens"),
                ("acronym_per1k", "Acronyms /1k tokens"),
                ("mgmt_per1k", "Management vocabulary /1k tokens"),
                ("mean_slen", "Mean sentence length")]
    fig, axes = plt.subplots(3, 2, figsize=(11, 9), sharex=True)
    for ax, (feat, label) in zip(axes.flat, f1_feats):
        ax.plot(ar["year"], ar[feat], marker=".", lw=1)
        ax.axvline(break_year, ls="--", lw=0.8)
        ax.set_title(label, fontsize=9)
    fig.suptitle("Assembled World Bank Annual Report series (fiscal-year units, "
                 "sibling organizations excluded)", fontsize=11)
    fig.supxlabel("fiscal year")
    fig.tight_layout()
    p = OUT / "F1_ar_assembled_classic.png"
    fig.savefig(p, dpi=150); plt.close(fig); paths.append(p)

    df = yearly_series(cfg)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    for ax, feat in zip(axes, ["tier1_per1k", "tier2_per1k"]):
        for st in sorted(df["stratum"].unique()):
            sub = df[df["stratum"] == st].sort_values("year")
            ax.plot(sub["year"], sub[feat], marker=".", lw=1, label=f"{st} (doc-level)")
        ax.plot(ar["year"], ar[feat], marker=".", lw=1.2, ls=":",
                label="annual_report (assembled)")
        ax.axvline(break_year, ls="--", lw=0.8)
        ax.set_ylabel(feat)
        ax.legend(fontsize=7)
    fig.suptitle("Tier-1 / Tier-2 marker rates per 1k tokens", fontsize=11)
    fig.supxlabel("year")
    fig.tight_layout()
    p = OUT / "F2_marker_tiers_by_stratum.png"
    fig.savefig(p, dpi=150); plt.close(fig); paths.append(p)
    return paths

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    OUT.mkdir(parents=True, exist_ok=True)
    t1, t2, t3 = t1_corpus(cfg), t2_its(cfg), t3_power(cfg)
    for name, df in [("T1_corpus", t1), ("T2_its", t2), ("T3_power", t3)]:
        df.to_csv(OUT / f"{name}.csv", index=False)
        print(f"[s11] wrote {OUT / (name + '.csv')} ({len(df)} rows)")
    figs = figures(cfg)
    for p in figs:
        print(f"[s11] wrote {p}")
    def block(df: pd.DataFrame) -> str:  # plain text; avoids a tabulate dependency
        return "```\n" + df.to_string(index=False) + "\n```"
    md = [
        "# Paper artifacts (regenerated — do not edit by hand)",
        "", "## T1 corpus composition", block(t1),
        "", "## T2 ITS at 2023 (descriptive; placebo_sig_frac near 1.0 means the",
        "placebo test does NOT isolate the 2023 cut for that feature)", block(t2),
        "", "## T3 power", block(t3),
    ]
    (OUT / "NUMBERS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"[s11] wrote {OUT / 'NUMBERS.md'}")

if __name__ == "__main__":
    main()
