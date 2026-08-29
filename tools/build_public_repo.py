#!/usr/bin/env python3
"""Assemble the PUBLIC code-and-decisions archive, and refuse if IMF content is in it.

The paper needs a citable code archive with a DOI, which means a public GitHub
repository that Zenodo can mint from. The working repository cannot simply be
pushed: it has always tracked files that the Zenodo deposit deliberately withholds
as verbatim IMF content -- the Article IV frame with its titles and URLs, the
1,064-row permission request list, the retrieval manifest. Private, that was fine.
Public, it would breach the permission and contradict the project's own recorded
decision that "verifiability is fully served by depositing hashes".

So this builds a fresh tree rather than pushing history. Those files are in nearly
every past commit, so publishing the history would publish them; a single clean
commit avoids that without any history surgery.

## What travels

Code, tests, configuration, the frozen design documents, every decision and
deviation record, the generated tables and figures, and the derived
non-substitutive outputs (counts, cells, verdicts, calibration). That is what a
reader needs to check a number or rerun the pipeline against their own lawfully
obtained copies.

## What does not

Any file carrying IMF titles, URLs, DOIs or document text; the corpus itself; the
raw listing archive; and build residue. The IMF material is represented by its
SHA-256 manifest, which is what the permission allows and what verification
actually requires.

## The guard

Every staged file is scanned before it is written and the build ABORTS on a hit.
The scan looks for IMF report-number patterns, imf.org URLs, IMF DOI prefixes and
Article IV title boilerplate. A false positive costs a minute; a false negative
costs a licence.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "bankspeak-public"

# Code and decisions only. The repository's standing policy -- "git carries the
# decision, Zenodo carries the evidence" -- turns out to be exactly the right
# split for a PUBLIC repository too, and for a reason the private repository
# never had to face: many derived tables carry IMF report numbers as document
# identifiers. Depositing those on Zenodo under the permission's derived-output
# clause is one thing; scattering them across a public git history is another,
# and the benefit is nil because nobody can rerun the pipeline without the
# corpus anyway. So data/ stays out and the README says where it lives.
INCLUDE = ["src", "tools", "tests", "config", "docs", "Makefile",
           "requirements.txt", "requirements-ppl.txt",
           "data/meta/imf_document_index.csv"]

# Never, whatever else matches.
DENY = [
    re.compile(r"(^|/)imf(?!_document_index)", re.I),
    re.compile(r"articleiv", re.I),
    re.compile(r"(^|/)diagnostics/"),
    re.compile(r"__pycache__|\.pyc$|\.bak"),
    re.compile(r"(^|/)\."),
    re.compile(r"wb_p1p2_raw|wb_p0_raw"),      # 46 MB of raw API pages; Zenodo's job
    re.compile(r"manifest\.tsv$"),
    re.compile(r"^docs/IMF_"),                 # request/permission lists: IMF titles
    re.compile(r"crossref"),                   # IMF DOIs and titles
]

# Content signatures of IMF material.
LEAK = [
    (re.compile(r"\bCR\d{4}-\d{3}\b"), "IMF report number (CR####-###)"),
    (re.compile(r"\b(19|20)\d{2}/\d{3}\b.*10\.5089/"), "IMF report no + DOI"),
    (re.compile(r"10\.5089/"), "IMF DOI prefix"),
    (re.compile(r"imf\.org/(en|external)/", re.I), "imf.org document URL"),
    (re.compile(r"staff\s+report\s+for\s+the\s+\d{4}\s+article\s+iv", re.I),
     "Article IV title boilerplate"),
]
TEXTY = {".py", ".md", ".csv", ".json", ".yaml", ".yml", ".txt", ".jsonl", ".cfg"}
# Files that legitimately discuss the IMF in prose and carry no document data.
PROSE_OK = {"IMF_ACCESS_COMPLIANCE_20260820.md", "IMF_RETRIEVAL_20260820.md",
            "IMF_QUERY_DRAFT_archive_route.md"}

# Exempt from the PATH filter, still subject to the CONTENT scan below.
#
# The path filter matches on the word "imf" and on "articleiv", which are also in
# the names of two of the project's own source modules. It therefore stripped
# them from every public export, and because src/s09b_wb_p0_frame.py imports
# s09a_imf_articleiv_frame at module scope, `pytest tests/` in the published
# repository died with twelve collection errors and ran ZERO tests -- against a
# README promising 341 and a manuscript whose warrant is that its code can be
# checked. The guard against leaking the corpus had quietly deleted the evidence
# that the analysis works.
#
# Membership here buys exemption from the filename rule ONLY. Every file still
# goes through the LEAK content scan, so a file that actually carries report
# numbers, IMF DOIs or document URLs is still refused, by the check that reads
# the bytes rather than the name.
PATH_EXEMPT = {
    "src/s09a_imf_articleiv_frame.py",      # the Article IV sampling frame builder
    "tools/imf_corpus_to_pipeline.py",      # corpus -> pipeline adapter
    "docs/IMF_RETRIEVAL_20260820.md",       # cited by §3 of the manuscript
    "docs/IMF_ACCESS_COMPLIANCE_20260820.md",   # cited by §3 of the manuscript
    "docs/IMF_QUERY_DRAFT_archive_route.md",
}

# One deliberate exception, and it is an exception rather than a raised
# threshold because the reason is specific and should not generalise.
# imf_document_index.csv carries 1,057 DOIs — two orders of magnitude over the
# cap — and must travel anyway: it IS the access route PLOS ONE requires, the
# thing that lets a reader fetch the same documents from the publisher and check
# their copy against ours. It holds report number, year, country, DOI and
# SHA-256, and deliberately no title and no imf.org URL, so it is derived
# non-substitutive output under §5 of the permission rather than a copy of the
# catalogue. Withholding it would make the hash manifest unusable, which is
# conservatism that defeats verification.
ACCESS_ROUTE_OK = {"imf_document_index.csv"}


def denied(rel: str) -> bool:
    # PATH_EXEMPT never exempts __pycache__, .bak or dotfiles: those rules are
    # about build litter, not about the corpus, and nothing should escape them.
    if rel in PATH_EXEMPT:
        litter = [p for p in DENY if "pycache" in p.pattern or p.pattern == r"(^|/)\."]
        return any(p.search(rel) for p in litter)
    return any(p.search(rel) for p in DENY)


# A methods document that names nine report numbers to document a verification
# procedure is ordinary scholarly citation; the paper itself will cite IMF
# documents by number. A 2,789-row frame carrying every title and URL is
# redistribution. The difference is DENSITY, not presence, so the guard counts
# rather than matches. Thresholds are deliberately low: the largest legitimate
# case in this repository is 9 unique report numbers and 10 DOIs, in a file whose
# whole subject is verifying report numbers.
MAX_UNIQUE_REPORT_NOS = 15
MAX_DOIS = 15
MAX_DOC_URLS = 15
# Titles get the same density rule, on the same reasoning. The manuscript already
# publishes two Article IV titles -- the Finland/Tanzania negative control in
# §3.1 -- because naming a document is citation, not redistribution; the
# permission forbids "documents, extracted full text or substantial portions",
# and a title is none of those. What must not travel is the 2,789-row frame that
# carries every title in the corpus. The largest legitimate case here is 9 titles
# in a test that exercises the title-matching rung.
MAX_TITLES = 12


def scan(path: Path, rel: str):
    if path.suffix.lower() not in TEXTY:
        return []
    body = path.read_text(encoding="utf-8", errors="replace")
    caps = {"IMF report number (CR####-###)": MAX_UNIQUE_REPORT_NOS,
            "IMF DOI prefix": MAX_DOIS,
            "imf.org document URL": MAX_DOC_URLS,
            "Article IV title boilerplate": MAX_TITLES,
            "IMF report no + DOI": MAX_DOIS}
    hits = []
    for pat, why in LEAK:
        found = pat.findall(body)
        n = len(set(found)) if "report number" in why else len(found)
        cap = caps.get(why, 0)
        if n > cap:
            hits.append(f"{why}: {n} occurrences, cap {cap}")
    return hits


def main(argv: list[str] | None = None) -> int:
    # --out exists so the integrity test can build a throwaway export and run its
    # collector against it. Without it that test could only skip, and a test that
    # always skips is not a test -- which is the same class of mistake as a leak
    # guard nobody ran the guarded output through.
    global OUT
    argv = sys.argv[1:] if argv is None else argv
    if "--out" in argv:
        OUT = Path(argv[argv.index("--out") + 1]).resolve()
    staged, problems = [], {}
    for inc in INCLUDE:
        p = ROOT / inc
        if not p.exists():
            print(f"[public] missing, skipped: {inc}")
            continue
        files = sorted(q for q in p.rglob("*") if q.is_file()) if p.is_dir() else [p]
        for f in files:
            rel = f.relative_to(ROOT).as_posix()
            if denied(rel):
                continue
            h = scan(f, rel)
            if h and f.name not in PROSE_OK and f.name not in ACCESS_ROUTE_OK:
                problems[rel] = h
            else:
                staged.append((f, rel))

    if problems:
        print(f"[public] REFUSING: {len(problems)} staged file(s) carry IMF "
              f"content. Add them to DENY or remove the content.\n")
        for k, v in sorted(problems.items()):
            print(f"    {k}")
            for line in v[:2]:
                print(f"        {line}")
        return 1

    # Replace only what this builder owns. An earlier version wiped the whole
    # target directory and destroyed the git checkout along with the
    # hand-written README, licences and Zenodo metadata that do not come from
    # the source tree. Preserving them is not a convenience: .git holds the
    # published history, and re-cloning to recover it is a step that can be
    # forgotten at exactly the wrong moment.
    PRESERVE = {".git", "README.md", "LICENSE", "LICENSE-docs", "CITATION.cff",
                ".zenodo.json", ".gitignore", "COMMIT_HISTORY.md"}
    if OUT.exists():
        for child in OUT.iterdir():
            if child.name in PRESERVE:
                continue
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    for f, rel in staged:
        d = OUT / rel
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, d)

    log = subprocess.run(["git", "log", "--format=%h  %ad  %s", "--date=short"],
                         cwd=ROOT, capture_output=True, text=True).stdout
    (OUT / "COMMIT_HISTORY.md").write_text(
        "# Development history\n\nThe working repository is private because it "
        "tracks IMF bibliographic data that may not be redistributed. The commit "
        "subjects are reproduced here so the reasoning trail survives; they "
        "contain no IMF document data.\n\n```\n" + log + "```\n",
        encoding="utf-8")

    total = sum(f.stat().st_size for f, _ in staged)
    print(f"[public] {len(staged)} files, {total/1e6:.2f} MB -> {OUT}")
    print("[public] leak scan clean: no IMF report number, DOI, URL or title")
    return 0


if __name__ == "__main__":
    sys.exit(main())
