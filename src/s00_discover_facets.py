"""s00 — enumerate real facet values (docty_exact, majdocty_exact, lang_exact) and
diff them against config guesses. (Rationale: D-open-item; never hardcode blindly.)"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from utils import ROOT, load_config, session_for, get_with_retry

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    cfg = load_config(ap.parse_args().config)
    sess = session_for(cfg)
    params = {"format": "json", "rows": 0, "fct": "docty_exact,majdocty_exact,lang_exact"}
    r = get_with_retry(sess, cfg["api"]["base_url"], params, cfg)
    payload = r.json()
    out = ROOT / "data" / "meta" / "facets.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[s00] wrote {out}")
    # Best-effort diff against config guesses
    text = json.dumps(payload).lower()
    for stratum, spec in sorted(cfg["strata"].items()):
        for label in spec["docty_exact"]:
            flag = "OK " if label.lower() in text else "MISSING"
            print(f"[s00] {flag} config label for {stratum!r}: {label!r}")
    print("[s00] Inspect facets.json for exact labels (incl. historical variants) "
          "and correct config/config.yaml BEFORE running s01.")

if __name__ == "__main__":
    main()
