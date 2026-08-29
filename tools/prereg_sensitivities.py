#!/usr/bin/env python3
"""The two secondary sensitivities PREREG §4 promised and the paper never reported.

PREREG v0.5 §4, verbatim:

    Secondary sensitivity: HAC(3) OLS on the annual paired log-rate difference
    d_k = log((y_WB+0.5)/Tokens_WB) - log((y_IMF+0.5)/Tokens_IMF) regressed on
    {1, c_year, post} -- the +0.5 continuity constant is the frozen zero-count
    rule. Document-level QML with institution x year clustering is a reported
    sensitivity only.

Neither appeared in the manuscript, the generated tables, the machine outputs or
the code. An independent third-eye review found the gap on 2026-08-29 and called
it the paper's most dangerous defect, correctly: a study whose entire warrant is
adherence to a frozen plan cannot quietly omit two analyses that plan says will
be reported. That reads as selective preregistration whether or not it was.

This module runs both. It does not choose between them and the confirmatory
result -- PASS-P remains the governing test, and these remain what the plan calls
them, reported sensitivities.

## What they show, and why it is not comfortable

The two inference routes disagree about WHICH panel looks nominally significant.
PASS-P gives P1 p = 0.0142 and P2 p = 0.0929. HAC(3) gives P1 p = 0.162 and P2
p = 0.0095. Removing the guard family flips the sign in both panels under HAC(3),
significantly so on P2. A result whose apparent significance moves between panels
when the inference method changes is not a result; it is the same instability the
concentration guard and the leave-one-out check already found, arriving by a
third route. That belongs in the paper, and it strengthens the negative reading
rather than weakening it.

## A note on the +0.5

The continuity constant is applied inside each institution's log rate exactly as
the plan writes it, before differencing. It is not a smoothing choice made here.
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
OUT = ROOT / "data" / "analysis" / "prereg_sensitivities.json"
POST_LO = 2023
HAC_LAGS = 3


def _cells(panel: str, col: str) -> dict:
    with (PANELS / f"cells_{panel}.csv").open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    out: dict = {}
    for r in rows:
        out.setdefault(int(r["year"]), {})[r["institution"]] = (
            float(r[col]), float(r["tokens"]))
    return out


def hac3_annual_difference(panel: str, col: str) -> dict:
    """PREREG §4 secondary sensitivity, exactly as written."""
    d = _cells(panel, col)
    years = sorted(d)
    m = float(np.median(years))
    dk, cy, post = [], [], []
    for y in years:
        wb, imf = d[y]["WB"], d[y]["IMF"]
        dk.append(np.log((wb[0] + 0.5) / wb[1]) - np.log((imf[0] + 0.5) / imf[1]))
        cy.append(y - m)
        post.append(1.0 if y >= POST_LO else 0.0)
    X = sm.add_constant(np.column_stack([cy, post]))
    fit = sm.OLS(np.array(dk), X).fit(
        cov_type="HAC", cov_kwds={"maxlags": HAC_LAGS, "use_correction": True})
    p_ = np.asarray(fit.params)
    se = np.asarray(fit.bse)
    pv = np.asarray(fit.pvalues)
    ci = np.asarray(fit.conf_int())
    return {"n_years": len(years), "centring_year": m,
            "post_beta": float(p_[2]), "post_se_hac3": float(se[2]),
            "post_p": float(pv[2]),
            "post_ci95": [float(ci[2][0]), float(ci[2][1])],
            "trend_beta": float(p_[1]), "trend_p": float(pv[1])}


def doclevel_qml(panel: str, col: str) -> dict:
    """Poisson QML on DOCUMENT counts, same design, clustered by institution x year.

    The reviewer could not run this because docs_P*.csv was omitted from the
    review bundle -- an oversight, not a data restriction. The file carries only
    derived counts and token totals, which the IMF permission allows.
    """
    f = PANELS / f"docs_{panel}.csv"
    if not f.exists():
        return {"status": "unavailable", "reason": f"{f.name} missing"}
    with f.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if col != "count":
        # docs_P*.csv carries only the total Tier-1 count. A silent
        # `r.get(col, r["count"])` fallback produced IDENTICAL results for the
        # all-families and guard-removed columns — the exact class of quiet
        # substitution this project exists to refuse. The guard-removed document
        # counts are rebuilt from the per-family columns in family_counts.csv,
        # which is where build_panel_cells derives the cell-level version too.
        fam = {}
        with (ROOT / "data/features/family_counts.csv").open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                fam[r["id"]] = r
        drop = ["fam_underscore"]
        if col == "count_ex_underscore_pivotal":
            drop.append("fam_pivotal")
        missing = [r["id"] for r in rows if r["id"] not in fam]
        if missing:
            return {"status": "unavailable",
                    "reason": f"{len(missing)} document(s) absent from "
                              f"family_counts.csv; refusing to substitute"}
        for r in rows:
            r[col] = str(float(r["count"])
                         - sum(float(fam[r["id"]][d]) for d in drop))
    df = pd.DataFrame([{"institution": r["institution"], "year": int(r["year"]),
                        "tokens": float(r["tokens"]), "count": float(r[col])}
                       for r in rows if float(r["tokens"]) > 0])
    years = np.array(sorted(df["year"].unique()))
    m = float(np.median(years))
    wb = (df["institution"] == "WB").astype(float).to_numpy()
    cy = df["year"].to_numpy() - m
    post = (df["year"].to_numpy() >= POST_LO).astype(float)
    yd = pd.get_dummies(df["year"], drop_first=True, dtype=float).to_numpy()
    X = np.column_stack([np.ones(len(df)), yd, wb, wb * cy, wb * post])
    names = (["const"] + [f"y{i}" for i in range(yd.shape[1])]
             + ["WB", "WB_cyear", "WB_post"])
    groups = (df["institution"] + ":" + df["year"].astype(str)).to_numpy()
    fit = sm.GLM(df["count"], X, family=sm.families.Poisson(),
                 offset=np.log(df["tokens"])).fit(
        cov_type="cluster", cov_kwds={"groups": groups})
    j = names.index("WB_post")
    p_ = np.asarray(fit.params); se = np.asarray(fit.bse); pv = np.asarray(fit.pvalues)
    ci = np.asarray(fit.conf_int())
    return {"status": "ok", "n_documents": int(len(df)),
            "n_clusters": int(len(set(groups))),
            "post_beta": float(p_[j]), "post_se_cluster": float(se[j]),
            "post_p": float(pv[j]),
            "post_ci95": [float(ci[j][0]), float(ci[j][1])],
            "trend_beta": float(p_[names.index("WB_cyear")])}


def main() -> int:
    out: dict = {"source": "PREREG v0.5 §4 secondary sensitivities",
                 "governing_test_remains": "PASS-P (frozen)", "results": {}}
    print("PREREG §4 — the two promised sensitivities, run at last\n")
    for panel in ("P1", "P2"):
        out["results"][panel] = {}
        for col, lab in (("count", "all Tier-1"),
                         ("count_ex_underscore", "excl. underscore")):
            h = hac3_annual_difference(panel, col)
            q = doclevel_qml(panel, col)
            out["results"][panel][lab] = {"hac3_annual": h, "doclevel_qml": q}
            print(f"  {panel} {lab:17s} HAC(3) post={h['post_beta']:+.3f} "
                  f"se={h['post_se_hac3']:.3f} p={h['post_p']:.4f}"
                  + (f"   |  doc-QML post={q['post_beta']:+.3f} "
                     f"p={q['post_p']:.4f} (clusters {q['n_clusters']})"
                     if q.get("status") == "ok" else f"   |  doc-QML {q}"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\n[prereg] wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
