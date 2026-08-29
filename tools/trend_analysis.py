#!/usr/bin/env python3
"""What the differential trend term is, once you stop treating it as bookkeeping.

The frozen design carries tau = WB x centred_year alongside beta = WB x post.
Until the 2026-08-27 audit the manuscript never mentioned tau, and used a wrong
mechanism to explain why beta collapses under the concentration guard. The real
answer is that tau absorbs the gap. That raises a question the paper had not
asked: what IS tau?

This module answers it reproducibly, and separates what is preregistered from
what is not.

## Preregistered

PREREG §9 requires the `WB:c_year` estimate with its PASS-E percentile interval
"reported prominently in every confirmatory output". Those intervals come from
the frozen engine and are read here from the committed battery JSON, never
recomputed — a naive Poisson standard error on these cells is far too small
(year-level overdispersion, sigma_delta = 0.3205) and quoting one beside a
bootstrap interval would flatter the result.

## Not preregistered, and labelled as such

Everything else below: the pre-period-only refit, the per-institution
decomposition, the guard-family variants. These are post-hoc. Intervals for them
use the delete-one-year jackknife over the common-year sequence -- the same
interval method PREREG §3 fixes for the validation outcomes, chosen here because
it is cheap, it respects the year as the resampling unit, and it is not the
frozen engine pretending to be applied outside its remit.

## The question that motivates it

If tau is significant on 1999-2022 data ALONE, the divergence between the two
institutions predates the LLM era entirely, and the post-2022 test is measuring
the tail of something much longer. That is a different paper from "we looked for
an LLM break and found nothing", and it is the honest one.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
PANELS = ROOT / "data" / "analysis" / "panels"
OUT = ROOT / "data" / "analysis" / "trend_analysis.json"
POST_LO = 2023


def cells(panel: str, col: str = "count") -> pd.DataFrame:
    with (PANELS / f"cells_{panel}.csv").open(encoding="utf-8") as fh:
        rs = list(csv.DictReader(fh))
    return pd.DataFrame([{"institution": r["institution"], "year": int(r["year"]),
                          "count": float(r[col]), "tokens": float(r["tokens"])}
                         for r in rs])


def _design(df: pd.DataFrame, with_post: bool):
    df = df.sort_values(["year", "institution"]).reset_index(drop=True)
    years = np.array(sorted(df["year"].unique()))
    m = float(np.median(years))
    wb = (df["institution"] == "WB").astype(float).to_numpy()
    cy = df["year"].to_numpy() - m
    yd = pd.get_dummies(df["year"], drop_first=True, dtype=float).to_numpy()
    cols = [np.ones(len(df)), yd, wb, wb * cy]
    names = ["const"] + [f"y{i}" for i in range(yd.shape[1])] + ["WB", "WB_cyear"]
    if with_post:
        cols.append(wb * (df["year"].to_numpy() >= POST_LO).astype(float))
        names.append("WB_post")
    return df, np.column_stack(cols), names, years


def fit(df: pd.DataFrame, with_post: bool, coef: str = "WB_cyear") -> float:
    d, X, names, _ = _design(df, with_post)
    r = sm.GLM(d["count"], X, family=sm.families.Poisson(),
               offset=np.log(d["tokens"])).fit()
    return float(np.asarray(r.params)[names.index(coef)])


def jackknife(df: pd.DataFrame, with_post: bool, coef: str = "WB_cyear"):
    """Delete-one-year jackknife: SE = sqrt((T-1)/T * sum (theta_-k - theta_bar)^2).

    The year is the resampling unit because the shock that governs power in this
    design is year-level. Deleting a document would understate it by an order of
    magnitude."""
    theta = fit(df, with_post, coef)
    years = sorted(df["year"].unique())
    reps = []
    for y in years:
        sub = df[df["year"] != y]
        if sub["year"].nunique() < 4:
            continue
        try:
            reps.append(fit(sub, with_post, coef))
        except Exception:
            continue
    T = len(reps)
    if T < 3:
        return theta, float("nan"), (float("nan"), float("nan")), T
    bar = float(np.mean(reps))
    se = float(np.sqrt((T - 1) / T * np.sum((np.array(reps) - bar) ** 2)))
    return theta, se, (theta - 1.96 * se, theta + 1.96 * se), T


def own_trend(df: pd.DataFrame, inst: str):
    s = df[df["institution"] == inst].sort_values("year")
    X = sm.add_constant(s["year"].to_numpy() - float(np.median(s["year"])))
    r = sm.GLM(s["count"], X, family=sm.families.Poisson(),
               offset=np.log(s["tokens"])).fit()
    return float(np.asarray(r.params)[1])


def main() -> int:
    out: dict = {"preregistered": {}, "post_hoc": {}}

    for P in ("P1", "P2"):
        b = json.loads((PANELS / f"{P}_battery.json").read_text(encoding="utf-8"))
        out["preregistered"][P] = {
            "tau_hat": b["trend"]["beta"],
            "ci_passe_percentile": b["trend"]["ci_percentile"],
            "source": "frozen engine, same PASS-E draws as the primary CI",
            "beta_hat_WB_post": b["primary_m2"]["beta_hat"],
        }

    print("=== PREREGISTERED (frozen engine, full window)")
    for P, d in out["preregistered"].items():
        lo, hi = d["ci_passe_percentile"]
        print(f"  {P}: tau = {d['tau_hat']:+.4f}  PASS-E CI [{lo:.3f}, {hi:.3f}]"
              f"   ({100*(np.exp(d['tau_hat'])-1):+.1f}%/yr)")

    print("\n=== POST-HOC: does tau survive on PRE-PERIOD DATA ALONE (1999-2022)?")
    for P in ("P1", "P2"):
        rec = {}
        for col, lab in (("count", "all_tier1"),
                         ("count_ex_underscore", "ex_underscore")):
            d = cells(P, col)
            pre = d[d["year"] < POST_LO]
            th, se, ci, T = jackknife(pre, with_post=False)
            rec[lab] = {"tau_hat": th, "jackknife_se": se,
                        "ci_jackknife": list(ci), "years": int(pre["year"].nunique()),
                        "jackknife_reps": T,
                        "pct_per_year": 100 * (float(np.exp(th)) - 1)}
            print(f"  {P} {lab:14s} tau = {th:+.4f}  jack SE {se:.4f}  "
                  f"CI [{ci[0]:+.4f}, {ci[1]:+.4f}]  ({rec[lab]['pct_per_year']:+.1f}%/yr)")
        d = cells(P)
        pre = d[d["year"] < POST_LO]
        rec["own_trends_pre2023"] = {
            inst: {"slope": own_trend(pre, inst),
                   "pct_per_year": 100 * (float(np.exp(own_trend(pre, inst))) - 1)}
            for inst in ("WB", "IMF")}
        out["post_hoc"][P] = rec
        w = rec["own_trends_pre2023"]["WB"]["pct_per_year"]
        i = rec["own_trends_pre2023"]["IMF"]["pct_per_year"]
        print(f"  {P} decomposition 1999-2022: WB {w:+.1f}%/yr, IMF {i:+.1f}%/yr")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n[trend] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
