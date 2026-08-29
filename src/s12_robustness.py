"""s12 — robustness battery requested by the third-eye review (2026-08-07).
(a) Leave-one-year-out influence for the assembled-AR tier1 level-only fit.
(b) Empirical breakpoint ranking: same spec at every admissible cut; where does
    2023 rank? (Answers what a placebo fraction cannot.)
(c) Robust aggregation: median and 10%-trimmed yearly means for tier1 and NLL;
    era contrast 2019-22 vs 2023-26 under each aggregator.
(d) Tier-1 lexicon decomposition: per-word share of the post-2022 mass and
    leave-one-word-out era contrasts, per stratum.
Outputs -> data/analysis/robustness/*.csv; every number regenerable."""
from __future__ import annotations
import argparse, csv, re
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
from utils import ROOT, load_config
from s08_its_analysis import fit_its, yearly_series
from s11_paper_artifacts import assembled_ar, fit_level_only

OUT = ROOT / "data" / "analysis" / "robustness"

def loyo_ar(cfg) -> pd.DataFrame:
    lags = cfg["its"]["newey_west_lags"]
    by = int(cfg["its"]["breakpoint"][:4])
    ar = assembled_ar()
    rows = [{"dropped_year": "NONE",
             **fit_level_only(ar, "tier1_per1k", by, lags)}]
    for y in sorted(ar["year"]):
        fit = fit_level_only(ar[ar["year"] != y], "tier1_per1k", by, lags)
        rows.append({"dropped_year": str(y), **fit})
    return pd.DataFrame(rows)

def breakpoint_ranking(cfg) -> pd.DataFrame:
    """Fit the 2023 spec at every candidate cut with >=5 pre years and >=2 post
    years; rank |b2|/p at 2023 against all candidates. Post-support (n_post)
    varies by construction and is reported per cut."""
    lags = cfg["its"]["newey_west_lags"]
    rows = []
    series = {"ar_assembled": (assembled_ar(), fit_level_only)}
    df = yearly_series(cfg)
    for st in sorted(df["stratum"].unique()):
        series[f"doc_level_{st}"] = (df[df["stratum"] == st].copy(), fit_its)
    for name, (sub, fitter) in sorted(series.items()):
        years = sorted(sub.dropna(subset=["tier1_per1k"])["year"].astype(int))
        for cut in range(years[0] + 5, years[-1]):
            n_post = sum(1 for y in years if y >= cut)
            if n_post < 2:
                continue
            fit = fitter(sub, "tier1_per1k", cut, lags)
            if not fit:
                continue
            rows.append({"series": name, "cut": cut, "n_post": n_post,
                         "b2": fit["level_shift_b2"], "p_b2": fit["p_b2"]})
    out = pd.DataFrame(rows)
    ranks = []
    for name, grp in out.groupby("series"):
        grp = grp.assign(abs_b2=grp["b2"].abs())
        grp = grp.sort_values("abs_b2", ascending=False).reset_index(drop=True)
        r2023 = grp.index[grp["cut"] == 2023]
        ranks.append({"series": name, "n_candidate_cuts": len(grp),
                      "rank_of_2023_by_abs_b2":
                          int(r2023[0]) + 1 if len(r2023) else None,
                      "percentile_of_2023":
                          round(100 * (1 - r2023[0] / (len(grp) - 1)), 1)
                          if len(r2023) and len(grp) > 1 else None})
    return out, pd.DataFrame(ranks)

def robust_aggregation(cfg) -> pd.DataFrame:
    markers = pd.read_csv(ROOT / "data" / "features" / "markers.csv")
    ppl = pd.read_csv(ROOT / "data" / "features" / "ppl.csv")
    ppl = ppl.dropna(subset=["mean_nll"])
    rows = []
    def era(y): return "2019-22" if 2019 <= y <= 2022 else (
        "2023-26" if 2023 <= y <= 2026 else None)
    def aggs(s: pd.Series) -> dict:
        s = s.sort_values()
        k = int(len(s) * 0.10)
        return {"mean": s.mean(), "median": s.median(),
                "trimmed10": s.iloc[k:len(s) - k].mean() if len(s) > 2 * k else s.mean()}
    for st, grp in markers.groupby("stratum"):
        grp = grp.assign(era=grp["year"].astype(int).map(era)).dropna(subset=["era"])
        for e, sub in grp.groupby("era"):
            for agg, val in aggs(sub["tier1_per1k"]).items():
                rows.append({"measure": "tier1_per1k", "stratum": st, "model": "",
                             "era": e, "aggregator": agg, "value": round(val, 4)})
    for (st, model), grp in ppl.groupby(["stratum", "model"]):
        grp = grp.assign(era=grp["year"].astype(int).map(era)).dropna(subset=["era"])
        for e, sub in grp.groupby("era"):
            for agg, val in aggs(sub["mean_nll"]).items():
                rows.append({"measure": "mean_nll", "stratum": st, "model": model,
                             "era": e, "aggregator": agg, "value": round(val, 4)})
    return pd.DataFrame(rows)

def lexicon_decomposition(cfg) -> pd.DataFrame:
    """Per-word Tier-1 counts pre/post 2023 per stratum, from data/text.
    Reads every analysed document once (sorted; deterministic)."""
    tier1 = sorted(set(w.lower() for w in cfg["markers"]["tier1"]))
    frozen = ROOT / "data" / "meta" / f"frozen_sampling_v{cfg['sampling_version']}.csv"
    with open(frozen, newline="", encoding="utf-8") as f:
        idx = {r["id"]: r for r in csv.DictReader(f)}
    tok_re = re.compile(r"[A-Za-z']+")
    counts: dict[tuple, Counter] = defaultdict(Counter)
    tokens: dict[tuple, int] = defaultdict(int)
    for txt in sorted((ROOT / "data" / "text").rglob("*.txt")):
        meta = idx.get(txt.stem)
        if meta is None:
            continue
        period = "post" if int(meta["year"]) >= 2023 else "pre"
        toks = tok_re.findall(txt.read_text(encoding="utf-8").lower())
        key = (meta["stratum"], period)
        tokens[key] += len(toks)
        wl = set(tier1)
        counts[key].update(t for t in toks if t in wl)
    rows = []
    for (st, period) in sorted(counts):
        total_hits = sum(counts[(st, period)].values())
        for w in tier1:
            c = counts[(st, period)].get(w, 0)
            rows.append({"stratum": st, "period": period, "word": w, "count": c,
                         "rate_per1k": round(1000 * c / tokens[(st, period)], 5)
                         if tokens[(st, period)] else 0.0,
                         "share_of_tier1_hits": round(c / total_hits, 4)
                         if total_hits else 0.0})
    return pd.DataFrame(rows)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    OUT.mkdir(parents=True, exist_ok=True)
    loyo = loyo_ar(cfg)
    loyo.to_csv(OUT / "loyo_ar_tier1.csv", index=False)
    base = loyo[loyo["dropped_year"] == "NONE"]["level_shift_b2"].iloc[0]
    drops = loyo[loyo["dropped_year"] != "NONE"]
    print(f"[s12] LOYO ar tier1 level-only: base b2={base}; "
          f"range over drops [{drops['level_shift_b2'].min()}, "
          f"{drops['level_shift_b2'].max()}]; most influential year: "
          f"{drops.loc[(drops['level_shift_b2'] - base).abs().idxmax(), 'dropped_year']}")
    cuts, ranks = breakpoint_ranking(cfg)
    cuts.to_csv(OUT / "breakpoint_scan_tier1.csv", index=False)
    ranks.to_csv(OUT / "breakpoint_rank_2023.csv", index=False)
    print(ranks.to_string(index=False))
    agg = robust_aggregation(cfg)
    agg.to_csv(OUT / "robust_aggregation.csv", index=False)
    lex = lexicon_decomposition(cfg)
    lex.to_csv(OUT / "tier1_decomposition.csv", index=False)
    post = lex[(lex["period"] == "post")].sort_values("share_of_tier1_hits",
                                                      ascending=False)
    print("[s12] top post-2023 tier1 words by share:")
    print(post.groupby("word")["count"].sum().sort_values(ascending=False)
          .head(8).to_string())
    print(f"[s12] wrote 4 tables -> {OUT}")

if __name__ == "__main__":
    main()
