#!/usr/bin/env python3
"""Calibrate the preregistered decision rule as a FAMILY, jointly, exactly.

S10.4 measured something real and reported it as something else. What it
measured: the per-panel probability that PASS-P's raw two-sided p falls below
0.05, with P1 and P2 simulated in separate loops under each panel's own fitted
null, and with the inner p sampled by Monte Carlo. What the manuscript said it
measured: the size of the governing test. Those are not the same quantity, and
three separate things stand between them.

  1. The panels are not independent. P1 is ICR x IMF and P2 is PAD x IMF, and
     the IMF arm is not merely similar across the two panels -- it is the same
     twenty-seven cells, byte for byte. Half of every panel is shared. Drawing
     the two panels in separate loops throws that away and replaces a strongly
     dependent pair with an independent one.
  2. The rule is not a raw threshold. PREREG SS5/B6 (src/s13_validation_battery
     .holm_family) sorts the two p-values and rejects the smaller only at
     alpha/2 = 0.025, the larger only at alpha = 0.05, and calls the family
     confirmed only if some panel clears Holm AND C2 AND C3 AND C4. A raw 0.05
     rate is not an estimate of that.
  3. The inner p does not need sampling. Twenty-seven years partition into nine
     three-year blocks, so the sign support is exactly 2^9 = 512 and the
     p-value is a count, not a draw. S10.4 sampled B = 999 signs out of 512
     possible ones, which adds resolution noise to a quantity that has none.

External review made all three points and ran its own joint diagnostic. This
answers with the full ladder, because the honest result is not one number: the
family error rate depends on the null's mean structure far more than on
anything the Holm step does, and the ladder is what shows that.

  s10_4_asbuilt        per-panel fitted null, panels independent, MC inner p
  s10_4_exact          the same, inner p enumerated instead of sampled
  s10_4_exact_holm     the same, with Holm applied -- FWER under independence
  fitted_joint         one shared year profile, ONE IMF draw feeding both
                       panels, one shared WB shock -- the real dependence
  fitted_joint_indep   the same means, but independent WB shocks
  fitted_joint_no_*    the same means with the year profile and/or the WB
                       differential trend switched off, one at a time
  observed_rates_flat  no year effects; each series at its own pooled rate
  prereg_obs_tokens    PREREG SS8's flat parity rate on observed tokens
  prereg_literal       PREREG SS8 exactly: projected tokens, IMF at parity,
                       delta starting at zero -- reproduces the 0.039 that
                       docs/MDE_P1P2_20260820.md has recorded since August

The ladder's two ends differ by a factor of three and both are defensible
nulls. That is the finding, and none of the three defects above is what makes
the difference: enumerating the inner p moves nothing, and applying Holm to
jointly drawn panels LOWERS the family error, because a shared comparator arm
makes the two p-values positively dependent and for two hypotheses Holm's worst
case is independence.

What moves it is the null's mean structure, and the component scenarios say
which part: switching off the World Bank differential trend costs more than
switching off the year profile, switching off both lands on the flat null, and
the flat null is CONSERVATIVE under the same shock that makes the fitted null
anti-conservative.

Two candidate mechanisms were tested here and BOTH are refuted by this tool's
own diagnostics. They are left in the output so nobody has to take the refutal
on trust.

  shock-to-noise. observed_rates_flat carries a HIGHER ratio of shock sd to
  sampling noise than fitted_joint, and less than half its family error. The
  ratio cannot be the cause.

  block-nine leverage. The share of the statistic's variance sitting in the
  last block runs 0.33-0.37 in the inflated scenarios and 0.44-0.48 in the
  well-behaved ones -- the wrong way round. It runs the wrong way for a
  reason: when one block dominates the studentised denominator, |eta.S| is
  close to |sum S| for every sign pattern, so nearly all 512 patterns count as
  hits and the test goes conservative. High leverage buys conservatism here,
  not size.

What IS established, and is all that should be claimed:

  1. Under the fitted mean structure the test is correctly sized with no shock
     at all (0.045) and anti-conservative with one.
  2. Roughly two fifths of the excess survives at rho = 0 -- an i.i.d.
     multiplicative World Bank overdispersion, no serial dependence anywhere
     (0.063 against 0.045). So "serial dependence is the cause" is too strong;
     unmodelled one-armed overdispersion is doing a large part of it.
  3. Under a flat mean structure the same shock at the same rho and sigma
     produces 0.028 -- below nominal.

No third mechanism is offered. The ladder is reproducible and the numbers are
what they are; the reason the mean structure matters this much is not
established here and is not asserted.

C2 and C3 are not simulated -- C2 needs a standardized document-level redraw
and C3 needs the guard count series, and inventing null processes for those
would be modelling, not calibration. C4 is simulated where marked, because it
is computable from the same cells. Since the governing rule is a conjunction,
every family rate here is an UPPER BOUND on the rate of the full C1-C4 rule.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from bootstrap_engine import (build_design, _fit, _pair_index,      # noqa: E402
                              POST_LO, POST_HI, BLOCK_LEN, SEED)

ALPHA = 0.05                       # PREREG SS5 family alpha; Holm gives .025/.05
RHO, SIGMA_DELTA = 0.5, 0.3205     # PREREG SS8; SIGMA_DELTA is the INNOVATION sd
ALPHA_NB2 = {"P1": 0.0520, "P2": 0.0425}   # dof-corrected, S10.4a
PREREG_RATE = 2.767e-5             # PREREG SS8 base rate, per token, IMF at parity
PANELS = ("P1", "P2")
CELLS = {p: ROOT / "data" / "analysis" / "panels" / f"cells_{p}.csv" for p in PANELS}
TEMPLATES = {"P1": ROOT / "data/analysis/mde_p1p2/template_p1.csv",
             "P2": ROOT / "data/analysis/mde_p1p2/template_p2.csv",
             "IMF": ROOT / "data/analysis/mde_p1p2/template_imf.csv"}
OUT = ROOT / "data" / "analysis" / "joint_holm_calibration.json"


# --------------------------------------------------------------- machinery --
def irls_poisson(y, X, off, tol=1e-13, maxit=200):
    """Poisson IRLS returning fitted means.

    Same estimator as the frozen engine's statsmodels GLM; kept separate only
    because this runs it a few hundred thousand times. _assert_irls_matches
    pins it against statsmodels on the real cells before any scenario runs, so
    the speed is not bought with a different answer.
    """
    b, *_ = np.linalg.lstsq(X, np.log(y + 0.5) - off, rcond=None)
    for _ in range(maxit):
        eta = X @ b + off
        mu = np.exp(eta)
        z = eta - off + (y - mu) / mu
        A = X * mu[:, None]
        bn, *_ = np.linalg.lstsq(X.T @ A, X.T @ (mu * z), rcond=None)
        if np.max(np.abs(bn - b)) < tol:
            return np.exp(X @ bn + off), bn
        b = bn
    return np.exp(X @ b + off), b


def _signs(n_blocks: int) -> np.ndarray:
    return np.array(list(itertools.product([-1.0, 1.0], repeat=n_blocks)))


_SIGN_CACHE: dict[int, np.ndarray] = {}


def sign_matrix(n_blocks: int) -> np.ndarray:
    if n_blocks not in _SIGN_CACHE:
        _SIGN_CACHE[n_blocks] = _signs(n_blocks)
    return _SIGN_CACHE[n_blocks]


class Design:
    """Everything about a panel's design that does not change with the counts.

    X, the offset and the year pairing are fixed by the years and the token
    vector, so they are built once. Only y is redrawn.
    """

    def __init__(self, cells: pd.DataFrame):
        df, X, names, y, off, years = build_design(
            cells[["institution", "year", "count", "tokens"]], "WB")
        self.df, self.X, self.names, self.y0, self.off = df, X, names, y, off
        self.years = years
        self.pair, self.T = _pair_index(df, years, "WB")
        self.j = names.index("WB_post")
        self.Xr = np.delete(X, self.j, axis=1)
        self.xj = X[:, self.j]
        self.wb = (df["institution"] == "WB").to_numpy()
        self.year_of = df["year"].to_numpy()
        self.tokens = df["tokens"].to_numpy(dtype=float)
        self.n_blocks = int(np.ceil(self.T / BLOCK_LEN))
        self.signs = sign_matrix(self.n_blocks)

    def exact_p(self, y: np.ndarray) -> float:
        """PASS-P's p by enumeration over all 2^n_blocks sign patterns.

        Identical arithmetic to bootstrap_engine.wild_score_p with alpha = 0
        (the confirmatory arm is Poisson QML), except that the sign vectors are
        enumerated rather than drawn, so the returned value is the exact
        randomisation p and not an estimate of it.
        """
        mu0, _ = irls_poisson(y, self.Xr, self.off)
        coef, *_ = np.linalg.lstsq(self.Xr.T @ (self.Xr * mu0[:, None]),
                                   self.Xr.T @ (mu0 * self.xj), rcond=None)
        s = (self.xj - self.Xr @ coef) * (y - mu0)
        S_year = np.array([s[self.pair[k]].sum() for k in range(self.T)])
        blocks = np.array([S_year[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum()
                           for b in range(self.n_blocks)])
        denom = float(np.sqrt((blocks ** 2).sum()))
        if denom == 0.0:
            return 1.0
        t_obs = abs(float(blocks.sum())) / denom
        stat = np.abs(self.signs @ blocks) / denom
        return float((stat >= t_obs - 1e-12).sum()) / self.signs.shape[0]

    def beta_post(self, y: np.ndarray) -> float:
        _, b = irls_poisson(y, self.X, self.off)
        return float(b[self.j])


_LOPO_CACHE: dict[tuple, Design] = {}


def lopo_design(cells: pd.DataFrame, key: str, drop_year: int) -> Design:
    k = (key, drop_year)
    if k not in _LOPO_CACHE:
        _LOPO_CACHE[k] = Design(cells[cells["year"] != drop_year])
    return _LOPO_CACHE[k]


def c4_ok(des: Design, y: np.ndarray, key: str, cells: pd.DataFrame) -> bool:
    """PREREG SS5 condition 4, exactly: delete each post year in turn; the
    UNADJUSTED PASS-P p must stay below 0.10 and the coefficient must keep its
    sign. Here the inner p is enumerated rather than sampled."""
    beta_ref = des.beta_post(y)
    if beta_ref == 0.0:
        return False
    keep_rows = {yy: (des.year_of != yy) for yy in (POST_LO, POST_LO + 1, POST_HI)}
    for yy in (POST_LO, POST_LO + 1, POST_HI):
        sub = lopo_design(cells, key, yy)
        ysub = y[keep_rows[yy]]
        if sub.exact_p(ysub) >= 0.10:
            return False
        b = sub.beta_post(ysub)
        if b == 0.0 or (b > 0) != (beta_ref > 0):
            return False
    return True


def holm2(p1: float, p2: float, alpha: float = ALPHA) -> tuple[bool, bool]:
    """PREREG SS5/B6 step-down over exactly two panels, in P1/P2 order out."""
    lo_is_1 = p1 <= p2
    plo, phi = (p1, p2) if lo_is_1 else (p2, p1)
    rlo = plo < alpha / 2
    rhi = bool(rlo and phi < alpha)
    return (rlo, rhi) if lo_is_1 else (rhi, rlo)


# ------------------------------------------------------------ null means ----
def joint_fitted_means(cells: dict[str, pd.DataFrame]) -> dict[str, np.ndarray]:
    """One shared year profile for the Fund arm, a level and a differential
    linear trend for each World Bank arm, WB_post held at zero.

    The per-panel restricted fit S10.4 used gives the IMF arm a different mean
    in each panel, which makes a shared IMF draw incoherent. Stacking the three
    series under one set of year effects fixes that: the comparator has one
    null mean, so it can be drawn once and handed to both panels the way the
    real data hand it to both panels.
    """
    imf = cells["P1"][cells["P1"]["institution"] == "IMF"].sort_values("year")
    years = imf["year"].to_numpy()
    m = float(np.median(years))
    rows_y, rows_x, rows_off = [], [], []
    ydum = np.eye(len(years))
    for k, yy in enumerate(years):                      # IMF arm
        rows_y.append(float(imf["count"].to_numpy()[k]))
        rows_x.append(np.concatenate([ydum[k], [0, 0, 0, 0]]))
        rows_off.append(np.log(float(imf["tokens"].to_numpy()[k])))
    for pi, p in enumerate(PANELS):                     # each WB arm
        wb = cells[p][cells[p]["institution"] == "WB"].sort_values("year")
        for k, yy in enumerate(wb["year"].to_numpy()):
            ind = np.zeros(4)
            ind[2 * pi] = 1.0
            ind[2 * pi + 1] = float(yy) - m
            rows_y.append(float(wb["count"].to_numpy()[k]))
            rows_x.append(np.concatenate([ydum[k], ind]))
            rows_off.append(np.log(float(wb["tokens"].to_numpy()[k])))
    y = np.array(rows_y)
    X = np.array(rows_x)
    off = np.array(rows_off)
    mu, b = irls_poisson(y, X, off)
    T = len(years)
    out = {"years": years, "IMF": mu[:T],
           "P1": mu[T:2 * T], "P2": mu[2 * T:3 * T]}
    # The pieces, kept so the ladder can switch them off one at a time. The
    # gap between this null and a flat one turned out to be the whole story,
    # and "the shock is louder here" does not explain it -- observed_rates_flat
    # has a HIGHER shock-to-noise ratio and a LOWER size. So the components
    # have to be separable or the mechanism stays a guess.
    out["_year_eff"] = b[:T]                 # shared log year profile a_t
    out["_gamma"] = {p: float(b[T + 2 * i]) for i, p in enumerate(PANELS)}
    out["_tau"] = {p: float(b[T + 2 * i + 1]) for i, p in enumerate(PANELS)}
    out["_cyear"] = years.astype(float) - float(np.median(years))
    return out


def component_means(cells, jf, keep_year: bool, keep_tau: bool):
    """The joint fitted null with the year profile and/or the World Bank
    differential trend switched off, everything else held.

    keep_year=False replaces the estimated year profile a_t with its
    token-weighted mean, so each series keeps its own average rate but loses
    the year-to-year wiggle. keep_tau=False sets the differential linear trend
    to zero, so the null's World Bank arm stops growing relative to the Fund.
    """
    years = jf["years"]
    imf = cells["P1"][cells["P1"]["institution"] == "IMF"].sort_values("year")
    tok_imf = imf["tokens"].to_numpy(dtype=float)
    a = jf["_year_eff"].copy()
    if not keep_year:
        a = np.full_like(a, float(np.average(a, weights=tok_imf)))
    out = {"years": years, "IMF": np.exp(a) * tok_imf}
    for p in PANELS:
        wb = cells[p][cells[p]["institution"] == "WB"].sort_values("year")
        tok = wb["tokens"].to_numpy(dtype=float)
        eta = a + jf["_gamma"][p]
        if keep_tau:
            eta = eta + jf["_tau"][p] * jf["_cyear"]
        out[p] = np.exp(eta) * tok
    return out


def perpanel_fitted_means(des: Design) -> np.ndarray:
    """The restricted fit S10.4 used: WB_post dropped, everything else free."""
    mu0, _ = irls_poisson(des.y0, des.Xr, des.off)
    return mu0


def flat_means(cells: dict[str, pd.DataFrame], rate: float | None):
    """No year effects at all. rate=None gives each series its own observed
    pooled rate; a number puts every series on that rate, which is what
    PREREG SS8 did when it set the comparator at parity."""
    out = {}
    imf = cells["P1"][cells["P1"]["institution"] == "IMF"].sort_values("year")
    out["years"] = imf["year"].to_numpy()
    tk = imf["tokens"].to_numpy(dtype=float)
    r = rate if rate is not None else imf["count"].sum() / tk.sum()
    out["IMF"] = r * tk
    for p in PANELS:
        wb = cells[p][cells[p]["institution"] == "WB"].sort_values("year")
        tk = wb["tokens"].to_numpy(dtype=float)
        r = rate if rate is not None else wb["count"].sum() / tk.sum()
        out[p] = r * tk
    return out


def template_means(rate: float):
    """PREREG SS8's own projected token vectors, all series at `rate`.

    These tokens are NOT the observed ones, so a scenario built on them needs
    its own design: the model's offset has to be the same token vector the
    counts were generated against, or the simulated series carries a
    year-varying rate the design cannot see. Carried as `tokens`.
    """
    out, tok = {}, {}
    t = pd.read_csv(TEMPLATES["IMF"]).sort_values("year")
    out["years"] = t["year"].to_numpy()
    tok["IMF"] = t["tokens"].to_numpy(dtype=float)
    out["IMF"] = rate * tok["IMF"]
    for p in PANELS:
        t = pd.read_csv(TEMPLATES[p]).sort_values("year")
        if not np.array_equal(t["year"].to_numpy(), out["years"]):
            raise SystemExit(f"[joint] template {p} covers different years "
                             "than the IMF template")
        tok[p] = t["tokens"].to_numpy(dtype=float)
        out[p] = rate * tok[p]
    out["tokens"] = tok
    return out


def designs_for_tokens(means: dict) -> dict[str, Design]:
    """A design per panel whose offset is the scenario's own token vector."""
    tok = means["tokens"]
    out = {}
    for p in PANELS:
        rows = []
        for k, yy in enumerate(means["years"]):
            rows.append({"institution": "WB", "year": int(yy),
                         "count": int(round(means[p][k])), "tokens": tok[p][k]})
            rows.append({"institution": "IMF", "year": int(yy),
                         "count": int(round(means["IMF"][k])),
                         "tokens": tok["IMF"][k]})
        out[p] = Design(pd.DataFrame(rows))
    return out


# ------------------------------------------------------------- simulation ---
def ar1(rng, T, rho, sigma, start):
    d = np.empty(T)
    d[0] = 0.0 if start == "zero" else rng.normal(0, sigma / np.sqrt(1 - rho ** 2))
    for t in range(1, T):
        d[t] = rho * d[t - 1] + rng.normal(0, sigma)
    return d


def block_leverage(spec, designs, means, rho, sigma, n=400) -> dict:
    """How much of the test statistic's mass block nine carries.

    PASS-P studentises by sqrt(sum(S_block^2)) and then flips nine signs as if
    the nine blocks were exchangeable. They are not: if the null's World Bank
    arm grows, the late years carry larger counts, the score's variance
    concentrates there, and the last block -- which IS the post window, 2023-25
    -- dominates. Under exchangeability each block would hold 1/9 = 0.111 of
    the mass.

    This is the measurement that replaced a wrong explanation. The first draft
    of this tool reported a shock-to-noise ratio and implied the size inflation
    followed it; it does not. observed_rates_flat carries a HIGHER ratio than
    fitted_joint and a much LOWER size, so the ratio cannot be the mechanism.
    Leverage can, and this measures it directly.
    """
    T = len(means["years"])
    rng = np.random.default_rng(spec["seed"] + 991)
    shares, hh = [], []
    for _ in range(n):
        d = (ar1(rng, T, rho, sigma, spec.get("start", "stationary"))
             if spec["shock"] != "none" else None)
        y_imf = draw_counts(rng, means["IMF"], None, False, 0.0)
        des = designs["P1"]
        y_wb = draw_counts(rng, means["P1"], d, False, 0.0)
        y = assemble(des, y_wb, y_imf)
        mu0, _ = irls_poisson(y, des.Xr, des.off)
        coef, *_ = np.linalg.lstsq(des.Xr.T @ (des.Xr * mu0[:, None]),
                                   des.Xr.T @ (mu0 * des.xj), rcond=None)
        s = (des.xj - des.Xr @ coef) * (y - mu0)
        S_year = np.array([s[des.pair[k]].sum() for k in range(des.T)])
        blocks = np.array([S_year[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum()
                           for b in range(des.n_blocks)])
        sq = blocks ** 2
        tot = float(sq.sum())
        if tot <= 0:
            continue
        shares.append(float(sq[-1]) / tot)
        hh.append(float(np.sum((sq / tot) ** 2)))
    return {"blocks": int(designs["P1"].n_blocks),
            "equal_share": 1.0 / designs["P1"].n_blocks,
            "block9_variance_share": float(np.mean(shares)),
            "herfindahl_over_blocks": float(np.mean(hh)),
            "draws": len(shares)}


def shock_to_noise(means: dict, sigma: float, rho: float) -> dict:
    """How large the serially dependent component is beside sampling noise.

    On the log scale a Poisson cell carries sd ~ 1/sqrt(mu); the shock's
    stationary sd is sigma/sqrt(1-rho^2). What the test sees is the WB-minus-IMF
    contrast, so the comparison is against the two arms' noise combined.

    Reported because it is worth knowing, and explicitly NOT as the explanation
    of the ladder: observed_rates_flat carries a higher ratio than fitted_joint
    and less than half its family error. See block_leverage for the mechanism
    that does track the ladder.
    """
    s = sigma / np.sqrt(1 - rho ** 2)
    out = {"shock_sd_stationary": float(s)}
    for p in PANELS:
        nw = float(np.mean(1.0 / np.sqrt(means[p])))
        ni = float(np.mean(1.0 / np.sqrt(means["IMF"])))
        out[p] = {"mean_mu_wb": float(np.mean(means[p])),
                  "mean_mu_imf": float(np.mean(means["IMF"])),
                  "contrast_noise_sd": float(np.sqrt(nw ** 2 + ni ** 2)),
                  "shock_to_noise": float(s / np.sqrt(nw ** 2 + ni ** 2))}
    return out


def run_scenario(spec, designs, cells, reps, obs_p, progress=True):
    """One null, `reps` replicates, both panels, the exact rule."""
    means = spec["means"]
    if "tokens" in means:                 # scenario supplies its own offsets
        designs = designs_for_tokens(means)
    T = len(means["years"])
    joint = spec["joint"]
    shock = spec["shock"]
    start = spec.get("start", "stationary")
    rho, sigma = spec.get("rho", RHO), spec.get("sigma", SIGMA_DELTA)
    nb2 = spec.get("nb2", False)
    do_c4 = spec.get("c4", False)
    rng = np.random.default_rng(spec["seed"])

    p1s, p2s = np.empty(reps), np.empty(reps)
    fam_holm = np.zeros(reps, dtype=bool)
    both = np.zeros(reps, dtype=bool)
    fam_c1c4 = np.zeros(reps, dtype=bool) if do_c4 else None

    for r in range(reps):
        if spec.get("param_uncertainty"):
            rho = float(rng.uniform(*spec["rho_range"]))
            sigma = float(rng.uniform(*spec["sigma_range"]))
        ps = {}
        if joint:
            d_shared = (ar1(rng, T, rho, sigma, start)
                        if shock == "shared" else None)
            y_imf = draw_counts(rng, means["IMF"], None, nb2, ALPHA_NB2["P1"])
            for p in PANELS:
                d = (d_shared if shock == "shared"
                     else ar1(rng, T, rho, sigma, start) if shock == "independent"
                     else None)
                y_wb = draw_counts(rng, means[p], d, nb2, ALPHA_NB2[p])
                ps[p] = designs[p].exact_p(assemble(designs[p], y_wb, y_imf))
                if do_c4:
                    ys = assemble(designs[p], y_wb, y_imf)
                    ps[p + "_y"] = ys
        else:
            for p in PANELS:
                d = (ar1(rng, T, rho, sigma, start) if shock != "none" else None)
                mu = means[p + "_full"]
                wbm = designs[p].wb
                eta = np.log(mu).copy()
                if d is not None:
                    pos = {yy: i for i, yy in enumerate(means["years"])}
                    eta = eta + wbm * np.array([d[pos[yy]]
                                                for yy in designs[p].year_of])
                lam = np.exp(eta)
                if nb2:
                    a = ALPHA_NB2[p]
                    lam = rng.gamma(shape=1.0 / a, scale=a * lam)
                ys = rng.poisson(lam).astype(float)
                ps[p] = (designs[p].exact_p(ys) if spec.get("exact", True)
                         else mc_p(designs[p], ys, rng, spec.get("B", 999)))
                if do_c4:
                    ps[p + "_y"] = ys
        p1s[r], p2s[r] = ps["P1"], ps["P2"]
        r1, r2 = holm2(ps["P1"], ps["P2"])
        fam_holm[r] = r1 or r2
        both[r] = r1 and r2
        if do_c4:
            ok = False
            for p, rej in (("P1", r1), ("P2", r2)):
                if rej and c4_ok(designs[p], ps[p + "_y"], p, cells[p]):
                    ok = True
                    break
            fam_c1c4[r] = ok
        if progress and (r + 1) % 500 == 0:
            print(f"    [{spec['name']}] {r + 1}/{reps}", flush=True)

    def rate(v):
        return float(np.mean(v))

    def se(v):
        m = float(np.mean(v))
        return float(np.sqrt(m * (1 - m) / len(v)))

    out = {
        "name": spec["name"], "description": spec["desc"], "reps": int(reps),
        "joint": bool(joint), "shock": shock, "shock_start": start,
        "rho": (None if spec.get("param_uncertainty") else float(rho)),
        "sigma_delta": (None if spec.get("param_uncertainty") else float(sigma)),
        "nb2": bool(nb2), "inner_p": "exact_512" if spec.get("exact", True)
                                     else f"monte_carlo_B{spec.get('B', 999)}",
        "p1_raw_size_at_0.05": rate(p1s < 0.05),
        "p2_raw_size_at_0.05": rate(p2s < 0.05),
        "p1_raw_size_at_0.025": rate(p1s < 0.025),
        "p2_raw_size_at_0.025": rate(p2s < 0.025),
        "holm_familywise_error_rate": rate(fam_holm),
        "holm_fwer_mc_se": se(fam_holm),
        "holm_both_panels_rejected": rate(both),
        "tail_p1_at_or_below_observed": rate(p1s <= obs_p["P1"] + 1e-12),
        "tail_p2_at_or_below_observed": rate(p2s <= obs_p["P2"] + 1e-12),
        "tail_min_at_or_below_observed_p1": rate(
            np.minimum(p1s, p2s) <= obs_p["P1"] + 1e-12),
        "median_p1": float(np.median(p1s)), "median_p2": float(np.median(p2s)),
    }
    if do_c4:
        out["c1_and_c4_family_rate"] = rate(fam_c1c4)
        out["c1_and_c4_mc_se"] = se(fam_c1c4)
    if not spec.get("param_uncertainty"):
        out["diagnostics"] = shock_to_noise(means, sigma, rho)
        out["diagnostics"]["leverage"] = block_leverage(
            spec, designs, means, rho, sigma)
    return out


def draw_counts(rng, mu, d, nb2, alpha):
    lam = mu * np.exp(d) if d is not None else np.asarray(mu, dtype=float)
    if nb2 and alpha > 0:
        lam = rng.gamma(shape=1.0 / alpha, scale=alpha * lam)
    return rng.poisson(lam).astype(float)


def assemble(des: Design, y_wb, y_imf) -> np.ndarray:
    """Place the two arms' draws back into the design's row order."""
    y = np.empty(len(des.df))
    y[des.wb] = y_wb
    y[~des.wb] = y_imf
    return y


def mc_p(des: Design, y, rng, B):
    """The sampled inner p, kept only so `s10_4_asbuilt` really is as built."""
    mu0, _ = irls_poisson(y, des.Xr, des.off)
    coef, *_ = np.linalg.lstsq(des.Xr.T @ (des.Xr * mu0[:, None]),
                               des.Xr.T @ (mu0 * des.xj), rcond=None)
    s = (des.xj - des.Xr @ coef) * (y - mu0)
    S_year = np.array([s[des.pair[k]].sum() for k in range(des.T)])
    blocks = np.array([S_year[b * BLOCK_LEN:(b + 1) * BLOCK_LEN].sum()
                       for b in range(des.n_blocks)])
    denom = float(np.sqrt((blocks ** 2).sum()))
    if denom == 0.0:
        return 1.0
    t_obs = abs(float(blocks.sum())) / denom
    eta = rng.choice([-1.0, 1.0], size=(B, des.n_blocks))
    hits = int((np.abs(eta @ blocks) / denom >= t_obs).sum())
    return (1 + hits) / (B + 1)


# ------------------------------------------------------------------ guard ---
def _assert_irls_matches(designs):
    """The fast fit must be the frozen fit. Checked on the real cells, both
    panels, restricted and full, before any scenario is allowed to run."""
    import statsmodels.api as sm
    worst = 0.0
    for p, des in designs.items():
        for X in (des.Xr, des.X):
            ref = np.asarray(_fit(des.y0, X, des.off,
                                  sm.families.Poisson()).fittedvalues)
            got, _ = irls_poisson(des.y0, X, des.off)
            worst = max(worst, float(np.max(np.abs(got - ref) / ref)))
    if worst > 1e-9:
        raise SystemExit(f"[joint] IRLS departs from statsmodels by {worst:.3e} "
                         "— refusing to run a calibration on a different fit")
    return worst


def _assert_shared_imf(cells):
    """The whole joint construction rests on this being literally true."""
    a = cells["P1"][cells["P1"]["institution"] == "IMF"].sort_values("year")
    b = cells["P2"][cells["P2"]["institution"] == "IMF"].sort_values("year")
    for col in ("year", "count", "tokens"):
        if not np.array_equal(a[col].to_numpy(), b[col].to_numpy()):
            raise SystemExit(f"[joint] the IMF arm differs between panels in "
                             f"{col!r}; the shared-draw scenarios would be wrong")


def observed_exact_p(designs):
    return {p: designs[p].exact_p(designs[p].y0) for p in PANELS}


# ------------------------------------------------------------------- main ---
def build_scenarios(cells, designs, reps_c4):
    jf = joint_fitted_means(cells)
    pp = {p + "_full": perpanel_fitted_means(designs[p]) for p in PANELS}
    pp["years"] = jf["years"]
    # The per-panel restricted fit gives the Fund arm a DIFFERENT mean in each
    # panel — which is exactly why a shared draw is incoherent under it. The
    # diagnostic reports P1's, and the arm split is carried on the same dict so
    # shock_to_noise can read it.
    for p in PANELS:
        pp[p] = pp[p + "_full"][designs[p].wb]
    pp["IMF"] = pp["P1_full"][~designs["P1"].wb]
    pp_arms = {k: pp[k] for k in ("years", "P1", "P2", "IMF")}

    obs_flat = flat_means(cells, None)
    par_flat = flat_means(cells, PREREG_RATE)
    tmpl = template_means(PREREG_RATE)

    S = []
    S.append(dict(name="s10_4_asbuilt", desc=(
        "S10.4 as it was built: each panel under its OWN restricted fit, the "
        "two panels drawn in separate loops, inner p sampled at B=999. No Holm. "
        "Reproduced here only so the ladder starts where the supplement did."),
        means=pp, joint=False, shock="shared", start="stationary",
        exact=False, B=999, seed=SEED + 8101, c4=False))
    S.append(dict(name="s10_4_exact", desc=(
        "The same null and the same independence, with the inner p ENUMERATED "
        "over all 512 sign patterns instead of sampled. Isolates how much of "
        "S10.4's number was bootstrap resolution."),
        means=pp, joint=False, shock="shared", start="stationary",
        seed=SEED + 8102, c4=False))
    S.append(dict(name="s10_4_exact_holm", desc=(
        "Same again; the family verdict is now the preregistered Holm step-down "
        "rather than a raw 0.05 threshold. Panels still independent, which for "
        "two hypotheses is the WORST case for Holm's family error."),
        means=pp, joint=False, shock="shared", start="stationary",
        seed=SEED + 8103, c4=True))
    S.append(dict(name="fitted_joint", desc=(
        "The real dependence: one shared year profile, ONE Fund draw handed to "
        "both panels exactly as the data hand it to both, one shared World Bank "
        "differential shock. This is what src/mde_sim.py already did for power "
        "and what S10.4 should have done for size."),
        means=jf, joint=True, shock="shared", start="stationary",
        seed=SEED + 8104, c4=True))
    S.append(dict(name="fitted_joint_indep_shock", desc=(
        "Shared Fund draw, but the two World Bank arms get independent shocks. "
        "Brackets the dependence assumption from the other side."),
        means=jf, joint=True, shock="independent", start="stationary",
        seed=SEED + 8105, c4=False))
    S.append(dict(name="fitted_joint_nb2", desc=(
        "fitted_joint plus the dof-corrected NB2 dispersion (S10.4a)."),
        means=jf, joint=True, shock="shared", start="stationary", nb2=True,
        seed=SEED + 8106, c4=False))
    S.append(dict(name="fitted_joint_poisson_only", desc=(
        "fitted_joint means with no serial shock at all. Separates the mean "
        "structure's contribution from the dependence's."),
        means=jf, joint=True, shock="none", seed=SEED + 8107, c4=False))
    S.append(dict(name="fitted_joint_no_wb_trend", desc=(
        "fitted_joint with the World Bank differential linear trend set to "
        "zero and everything else held. Isolates what the null's growing World "
        "Bank arm contributes -- a growing arm puts more of the score's mass in "
        "the late years, which is where block nine and POST both sit."),
        means=component_means(cells, jf, keep_year=True, keep_tau=False),
        joint=True, shock="shared", start="stationary",
        seed=SEED + 8112, c4=False))
    S.append(dict(name="fitted_joint_no_year_profile", desc=(
        "fitted_joint with the estimated year profile flattened to its "
        "token-weighted mean, the World Bank trend kept. Isolates what the "
        "year-to-year wiggle in the fitted mean contributes."),
        means=component_means(cells, jf, keep_year=False, keep_tau=True),
        joint=True, shock="shared", start="stationary",
        seed=SEED + 8113, c4=False))
    S.append(dict(name="fitted_joint_neither", desc=(
        "Both switched off: flat year profile, no differential trend. Should "
        "meet observed_rates_flat, and if it does the two components account "
        "for the whole distance between the ladder's ends."),
        means=component_means(cells, jf, keep_year=False, keep_tau=False),
        joint=True, shock="shared", start="stationary",
        seed=SEED + 8114, c4=False))
    S.append(dict(name="observed_rates_flat", desc=(
        "Year effects removed; each series held at its own observed pooled "
        "rate, so the Fund arm keeps its real level. The first rung that is "
        "not conditioned on fitted year effects."),
        means=obs_flat, joint=True, shock="shared", start="stationary",
        seed=SEED + 8108, c4=False))
    S.append(dict(name="prereg_parity_obs_tokens", desc=(
        "PREREG SS8's flat parity rate 2.767e-5 on the OBSERVED token vectors. "
        "Isolates the parity assumption from the token projection."),
        means=par_flat, joint=True, shock="shared", start="stationary",
        seed=SEED + 8109, c4=False))
    S.append(dict(name="prereg_literal", desc=(
        "PREREG SS8 exactly as src/mde_sim.py implements it: projected token "
        "templates, every series at the parity rate, and the shock started at "
        "zero rather than at its stationary draw. Should land near the 0.039 "
        "that docs/MDE_P1P2_20260820.md recorded in August."),
        means=tmpl, joint=True, shock="shared", start="zero",
        seed=SEED + 8110, c4=False))
    S.append(dict(name="prereg_literal_stationary_start", desc=(
        "prereg_literal with the shock started from its stationary "
        "distribution. The preregistered simulator opens delta at zero, which "
        "damps the first years' dependence; this measures that."),
        means=tmpl, joint=True, shock="shared", start="stationary",
        seed=SEED + 8111, c4=False))
    for rho in (0.0, 0.3, 0.7):
        S.append(dict(name=f"fitted_joint_rho{rho}", desc=(
            f"fitted_joint at rho = {rho}, sigma unchanged."),
            means=jf, joint=True, shock="shared", start="stationary",
            rho=rho, seed=SEED + 8120 + int(rho * 10), c4=False))
    for sg in (0.16, 0.48):
        S.append(dict(name=f"fitted_joint_sigma{sg}", desc=(
            f"fitted_joint at sigma_delta = {sg}, rho unchanged."),
            means=jf, joint=True, shock="shared", start="stationary",
            sigma=sg, seed=SEED + 8140 + int(sg * 100), c4=False))
    S.append(dict(name="fitted_joint_param_uncertainty", desc=(
        "fitted_joint with rho and sigma redrawn every replicate from "
        "U(0.2,0.8) and U(0.20,0.45); the frozen pair is a point estimate and "
        "was never given an interval."),
        means=jf, joint=True, shock="shared", start="stationary",
        param_uncertainty=True, rho_range=(0.2, 0.8),
        sigma_range=(0.20, 0.45), seed=SEED + 8160, c4=False))
    for s in S:
        s.setdefault("c4", False)
        if s["c4"]:
            s["_reps"] = reps_c4
    return S, pp_arms


def main(reps: int = 2000, reps_c4: int = 1000, only: str | None = None) -> int:
    cells = {p: pd.read_csv(CELLS[p]) for p in PANELS}
    _assert_shared_imf(cells)
    designs = {p: Design(cells[p]) for p in PANELS}
    worst = _assert_irls_matches(designs)
    obs = observed_exact_p(designs)
    print(f"[joint] IRLS vs statsmodels, worst relative gap {worst:.2e}")
    print(f"[joint] observed exact PASS-P p: P1 {obs['P1']:.6f} "
          f"({round(obs['P1'] * 512)}/512), P2 {obs['P2']:.6f} "
          f"({round(obs['P2'] * 512)}/512)")
    r1, r2 = holm2(obs["P1"], obs["P2"])
    print(f"[joint] observed Holm verdict: P1 reject={r1}, P2 reject={r2}\n")

    scen, pp_arms = build_scenarios(cells, designs, reps_c4)
    if only:
        want = set(only.split(","))
        scen = [s for s in scen if s["name"] in want]
        if not scen:
            raise SystemExit(f"[joint] no scenario named in {only!r}")

    res = {"alpha_family": ALPHA, "holm_levels": [ALPHA / 2, ALPHA],
           "inner_support": 512, "block_len": BLOCK_LEN,
           "observed_exact_p": obs,
           "observed_holm": {"P1": bool(r1), "P2": bool(r2)},
           "rho_frozen": RHO, "sigma_delta_frozen": SIGMA_DELTA,
           "nb2_alpha_corrected": ALPHA_NB2,
           "conditions_simulated": ["C1 (PASS-P + Holm)", "C4 (LOPO) where marked"],
           "conditions_not_simulated": ["C2 (stability: NB2 + standardized "
                                        "variant)", "C3 (concentration guard)"],
           "family_rates_are_upper_bounds": True,
           "scenarios": []}
    for spec in scen:
        n = spec.pop("_reps", reps)
        print(f"[joint] {spec['name']} ({n} reps"
              f"{', with C4' if spec.get('c4') else ''})", flush=True)
        r = run_scenario(spec, designs, cells, n, obs)
        res["scenarios"].append(r)
        print(f"    raw@.05  P1 {r['p1_raw_size_at_0.05']:.4f}  "
              f"P2 {r['p2_raw_size_at_0.05']:.4f}   "
              f"HOLM FWER {r['holm_familywise_error_rate']:.4f} "
              f"(SE {r['holm_fwer_mc_se']:.4f})"
              + (f"   C1&C4 {r['c1_and_c4_family_rate']:.4f}"
                 if 'c1_and_c4_family_rate' in r else ""), flush=True)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"\n[joint] wrote {OUT.relative_to(ROOT)}")

    print(f"\n{'scenario':34s} {'P1@.05':>7s} {'P2@.05':>7s} {'FWER':>7s} "
          f"{'SE':>6s} {'S/N':>6s} {'blk9':>6s}")
    print("-" * 81)
    for r in res["scenarios"]:
        d = r.get("diagnostics")
        sn = f"{d['P1']['shock_to_noise']:6.2f}" if d else "     -"
        b9 = f"{d['leverage']['block9_variance_share']:6.3f}" if d else "     -"
        print(f"{r['name']:34s} {r['p1_raw_size_at_0.05']:7.4f} "
              f"{r['p2_raw_size_at_0.05']:7.4f} "
              f"{r['holm_familywise_error_rate']:7.4f} "
              f"{r['holm_fwer_mc_se']:6.4f} {sn} {b9}")
    print(f"\n(blk9 = share of the statistic's variance in block nine, the "
          f"post window; equal share would be {1/9:.3f})")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2000)
    ap.add_argument("--reps-c4", type=int, default=1000)
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    sys.exit(main(a.reps, a.reps_c4, a.only))
