"""Machine-readable 28-form -> 13-family Tier-1 outcome (PREREG v0.3 §3, App. A).
The single matching rule, exact integer counters. Round-4 precondition 4."""
from __future__ import annotations
import hashlib, re
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
FAMILIES_YAML = ROOT / "config" / "families.yaml"
TOKEN_RE = re.compile(r"[A-Za-z']+")          # identical to src/textstats.py

def load_families(path: Path = FAMILIES_YAML) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    fams = cfg["families"]
    forms = [w for ws in fams.values() for w in ws]
    if len(fams) != 13:
        raise ValueError(f"expected 13 families, got {len(fams)}")
    if len(forms) != 28 or len(set(forms)) != 28:
        raise ValueError(f"expected 28 unique forms, got {len(forms)}")
    cfg["_form2fam"] = {w: f for f, ws in fams.items() for w in ws}
    cfg["_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return cfg

_CFG = None
def _cfg() -> dict:
    global _CFG
    if _CFG is None:
        _CFG = load_families()
    return _CFG

def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def count_families(text: str) -> dict:
    """-> {eligible_tokens, tier1_count, fam_<name>: int x13}. Exact integers."""
    toks = tokens(text)
    f2f = _cfg()["_form2fam"]
    out = {f"fam_{f}": 0 for f in _cfg()["families"]}
    total = 0
    for t in toks:
        fam = f2f.get(t)
        if fam is not None:
            out[f"fam_{fam}"] += 1
            total += 1
    out["eligible_tokens"] = len(toks)
    out["tier1_count"] = total
    return out

def verify_against_repo_config(config_yaml: Path) -> None:
    """Assert the 28 forms equal config.yaml markers.tier1 (order-free)."""
    cfg = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))
    tier1 = set(w.lower() for w in cfg["markers"]["tier1"])
    forms = set(_cfg()["_form2fam"])
    if tier1 != forms:
        raise AssertionError(f"mismatch: only-in-config={sorted(tier1-forms)} "
                             f"only-in-families={sorted(forms-tier1)}")

if __name__ == "__main__":
    c = load_families()
    print(f"[families] 13 families / 28 forms OK; sha256={c['_sha256']}")
