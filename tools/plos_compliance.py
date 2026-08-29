#!/usr/bin/env python3
"""Measure the manuscript against PLOS ONE's stated submission limits.

Read from the journal's own pages on 2026-08-29:

  journals.plos.org/plosone/s/submission-guidelines
    full title      "250 characters"
    short title     "100 characters"
    title style     "sentence case (only the first word of the text, proper
                     nouns, and genus names are capitalized)"
    abstract        "not exceed 300 words"; must not include "Citations";
                    avoid "Abbreviations, if possible"
    references      "PLOS uses 'Vancouver' style"; numbered, "[19]"
    length          "Manuscripts can be any length."
    disclosures     financial disclosure and competing interests go in the
                    submission form and "should not be in your manuscript file"
  journals.plos.org/plosone/s/getting-started
    "PLOS ONE waives all formatting requirements until your manuscript has
     received a provisional Editorial Accept decision."

That last sentence is why this tool reports two severities rather than one.
A BLOCKER is a limit that binds at initial submission, because it is a field in
the submission form or a rule the desk screen applies. An ACCEPT-STAGE item is
real but waived until the paper is provisionally accepted, and treating it as
urgent would burn effort on a manuscript that may never need it.

The abstract word count is deliberately strict: it splits on whitespace, so a
spaced em-dash counts as a word. That over-counts against us, which is the
direction an author wants a limit checked in.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"

TITLE_MAX = 250
SHORT_TITLE_MAX = 100
ABSTRACT_MAX = 300

# PLOS's required order. Ours renames the middle: §§3-5 are Materials and
# Methods under three headings, which the guidelines permit ("can be renamed").
REQUIRED_ORDER = ["Abstract", "Introduction", "Results", "Discussion", "References"]


def load(path: Path | None = None) -> str:
    return (path or PAPER).read_text(encoding="utf-8")


def plain(s: str) -> str:
    return re.sub(r"[*_`]", "", s)


def check_title(s: str, out: list) -> None:
    title = s.split("\n", 1)[0].lstrip("# ").strip()
    n = len(title)
    out.append(("BLOCKER" if n > TITLE_MAX else "ok",
                f"full title {n} characters (limit {TITLE_MAX})"))

    # Sentence case is an accept-stage style rule, and it cannot be decided
    # mechanically: "World Bank" and "Bankspeak" are proper nouns that must stay
    # capitalised. So report the candidates and let a human rule on them.
    words = re.findall(r"\b[A-Z][a-z]+\b", title)
    first = title.split()[0].rstrip(":")
    after_colon = re.findall(r":\s+([A-Z][a-z]+)", title)
    proper = {"World", "Bank", "Bankspeak", first, *after_colon}
    caps = [w for w in words if w not in proper]
    if caps:
        out.append(("ACCEPT-STAGE",
                    "title is not in sentence case; capitalised words that are "
                    f"not proper nouns: {', '.join(sorted(set(caps)))}"))


def check_abstract(s: str, out: list) -> None:
    m = re.search(r"^## Abstract\n(.*?)\n---\n", s, re.S | re.M)
    if not m:
        out.append(("BLOCKER", "no abstract section found"))
        return
    body = plain(m.group(1)).strip()
    n = len(body.split())
    out.append(("BLOCKER" if n > ABSTRACT_MAX else "ok",
                f"abstract {n} words (limit {ABSTRACT_MAX}; whitespace split, "
                "so spaced em-dashes count against us)"))

    cites = re.findall(r"\((?:19|20)\d{2}[a-z]?\)|\[\d+\]", body)
    out.append(("BLOCKER" if cites else "ok",
                f"abstract citations: {cites or 'none'}"))

    abbr = sorted(set(re.findall(r"\b[A-Z]{2,}\b", body)))
    if abbr:
        out.append(("NOTE", f"abstract abbreviations (avoid 'if possible'): {abbr}"))


def check_sections(s: str, out: list) -> None:
    heads = [h.strip() for h in re.findall(r"^## +(.*)$", s, re.M)]
    seen, pos = [], -1
    ok = True
    for want in REQUIRED_ORDER:
        for i, h in enumerate(heads):
            if want.lower() in re.sub(r"^\d+\.\s*", "", h).lower():
                if i < pos:
                    ok = False
                pos = i
                seen.append(want)
                break
        else:
            ok = False
            out.append(("BLOCKER", f"required section missing: {want}"))
    out.append(("ok" if ok else "ACCEPT-STAGE",
                f"section order {'follows' if ok else 'departs from'} PLOS order "
                f"({' -> '.join(seen)})"))


def check_references(s: str, out: list) -> None:
    refs = s.split("## References", 1)[1] if "## References" in s else ""
    numbered = bool(re.search(r"^\s*1\.\s+\w", refs, re.M))
    body = s.split("## References", 1)[0]
    bracket = len(re.findall(r"\[\d+(?:[,–-]\d+)*\]", body))
    authordate = len(re.findall(r"[A-Z][A-Za-zÀ-ÿ'’-]+"
                                r"(?:\s*&\s*[A-Z][A-Za-zÀ-ÿ'’-]+|\s+et al\.)?"
                                r"\s*\((?:19|20)\d{2}[a-z]?\)", body))
    out.append(("ok" if numbered and bracket and not authordate else "ACCEPT-STAGE",
                f"reference style: {'numbered' if numbered else 'author-date'} list, "
                f"{bracket} bracketed and {authordate} author-date in-text "
                "(PLOS uses numbered Vancouver)"))


def check_disclosures(s: str, out: list) -> None:
    # These belong in the submission form, and PLOS says in as many words that
    # they should not be in the manuscript file. A stray one is a revision
    # request, not a rejection, so it is not a blocker.
    for label, pat in [("financial disclosure", r"(?i)^#+.*funding|financial disclosure"),
                       ("competing interests", r"(?i)^#+.*competing interest")]:
        if re.search(pat, s, re.M):
            out.append(("NOTE", f"{label} appears in the manuscript file; PLOS "
                                "wants it in the submission form only"))


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    s = load(Path(argv[0]) if argv else None)
    out: list[tuple[str, str]] = []
    check_title(s, out)
    check_abstract(s, out)
    check_sections(s, out)
    check_references(s, out)
    check_disclosures(s, out)

    width = max(len(sev) for sev, _ in out)
    for sev, msg in out:
        print(f"  {sev.upper():{width}s}  {msg}")
    blockers = [m for sev, m in out if sev == "BLOCKER"]
    later = [m for sev, m in out if sev == "ACCEPT-STAGE"]
    print(f"\n[plos] {len(blockers)} blocker(s) at initial submission, "
          f"{len(later)} item(s) deferred to provisional accept")
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
