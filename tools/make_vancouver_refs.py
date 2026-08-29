#!/usr/bin/env python3
"""Build the numbered Vancouver reference list from Crossref, not from memory.

PLOS ONE waives formatting until a provisional Editorial Accept, so this is not
needed to submit. It is written now because of how the predecessor paper from
this project failed: not on its argument, but on citations that had drifted from
what the sources actually say. Retyping twenty-five references into a second
format at the moment an editor asks for them — under time pressure, at the end of
a review — is exactly the situation that produced that outcome. So the conversion
is a command, and its input is the publisher's own metadata.

What it does:

  * resolves every DOI in the reference list against Crossref and takes the
    author list, title, journal, volume, issue and pages from the response;
  * orders the list by first appearance in the body — every entry, including
    the ones it cannot resolve, because a number is a position and not a
    property of the metadata;
  * prints the author-date -> number map, so the in-text conversion is a lookup
    rather than a reading;
  * REFUSES to invent an entry it cannot resolve. Two conference papers carry no
    DOI; they keep their place in the numbering and are marked for hand entry,
    with the stable proceedings URL already recorded in the manuscript.

Vancouver lists the first six authors and then "et al.". Crossref returns the
full list, so that rule is applied here rather than inherited from a compressed
entry that had already dropped the names.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
OUT = ROOT / "docs" / "REFERENCES_vancouver.md"
API = "https://api.crossref.org/works/"
MAIL = "kapsul.yonetim@gmail.com"
VANCOUVER_AUTHOR_CAP = 6


def split_paper() -> tuple[str, str]:
    s = PAPER.read_text(encoding="utf-8")
    body, refs = s.split("## References", 1)
    return " ".join(body.split()), refs


def parse_entries(refs: str) -> list[dict]:
    """Same splitting rule as tools/audit_citations.py, and for the same reason:
    entries are ' · '-separated WITHIN a themed paragraph, and splitting on the
    separator alone lets a DOI-less entry swallow the next entry's DOI."""
    out = []
    for para in re.split(r"\n\s*\n", refs):
        para = re.sub(r"\*\*[^*]+\*\*", "", para)
        if para.strip().startswith("*") or len(para.strip()) < 40:
            continue
        for chunk in re.split(r"\s·\s", para):
            chunk = " ".join(chunk.split())
            if len(chunk) < 30:
                continue
            m = re.search(r"10\.\d{4,9}/[^\s,;)]+", chunk)
            a = re.match(r"([A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+(?:\s+[A-ZÇÖÜĞŞİ][A-Za-zÀ-ÿ'-]+)*),\s*[A-Z]\.",
                         chunk)
            y = re.search(r"\((\d{4}[a-z]?)\)", chunk)      # keep the a/b suffix
            out.append({"raw": chunk, "doi": m.group(0).rstrip(".") if m else None,
                        "first_author": a.group(1) if a else None,
                        "year": y.group(1) if y else None})
    return out


def first_mention(body: str, surname: str, year: str) -> int:
    """Position of the earliest in-text citation of this entry, or a large
    sentinel so unresolvable entries sort last rather than silently to the front.

    The surname has to appear within a short window before the year, because
    'Liang et al. 2025a, 2025b' cites two entries from one surname and a plain
    surname search would give both the same position.
    """
    best = 10**9
    for m in re.finditer(re.escape(year) + r"\b", body):
        window = body[max(0, m.start() - 60):m.start()]
        if surname in window:
            best = min(best, m.start())
    return best


def crossref(doi: str) -> dict | None:
    r = requests.get(API + doi, timeout=30,
                     headers={"User-Agent": f"vancouver-refs (mailto:{MAIL})"})
    if r.status_code != 200:
        return None
    return r.json()["message"]


def authors(m: dict) -> str:
    names = []
    for a in m.get("author") or []:
        fam = a.get("family")
        if not fam:
            continue
        given = a.get("given", "")
        initials = "".join(p[0] for p in re.split(r"[\s.\-]+", given) if p)
        names.append(f"{fam} {initials}".strip())
    if not names:
        return "[authors missing from Crossref — enter by hand]"
    if len(names) > VANCOUVER_AUTHOR_CAP:
        # No trailing period here: format_entry adds one, and the first version
        # of this returned "et al." and then got "et al..".
        return ", ".join(names[:VANCOUVER_AUTHOR_CAP]) + ", et al"
    return ", ".join(names)


def year_of(m: dict) -> str:
    for k in ("published-print", "issued", "published-online"):
        v = m.get(k, {}).get("date-parts", [[None]])[0][0]
        if v:
            return str(v)
    return "n.d."


def format_entry(m: dict) -> str:
    """Crossref is the authority on who wrote it and where it appeared. It is NOT
    always the authority on the title: some records carry a truncated one (the
    Moretti and Pestre record is deposited as "Bankspeak" with the subtitle
    dropped), and title capitalisation follows whatever the publisher deposited
    rather than Vancouver's sentence case. Both are flagged for a human below
    rather than repaired here, because repairing a title automatically is how a
    citation drifts."""
    title = (m.get("title") or [""])[0].rstrip(".")
    journal = (m.get("container-title") or [""])[0]
    vol, iss, pg = m.get("volume"), m.get("issue"), m.get("page")
    bits = f"{journal}. {year_of(m)}"
    if vol:
        bits += f";{vol}"
        if iss:
            bits += f"({iss})"
    # Journals that number articles instead of paginating put the identifier in
    # article-number, and dropping it leaves an entry a reader cannot look up:
    # "Science Advances. 2025;11(27)." names no article.
    art = m.get("article-number")
    if pg:
        bits += f":{pg}"
    elif art:
        bits += f":{art}"
    doi = m.get("DOI")
    return f"{authors(m)}. {title}. {bits}. doi:{doi}"


def main() -> int:
    body, refs = split_paper()
    entries = parse_entries(refs)
    for e in entries:
        e["pos"] = (first_mention(body, e["first_author"] or "\0", e["year"] or "\0")
                    if e["first_author"] and e["year"] else 10**9)

    # An entry the body never cites would sort to the sentinel and quietly take
    # the last number. The citation audit says there is no such entry; this
    # asserts it here too, because the number a reader follows depends on it.
    orphan = [e for e in entries if e["pos"] >= 10**9]
    if orphan:
        print("  REFUSING: entries with no in-text citation, so citation order "
              "is undefined: "
              + ", ".join(f"{e['first_author']} {e['year']}" for e in orphan),
              file=sys.stderr)
        return 1

    # Numbering follows first appearance for EVERY entry, including the ones
    # Crossref cannot supply. An earlier version of this function appended the
    # DOI-less conference papers after the resolved ones, which put Juzek & Ward
    # at 24 when the body cites it fourth — a correctly generated list in the
    # wrong order, which is worse than an obviously incomplete one.
    ordered, n_manual = [], 0
    for e in sorted(entries, key=lambda x: (x["pos"], x["raw"])):
        if e["doi"]:
            m = crossref(e["doi"])
            time.sleep(0.3)
        else:
            m = None
        if m is None:
            if e["doi"]:
                print(f"  REFUSING to guess: {e['doi']} did not resolve",
                      file=sys.stderr)
            n_manual += 1
            ordered.append({**e, "vancouver": None})
        else:
            ordered.append({**e, "vancouver": format_entry(m)})
        mark = "hand" if ordered[-1]["vancouver"] is None else "ok  "
        print(f"  {len(ordered):2d}. {mark}  {e['first_author']} {e['year']}")

    lines = ["# Reference list in numbered Vancouver style",
             "",
             "Generated by `tools/make_vancouver_refs.py` from Crossref metadata, "
             "ordered by first appearance in the body. PLOS ONE waives formatting "
             "until provisional acceptance, so this is held ready rather than "
             "applied to the manuscript.",
             "",
             "## Numbered list", ""]
    short_titles = []
    for i, e in enumerate(ordered, 1):
        if e["vancouver"]:
            lines.append(f"{i}. {e['vancouver']}")
            t = e["vancouver"].split(". ")[1] if ". " in e["vancouver"] else ""
            if len(t.split()) <= 2:
                short_titles.append(f"[{i}] {t}")
        else:
            lines.append(f"{i}. **[hand-enter — no DOI to resolve]** {e['raw']}")
    if short_titles:
        lines += ["", "## Check by hand before use", "",
                  "Crossref returned a suspiciously short title for these; "
                  "compare against the manuscript entry, which may be fuller: "
                  + "; ".join(short_titles),
                  "",
                  "Article-title capitalisation comes from the publisher's "
                  "deposit and is not normalised to Vancouver sentence case here."]
    lines += ["", "## In-text conversion map", "",
              "Numbers follow first appearance in the body, which is what "
              "Vancouver ordering means.", "",
              "| author-date in the body | number |", "|---|---|"]
    for i, e in enumerate(ordered, 1):
        lines.append(f"| {e['first_author']} {e['year']} | [{i}] |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[vancouver] {len(ordered) - n_manual} resolved from Crossref, "
          f"{n_manual} need hand entry; wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
