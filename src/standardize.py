"""PREREG v0.5 §6: period-valid direct standardization (round-6 repair).

The v0.4 estimator w = pi_g / p_pre,i,g standardized only the PRE distribution;
applied to post documents it produced arbitrary compositions (reviewer's
counterexample: target (.5,.5) -> weighted post (.9,.1)). Replacement, frozen:

  standardized rate  R~_it = sum_g pi_g * r_{i,g,t},   r = count/tokens per cell
  standardized cells Count~_it = R~_it * Tokens_it (non-integer; analyzed with
  allow_noninteger=True, rounding disabled in PASS-E per engine contract).

pi_g = pooled pre-2023 TOKEN shares over common-support groups (support in BOTH
institutions in BOTH periods). Per-(i,t) coverage: groups with zero tokens in
that cell drop out and pi is renormalized over available groups; coverage_it
(token-share of pi retained) is reported, min coverage feeds the hard-fail rule."""
from __future__ import annotations
import numpy as np
import pandas as pd

def build_pi(docs: pd.DataFrame, post_lo: int = 2023) -> pd.Series:
    d = docs[docs["year"] < post_lo]
    have = d.groupby(["institution", "group"])["tokens"].sum().unstack(fill_value=0)
    common = have.columns[(have > 0).all(axis=0)] if len(have) == 2 else have.columns
    post = docs[docs["year"] >= post_lo]
    hp = post.groupby(["institution", "group"])["tokens"].sum().unstack(fill_value=0)
    common = [g for g in common if g in hp.columns and (hp[g] > 0).all()]
    tok = d[d["group"].isin(common)].groupby("group")["tokens"].sum()
    return tok / tok.sum()

def standardize_cells(docs: pd.DataFrame, pi: pd.Series | None = None,
                      post_lo: int = 2023) -> pd.DataFrame:
    """docs: institution, year, group, count, tokens (doc- or cell-level).
    Returns institution-year standardized cells + coverage diagnostics."""
    if pi is None:
        pi = build_pi(docs, post_lo)
    g = (docs[docs["group"].isin(pi.index)]
         .groupby(["institution", "year", "group"])[["count", "tokens"]].sum()
         .reset_index())
    g["rate"] = g["count"] / g["tokens"]
    out, dropped = [], []
    for (i, t), sub in g.groupby(["institution", "year"]):
        sub = sub.set_index("group")
        avail = [x for x in pi.index if x in sub.index and sub.loc[x, "tokens"] > 0]
        cov = float(pi[avail].sum())
        if cov == 0:
            continue
        pin = pi[avail] / cov
        rate = float((pin * sub.loc[avail, "rate"]).sum())
        tok = float(sub["tokens"].sum())
        out.append({"institution": i, "year": int(t), "count": rate * tok,
                    "tokens": tok, "coverage": cov,
                    "std_rate": rate, "n_groups": len(avail)})
    res = pd.DataFrame(out).sort_values(["year", "institution"]).reset_index(drop=True)
    res.attrs["pi"] = pi
    res.attrs["min_coverage"] = float(res["coverage"].min()) if len(res) else 0.0
    exp = set((str(i), int(t)) for i, t in
              docs[["institution", "year"]].drop_duplicates()
              .itertuples(index=False))
    got = (set((str(i), int(t)) for i, t in
               res[["institution", "year"]].itertuples(index=False))
           if len(res) else set())
    res.attrs["dropped_cells"] = [
        {"institution": i, "year": t} for i, t in sorted(exp - got)]
    return res
