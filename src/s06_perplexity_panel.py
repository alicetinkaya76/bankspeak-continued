"""s06 — OPTIONAL/heavy. Perplexity under pinned FROZEN pre-ChatGPT models (D6).
Rationale: a model whose training data predates Nov 2022 cannot contain post-2022 LLM
style; its perplexity on new WB prose measures deviation from pre-LLM institutional
English. Local + pinned = reproducible instrument (no API drift).
Run explicitly (not in Makefile default). Device: mps (MacBook) / cuda / cpu."""
from __future__ import annotations
import argparse, csv, random, sys
from pathlib import Path
from utils import ROOT, load_config
from s04_features_classic import doc_index

def pick_device(pref: str):
    import torch
    if pref != "auto":
        return pref
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"

def doc_nll(model, tok, device, text: str, max_tokens: int, stride: int) -> float:
    import torch
    enc = tok(text, return_tensors="pt", truncation=True, max_length=max_tokens)
    ids = enc.input_ids.to(device)
    nlls, n = [], ids.size(1)
    for start in range(0, n, stride):
        end = min(start + stride, n)
        chunk = ids[:, max(0, end - stride):end]
        if chunk.size(1) < 2:
            continue
        with torch.no_grad():
            out = model(chunk, labels=chunk)
        nlls.append(out.loss.item() * (chunk.size(1) - 1))
    total = sum(chunk_len for chunk_len in
                [min(stride, n - s) - 1 for s in range(0, n, stride)] if chunk_len > 0)
    return sum(nlls) / total if total else float("nan")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(ROOT / "config" / "config.yaml"))
    args = ap.parse_args()
    cfg = load_config(args.config)
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError:
        sys.exit("[s06] install extras first: pip install -r requirements-ppl.txt")
    device = pick_device(cfg["perplexity"]["device"])
    print(f"[s06] device={device}")
    idx = doc_index(cfg)
    txts = sorted((ROOT / "data" / "text").rglob("*.txt"))
    # PREREG v0.3 §7: one frozen document rule on every device — the full
    # eligible population is scored; the CPU per-cell subsample is abolished
    # (hardware-dependent analysis samples are not acceptable, round-4 §3.3).
    print(f"[s06] hardware-invariant mode: scoring all {len(txts)} docs on {device}")
    rows = []
    for spec in cfg["perplexity"]["models"]:
        hf_id, rev = spec["hf_id"], spec["revision"]
        print(f"[s06] loading {hf_id}@{rev}")
        tok = AutoTokenizer.from_pretrained(hf_id, revision=rev)
        model = AutoModelForCausalLM.from_pretrained(hf_id, revision=rev).to(device).eval()
        for t in txts:
            m = idx.get(t.stem)
            if m is None:
                continue
            nll = doc_nll(model, tok, device, t.read_text(encoding="utf-8"),
                          cfg["perplexity"]["max_tokens_per_doc"],
                          cfg["perplexity"]["stride"])
            rows.append({"id": t.stem, "stratum": m["stratum"], "year": m["year"],
                         "model": hf_id, "mean_nll": round(nll, 4)})
        del model
    out = ROOT / "data" / "features" / "ppl.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "stratum", "year", "model", "mean_nll"])
        w.writeheader(); w.writerows(rows)
    print(f"[s06] wrote {out} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
