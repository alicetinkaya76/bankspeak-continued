"""G1 genre adjudication (PREREG v0.5 §2; round-6 corrections).

Global deterministic draw: rank ALL candidate rows by
SHA256(f"{seed}|{id}") ascending, take 20 — independent of any per-cell
sampler. Outcome-blind sheet: audit_key + title (+abstract if present) only;
institution/genre labels are not written. Scoring: four binary items per row,
blank/uncertain = 0; a row passes iff all four are 1; G1 PASS iff >= 16/20.
Rows lacking an abstract are flagged title_only."""
from __future__ import annotations
import argparse, hashlib
from pathlib import Path
import pandas as pd

ITEMS = ["i1_recurring_country_surveillance", "i2_not_project_tied",
         "i3_staff_analytical_report", "i4_periodic_cycle"]

def rank_key(seed: int, cid: str) -> str:
    return hashlib.sha256(f"{seed}|{cid}".encode()).hexdigest()

def draw(frame: pd.DataFrame, seed: int = 20260806, n: int = 20) -> pd.DataFrame:
    d = frame.copy()
    if len(d) < n:                            # round-7: G1 needs exactly 20
        raise ValueError(f"G1 draw requires >= {n} candidates; frame has "
                         f"{len(d)} — record the gate as FAILED instead")
    d["_k"] = d["id"].astype(str).map(lambda c: rank_key(seed, c))
    d = d.sort_values("_k").head(n).drop(columns="_k").reset_index(drop=True)
    d.insert(0, "audit_key", range(1, len(d) + 1))
    return d

def write_sheet(sel: pd.DataFrame, out: Path) -> None:
    cols = ["audit_key", "title"] + (["abstract"] if "abstract" in sel else [])
    sheet = sel[cols].copy()
    sheet["title_only"] = ("abstract" not in sel) | \
        (sel["abstract"].fillna("").eq("") if "abstract" in sel else True)
    for c in ITEMS:
        sheet[c] = ""
    sheet.to_csv(out, index=False)

def score(sheet: pd.DataFrame) -> dict:
    ok = pd.Series(True, index=sheet.index)
    for c in ITEMS:
        v = pd.to_numeric(sheet[c], errors="coerce").fillna(0)
        ok &= v == 1
    n_pass = int(ok.sum())
    size_ok = len(sheet) == 20                # round-7: >=16 OF 20, exactly
    return {"n": len(sheet), "n_pass": n_pass,
            "sheet_size_valid": bool(size_ok),
            "g1_pass": bool(size_ok and n_pass >= 16),
            "title_only_n": int(sheet.get("title_only", pd.Series(dtype=bool))
                                .fillna(False).sum())}

def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw"); d.add_argument("--frame", required=True)
    d.add_argument("--out", required=True); d.add_argument("--seed", type=int,
                                                           default=20260806)
    s = sub.add_parser("score"); s.add_argument("--sheet", required=True)
    a = ap.parse_args()
    if a.cmd == "draw":
        sel = draw(pd.read_csv(a.frame), a.seed)
        write_sheet(sel, Path(a.out))
        print(f"[g1] wrote outcome-blind sheet: {len(sel)} rows -> {a.out}")
    else:
        print(score(pd.read_csv(a.sheet)))

if __name__ == "__main__":
    main()
