"""Round-4 Stage-A precondition 2: replace revision: main with immutable
commit hashes for gpt2 and EleutherAI/pythia-1.4b. Requires network +
huggingface_hub. --write patches config/config.yaml with a backup."""
from __future__ import annotations
import argparse, datetime, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ["gpt2", "EleutherAI/pythia-1.4b"]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    try:
        from huggingface_hub import HfApi
    except ImportError:
        sys.exit("[pin] pip install huggingface_hub (it is in requirements-ppl.txt)")
    api = HfApi()
    shas = {m: api.model_info(m).sha for m in MODELS}
    for m, s in shas.items():
        print(f"[pin] {m}: {s}")
    if not a.write:
        print("[pin] dry run — rerun with --write to patch config/config.yaml")
        return
    cfgp = ROOT / "config" / "config.yaml"
    s = cfgp.read_text(encoding="utf-8")
    for m, sha in shas.items():
        pat = re.compile(
            r'(hf_id:\s*["\']?' + re.escape(m) + r'["\']?\s*\n\s*revision:\s*)["\']?main["\']?')
        if not pat.search(s):
            sys.exit(f"[pin] ABORT — could not find revision: main after hf_id {m}")
        s = pat.sub(lambda mo: mo.group(1) + f'"{sha}"', s, count=1)
    bak = cfgp.with_suffix(".yaml.bak-" + datetime.date.today().isoformat())
    shutil.copy2(cfgp, bak)
    cfgp.write_text(s, encoding="utf-8")
    print(f"[pin] wrote immutable revisions into {cfgp} (backup {bak.name})")

if __name__ == "__main__":
    main()
