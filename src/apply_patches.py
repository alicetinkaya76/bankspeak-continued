"""Round-4 targeted repairs to s08 (full-precision placebo thresholds +
E3-aligned language) and s06 (hardware-invariant NLL population).
Safe: exact-match asserts, .bak-round4 backups, idempotent (skips if applied)."""
from __future__ import annotations
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATCHES = [
    ("src/s08_its_analysis.py",
     '''    return {"n_years": len(sub),
            "level_shift_b2": round(res.params["post"], 4),
            "p_b2": round(res.pvalues["post"], 4),
            "slope_change_b3": round(res.params["t_post"], 4),
            "p_b3": round(res.pvalues["t_post"], 4),
            "pre_trend_slope": round(pre_slope, 4)}''',
     '''    return {"n_years": len(sub),
            "level_shift_b2": round(res.params["post"], 4),
            "p_b2": round(res.pvalues["post"], 4),
            "slope_change_b3": round(res.params["t_post"], 4),
            "p_b3": round(res.pvalues["t_post"], 4),
            "p_b2_exact": float(res.pvalues["post"]),
            "p_b3_exact": float(res.pvalues["t_post"]),
            "pre_trend_slope": round(pre_slope, 4)}''',
     "s08: emit full-precision p-values alongside rounded display values"),
    ("src/s08_its_analysis.py",
     '''                if pf and (pf["p_b2"] < 0.05 or pf["p_b3"] < 0.05):''',
     '''                if pf and (pf["p_b2_exact"] < 0.05 or pf["p_b3_exact"] < 0.05):''',
     "s08: placebo threshold decided on full-precision p-values"),
    ("src/s08_its_analysis.py",
     '''    print("[s08] REMINDER: outputs describe discontinuities; attribution language "
          "is out of scope by design (D2).")''',
     '''    print("[s08] REMINDER: scans are descriptive and endpoint-sensitive; they do "
          "not identify a unique break date, trajectory shape, or mechanism (E3/D2).")''',
     "s08: output language aligned with adopted E3 wording"),
    ("src/s06_perplexity_panel.py",
     '''    if device == "cpu":
        rng = random.Random(cfg["seed"])
        by_cell: dict[tuple, list] = {}
        for t in txts:
            m = idx.get(t.stem)
            if m:
                by_cell.setdefault((m["stratum"], m["year"]), []).append(t)
        cap = cfg["perplexity"]["cpu_subsample_docs_per_cell"]
        txts = sorted(t for cell in sorted(by_cell) for t in
                      (by_cell[cell] if len(by_cell[cell]) <= cap
                       else rng.sample(sorted(by_cell[cell]), cap)))
        print(f"[s06] cpu mode: subsampled to {len(txts)} docs")''',
     '''    # PREREG v0.3 §7: one frozen document rule on every device — the full
    # eligible population is scored; the CPU per-cell subsample is abolished
    # (hardware-dependent analysis samples are not acceptable, round-4 §3.3).
    print(f"[s06] hardware-invariant mode: scoring all {len(txts)} docs on {device}")''',
     "s06: hardware-invariant NLL population"),
]

def main() -> None:
    changed = 0
    for rel, old, new, note in PATCHES:
        p = ROOT / rel
        if not p.exists():
            sys.exit(f"[patch] MISSING {p} — run from the repo root")
        s = p.read_text(encoding="utf-8")
        if new in s:
            print(f"[patch] already applied: {note}")
            continue
        if old not in s:
            sys.exit(f"[patch] ABORT — expected block not found in {rel} "
                     f"(file drifted; apply by hand):\n{note}")
        bak = p.with_suffix(p.suffix + ".bak-round4")
        if not bak.exists():
            shutil.copy2(p, bak)
        p.write_text(s.replace(old, new, 1), encoding="utf-8")
        changed += 1
        print(f"[patch] applied: {note} (backup: {bak.name})")
    print(f"[patch] done — {changed} change(s). NOTE: also delete the now-unused "
          f"'cpu_subsample_docs_per_cell' key and the unimplemented low-cell "
          f"'widen' comment from config/config.yaml (grep: cpu_subsample / widen).")

if __name__ == "__main__":
    main()
