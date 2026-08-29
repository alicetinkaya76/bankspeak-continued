"""Pure-stdlib text measures (D4, D5). Deterministic; unit-tested offline.
All rates are per-token or per-100/per-1k tokens so document length cancels."""
from __future__ import annotations
import re, statistics

TOKEN_RE = re.compile(r"[A-Za-z']+")
NOMINAL_RE = re.compile(r"\b[A-Za-z]+(?:tion|sion|ment|ance|ence|ity)s?\b", re.I)
ACRONYM_RE = re.compile(r"\b[A-Z]{2,6}\b")
YEAR_RE = re.compile(r"\b(1[89]\d{2}|20\d{2})\b")
MONTHS = {"january","february","march","april","may","june","july",
          "august","september","october","november","december"}
DEICTIC_RE = re.compile(r"\b(?:last|next)\s+(?:year|month|decade|week)\b", re.I)

def tokens(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())

def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"[.!?]+", text) if len(s.split()) > 2]

def rate_from_list(toks: list[str], words: list[str], per: int = 1000) -> float:
    wl = set(w.lower() for w in words)
    n = len(toks)
    return per * sum(1 for t in toks if t in wl) / n if n else 0.0

def nominalization_per100(text: str, toks: list[str]) -> float:
    n = len(toks)
    return 100 * len(NOMINAL_RE.findall(text)) / n if n else 0.0

def acronym_per1k(text: str, toks: list[str]) -> float:
    n = len(toks)
    hits = [a for a in ACRONYM_RE.findall(text) if a not in {"II", "III", "IV", "VI"}]
    return 1000 * len(hits) / n if n else 0.0

def and_per100(toks: list[str]) -> float:
    n = len(toks)
    return 100 * toks.count("and") / n if n else 0.0

def temporal_anchor_per1k(text: str, toks: list[str]) -> float:
    """Explicit years + month names + deictic time phrases (D4: Bankspeak's
    'loss of temporal anchoring' proxy)."""
    n = len(toks)
    if not n:
        return 0.0
    hits = len(YEAR_RE.findall(text)) + sum(1 for t in toks if t in MONTHS) \
        + len(DEICTIC_RE.findall(text))
    return 1000 * hits / n

def mean_sentence_len(text: str) -> float:
    sl = [len(TOKEN_RE.findall(s)) for s in sentences(text)]
    return round(statistics.mean(sl), 2) if sl else 0.0

def mattr(toks: list[str], window: int = 500) -> float:
    """Moving-average TTR — length-fair lexical diversity."""
    if len(toks) < window:
        return round(len(set(toks)) / len(toks), 4) if toks else 0.0
    vals = []
    for i in range(0, len(toks) - window + 1, window):
        w = toks[i:i + window]
        vals.append(len(set(w)) / window)
    return round(statistics.mean(vals), 4)

def compute_classic(text: str, mgmt_lexicon: list[str]) -> dict:
    toks = tokens(text)
    return {
        "tokens": len(toks),
        "nominal_per100": round(nominalization_per100(text, toks), 3),
        "acronym_per1k": round(acronym_per1k(text, toks), 3),
        "and_per100": round(and_per100(toks), 3),
        "temporal_per1k": round(temporal_anchor_per1k(text, toks), 3),
        "mean_slen": mean_sentence_len(text),
        "mattr500": mattr(toks),
        "mgmt_per1k": round(rate_from_list(toks, mgmt_lexicon), 3),
    }

def compute_markers(text: str, tier1: list[str], tier2: list[str]) -> dict:
    toks = tokens(text)
    return {
        "tokens": len(toks),
        "tier1_per1k": round(rate_from_list(toks, tier1), 4),
        "tier2_per1k": round(rate_from_list(toks, tier2), 4),
    }
