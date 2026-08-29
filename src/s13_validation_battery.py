"""PREREG v0.5 SS5 decision conditions, SS3 validation outcomes, and SS9
sensitivity analyses -- executable orchestration (round-6 blocker 8; the
[BUILD] half of amendment B8).

Every component consumes institution x year cells (plus doc-level rows for the
validation outcomes and grouped rows for the standardized variant) and returns
machine-readable JSON. Bootstrap components reuse the frozen engine primitives
(bootstrap_engine): same input contract, same pairing, same block length.
Seed-offset registry -- no two procedures share draws unless the prereg says
they must:

    PASS-P                      seed + b            (engine, unchanged)
    PASS-E                      seed + 500000 + b   (engine, unchanged)
    event-study PASS-E          seed + 600000 + b
    H-SHARED block bootstrap    seed + 700000 + b

The differential-trend CI is NOT re-simulated here: it is read from the SAME
PASS-E draws inside the engine (trend_beta_hat / trend_ci_percentile).

Freeze discipline: the CLI refuses to run without --i-am-post-sap (PREREG
SS11: no WB outcome analysis before the SAP timestamp). Fixture tests import
the functions directly on synthetic data."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

from bootstrap_engine import (two_pass, build_design, wild_score_p,
                              _pair_index, _fit, _converged, mom_alpha,
                              passe_multi, POST_LO, POST_HI, BLOCK_LEN, SEED)

ES_SEED_OFFSET = 600_000
HS_SEED_OFFSET = 700_000
CONTINUITY = 0.5          # frozen zero-count rule (PREREG SS4.2 secondary)
LOPO_P = 0.10             # SS5 condition 4, unadjusted
STABILITY_RATIO = 0.50    # SS5 condition 2
COVERAGE_FLOOR = 0.80     # SS6 hard-fail (min post-period coverage)
ESS_FLOOR_FRAC = 0.50     # SS6 ESS floor fraction (token masses under pi)


# ---------------------------------------------------------------- helpers --
def _jsonable(o):
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return [_jsonable(v) for v in o.tolist()]
    return o


def _governing_interval(res: dict):
    """The CI that governs a decision clause, after the SS4.2 escalation
    ladder as already applied by the engine. jackknife_poisson is the frozen
    NB2 fallback (its interval is stored in ci_percentile)."""
    g = res.get("governing_ci")
    if g in ("ci_percentile", "jackknife_poisson"):
        return res.get("ci_percentile")
    if g == "ci_wald_boot":
        return res.get("ci_wald_boot")
    return None                                    # "failed"


def _excludes_zero(ci) -> bool:
    if ci is None:
        return False
    lo, hi = float(ci[0]), float(ci[1])
    if math.isnan(lo) or math.isnan(hi):
        return False
    return lo > 0.0 or hi < 0.0


def _same_sign(a: float, b: float) -> bool:
    return (a > 0) == (b > 0) and a != 0 and b != 0


# ------------------------------------------------- SS3 validation outcomes --
def _doc_design(docs: pd.DataFrame, wb_label: str):
    d = docs.copy()
    for c in ("institution", "year", "tokens"):
        if c not in d.columns:
            raise ValueError(f"docs missing column {c!r}")
    d = d.sort_values(["year", "institution"]).reset_index(drop=True)
    years = np.array(sorted(d["year"].unique()))
    m = float(np.median(years))
    wb = (d["institution"] == wb_label).astype(float).to_numpy()
    c_year = d["year"].to_numpy(dtype=float) - m
    post = ((d["year"] >= POST_LO) & (d["year"] <= POST_HI)).astype(float).to_numpy()
    ydum = pd.get_dummies(d["year"], drop_first=True, dtype=float)
    X = np.column_stack([np.ones(len(d)), ydum.to_numpy(), wb, wb * c_year,
                         wb * post, np.log(d["tokens"].to_numpy(dtype=float))])
    names = (["const"] + [f"y{c}" for c in ydum.columns]
             + ["WB", "WB_cyear", "WB_post", "log_tokens"])
    return d, X, names, years


def _jackknife_doc_model(docs, wb_label, endog_fn, family):
    """Delete-one-year jackknife over the common-year sequence for a
    doc-level GLM with the SS3 design; SE = sqrt((T-1)/T * sum((th-thbar)^2))."""
    d, X, names, years = _doc_design(docs, wb_label)
    j = names.index("WB_post")
    full = sm.GLM(endog_fn(d), X, family=family).fit()
    if not _converged(full):
        return {"status": "fit_failed"}
    beta = float(full.params[j])
    th = []
    for yy in years:
        sub = docs[docs["year"] != yy]
        d2, X2, n2, _ = _doc_design(sub, wb_label)
        try:
            r2 = sm.GLM(endog_fn(d2), X2, family=family).fit()
            if not _converged(r2):
                return {"status": "jackknife_fit_failed", "year": int(yy)}
            th.append(float(r2.params[n2.index("WB_post")]))
        except Exception:
            return {"status": "jackknife_fit_failed", "year": int(yy)}
    th = np.asarray(th)
    Tn = len(th)
    se = float(np.sqrt((Tn - 1) / Tn * np.sum((th - th.mean()) ** 2)))
    out = {"status": "ok", "beta": beta, "se_jackknife": se,
           "ci": [beta - 1.96 * se, beta + 1.96 * se],
           "T": int(Tn), "n_docs": int(len(docs))}
    try:  # Pearson-scale quasi-dispersion, reported (B8)
        out["quasi_dispersion"] = float(full.pearson_chi2 / full.df_resid)
    except Exception:
        out["quasi_dispersion"] = float("nan")
    return out


def validation_prevalence(docs: pd.DataFrame, wb_label: str = "WB") -> dict:
    """Doc-level >=1-family indicator; logit with the SS4 design + log tokens;
    delete-one-year jackknife CI (PREREG SS3)."""
    return _jackknife_doc_model(docs, wb_label,
                                lambda d: d["hit"].to_numpy(dtype=float),
                                sm.families.Binomial())


def validation_breadth(docs: pd.DataFrame, wb_label: str = "WB") -> dict:
    """Distinct families per document out of 13; quasi-binomial(13) with the
    same design; Pearson quasi-dispersion reported; same jackknife (B8)."""
    def endog(d):
        k = d["breadth"].to_numpy(dtype=float)
        return np.column_stack([k, 13.0 - k])
    return _jackknife_doc_model(docs, wb_label, endog, sm.families.Binomial())


def consistency_rule(beta_primary: float, prevalence: dict, breadth: dict) -> dict:
    """SS3 prespecified rule: opposite-sign validation estimate with CI
    excluding 0 downgrades the confirmatory claim to count-specific."""
    flags = {}
    for name, res in (("prevalence", prevalence), ("breadth", breadth)):
        if res.get("status") != "ok":
            flags[name] = None
            continue
        flags[name] = bool((not _same_sign(res["beta"], beta_primary))
                           and _excludes_zero(res["ci"]))
    trig = [k for k, v in flags.items() if v]
    return {"opposite_sign_ci_excl0": flags,
            "downgrade_to_count_specific": bool(trig), "triggered_by": trig}


# --------------------------------------------------------- SS9 sensitivity --
def hshared(cells: pd.DataFrame, institution: str = "IMF", B: int = 9999,
            seed: int = SEED, block_len: int = BLOCK_LEN,
            continuity: float = CONTINUITY) -> dict:
    """H-SHARED: the comparator's own post-minus-pre pooled log-rate
    difference, circular block-3 bootstrap on that series ALONE (B8).
    Zero-count rule: the frozen +0.5 continuity constant."""
    sub = (cells[cells["institution"] == institution]
           .sort_values("year").reset_index(drop=True))
    years = sub["year"].to_numpy()
    y = sub["count"].to_numpy(dtype=float)
    tok = sub["tokens"].to_numpy(dtype=float)
    post = (years >= POST_LO) & (years <= POST_HI)

    def delta(idx):
        pm = post[idx]
        if pm.sum() == 0 or (~pm).sum() == 0:
            return None
        return (math.log((y[idx][pm].sum() + continuity) / tok[idx][pm].sum())
                - math.log((y[idx][~pm].sum() + continuity) / tok[idx][~pm].sum()))

    T = len(years)
    d_obs = delta(np.arange(T))
    n_blocks = int(np.ceil(T / block_len))
    draws, fails = [], 0
    for b in range(B):
        rng = np.random.default_rng(seed + HS_SEED_OFFSET + b)
        starts = rng.integers(0, T, size=n_blocks)
        order = np.concatenate([(s0 + np.arange(block_len)) % T
                                for s0 in starts])[:T]
        db = delta(order)
        if db is None:
            fails += 1
        else:
            draws.append(db)
    draws = np.asarray(draws)
    out = {"institution": institution, "delta_log_rate": d_obs,
           "B_valid": int(len(draws)), "fail_rate": fails / B, "T": int(T)}
    if len(draws):
        lo, hi = np.quantile(draws, [0.025, 0.975])
        out["ci_percentile"] = [float(lo), float(hi)]
    else:
        out["ci_percentile"] = [float("nan")] * 2
    return out


def make_bins(years, post=(POST_LO, POST_HI), width: int = 3,
              min_obs: int = 2):
    """3-year calendar bins anchored at the post window, counted backward.
    Round-7 repairs: (i) the earliest-bin merge is keyed to the number of
    OBSERVED years inside the bin (not its calendar width), cascading until
    the earliest bin holds >= 2 observed years; (ii) the reference bin is the
    one containing the LOWER-MEDIAN observed year -- a deterministic observed
    integer, well-defined for every permitted gap-containing common-year
    sequence. Returns ascending (lo, hi) list + reference index."""
    obs = sorted(set(int(v) for v in years))
    lo_all = obs[0]
    bins, hi = [], post[1]
    while hi >= lo_all:
        lo = hi - width + 1
        bins.append((max(lo, lo_all), hi))
        hi = lo - 1
    bins = sorted(bins)

    def n_obs(b):
        return sum(1 for y in obs if b[0] <= y <= b[1])

    # round-8: NO bin may be empty of observed years — an empty bin merges
    # into its immediately LATER neighbor (the last bin, if ever empty,
    # merges backward); the earliest bin must additionally hold >= min_obs
    # observed years (merging later, as before). Run to a fixpoint.
    changed = True
    while changed:
        changed = False
        for i in range(len(bins)):
            if n_obs(bins[i]) == 0 and len(bins) >= 2:
                if i + 1 < len(bins):
                    bins[i + 1] = (bins[i][0], bins[i + 1][1])
                else:
                    bins[i - 1] = (bins[i - 1][0], bins[i][1])
                bins.pop(i)
                changed = True
                break
        if not changed and len(bins) >= 2 and n_obs(bins[0]) < min_obs:
            bins[1] = (bins[0][0], bins[1][1])
            bins.pop(0)
            changed = True
    med = obs[(len(obs) - 1) // 2]           # lower median: always observed
    ref = next(i for i, (lo, hi) in enumerate(bins) if lo <= med <= hi)
    return bins, ref


def event_study(cells: pd.DataFrame, wb_label: str = "WB", B: int = 9999,
                seed: int = SEED, nb2: bool = False,
                allow_noninteger: bool = False,
                block_len: int = BLOCK_LEN) -> dict:
    """SS4.1 prespecified event-study display: WB x 3-year-bin indicators
    (reference = the bin containing the lower-median observed year), inference
    via the engine's generalized PASS-E (passe_multi) so the FULL SS4.2
    machinery applies -- floored share, small-count flag, Wald-boot interval,
    governing escalation, failed state, fail-closed NB2 jackknife fallback,
    noninteger mode (round-7 repair). Seed offset 600000."""
    _df0, _X, _n, _y, _o, years = build_design(cells, wb_label, allow_noninteger)
    bins, ref = make_bins(years)
    keep = [f"WBbin_{lo}_{hi}" for i, (lo, hi) in enumerate(bins) if i != ref]

    def design_fn(df):
        wb = (df["institution"] == wb_label).astype(float).to_numpy()
        ydum = pd.get_dummies(df["year"], drop_first=True, dtype=float)
        cols = [np.ones(len(df)), ydum.to_numpy(), wb]
        names = ["const"] + [f"y{c}" for c in ydum.columns] + ["WB"]
        for i, (lo, hi) in enumerate(bins):
            if i == ref:
                continue
            ind = ((df["year"] >= lo) & (df["year"] <= hi)
                   ).astype(float).to_numpy()
            cols.append(wb * ind)
            names.append(f"WBbin_{lo}_{hi}")
        return np.column_stack(cols), names

    res = passe_multi(cells[["institution", "year", "count", "tokens"]],
                      design_fn, keep, wb_label=wb_label, B=B,
                      block_len=block_len, seed=seed,
                      seed_offset=ES_SEED_OFFSET, nb2=nb2,
                      allow_noninteger=allow_noninteger)
    rows = []
    for i, (lo, hi) in enumerate(bins):
        if i == ref:
            rows.append({"bin": [lo, hi], "reference": True})
            continue
        rows.append({"bin": [lo, hi], "reference": False,
                     **res["coefs"][f"WBbin_{lo}_{hi}"]})
    # Round-9 (C22): the governing PASS-E state PROPAGATES — a failed
    # engine result or a zero-valid-bootstrap interval can never surface
    # under a top-level "ok".
    reasons = []
    if res["governing_ci"] == "failed" or res["method_ci"] in (
            "failed", "jackknife_failed"):
        reasons.append(f"engine_{res['governing_ci']}"
                       if res["governing_ci"] == "failed"
                       else f"engine_{res['method_ci']}")
    if int(res["B_valid_ci"]) == 0:
        reasons.append("no_valid_bootstrap_ci")
    status = "failed" if reasons else "ok"
    return {"status": status, "failure_reasons": reasons,
            "bins": rows, "reference_bin": list(bins[ref]),
            "alpha_hat": res["alpha_hat"], "method_ci": res["method_ci"],
            "governing_ci": res["governing_ci"],
            "ci_fail_rate": res["ci_fail_rate"],
            "true_floored_share": res["true_floored_share"],
            "small_count_regime": res["small_count_regime"],
            "rounding": res["rounding"], "B_valid_ci": res["B_valid_ci"]}


def placebo_2016(cells: pd.DataFrame, wb_label: str = "WB", B: int = 9999,
                 seed: int = SEED, nb2: bool = False,
                 block_len: int = BLOCK_LEN) -> dict:
    """SS9 fixed sensitivity: post16 = 1{2016 <= year <= 2018} estimated on
    pre-2023 common years only, PASS-P (B8). Implemented by taking the
    contract-validated design on the <=2022 subset and swapping the WB_post
    column for WB x post16."""
    sub = cells[cells["year"] <= 2022]
    df, X, names, y, off, years = build_design(sub, wb_label)
    pair, T = _pair_index(df, years, wb_label)
    j = names.index("WB_post")
    wb = (df["institution"] == wb_label).astype(float).to_numpy()
    p16 = ((df["year"] >= 2016) & (df["year"] <= 2018)).astype(float).to_numpy()
    X = X.copy()
    X[:, j] = wb * p16
    p, _, _ = wild_score_p(y, X, off, names, pair, T, B, block_len, seed, nb2)
    beta = float(_fit(y, X, off, sm.families.Poisson()).params[j])
    return {"p_pass_p": p, "beta": beta,
            "years_used": [int(years.min()), int(years.max())],
            "window": [2016, 2018]}


# --------------------------------------------- SS6 standardized variant ----
def _ess_tokens(std_docs: pd.DataFrame, pi: pd.Series, post_lo: int = POST_LO):
    """ESS floor on cell token masses under pi (amendment B4): per
    institution x period, over groups g with support, with renormalized
    weights pi~: ESS_tok = 1 / sum_g(pi~_g^2 / tok_g); floor =
    ESS_FLOOR_FRAC x total tokens of that institution x period. Equals total
    tokens exactly when pi~ matches the token shares."""
    d = std_docs.copy()
    d["period"] = np.where(d["year"] >= post_lo, "post", "pre")
    rows = []
    for (inst, per), sub in d.groupby(["institution", "period"]):
        tok = sub[sub["group"].isin(pi.index)].groupby("group")["tokens"].sum()
        tok = tok[tok > 0]
        total = float(sub["tokens"].sum())
        if len(tok) == 0 or total == 0:
            rows.append({"institution": inst, "period": per, "ess": 0.0,
                         "total_tokens": total, "ok": False})
            continue
        pin = pi[tok.index] / pi[tok.index].sum()
        ess = float(1.0 / np.sum(pin.to_numpy() ** 2 / tok.to_numpy()))
        rows.append({"institution": inst, "period": per, "ess": ess,
                     "total_tokens": total,
                     "ok": bool(ess >= ESS_FLOOR_FRAC * total)})
    return rows


def standardized_variant(std_docs: pd.DataFrame, wb_label: str = "WB",
                         B: int = 9999, seed: int = SEED) -> dict:
    """Period-valid direct standardization (SS6). Round-8 diagnostics
    contract: EVERY return — feasible or infeasible, whatever the primary
    reason — carries post_token_support, excluded_token_shares,
    dropped_cells, min_post_coverage, ess and pi_groups; ALL simultaneously
    failed gates are listed in `failures` (no masking), with the primary
    `reason` fixed by the frozen order: no_common_support_groups ->
    zero_coverage_post_cell -> post_token_support_below_0.80 ->
    post_coverage_below_floor -> ess_below_floor."""
    from standardize import build_pi, standardize_cells
    pi = build_pi(std_docs)
    d = std_docs.copy()
    d["period"] = np.where(d["year"] >= POST_LO, "post", "pre")
    support, excluded = {}, []
    for (inst, per), sub in d.groupby(["institution", "period"]):
        tot = float(sub["tokens"].sum())
        in_tok = (float(sub[sub["group"].isin(pi.index)]["tokens"].sum())
                  if len(pi) else 0.0)
        share = in_tok / tot if tot else 0.0
        excluded.append({"institution": inst, "period": per,
                         "excluded_token_share": 1.0 - share})
        if per == "post":
            support[inst] = share
    for inst in d["institution"].unique():
        support.setdefault(str(inst), 0.0)
    if len(pi):
        cells = standardize_cells(std_docs, pi=pi)
        dropped = cells.attrs.get("dropped_cells", [])
    else:
        cells = pd.DataFrame(columns=["institution", "year", "count",
                                      "tokens", "coverage"])
        dropped = [{"institution": str(i), "year": int(t)} for i, t in
                   std_docs[["institution", "year"]].drop_duplicates()
                   .itertuples(index=False)]
    dropped_post = [dc for dc in dropped if dc["year"] >= POST_LO]
    post = cells[cells["year"] >= POST_LO] if len(cells) else cells
    cov = (post.groupby("institution")["coverage"].min()
           if len(post) else pd.Series(dtype=float))
    cov_map = {k: float(v) for k, v in cov.items()} if len(cov) else {}
    cov_ok = len(cov) >= 2 and float(cov.min()) >= COVERAGE_FLOOR
    ess = _ess_tokens(std_docs, pi) if len(pi) else []
    ess_ok = bool(ess) and all(r["ok"] for r in ess)
    failures = []
    if len(pi) == 0:
        failures.append("no_common_support_groups")
    if dropped_post:
        failures.append("zero_coverage_post_cell")
    if len(support) < 2 or min(support.values()) < 0.80:
        failures.append("post_token_support_below_0.80")
    if not cov_ok:
        failures.append("post_coverage_below_floor")
    if not ess_ok:
        failures.append("ess_below_floor")
    diag = {"post_token_support": support,
            "excluded_token_shares": excluded,
            "dropped_cells": dropped,
            "min_post_coverage": cov_map,
            "ess": ess, "pi_groups": int(len(pi))}
    if failures:
        return {"feasible": False, "reason": failures[0],
                "failures": failures, **diag}
    res = two_pass(cells[["institution", "year", "count", "tokens"]],
                   wb_label=wb_label, B=B, seed=seed, allow_noninteger=True)
    return {"feasible": True, "failures": [], **diag, "result": res}


# ------------------------------------------------- SS5 conditions and run --
def _variant_ok(res_variant: dict, beta_m2: float) -> dict:
    b = res_variant.get("beta_hat", float("nan"))
    ratio = (abs(b - beta_m2) / abs(beta_m2)) if beta_m2 != 0 else float("inf")
    ci = _governing_interval(res_variant)
    ok = bool(ratio < STABILITY_RATIO and _same_sign(b, beta_m2)
              and _excludes_zero(ci))
    return {"beta": b, "ratio_to_m2": ratio, "governing_ci": ci,
            "governing_ci_name": res_variant.get("governing_ci"),
            "ok": ok}


def lopo(cells: pd.DataFrame, wb_label: str, beta_sign_ref: float,
         B: int = 9999, seed: int = SEED, nb2: bool = False,
         block_len: int = BLOCK_LEN) -> dict:
    """SS5 condition 4: for each post-year deletion, sign retained and
    UNADJUSTED PASS-P p < 0.10 (the deleted year leaves the index before
    blocking -- build_design on the subset does exactly that)."""
    rows, all_ok = [], True
    post_years = [yy for yy in (2023, 2024, 2025)
                  if yy in set(cells["year"].tolist())]
    for yy in post_years:
        sub = cells[cells["year"] != yy]
        df, X, names, y, off, years = build_design(sub, wb_label)
        pair, T = _pair_index(df, years, wb_label)
        p, _, _ = wild_score_p(y, X, off, names, pair, T, B, block_len,
                               seed, nb2)
        beta = float(_fit(y, X, off, sm.families.Poisson())
                     .params[names.index("WB_post")])
        ok = bool(p < LOPO_P and _same_sign(beta, beta_sign_ref))
        rows.append({"deleted_year": yy, "p_pass_p": p, "beta": beta, "ok": ok})
        all_ok = all_ok and ok
    return {"deletions": rows, "post_years_present": post_years,
            "ok": bool(all_ok and len(post_years) == 3)}


def run_panel(cells: pd.DataFrame, panel: str, docs: pd.DataFrame | None = None,
              std_docs: pd.DataFrame | None = None, wb_label: str = "WB",
              guard_col: str = "count_ex_underscore",
              stress_col: str = "count_ex_underscore_pivotal",
              alpha_holm: float = 0.05, B: int = 9999,
              seed: int = SEED, confirmatory: bool = False) -> dict:
    """confirmatory=True (family orchestration) makes the SS3 validation
    documents MANDATORY; the per-panel pass flag is reported at the SUPPLIED
    alpha only — the GOVERNING verdict is holm_family's (round-7 item 6)."""
    if confirmatory and docs is None:
        raise SystemExit(f"[s13] panel {panel}: docs (validation outcomes) "
                         "are REQUIRED in confirmatory/family mode (SS3).")
    base = cells[["institution", "year", "count", "tokens"]].copy()
    res_m2 = two_pass(base, wb_label=wb_label, B=B, seed=seed)
    beta_m2 = res_m2["beta_hat"]
    res_nb2 = two_pass(base, wb_label=wb_label, B=B, seed=seed, nb2=True)

    cond1 = {"p_pass_p": res_m2["p_two_sided"], "alpha_holm": alpha_holm,
             "ok": bool(res_m2["p_two_sided"] < alpha_holm)}

    variants = {"nb2": _variant_ok(res_nb2, beta_m2)}
    if std_docs is not None:
        std = standardized_variant(std_docs, wb_label=wb_label, B=B, seed=seed)
        variants["standardized"] = (
            dict(_variant_ok(std["result"], beta_m2),
                 feasible=True, min_post_coverage=std["min_post_coverage"])
            if std.get("feasible")
            else {"ok": False, "feasible": False,
                  "reason": std.get("reason"), **{k: v for k, v in std.items()
                                                  if k not in ("feasible",)}})
    else:
        variants["standardized"] = {"ok": False, "feasible": False,
                                    "reason": "std_docs_not_supplied"}
    cond2 = {"variants": variants,
             "ok": bool(all(v.get("ok") for v in variants.values()))}

    if guard_col in cells.columns:
        gcells = base.assign(count=cells[guard_col].to_numpy())
        gres = two_pass(gcells, wb_label=wb_label, B=B, seed=seed)
        gci = _governing_interval(gres)
        cond3 = {"beta": gres["beta_hat"], "governing_ci": gci,
                 "governing_ci_name": gres.get("governing_ci"),
                 "ok": bool(_same_sign(gres["beta_hat"], beta_m2)
                            and _excludes_zero(gci))}
    else:
        cond3 = {"ok": False, "reason": f"missing column {guard_col!r}"}
    stress = None
    if stress_col in cells.columns:                      # non-gating (SS3)
        scells = base.assign(count=cells[stress_col].to_numpy())
        sres = two_pass(scells, wb_label=wb_label, B=B, seed=seed)
        stress = {"beta": sres["beta_hat"],
                  "governing_ci": _governing_interval(sres)}

    cond4 = lopo(base, wb_label, beta_m2, B=B, seed=seed)

    out = {"panel": panel, "estimand": res_m2["estimand"],
           "primary_m2": res_m2, "nb2": res_nb2,
           "conditions": {"c1_holm_p": cond1, "c2_stability": cond2,
                          "c3_concentration_guard": cond3, "c4_lopo": cond4},
           "guard_stress_nongating": stress,
           "trend": {"beta": res_m2.get("trend_beta_hat"),
                     "ci_percentile": res_m2.get("trend_ci_percentile"),
                     "source": "same PASS-E draws (engine)"},
           "event_study": event_study(base, wb_label, B=B, seed=seed),
           "placebo_2016": placebo_2016(base, wb_label, B=B, seed=seed),
           "h_shared": hshared(base, B=B, seed=seed)}
    if docs is not None:
        prev = validation_prevalence(docs, wb_label)
        brd = validation_breadth(docs, wb_label)
        out["validation"] = {"prevalence": prev, "breadth": brd,
                             "consistency": consistency_rule(beta_m2, prev, brd)}
    out["panel_pass_at_supplied_alpha"] = bool(          # round-7 item 6:
        cond1["ok"] and cond2["ok"] and cond3["ok"]      # holm_family owns
        and cond4["ok"])                                 # the governing pass
    return _jsonable(out)


# ------------------------------------------ B6 four-state family decision --
def holm_family(panel_results: dict[str, dict], viable: list[str],
                alpha: float = 0.05, p0_failed: bool = False) -> dict:
    """Frozen four-state rule (amendment B6): both viable -> Holm
    (alpha/2, alpha) step-down; one viable -> singleton at alpha; none viable
    and P0 failed -> fallback state. Panels are never promoted."""
    viable = [v for v in viable if v in panel_results]
    if not viable and not p0_failed:          # round-7: impossible state
        raise ValueError("invalid family state: no viable panels while P0 has "
                         "not failed (PREREG SS2/SS5/SS11)")
    state = {2: "holm_pair", 1: "singleton", 0: "fallback"}[
        min(len(viable), 2)]
    decisions = {}
    if len(viable) >= 2:
        pv = {k: panel_results[k]["conditions"]["c1_holm_p"]["p_pass_p"]
              for k in viable}
        order = sorted(pv, key=pv.get)
        lo, hi = order[0], order[1]
        r_lo = pv[lo] < alpha / 2
        r_hi = bool(r_lo and pv[hi] < alpha)
        levels = {lo: alpha / 2, hi: alpha}
        rej = {lo: bool(r_lo), hi: r_hi}
        for k in viable:
            c = dict(panel_results[k]["conditions"])
            c1 = dict(c["c1_holm_p"], alpha_holm=levels[k], ok=rej[k])
            others_ok = all(c[x]["ok"] for x in
                            ("c2_stability", "c3_concentration_guard",
                             "c4_lopo"))
            decisions[k] = {"alpha_holm": levels[k], "c1_ok": rej[k],
                            "panel_pass": bool(rej[k] and others_ok)}
    elif len(viable) == 1:
        k = viable[0]
        c = panel_results[k]["conditions"]
        c1 = c["c1_holm_p"]["p_pass_p"] < alpha
        others_ok = all(c[x]["ok"] for x in
                        ("c2_stability", "c3_concentration_guard", "c4_lopo"))
        decisions[k] = {"alpha_holm": alpha, "c1_ok": bool(c1),
                        "panel_pass": bool(c1 and others_ok)}
    passing = [k for k, v in decisions.items() if v["panel_pass"]]
    family_pass = bool(passing)
    sentence = None
    if family_pass:
        sentence = ("a differential post-2022 change between the prespecified "
                    "WB and IMF series in the frozen lexical outcome; "
                    "mechanism unresolved")
        if set(viable) == {"P1", "P2"} and len(passing) == 1:
            other = ({"P1", "P2"} - set(passing)).pop()
            o = panel_results[other]["primary_m2"]
            sentence += (f" (panel {passing[0]}; panel {other}: "
                         f"beta={o['beta_hat']:+.3f}, "
                         f"95% CI {o['ci_percentile']})")
    return _jsonable({"state": state, "viable": viable, "alpha": alpha,
                      "p0_failed": bool(p0_failed), "decisions": decisions,
                      "family_pass": family_pass, "passing_panels": passing,
                      "headline_template": sentence})


# ------------------------------------------------------------------- CLI --
def _load_panel_inputs(spec: dict):
    cells = pd.read_csv(spec["cells"])
    docs = pd.read_csv(spec["docs"]) if spec.get("docs") else None
    std = pd.read_csv(spec["std_docs"]) if spec.get("std_docs") else None
    return cells, docs, std


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("panel")
    p.add_argument("--cells", required=True)
    p.add_argument("--docs")
    p.add_argument("--std-docs")
    p.add_argument("--panel", default="P1")
    p.add_argument("--alpha-holm", type=float, default=0.05)
    f = sub.add_parser("family")
    f.add_argument("--spec", required=True,
                   help="YAML: panels: {P1: {cells,docs,std_docs}, ...}; "
                        "viable: [P1, P2]; p0_failed: false")
    for x in (p, f):
        x.add_argument("--B", type=int, default=9999)
        x.add_argument("--seed", type=int, default=SEED)
        x.add_argument("--out")
        x.add_argument("--i-am-post-sap", action="store_true",
                       help="REQUIRED. PREREG SS11 freeze discipline: no WB "
                            "outcome analysis before the SAP timestamp.")
    a = ap.parse_args()
    if not a.i_am_post_sap:
        raise SystemExit("[s13] REFUSING to run: pass --i-am-post-sap only "
                         "after the SAP is externally timestamped (PREREG "
                         "SS11). Fixture tests import the functions directly.")
    if a.cmd == "panel":
        cells, docs, std = _load_panel_inputs(
            {"cells": a.cells, "docs": a.docs, "std_docs": a.std_docs})
        res = run_panel(cells, a.panel, docs, std,
                        alpha_holm=a.alpha_holm, B=a.B, seed=a.seed)
    else:
        spec = yaml.safe_load(Path(a.spec).read_text())
        panel_results = {}
        for name, ps in spec["panels"].items():
            cells, docs, std = _load_panel_inputs(ps)
            panel_results[name] = run_panel(cells, name, docs, std,
                                            confirmatory=True,
                                            B=a.B, seed=a.seed)
        res = {"panels": panel_results,
               "family": holm_family(panel_results, spec.get("viable", []),
                                     alpha=spec.get("alpha", 0.05),
                                     p0_failed=spec.get("p0_failed", False))}
    txt = json.dumps(res, indent=2)
    print(txt)
    if a.out:
        Path(a.out).write_text(txt)


if __name__ == "__main__":
    main()
