"""s08 — interrupted time series per stratum x feature (D2).
Segmented OLS: y_t = b0 + b1*t + b2*post + b3*(t - t0)*post, Newey-West (HAC) SEs.
Guardrails baked in: pre-trend slope reported; placebo breakpoints run on PRE-2022
data only; language of outputs is 'discontinuity', never attribution (CLAUDE.md rule 3)."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
import pandas as pd
import statsmodels.api as sm
from utils import ROOT, load_config

FEATURES = ["nominal_per100", "acronym_per1k", "and_per100", "temporal_per1k",
            "mean_slen", "mattr500", "mgmt_per1k", "tier1_per1k", "tier2_per1k"]

def yearly_series(cfg) -> pd.DataFrame:
    c = pd.read_csv(ROOT / "data" / "features" / "classic.csv")
    m = pd.read_csv(ROOT / "data" / "features" / "markers.csv")
    df = c.merge(m.drop(columns=["tokens"]), on=["id", "stratum", "year"], how="outer")
    df["year"] = df["year"].astype(int)
    agg = {f: "mean" for f in FEATURES if f in df.columns}
    agg["tokens"] = "sum"
    return df.groupby(["stratum", "year"], as_index=False).agg(agg)

def fit_its(sub: pd.DataFrame, feature: str, break_year: int, lags: int) -> dict:
    sub = sub.dropna(subset=[feature]).sort_values("year")
    if len(sub) < 8:
        return {}
    t = sub["year"] - sub["year"].min()
    post = (sub["year"] >= break_year).astype(int)
    X = sm.add_constant(pd.DataFrame({
        "t": t, "post": post, "t_post": (sub["year"] - break_year).clip(lower=0)}))
    res = sm.OLS(sub[feature], X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    pre = sub[sub["year"] < break_year]
    pre_slope = float("nan")
    if len(pre) >= 5:
        Xp = sm.add_constant(pre["year"] - pre["year"].min())
        pre_slope = sm.OLS(pre[feature], Xp).fit().params.iloc[1]
    return {"n_years": len(sub),
            "level_shift_b2": round(res.params["post"], 4),
            "p_b2": round(res.pvalues["post"], 4),
            "slope_change_b3": round(res.params["t_post"], 4),
            "p_b3": round(res.pvalues["t_post"], 4),
            "p_b2_exact": float(res.pvalues["post"]),
            "p_b3_exact": float(res.pvalues["t_post"]),
            "pre_trend_slope": round(pre_slope, 4)}

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    ap.add_argument("--plot-feature", default=None,
                    help="optionally save a per-stratum plot for one feature")
    args = ap.parse_args()
    cfg = load_config(args.config)
    lags = cfg["its"]["newey_west_lags"]
    break_year = int(cfg["its"]["breakpoint"][:4])
    placebo_years = sorted(int(d[:4]) for d in cfg["its"]["placebo_breakpoints"])
    df = yearly_series(cfg)
    rows = []
    for stratum in sorted(df["stratum"].unique()):
        sub = df[df["stratum"] == stratum]
        for feat in [f for f in FEATURES if f in sub.columns]:
            main_fit = fit_its(sub, feat, break_year, lags)
            if not main_fit:
                continue
            pre_only = sub[sub["year"] < break_year]
            n_sig_placebo = 0
            for py in placebo_years:
                pf = fit_its(pre_only, feat, py, lags)
                if pf and (pf["p_b2_exact"] < 0.05 or pf["p_b3_exact"] < 0.05):
                    n_sig_placebo += 1
            rows.append({"stratum": stratum, "feature": feat,
                         "breakpoint": break_year, **main_fit,
                         "placebo_sig_frac":
                             round(n_sig_placebo / len(placebo_years), 2)})
    out = ROOT / "data" / "analysis" / "its_results.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"[s08] wrote {out} ({len(rows)} stratum x feature fits)")
    print("[s08] REMINDER: scans are descriptive and endpoint-sensitive; they do "
          "not identify a unique break date, trajectory shape, or mechanism (E3/D2).")
    if args.plot_feature:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for stratum in sorted(df["stratum"].unique()):
            sub = df[df["stratum"] == stratum].sort_values("year")
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.plot(sub["year"], sub[args.plot_feature], marker="o", lw=1)
            ax.axvline(break_year, ls="--")
            ax.set_title(f"{args.plot_feature} — {stratum}")
            ax.set_xlabel("year"); ax.set_ylabel(args.plot_feature)
            fig.tight_layout()
            p = ROOT / "data" / "analysis" / f"plot_{stratum}_{args.plot_feature}.png"
            fig.savefig(p, dpi=150); plt.close(fig)
            print(f"[s08] plot -> {p}")

if __name__ == "__main__":
    main()
