"""s07 — power gate for Tier-1 claims (D7).
Model: token-level marker occurrence as Poisson with rate p per token.
Two-sample rate comparison (pre rate p0 vs post rate p1) on N tokens per group,
normal approximation on counts: lambda_i = N * p_i,
    power = Phi( (lambda1-lambda0)/sqrt(lambda0+lambda1) - z_{1-alpha} ).
Stage-0 context: micro bins (~2k tokens) had power ~0 for realistic rates — which is
exactly why Tier-1 nulls are uninformative until this gate passes (>=0.8)."""
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
from scipy.stats import norm
from utils import ROOT, load_config

def power_two_rates(p0: float, p1: float, n_tokens: float, alpha: float = 0.05) -> float:
    lam0, lam1 = n_tokens * p0, n_tokens * p1
    if lam0 + lam1 == 0:
        return 0.0
    z = norm.ppf(1 - alpha)
    return float(norm.cdf((lam1 - lam0) / math.sqrt(lam0 + lam1) - z))

def required_tokens(p0: float, p1: float, target: float = 0.8, alpha: float = 0.05) -> int:
    za, zb = norm.ppf(1 - alpha), norm.ppf(target)
    n = ((za + zb) ** 2) * (p0 + p1) / ((p1 - p0) ** 2)
    return int(math.ceil(n))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    ap.add_argument("--p0", type=float, default=2e-5,
                    help="pre-2022 Tier-1 word rate per token (default: conservative)")
    ap.add_argument("--p1", type=float, default=2e-4,
                    help="post-2022 rate per token under ~10x uplift hypothesis")
    args = ap.parse_args()
    cfg = load_config(args.config)
    req = required_tokens(args.p0, args.p1)
    print(f"[s07] p0={args.p0:g}, p1={args.p1:g} -> required tokens/group "
          f"for 0.8 power: {req:,}")
    markers = ROOT / "data" / "features" / "markers.csv"
    rows_out = [{"p0": args.p0, "p1": args.p1, "required_tokens_per_group": req}]
    if markers.exists():
        cells: dict[tuple, int] = {}
        with open(markers, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                key = (r["stratum"], r["year"])
                cells[key] = cells.get(key, 0) + int(r["tokens"])
        for (stratum, year), n in sorted(cells.items()):
            pw = power_two_rates(args.p0, args.p1, n)
            rows_out.append({"stratum": stratum, "year": year, "tokens": n,
                             "power": round(pw, 3)})
            print(f"[s07] {stratum} {year}: {n:,} tokens -> power {pw:.3f}")
    out = ROOT / "data" / "analysis" / "power.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    keys = sorted({k for r in rows_out for k in r})
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader(); w.writerows(rows_out)
    print(f"[s07] wrote {out}")

if __name__ == "__main__":
    main()
