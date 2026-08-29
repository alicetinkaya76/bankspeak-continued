"""PREREG v0.5 §8 interaction MDE simulation (round-6 repairs).

Repairs: (1) the failed-calibration FULL NESTED PASS-P power curve exists and is
the default whenever no accepted calibration is supplied; (2) inner B defaults
to the frozen 9,999; (3) P1/P2 are simulated JOINTLY with a shared IMF Article
IV series and Holm decisions; (4) a WB-specific differential AR(1) shock
delta_t (shared by both WB panels) generates serial dependence in the process
identifying WB:post — the old common shock was absorbed by C(year); (5) the
method-of-moments sigma hook is implemented: sigma_delta = sqrt(ln(1+alpha)),
alpha from a frozen trend-model MoM on WB pre-2023 cells; (6) branch-specific
token/doc projections enter via --cells-template / --tokens-per-doc."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from bootstrap_engine import (build_design, wild_score_p, _pair_index,
                              mom_alpha, POST_LO, POST_HI)

SEED = 20260806

def pass_p(cells: pd.DataFrame, B: int, seed: int, nb2: bool = False) -> float:
    df, X, names, y, off, years = build_design(cells, "WB")
    pair, T = _pair_index(df, years, "WB")
    p, _, _ = wild_score_p(y, X, off, names, pair, T, B, 3, seed, nb2)
    return p

def wald_z(cells: pd.DataFrame) -> float:
    df, X, names, y, off, _ = build_design(cells, "WB")
    fit = sm.GLM(y, X, family=sm.families.Poisson(), offset=off).fit(cov_type="HC1")
    j = names.index("WB_post")
    return float(fit.params[j] / fit.bse[j])

def sigma_from_cells(path: str) -> float:
    """Frozen MoM: WB pre-2023 cells, count ~ 1 + c_year + offset(log tokens),
    alpha = mom_alpha(y, mu), sigma_delta = sqrt(ln(1 + alpha))."""
    d = pd.read_csv(path)
    d = d[(d["institution"] == "WB") & (d["year"] < 2023)]
    y = d["count"].to_numpy(float)
    X = np.column_stack([np.ones(len(d)), d["year"].to_numpy(float) - d["year"].median()])
    off = np.log(d["tokens"].to_numpy(float))
    mu = np.asarray(sm.GLM(y, X, family=sm.families.Poisson(), offset=off).fit().fittedvalues)
    a = mom_alpha(y, mu)
    return float(np.sqrt(np.log1p(a)))

def simulate_joint(years, tokens, base_rate, theta1, theta2, rho, sigma_delta,
                   rng, tokens_p1=None, tokens_p2=None, rate_p1=None,
                   rate_p2=None, p2_years=None, tokens_imf=None,
                   rate_imf=None):
    """One replicate: shared IMF Article IV series; WB-P1 and WB-P2 share the
    differential AR(1) shock delta_t; independent Poisson noise per cell.
    Round-7: per-panel token vectors and base rates (defaults reproduce the
    legacy shared behavior draw-for-draw — the RNG call order is unchanged:
    delta, IMF, WB-P1, WB-P2); p2_years optionally restricts P2 to a later
    start (frozen common-year subset), with the SAME shared IMF draws kept on
    the overlap."""
    tokens_p1 = tokens if tokens_p1 is None else tokens_p1
    tokens_p2 = tokens if tokens_p2 is None else tokens_p2
    tokens_imf = tokens if tokens_imf is None else tokens_imf   # round-8
    rate_p1 = base_rate if rate_p1 is None else rate_p1
    rate_p2 = base_rate if rate_p2 is None else rate_p2
    rate_imf = base_rate if rate_imf is None else rate_imf      # round-8
    T = len(years)
    delta = np.zeros(T)
    for t in range(1, T):
        delta[t] = rho * delta[t-1] + rng.normal(0, sigma_delta)
    imf = [{"institution": "IMF", "year": int(yy),
            "count": int(rng.poisson(rate_imf * tokens_imf[k])),
            "tokens": tokens_imf[k]}
           for k, yy in enumerate(years)]
    def wb_panel(theta, tok, rate):
        rows = []
        for k, yy in enumerate(years):
            post = 1.0 if POST_LO <= yy <= POST_HI else 0.0
            lam = np.exp(np.log(rate) + delta[k] + theta * post) * tok[k]
            rows.append({"institution": "WB", "year": int(yy),
                         "count": int(rng.poisson(lam)), "tokens": tok[k]})
        return rows
    rows1 = wb_panel(theta1, tokens_p1, rate_p1)
    rows2 = wb_panel(theta2, tokens_p2, rate_p2)
    p1 = pd.DataFrame(rows1 + imf)
    p2 = pd.DataFrame(rows2 + imf)
    if p2_years is not None:
        keep = set(int(v) for v in p2_years)
        p2 = p2[p2["year"].isin(keep)].reset_index(drop=True)
    return p1, p2


def simulate_p0(years, tokens_p0, tokens_imf, rate_p0, rate_imf, theta, rho,
                sigma_delta, rng):
    """P0 singleton replicate (round-7): one genre-matched WB series against
    the shared IMF series; delta_t applies to the WB side. Deterministic RNG
    order: delta, IMF, WB-P0."""
    T = len(years)
    delta = np.zeros(T)
    for t in range(1, T):
        delta[t] = rho * delta[t-1] + rng.normal(0, sigma_delta)
    imf = [{"institution": "IMF", "year": int(yy),
            "count": int(rng.poisson(rate_imf * tokens_imf[k])),
            "tokens": tokens_imf[k]} for k, yy in enumerate(years)]
    rows = []
    for k, yy in enumerate(years):
        post = 1.0 if POST_LO <= yy <= POST_HI else 0.0
        lam = np.exp(np.log(rate_p0) + delta[k] + theta * post) * tokens_p0[k]
        rows.append({"institution": "WB", "year": int(yy),
                     "count": int(rng.poisson(lam)), "tokens": tokens_p0[k]})
    return pd.DataFrame(rows + imf)


def load_template(path, years, fallback_tokens=None, tokens_per_doc=None):
    """Template loader. Round-8: STRICT — a template must cover every
    simulation year; a missing year raises (silent flat-filling removed;
    fallback_tokens is ignored for coverage and kept only for
    call-compatibility). year,tokens[,docs]: tokens wins; docs is honored
    via docs x tokens_per_doc."""
    t = pd.read_csv(path)
    if "tokens" in t.columns:
        m = t.set_index("year")["tokens"]
    elif "docs" in t.columns:
        if tokens_per_doc is None:
            raise SystemExit("[mde] template has docs but no tokens; pass "
                             "--tokens-per-doc for the P0 projection")
        m = t.set_index("year")["docs"] * float(tokens_per_doc)
    else:
        raise SystemExit(f"[mde] template {path} needs a tokens or docs column")
    missing = [int(yy) for yy in years if yy not in m.index]
    if missing:
        raise SystemExit(f"[mde] template {path} is missing required "
                         f"year(s) {missing} — templates must cover every "
                         "simulation year (round-8 strictness)")
    want = {int(yy) for yy in years}
    extra = sorted(int(yy) for yy in m.index if int(yy) not in want)
    if extra:
        raise SystemExit(f"[mde] template {path} carries year(s) {extra} "
                         "outside the simulation grid — template years must "
                         "EXACTLY equal the grid (round-9)")
    vals = np.array([float(m[yy]) for yy in years])
    if (not np.all(np.isfinite(vals))) or np.any(vals <= 0):
        raise SystemExit(f"[mde] template {path} contains non-positive or "
                         "non-finite token value(s) — tokens must be finite "
                         "and > 0 (round-9)")
    return vals


def wald_singleton_decide(z, crit):
    """Round-8: the ACCEPTED calibration's critical value governs."""
    return bool(abs(z) >= crit)


def wald_holm2_decide(z1, z2, crit_full, crit_half):
    """Calibrated Holm step-down on |z|: larger vs the alpha/2 null
    quantile; on rejection, smaller vs the alpha quantile."""
    a1, a2 = abs(z1), abs(z2)
    if max(a1, a2) < crit_half:
        return False, False
    big_is_1 = a1 >= a2
    small = a2 if big_is_1 else a1
    r_small = bool(small >= crit_full)
    return (True, r_small) if big_is_1 else (r_small, True)


def _sha_file(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _tpl_id(path, flat_tokens):
    """Binding identity of a token source: file hash, or the flat value."""
    if path:
        return {"sha256": _sha_file(path)}
    return {"flat_tokens_per_year": float(flat_tokens)}


def _git_commit():
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, timeout=10)
        out = r.stdout.strip()
        return out if r.returncode == 0 and out else None
    except Exception:
        return None


def build_binding(a, years):
    """Round-9 (C21): the decision-input identity a calibration is bound to.
    A curve run may take the Wald shortcut ONLY when its own binding equals
    the calibration's, git commit included."""
    return {"family": a.family,
            "years": [int(y) for y in years],    # round-10: full vector
            "alpha": float(a.alpha), "rho": float(a.rho),
            "sigma_delta": float(a.sigma_delta),
            "companion": a.companion, "seed": SEED,
            "p2_start_year": a.p2_start_year,
            "tokens_per_doc": (float(a.tokens_per_doc)
                               if a.tokens_per_doc is not None else None),
            "base_rates": {"shared": float(a.base_rate),
                           "imf": a.base_rate_imf, "p1": a.base_rate_p1,
                           "p2": a.base_rate_p2, "p0": a.base_rate_p0},
            "templates": {"shared": _tpl_id(a.cells_template,
                                            a.tokens_per_year),
                          "imf": (_tpl_id(a.template_imf, None)
                                  if a.template_imf else None),
                          "p1": (_tpl_id(a.template_p1, None)
                                 if a.template_p1 else None),
                          "p2": (_tpl_id(a.template_p2, None)
                                 if a.template_p2 else None),
                          "p0": (_tpl_id(a.template_p0, None)
                                 if a.template_p0 else None)},
            "git_commit": _git_commit()}


PRODUCTION_NCAL = 200
PRODUCTION_B = 9999


def parse_years(spec: str) -> np.ndarray:
    """Round-10 (C26): the common-year sequence may carry calendar gaps.
    Accepts comma-separated items, each a single year or an a-b range,
    e.g. "1994-2025", "2018,2020", "1994-2000,2005-2010". Years must be
    strictly increasing after expansion; duplicates or disorder abort."""
    out = []
    for part in str(spec).split(","):
        part = part.strip()
        if not part:
            raise SystemExit(f"[mde] empty item in --years {spec!r}")
        if "-" in part:
            a, b = part.split("-", 1)
            lo, hi = int(a), int(b)
            if hi < lo:
                raise SystemExit(f"[mde] descending range {part!r} in "
                                 f"--years {spec!r}")
            out.extend(range(lo, hi + 1))
        else:
            out.append(int(part))
    arr = np.asarray(out, dtype=int)
    if len(arr) < 2:
        raise SystemExit(f"[mde] --years {spec!r} yields fewer than two "
                         "years")
    if np.any(np.diff(arr) <= 0):
        raise SystemExit(f"[mde] --years {spec!r} is not strictly "
                         "increasing after expansion (duplicate or "
                         "disordered years)")
    return arr


def holm2(p1: float, p2: float, alpha: float):
    """Holm step-down for two hypotheses at family level alpha."""
    (i1, pa), (i2, pb) = sorted(enumerate([p1, p2]), key=lambda t: t[1])
    r = [False, False]
    if pa < alpha / 2:
        r[i1] = True
        if pb < alpha:
            r[i2] = True
    return r[0], r[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["calibrate", "curve", "smoke"], required=True)
    ap.add_argument("--years", default="1994-2025",
                    help="comma list of years and a-b ranges; calendar "
                         "gaps allowed (round-10)")
    ap.add_argument("--calib-expected-sha256", default=None,
                    help="sha256 the --calib-json file MUST match for the "
                         "Wald shortcut (Stage-B binds this to the frozen "
                         "calibration_sha256)")
    ap.add_argument("--base-rate", type=float, default=6e-5)
    ap.add_argument("--tokens-per-year", type=float, default=2e6)
    ap.add_argument("--cells-template", default=None,
                    help="legacy shared CSV with per-year tokens (all panels)")
    ap.add_argument("--template-imf", default=None)
    ap.add_argument("--template-p1", default=None)
    ap.add_argument("--template-p2", default=None)
    ap.add_argument("--template-p0", default=None)
    ap.add_argument("--tokens-per-doc", type=float, default=None,
                    help="P0 projection: docs-column templates use "
                         "docs x tokens-per-doc (pooled WB ICR+PAD mean)")
    ap.add_argument("--base-rate-imf", type=float, default=None)
    ap.add_argument("--base-rate-p1", type=float, default=None)
    ap.add_argument("--base-rate-p2", type=float, default=None)
    ap.add_argument("--base-rate-p0", type=float, default=None)
    ap.add_argument("--p2-start-year", type=int, default=None,
                    help="restrict P2 to years >= this (frozen: 1996 at "
                         "Stage-B); default keeps the legacy full span")
    ap.add_argument("--family", choices=["p1p2", "p0"], default="p1p2",
                    help="p0 = SINGLETON decision at alpha (no Holm); the G4 "
                         "gate is computed in this mode")
    ap.add_argument("--rho", type=float, default=0.5)
    ap.add_argument("--sigma-delta", type=float, default=0.0)
    ap.add_argument("--sigma-from-cells", default=None)
    ap.add_argument("--companion", choices=["zero", "half", "full"], default="full")
    ap.add_argument("--theta-grid", default="0.0:1.2:0.05")
    ap.add_argument("--reps", type=int, default=1000)
    ap.add_argument("--ncal", type=int, default=200)
    ap.add_argument("--B", type=int, default=9999, help="inner PASS-P bootstrap size")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--calib-json", default=None,
                    help="calibrate-mode output; Wald shortcut used only if its "
                         "calibration_ok is true")
    ap.add_argument("--force-nested", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    years = parse_years(a.years)                 # round-10: gap-aware
    if a.cells_template:
        tokens = load_template(a.cells_template, years, a.tokens_per_year,
                               a.tokens_per_doc)
    else:
        tokens = np.full(len(years), a.tokens_per_year)
    def _tpl(path):
        return (load_template(path, years, a.tokens_per_year, a.tokens_per_doc)
                if path else tokens)
    tok_imf, tok_p1 = _tpl(a.template_imf), _tpl(a.template_p1)
    tok_p2, tok_p0 = _tpl(a.template_p2), _tpl(a.template_p0)
    r_imf = a.base_rate_imf if a.base_rate_imf is not None else a.base_rate
    r_p1 = a.base_rate_p1 if a.base_rate_p1 is not None else a.base_rate
    r_p2 = a.base_rate_p2 if a.base_rate_p2 is not None else a.base_rate
    r_p0 = a.base_rate_p0 if a.base_rate_p0 is not None else a.base_rate
    p2_years = (years[years >= a.p2_start_year]
                if a.p2_start_year is not None else None)
    if a.sigma_from_cells:
        a.sigma_delta = sigma_from_cells(a.sigma_from_cells)
        print(f"[mde] sigma_delta from cells (MoM): {a.sigma_delta:.4f}")
    if a.mode == "smoke":
        a.reps, a.ncal, a.B = 30, 10, 199

    comp = {"zero": 0.0, "half": 0.5, "full": 1.0}[a.companion]

    if a.mode in ("calibrate", "smoke"):
        zs, ps = [], []
        fam_pairs, fam_nested = [], []
        for i in range(a.ncal):
            rng = np.random.default_rng(SEED + i)
            if a.family == "p0":
                cal = simulate_p0(years, tok_p0, tok_imf, r_p0, r_imf, 0.0,
                                  a.rho, a.sigma_delta, rng)
                zs.append(abs(wald_z(cal)))
                ps.append(pass_p(cal, a.B, SEED + i))
            else:
                # round-9 (C21): the {P1,P2} calibration consumes BOTH
                # panels — pooled null |z| sample and a family-level nested
                # reference decision (P2 nested stream offset +150000+i).
                c1, c2 = simulate_joint(years, tokens, a.base_rate, 0.0, 0.0,
                                        a.rho, a.sigma_delta, rng,
                                        tokens_p1=tok_p1, tokens_p2=tok_p2,
                                        rate_p1=r_p1, rate_p2=r_p2,
                                        p2_years=p2_years,
                                        tokens_imf=tok_imf, rate_imf=r_imf)
                z1, z2 = abs(wald_z(c1)), abs(wald_z(c2))
                zs.extend([z1, z2])
                fam_pairs.append((z1, z2))
                p1_ = pass_p(c1, a.B, SEED + i)
                p2_ = pass_p(c2, a.B, SEED + 150_000 + i)
                fam_nested.append(bool(any(holm2(p1_, p2_, a.alpha))))
        zs_arr = np.asarray(zs)
        zs_sorted = np.sort(zs_arr)
        n_null = len(zs_arr)
        k = max(0, int(np.floor(a.alpha * (n_null + 1))) - 1)
        crit = float(zs_sorted[-(k + 1)])
        k_half = max(0, int(np.floor((a.alpha / 2.0) * (n_null + 1))) - 1)
        crit_half = float(zs_sorted[-(k_half + 1)])   # same estimator as crit
        if a.family == "p0":
            ps_arr = np.asarray(ps)
            boot_size = float(np.mean(ps_arr < a.alpha))
            concordance = float(np.mean((ps_arr < a.alpha)
                                        == (zs_arr > crit)))
        else:
            wald_fam = np.array([any(wald_holm2_decide(z1, z2, crit,
                                                       crit_half))
                                 for z1, z2 in fam_pairs])
            nested_fam = np.asarray(fam_nested)
            boot_size = float(np.mean(nested_fam))
            concordance = float(np.mean(wald_fam == nested_fam))
        calibration_ok = bool(a.alpha / 2 <= boot_size <= 2 * a.alpha
                              and concordance >= 0.95)
        calib = {"crit_abs_z": crit, "crit_abs_z_half": crit_half,
                 "boot_size_at_null": boot_size,
                 "wald_boot_concordance": concordance,
                 "calibration_ok": calibration_ok, "ncal": a.ncal, "B": a.B,
                 "sigma_delta": a.sigma_delta, "family": a.family,
                 "binding": build_binding(a, years)}
        print(json.dumps(calib, indent=2))
        if a.mode == "calibrate":
            if a.out:
                Path(a.out).write_text(json.dumps(calib))
            return
        a._calib = calib
    # Round-12 (C33): EVERY external calibration artifact passes the
    # provenance gate BEFORE calibration_ok is even consulted — bytes are
    # read ONCE; the frozen hash is MANDATORY and must match those bytes;
    # the SAME bytes are strict-parsed (nonstandard JSON constants
    # rejected); the shared recursive schema, the preregistered production
    # sizes and the decision-input binding are enforced; and the verified
    # hash is written to the run log UNCONDITIONALLY. Only then does
    # calibration_ok (or --force-nested) select the engine. Any gate
    # failure ABORTS the run: a Stage-B run must be able to PROVE which
    # calibration bytes it consumed.
    calib = getattr(a, "_calib", None)
    cal_data = calib if isinstance(calib, dict) else {}
    if calib is None and a.calib_json and not a.force_nested:
        from calib_schema import (validate_calibration,
                                  reject_nonstandard_constants)
        import hashlib as _hcs
        raw_cal = Path(a.calib_json).read_bytes()             # (1) once
        got_sha = _hcs.sha256(raw_cal).hexdigest()
        if not a.calib_expected_sha256:                       # (2) mandatory
            raise SystemExit(
                "[mde] ABORT -- an EXTERNAL calibration requires "
                "--calib-expected-sha256 (fail-closed; pass the frozen "
                "calibration_sha256) -- round-12")
        if got_sha != a.calib_expected_sha256:                # (3) match
            raise SystemExit(
                f"[mde] ABORT -- calibration file sha256 {got_sha[:16]}... "
                "does not match --calib-expected-sha256; the frozen "
                "calibration is the ONLY licensed artifact")
        try:                                                  # (4) same bytes
            cal_data = json.loads(
                raw_cal.decode("utf-8"),
                parse_constant=reject_nonstandard_constants)
        except SystemExit:
            raise
        except Exception as e:
            raise SystemExit(
                f"[mde] ABORT -- calibration is not strict JSON: {e}")
        errs = [f"calibration schema: {e}"                    # (5) schema,
                for e in validate_calibration(cal_data)]      # sizes,
        if cal_data.get("ncal") != PRODUCTION_NCAL or \
                cal_data.get("B") != PRODUCTION_B:
            errs.append(
                f"sizes ncal={cal_data.get('ncal')!r}/"
                f"B={cal_data.get('B')!r} are not the preregistered "
                f"production sizes {PRODUCTION_NCAL}/{PRODUCTION_B}")
        if isinstance(cal_data.get("binding"), dict):         # and binding
            want = build_binding(a, years)
            if cal_data["binding"] != want:
                errs.append("decision-input binding mismatch — the "
                            "calibration was produced for different "
                            "decision inputs")
        if errs:
            raise SystemExit("[mde] ABORT -- external calibration "
                             "rejected: " + "; ".join(errs))
        print(f"[mde] calibration artifact sha256 verified: {got_sha}")
    if a.force_nested:
        cal_data = {}
    use_wald = bool(cal_data) and cal_data.get("calibration_ok") is True
    crit_full = cal_data.get("crit_abs_z") if use_wald else None
    crit_half = cal_data.get("crit_abs_z_half") if use_wald else None
    decision = "wald_shortcut" if use_wald else "full_nested_pass_p"
    print(f"[mde] curve decision engine: {decision}")

    lo, hi, step = (float(v) for v in a.theta_grid.split(":"))
    grid = np.arange(lo, hi + 1e-9, step)
    rows = []
    for th in grid:
        if a.family == "p0":
            rej0 = 0
            for i in range(a.reps):
                rng = np.random.default_rng(SEED + 10_000 + i)
                c0 = simulate_p0(years, tok_p0, tok_imf, r_p0, r_imf, th,
                                 a.rho, a.sigma_delta, rng)
                if use_wald:
                    rej0 += wald_singleton_decide(wald_z(c0), crit_full)
                else:
                    rej0 += (pass_p(c0, a.B, SEED + 50_000 + i)
                             < a.alpha)          # SINGLETON at alpha, no Holm
            rows.append({"theta": round(float(th), 3),
                         "power_p0": rej0 / a.reps,
                         "power_family": rej0 / a.reps})
            continue
        rej1 = rej2 = rejfam = 0
        for i in range(a.reps):
            rng = np.random.default_rng(SEED + 10_000 + i)
            c1, c2 = simulate_joint(years, tokens, a.base_rate, th, comp * th,
                                    a.rho, a.sigma_delta, rng,
                                    tokens_p1=tok_p1, tokens_p2=tok_p2,
                                    rate_p1=r_p1, rate_p2=r_p2,
                                    p2_years=p2_years,
                                    tokens_imf=tok_imf, rate_imf=r_imf)
            if use_wald:
                r1h, r2h = wald_holm2_decide(wald_z(c1), wald_z(c2),
                                             crit_full, crit_half)
            else:
                p1 = pass_p(c1, a.B, SEED + 20_000 + i)
                p2 = pass_p(c2, a.B, SEED + 30_000 + i)
                r1h, r2h = holm2(p1, p2, a.alpha)
            rej1 += r1h; rej2 += r2h; rejfam += (r1h or r2h)
        rows.append({"theta": round(float(th), 3),
                     "power_p1": rej1 / a.reps, "power_p2": rej2 / a.reps,
                     "power_family": rejfam / a.reps})
    df = pd.DataFrame(rows)
    mde = df.loc[df["power_family"] >= 0.80, "theta"]
    print(df.to_string(index=False))
    print(f"[mde] family MDE80 = {float(mde.iloc[0]) if len(mde) else float('nan')} "
          f"(engine={decision}, family={a.family}, companion={a.companion}, "
          f"sigma_delta={a.sigma_delta})")
    if a.out:
        df.to_csv(a.out, index=False)

if __name__ == "__main__":
    main()
