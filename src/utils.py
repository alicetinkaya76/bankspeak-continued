"""Shared plumbing: config, polite HTTP, manifest, hashing. (D9, D10)"""
from __future__ import annotations
import hashlib, json, time, sys
from pathlib import Path
import yaml
import requests

ROOT = Path(__file__).resolve().parents[1]

def load_config(path: str | Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def session_for(cfg: dict) -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent":
        f"bankspeak-continued/0.1 (research; contact: {cfg['contact_email']})"})
    return s

def get_with_retry(sess: requests.Session, url: str, params: dict, cfg: dict,
                   attempt_hook=None):
    """GET with exponential backoff on 429/5xx; polite sleep after every call.
    Permanent client errors (403/404/...) raise immediately — retrying cannot
    fix them. Round-11 (C30): when attempt_hook is given, EVERY retried
    429/5xx response body is archived verbatim from INSIDE the retry layer
    via attempt_hook(params_dict, raw_bytes, status_code); a retried
    response without a raw byte body aborts."""
    api = cfg["api"]
    last_err = None
    for attempt in range(api["max_retries"]):
        try:
            r = sess.get(url, params=params, timeout=api["timeout"])
        except requests.RequestException as e:
            last_err = e
            time.sleep(api["backoff_base"] ** attempt)
            continue
        if r.status_code == 200:
            time.sleep(api["sleep_seconds"])
            return r
        if r.status_code in (429, 500, 502, 503, 504):
            if attempt_hook is not None:
                raw = getattr(r, "content", None)
                if raw is None:
                    raise RuntimeError("[retry] transport exposes no raw "
                                       "byte body on a retried response; "
                                       "live capture archives every "
                                       "attempt")
                attempt_hook(dict(params), raw, r.status_code)
            wait = api["backoff_base"] ** attempt
            print(f"[retry] HTTP {r.status_code}; sleeping {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
            continue
        r.raise_for_status()
    raise RuntimeError(f"GET failed after {api['max_retries']} attempts: {url} ({last_err})")

def iter_documents(payload: dict):
    """The API nests records under 'documents' keyed by 'D<id>' and ALSO puts a
    'facets' key inside that dict — skip it (observed in live response, 6 Aug 2026)."""
    docs = payload.get("documents", {}) or {}
    for k in sorted(docs.keys()):
        if k == "facets":
            continue
        yield docs[k]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def manifest_path() -> Path:
    return ROOT / "data" / "meta" / "manifest.tsv"

def manifest_ids() -> set[str]:
    p = manifest_path()
    if not p.exists():
        return set()
    return {line.split("\t", 1)[0] for line in p.read_text(encoding="utf-8").splitlines() if line}

def manifest_append(doc_id: str, url: str, path: Path, digest: str) -> None:
    """Append-only (D10). Caller must check manifest_ids() first."""
    with open(manifest_path(), "a", encoding="utf-8") as f:
        f.write(f"{doc_id}\t{digest}\t{url}\t{path.as_posix()}\t{time.strftime('%Y-%m-%d')}\n")

def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")

def read_jsonl(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
