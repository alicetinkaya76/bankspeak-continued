#!/usr/bin/env python3
"""Audit the reference list against Crossref, and against the text that cites it.

The predecessor paper from this project was rejected partly for unverified and
drifted citations, so this runs the check rather than repeating the assurance. It
does three things a manual pass reliably gets wrong:

1. **Resolves every DOI against Crossref** and compares the returned year,
   container title, volume and pages with what the manuscript prints. A DOI that
   resolves is not the same as a DOI whose metadata matches, and drift lives in
   the difference.
2. **Cross-checks in-text citations against the list in both directions.** An
   in-text mention with no entry is fatal; an entry nobody cites is padding a
   referee will notice. Both are easy to introduce while editing and neither is
   visible from reading one end.
3. **Reports what it could not check**, rather than passing it silently. Entries
   without a DOI — conference proceedings, working papers — are listed as
   unresolvable-here so a human knows exactly what is left to verify by hand.

It does NOT check whether a cited work supports the claim citing it. No tool can;
that is left to the reviewer and named as their task in the third-eye brief.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
OUT = ROOT / "data" / "analysis" / "citation_audit.json"


def _cache() -> dict:
    """Per-DOI Crossref results from the last online run, for --offline."""
    if not OUT.exists():
        return {}
    try:
        prev = json.loads(OUT.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {e["doi"]: e.get("check", {})
            for e in prev.get("entries", []) if e.get("doi")}


CACHE = _cache()
API = "https://api.crossref.org/works/"
MAIL = "kapsul.yonetim@gmail.com"          # Crossref's polite pool


def split_paper() -> tuple[str, str]:
    """Return the body with whitespace normalised, and the raw reference section.

    The body is normalised because a surname wrapped across a line break — "De\n
    Francesco" — is invisible to a substring search, and the first version of this
    audit reported De Francesco & Guaschino as an uncited entry on exactly that
    basis. Three parser defects in this file have now produced three false
    citation findings, which is a fair illustration of why the audit's own output
    needs checking before anyone acts on it.
    """
    s = PAPER.read_text(encoding="utf-8")
    assert "## References" in s, "no reference section"
    body, refs = s.split("## References", 1)
    return " ".join(body.split()), refs


def parse_entries(refs: str) -> list[dict]:
    """Entries are separated by ' · ' WITHIN themed paragraphs, and paragraphs
    are separated by blank lines.

    Splitting on ' · ' alone runs the last entry of one paragraph into the first
    of the next, and the first version of this function did exactly that: an
    entry with no DOI (conference proceedings) silently absorbed the DOI of the
    entry after it, and reported Juzek & Ward as drifting to Gehrmann's paper.
    That is a parser defect masquerading as a citation defect, which is the worst
    kind of output an audit tool can produce — it would have sent someone to
    'fix' a reference that was correct.
    """
    out = []
    for para in re.split(r"\n\s*\n", refs):
        para = re.sub(r"\*\*[^*]+\*\*", "", para)          # drop the theme label
        if para.strip().startswith("*") or len(para.strip()) < 40:
            continue                                       # the italic preamble
        for chunk in re.split(r"\s·\s", para):
            chunk = " ".join(chunk.split())
            if len(chunk) < 30:
                continue
            m = re.search(r"10\.\d{4,9}/[^\s,;)]+", chunk)
            doi = m.group(0).rstrip(".") if m else None
            # Surnames can be multi-word ("Lopez Bernal", "De Francesco") and are
            # followed by a comma-initial. Take everything up to that comma.
            a = re.match(r"([A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+(?:\s+[A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+)*),\s*[A-Z]\.",
                         chunk)
            y = re.search(r"\((\d{4})[a-z]?\)", chunk)
            out.append({"raw": chunk[:200], "doi": doi,
                        "first_author": a.group(1) if a else None,
                        "year": int(y.group(1)) if y else None})
    return out


def crossref(doi: str) -> dict:
    try:
        r = requests.get(API + doi, timeout=30,
                         headers={"User-Agent": f"citation-audit (mailto:{MAIL})"})
        if r.status_code != 200:
            return {"status": r.status_code}
        m = r.json()["message"]
        # Print year first. Crossref often carries an earlier online-first date,
        # and treating that as the canonical year turns correct citations into
        # false drift reports — Lopez Bernal (2017) is IJE 46(1), print 2017,
        # online 2016, and the first version of this flagged it.
        yr = None
        for k in ("published-print", "issued", "published-online"):
            v = m.get(k, {}).get("date-parts", [[None]])[0][0]
            if v:
                yr = v
                break
        alt = [m.get(k, {}).get("date-parts", [[None]])[0][0]
               for k in ("published-print", "published-online", "issued")]
        return {"status": 200, "year": yr,
                "years_seen": [x for x in alt if x],
                "container": (m.get("container-title") or [""])[0],
                "volume": m.get("volume"), "page": m.get("page"),
                "title": (m.get("title") or [""])[0][:90],
                "first_author": (m.get("author") or [{}])[0].get("family")}
    except Exception as e:
        return {"status": None, "error": type(e).__name__}


def main(offline: bool = False) -> int:
    """offline reuses the stored per-entry verdicts instead of asking Crossref.

    Added after an external reading found that an invocation with --offline made
    thirty-one live HTTP requests and rewrote a git-tracked file during what the
    caller believed was a read-only audit: argparse was never wired up, so the
    flag was accepted by the shell and ignored by the program. Silently ignoring
    an argument is worse than rejecting it, and both are now impossible.
    """
    body, refs = split_paper()
    entries = parse_entries(refs)
    print(f"Reference list: {len(entries)} entries parsed\n")

    problems = []
    for e in entries:
        if not e["doi"]:
            e["check"] = {"verdict": "no DOI — verify by hand"}
            problems.append(f"{e['first_author']} {e['year']}: no DOI in entry")
            continue
        if offline:
            cached = CACHE.get(e["doi"])
            if cached is None:
                e["check"] = {"verdict": "not in the cached audit"}
                problems.append(f"{e['first_author']} {e['year']}: no cached "
                                "Crossref result; rerun without --offline")
                continue
            cr = {k: v for k, v in cached.items() if k != "verdict"}
        else:
            cr = crossref(e["doi"])
            time.sleep(0.3)                   # be polite to Crossref
        if cr.get("status") != 200:
            e["check"] = {"verdict": "DOI DOES NOT RESOLVE", **cr}
            problems.append(f"{e['first_author']} {e['year']}: DOI "
                            f"{e['doi']} -> {cr.get('status')}")
            continue
        drift = []
        if e["year"] and cr.get("years_seen") and e["year"] not in cr["years_seen"]:
            drift.append(f"year {e['year']} vs Crossref {cr['years_seen']}")
        if (e["first_author"] and cr.get("first_author")
                and e["first_author"].lower() != cr["first_author"].lower()):
            drift.append(f"first author {e['first_author']} vs "
                         f"{cr['first_author']}")
        e["check"] = {"verdict": "drift" if drift else "verified",
                      "drift": drift, **cr}
        mark = "DRIFT" if drift else "ok   "
        print(f"  {mark} {str(e['first_author'])[:18]:18s} {e['year']}  "
              f"{e['doi'][:44]}")
        if drift:
            for d in drift:
                print(f"          {d}")
            problems.append(f"{e['first_author']} {e['year']}: " + "; ".join(drift))

    # --- two-way in-text cross-check
    surnames = {e["first_author"] for e in entries if e["first_author"]}
    # Word boundaries, not substrings. A surname that is a prefix of a common
    # word passes a substring test against any body text: "Ban" is inside "Bank",
    # which this paper contains hundreds of times, so an uncited Ban entry would
    # have been reported as cited without anyone citing it. The check would still
    # have returned "none" and meant nothing.
    def cited(name: str) -> bool:
        return re.search(rf"(?<![A-Za-zÀ-ÿ]){re.escape(name)}(?![A-Za-zÀ-ÿ])",
                         body) is not None
    uncited = sorted(n for n in surnames if n and not cited(n))
    intext = set(re.findall(r"([A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+)"
                            r"(?:\s*&\s*[A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+|\s+et al\.)"
                            r"\s*\(\d{4}[a-z]?\)", body))
    unlisted = sorted(n for n in intext if n not in surnames)

    print(f"\n  entries never cited in the body: {uncited or 'none'}")
    print(f"  in-text citations with no entry: {unlisted or 'none'}")
    problems += [f"uncited entry: {n}" for n in uncited]
    problems += [f"in-text citation with no reference entry: {n}" for n in unlisted]

    if offline:
        # An offline audit reports; it does not overwrite the record it read.
        print(f"\n[cite] {len(problems)} problem(s); offline, "
              f"{OUT.relative_to(ROOT)} not rewritten")
        return 1 if problems else 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"n_entries": len(entries), "entries": entries,
                               "uncited_entries": uncited,
                               "unlisted_intext": unlisted,
                               "problems": problems}, indent=1),
                   encoding="utf-8")
    print(f"\n[cite] {len(problems)} problem(s); wrote {OUT.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--offline", action="store_true",
                    help="reuse the stored Crossref verdicts and write nothing")
    sys.exit(main(ap.parse_args().offline))
