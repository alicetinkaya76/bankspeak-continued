"""PREREG v0.5 §4 primary model + §4.2 two-pass inference (round-6 repairs).

Round-6 blockers repaired here:
 - build_design rejects duplicate/malformed cells (exactly one row per
   institution×year; finite tokens>0; counts >=0, integer unless
   allow_noninteger for standardized cells, which also disables rounding);
 - NB2 path made a valid QML score test: alpha by frozen method-of-moments
   (clip [0,10]) from the Poisson fit, score contribution carries 1/(1+alpha*mu),
   PASS-E uses V=mu+alpha*mu^2, non-convergence falls back to the
   delete-one-year Poisson jackknife CI;
 - PASS-E additionally records the WB_cyear coefficient from the SAME draws
   (trend_beta_hat / trend_ci_percentile; PREREG v0.5 SS9 differential-trend CI);
 - PASS-E counts returned non-converged fits as failures, emits
   small_count_regime (floored share > 5%), names the governing CI after the
   escalation ladder, and freezes NumPy ties-to-even rounding explicitly.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm

POST_LO, POST_HI = 2023, 2025
BLOCK_LEN = 3
SEED = 20260806
CI_SEED_OFFSET = 500_000
ALPHA_CLIP = (0.0, 10.0)
FAIL_HARD, FAIL_SOFT, FLOOR_FLAG = 0.5, 0.01, 0.05   # SS4.2 escalation ladder

def mom_alpha(y, mu) -> float:
    """Frozen NB2 dispersion estimator: max(0, sum((y-mu)^2 - mu)/sum(mu^2))."""
    num = float(np.sum((y - mu) ** 2 - mu)); den = float(np.sum(mu ** 2))
    return float(np.clip(num / den if den > 0 else 0.0, *ALPHA_CLIP))

def build_design(cells: pd.DataFrame, wb_label: str, allow_noninteger: bool = False):
    df = cells.copy()
    for c in ("institution", "year", "count", "tokens"):
        if c not in df.columns:
            raise ValueError(f"cells missing column {c!r}")
    dup = df.duplicated(subset=["institution", "year"])
    if dup.any():
        bad = df.loc[dup, ["institution", "year"]].to_records(index=False).tolist()
        raise ValueError(f"duplicate institution-year cells: {bad}")
    if not np.all(np.isfinite(df["tokens"])) or (df["tokens"] <= 0).any():
        raise ValueError("tokens must be finite and > 0 in every cell")
    if not np.all(np.isfinite(df["count"])) or (df["count"] < 0).any():
        raise ValueError("counts must be finite and >= 0")
    if not allow_noninteger:
        cvals = df["count"].to_numpy(dtype=float)
        if not np.array_equal(cvals, np.round(cvals)):   # exact; no tolerance
            raise ValueError("non-integer counts require allow_noninteger=True "
                             "(standardized cells); counts must equal their "
                             "rounded values exactly")
    df = df.sort_values(["year", "institution"]).reset_index(drop=True)
    years = np.array(sorted(df["year"].unique()))
    insts = sorted(df["institution"].unique())
    if len(insts) != 2 or wb_label not in insts:
        raise ValueError(f"need exactly 2 institutions incl. {wb_label!r}; got {insts}")
    if (df.groupby("year").size() != 2).any():
        raise ValueError("common-year rule violated: exactly one cell per "
                         "institution per year")
    m = float(np.median(years))
    wb = (df["institution"] == wb_label).astype(float).to_numpy()
    c_year = df["year"].to_numpy() - m
    post = ((df["year"] >= POST_LO) & (df["year"] <= POST_HI)).astype(float).to_numpy()
    ydum = pd.get_dummies(df["year"], drop_first=True, dtype=float)
    X = np.column_stack([np.ones(len(df)), ydum.to_numpy(), wb, wb * c_year, wb * post])
    names = ["const"] + [f"y{c}" for c in ydum.columns] + ["WB", "WB_cyear", "WB_post"]
    y = df["count"].to_numpy(dtype=float)
    off = np.log(df["tokens"].to_numpy(dtype=float))
    return df, X, names, y, off, years

def _fit(y, X, off, family):
    return sm.GLM(y, X, family=family, offset=off).fit()

def _converged(res) -> bool:
    return bool(getattr(res, "converged", True))

def _pair_index(df, years, wb_label):
    pos = {yy: k for k, yy in enumerate(years)}
    T = len(years)
    pair = np.full((T, 2), -1, dtype=int)
    for i, row in df.iterrows():
        pair[pos[row["year"]], 0 if row["institution"] == wb_label else 1] = i
    return pair, T

def wild_score_p(y, X, off, names, pair, T, B, block_len, seed, nb2: bool):
    """PASS-P: studentized block wild score test for WB_post (Poisson QML mean;
    NB2 handled as a working-variance QML score with frozen MoM alpha)."""
    j = names.index("WB_post")
    Xr = np.delete(X, j, axis=1)
    restr = _fit(y, Xr, off, sm.families.Poisson())
    mu0 = np.asarray(restr.fittedvalues)
    alpha = mom_alpha(y, mu0) if nb2 else 0.0
    W = mu0 / (1.0 + alpha * mu0)
    xj = X[:, j]
    A = Xr * W[:, None]
    coef, *_ = np.linalg.lstsq(Xr.T @ A, Xr.T @ (W * xj), rcond=None)
    x_t = xj - Xr @ coef
    s = x_t * (y - mu0) / (1.0 + alpha * mu0)      # NB2 quasi-score factor
    S_year = np.array([s[pair[k]].sum() for k in range(T)])
    n_blocks = int(np.ceil(T / block_len))
    S_block = np.array([S_year[b*block_len:(b+1)*block_len].sum()
                        for b in range(n_blocks)])
    denom = float(np.sqrt((S_block ** 2).sum()))
    if denom == 0.0:
        return 1.0, B, alpha
    T_obs = float(S_block.sum()) / denom
    hits = 0
    for b in range(B):
        eta = np.random.default_rng(seed + b).choice([-1.0, 1.0], size=n_blocks)
        if abs(float((eta * S_block).sum()) / denom) >= abs(T_obs):
            hits += 1
    return (1 + hits) / (B + 1), B, alpha

def jackknife_ci(cells, wb_label, allow_noninteger=False):
    """Delete-one-year Poisson QML jackknife CI for WB_post (NB2 fallback)."""
    df, X, names, y, off, years = build_design(cells, wb_label, allow_noninteger)
    j = names.index("WB_post")
    full = _fit(y, X, off, sm.families.Poisson())
    if not _converged(full):                 # round-7: fallback is fail-closed
        raise RuntimeError("jackknife fallback: full Poisson fit non-converged")
    th = []
    for yy in years:
        sub = cells[cells["year"] != yy]
        d2, X2, n2, y2, off2, _ = build_design(sub, wb_label, allow_noninteger)
        r2 = _fit(y2, X2, off2, sm.families.Poisson())
        if not _converged(r2):
            raise RuntimeError("jackknife fallback: deletion fit non-converged "
                               f"(year {yy})")
        th.append(float(r2.params[n2.index("WB_post")]))
    th = np.asarray(th); Tn = len(th)
    se = float(np.sqrt((Tn - 1) / Tn * np.sum((th - th.mean()) ** 2)))
    b = float(full.params[j])
    return [b - 1.96 * se, b + 1.96 * se], se

def _jackknife_multi(cells, design_fn, coef_names, wb_label,
                     allow_noninteger, fit_fn=None):
    """Delete-one-year Poisson QML jackknife for an arbitrary design's named
    coefficients (frozen NB2 fallback, generalized; fail-closed: any
    non-converged fit or vanished coefficient raises)."""
    fit_fn = fit_fn or _fit
    df, _X0, _n0, y, off, years = build_design(cells, wb_label, allow_noninteger)
    X, names = design_fn(df)
    full = fit_fn(y, X, off, sm.families.Poisson())
    if not _converged(full):
        raise RuntimeError("jackknife_multi: full Poisson fit non-converged")
    beta = {k: float(full.params[names.index(k)]) for k in coef_names}
    th = {k: [] for k in coef_names}
    for yy in years:
        sub = cells[cells["year"] != yy]
        d2, _x, _n, y2, off2, _yrs = build_design(sub, wb_label, allow_noninteger)
        X2, n2 = design_fn(d2)
        r2 = fit_fn(y2, X2, off2, sm.families.Poisson())
        if not _converged(r2):
            raise RuntimeError("jackknife_multi: deletion fit non-converged "
                               f"(year {yy})")
        for k in coef_names:
            if k not in n2:
                raise RuntimeError(f"jackknife_multi: coefficient {k} vanished "
                                   f"in the year-{yy} deletion design")
            th[k].append(float(r2.params[n2.index(k)]))
    out = {}
    for k, arr in th.items():
        a = np.asarray(arr); Tn = len(a)
        se = float(np.sqrt((Tn - 1) / Tn * np.sum((a - a.mean()) ** 2)))
        out[k] = {"beta": beta[k], "ci": [beta[k] - 1.96 * se,
                                          beta[k] + 1.96 * se],
                  "se_jackknife": se}
    return out


def passe_multi(cells, design_fn, coef_names, wb_label="WB", B=9999,
                block_len=BLOCK_LEN, seed=SEED, seed_offset=CI_SEED_OFFSET,
                nb2=False, allow_noninteger=False, fit_fn=None):
    """Generalized PASS-E for an arbitrary full-model design, sharing the FULL
    SS4.2 machinery (round-7 repair): Poisson QML -> frozen MoM alpha -> NB2
    family; convergence-counted paired circular block transplant (replicate b
    seeded seed+seed_offset+b); TRUE floored share + small-count flag;
    percentile + Wald-boot CIs per named coefficient under the governing
    escalation ladder (>FAIL_SOFT -> wald_boot governs; >FAIL_HARD or zero
    valid -> failed); NB2 full-fit non-convergence -> delete-one-year Poisson
    jackknife, itself fail-closed; noninteger reconstruction mode.
    estimation_ci keeps its own frozen loop for WB_post/WB_cyear (selftest
    values pinned bit-identical); the shared threshold constants guard drift."""
    fit_fn = fit_fn or _fit
    df, _X0, _n0, y, off, years = build_design(cells, wb_label, allow_noninteger)
    pair, T = _pair_index(df, years, wb_label)
    X, names = design_fn(df)
    missing = [k for k in coef_names if k not in names]
    if missing:
        raise ValueError(f"design lacks coefficients {missing}")
    # round-8 estimability guards: every requested coefficient's column must
    # have support, and the design must be full column rank — an all-zero or
    # collinear column yields numerical residue, not an estimate.
    for k in coef_names:
        if not np.any(X[:, names.index(k)] != 0):
            raise ValueError(f"design column {k} has no support (all-zero) "
                             "— not estimable")
    if np.linalg.matrix_rank(X) < X.shape[1]:
        raise ValueError("design matrix is rank deficient — not estimable")
    fam_p = sm.families.Poisson()
    full_p = fit_fn(y, X, off, fam_p)
    alpha = mom_alpha(y, np.asarray(full_p.fittedvalues)) if nb2 else 0.0
    fam = (sm.families.NegativeBinomial(alpha=alpha)
           if nb2 and alpha > 0 else fam_p)
    try:
        full = fit_fn(y, X, off, fam)
        assert _converged(full)
    except Exception:
        try:
            jk = _jackknife_multi(cells, design_fn, coef_names, wb_label,
                                  allow_noninteger, fit_fn)
        except Exception:
            return {"alpha_hat": alpha, "method_ci": "jackknife_failed",
                    "governing_ci": "failed", "B_valid_ci": 0,
                    "ci_fail_rate": 1.0, "true_floored_share": float("nan"),
                    "small_count_regime": False, "rounding": "n/a",
                    "coefs": {k: {"beta": float("nan"),
                                  "ci_percentile": [float("nan")] * 2}
                              for k in coef_names}}
        return {"alpha_hat": alpha, "method_ci": "jackknife_fallback",
                "governing_ci": "jackknife_poisson", "B_valid_ci": 0,
                "ci_fail_rate": 1.0, "true_floored_share": float("nan"),
                "small_count_regime": False, "rounding": "n/a",
                "coefs": {k: {"beta": jk[k]["beta"],
                              "ci_percentile": jk[k]["ci"],
                              "se_jackknife": jk[k]["se_jackknife"]}
                          for k in coef_names}}
    beta = {k: float(full.params[names.index(k)]) for k in coef_names}
    mu = np.asarray(full.fittedvalues)
    V = mu * (1.0 + alpha * mu) if alpha > 0 else mu
    sd = np.sqrt(V)
    r = (y - mu) / sd
    n_blocks = int(np.ceil(T / block_len))
    stats = {k: [] for k in coef_names}
    fails, floor_events, cells_total = 0, 0, 0
    for b in range(B):
        rng = np.random.default_rng(seed + seed_offset + b)
        starts = rng.integers(0, T, size=n_blocks)
        order = np.concatenate([(s0 + np.arange(block_len)) % T
                                for s0 in starts])[:T]
        rstar = np.empty_like(r)
        for k_new, k_src in enumerate(order):
            rstar[pair[k_new]] = r[pair[k_src]]
        recon = mu + sd * rstar
        floor_events += int((recon < 0).sum()); cells_total += recon.size
        ystar = np.maximum(0.0, recon if allow_noninteger else np.round(recon))
        try:
            res = fit_fn(ystar, X, off, fam)
            if not _converged(res):
                fails += 1; continue
            for k in coef_names:
                stats[k].append(float(res.params[names.index(k)]))
        except Exception:
            fails += 1
    floored = floor_events / max(1, cells_total)
    fail_rate = fails / B
    n_valid = len(stats[coef_names[0]]) if coef_names else 0
    out = {"alpha_hat": alpha, "B_valid_ci": int(n_valid),
           "ci_fail_rate": fail_rate, "true_floored_share": floored,
           "small_count_regime": bool(floored > FLOOR_FLAG),
           "rounding": "none" if allow_noninteger else "numpy-ties-to-even"}
    if fail_rate > FAIL_HARD or n_valid == 0:
        out.update(method_ci="failed", governing_ci="failed",
                   coefs={k: {"beta": beta[k],
                              "ci_percentile": [float("nan")] * 2}
                          for k in coef_names})
        return out
    method = "percentile" if fail_rate <= FAIL_SOFT else "wald_boot"
    coefs = {}
    for k in coef_names:
        arr = np.asarray(stats[k])
        lo, hi = np.quantile(arr, [0.025, 0.975])
        sd_b = float(arr.std(ddof=1))
        coefs[k] = {"beta": beta[k],
                    "ci_percentile": [float(lo), float(hi)],
                    "ci_wald_boot": [beta[k] - 1.96 * sd_b,
                                     beta[k] + 1.96 * sd_b],
                    "sd_boot": sd_b}
    out.update(method_ci=method,
               governing_ci=("ci_percentile" if method == "percentile"
                             else "ci_wald_boot"), coefs=coefs)
    return out


def estimation_ci(cells, y, X, off, names, pair, T, B, block_len, seed,
                  nb2: bool, wb_label: str, allow_noninteger: bool,
                  fit_fn=None):
    """PASS-E: full-model paired circular-block residual transplant."""
    fit_fn = fit_fn or _fit
    j = names.index("WB_post")
    jt = names.index("WB_cyear") if "WB_cyear" in names else None
    fam_p = sm.families.Poisson()
    full_p = fit_fn(y, X, off, fam_p)
    alpha = mom_alpha(y, np.asarray(full_p.fittedvalues)) if nb2 else 0.0
    fam = sm.families.NegativeBinomial(alpha=alpha) if nb2 and alpha > 0 else fam_p
    try:
        full = fit_fn(y, X, off, fam)
        assert _converged(full)
    except Exception:
        try:
            ci, se = jackknife_ci(cells, wb_label, allow_noninteger)  # frozen
        except Exception:                    # round-7: affected condition fails
            return {"beta_hat": float(full_p.params[j]), "alpha_hat": alpha,
                    "trend_beta_hat": (float(full_p.params[jt]) if jt is not None
                                       else float("nan")),
                    "trend_ci_percentile": [float("nan")] * 2,
                    "ci_percentile": [float("nan")] * 2,
                    "governing_ci": "failed", "method_ci": "jackknife_failed",
                    "sd_boot": float("nan"), "B_valid_ci": 0,
                    "ci_fail_rate": 1.0, "true_floored_share": float("nan"),
                    "small_count_regime": False, "rounding": "n/a"}
        return {"beta_hat": float(full_p.params[j]), "alpha_hat": alpha,
                "trend_beta_hat": (float(full_p.params[jt]) if jt is not None
                                   else float("nan")),
                "trend_ci_percentile": [float("nan")] * 2,
                "ci_percentile": ci, "governing_ci": "jackknife_poisson",
                "method_ci": "jackknife_fallback", "sd_boot": se,
                "B_valid_ci": 0, "ci_fail_rate": 1.0,
                "true_floored_share": float("nan"), "small_count_regime": False,
                "rounding": "n/a"}
    beta_hat = float(full.params[j])
    trend_hat = float(full.params[jt]) if jt is not None else float("nan")
    mu = np.asarray(full.fittedvalues)
    V = mu * (1.0 + alpha * mu) if alpha > 0 else mu
    sd = np.sqrt(V)
    r = (y - mu) / sd
    n_blocks = int(np.ceil(T / block_len))
    stats, stats_t, fails, floor_events, cells_total = [], [], 0, 0, 0
    for b in range(B):
        rng = np.random.default_rng(seed + CI_SEED_OFFSET + b)
        starts = rng.integers(0, T, size=n_blocks)
        order = np.concatenate([(s0 + np.arange(block_len)) % T
                                for s0 in starts])[:T]
        rstar = np.empty_like(r)
        for k_new, k_src in enumerate(order):
            rstar[pair[k_new]] = r[pair[k_src]]
        recon = mu + sd * rstar
        floor_events += int((recon < 0).sum()); cells_total += recon.size
        ystar = np.maximum(0.0, recon if allow_noninteger else np.round(recon))
        try:
            res = fit_fn(ystar, X, off, fam)
            if not _converged(res):
                fails += 1; continue
            stats.append(float(res.params[j]))
            stats_t.append(float(res.params[jt]) if jt is not None
                           else float("nan"))
        except Exception:
            fails += 1
    stats = np.asarray(stats); stats_t = np.asarray(stats_t)
    floored = floor_events / max(1, cells_total)
    fail_rate = fails / B
    out = {"beta_hat": beta_hat, "alpha_hat": alpha,
           "trend_beta_hat": trend_hat,
           "B_valid_ci": int(len(stats)), "ci_fail_rate": fail_rate,
           "true_floored_share": floored,
           "small_count_regime": bool(floored > FLOOR_FLAG),
           "rounding": "none" if allow_noninteger else "numpy-ties-to-even"}
    if fail_rate > FAIL_HARD or len(stats) == 0:
        out.update(ci_percentile=[float("nan")] * 2, method_ci="failed",
                   governing_ci="failed",
                   trend_ci_percentile=[float("nan")] * 2)
        return out
    lo, hi = np.quantile(stats, [0.025, 0.975])
    tlo, thi = (np.quantile(stats_t, [0.025, 0.975])
                if jt is not None and len(stats_t) else (float("nan"),) * 2)
    sd_b = float(stats.std(ddof=1))
    wald = [beta_hat - 1.96 * sd_b, beta_hat + 1.96 * sd_b]
    method = "percentile" if fail_rate <= FAIL_SOFT else "wald_boot"
    out.update(ci_percentile=[float(lo), float(hi)], ci_wald_boot=wald,
               trend_ci_percentile=[float(tlo), float(thi)],
               sd_boot=sd_b, method_ci=method,
               governing_ci=("ci_percentile" if method == "percentile"
                             else "ci_wald_boot"))
    return out

def two_pass(cells: pd.DataFrame, wb_label: str = "WB", B: int = 9999,
             block_len: int = BLOCK_LEN, seed: int = SEED,
             nb2: bool = False, allow_noninteger: bool = False,
             fit_fn=None) -> dict:
    df, X, names, y, off, years = build_design(cells, wb_label, allow_noninteger)
    pair, T = _pair_index(df, years, wb_label)
    p, Bp, alpha_p = wild_score_p(y, X, off, names, pair, T, B, block_len,
                                  seed, nb2)
    res = estimation_ci(cells, y, X, off, names, pair, T, B, block_len, seed,
                        nb2, wb_label, allow_noninteger, fit_fn)
    res.update(p_two_sided=p, method_p="wild_score_block", B_valid_p=Bp,
               alpha_hat_p=alpha_p, T_common_years=T, block_len=block_len,
               estimand="WB_post (log-rate)")
    return res

block_bootstrap = two_pass   # backward-compatible name

def _mk(theta, tokens, seed=7, overdisp=0.0):
    rng = np.random.default_rng(seed); rows = []
    for yy in range(1994, 2026):
        g = rng.normal(0, overdisp) if overdisp else 0.0
        for inst in ("WB", "IMF"):
            bump = theta if (inst == "WB" and POST_LO <= yy <= POST_HI) else 0.0
            gd = rng.normal(0, overdisp) if overdisp else 0.0
            lam = np.exp(np.log(6e-5) + bump + g + gd) * tokens
            rows.append({"institution": inst, "year": yy,
                         "count": int(rng.poisson(lam)), "tokens": tokens})
    return pd.DataFrame(rows)

def _selftest() -> None:
    for tag, th, tok, nb2, od in [("null-large", 0.0, 2_000_000, False, 0.0),
                                  ("effect-large", 0.9, 2_000_000, False, 0.0),
                                  ("null-small", 0.0, 40_000, False, 0.0),
                                  ("nb2-overdispersed", 0.0, 2_000_000, True, 0.35)]:
        r = two_pass(_mk(th, tok, overdisp=od), B=299, nb2=nb2)
        inside = r["ci_percentile"][0] <= r["beta_hat"] <= r["ci_percentile"][1]
        print(f"[selftest {tag}] beta={r['beta_hat']:+.3f} p={r['p_two_sided']:.3f} "
              f"ci={[round(x,3) for x in r['ci_percentile']]} beta_in_ci={inside} "
              f"floored={r['true_floored_share']:.4f} alpha={r['alpha_hat']:.3f} "
              f"governing={r['governing_ci']}")
    try:
        d = _mk(0.0, 1e6); d = pd.concat([d, d.iloc[[0]]])
        two_pass(d, B=9)
    except ValueError as e:
        print(f"[selftest duplicate-rejection] OK ({str(e)[:60]}...)")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells"); ap.add_argument("--out")
    ap.add_argument("--wb-label", default="WB")
    ap.add_argument("--B", type=int, default=9999)
    ap.add_argument("--nb2", action="store_true")
    ap.add_argument("--allow-noninteger", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        _selftest(); return
    res = two_pass(pd.read_csv(a.cells), wb_label=a.wb_label, B=a.B,
                   nb2=a.nb2, allow_noninteger=a.allow_noninteger)
    print(json.dumps(res, indent=2))
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
