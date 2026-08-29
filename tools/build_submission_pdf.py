#!/usr/bin/env python3
"""Build the single PDF that PLOS ONE's format-free initial submission wants.

  "PLOS ONE waives all formatting requirements until your manuscript has
   received a provisional Editorial Accept decision."  -- getting-started page

so what is uploaded is one PDF containing the text and the figures. This builds
it from the Markdown source rather than from a hand-maintained second copy,
because a manuscript that exists twice drifts, and this project has already paid
for one drift.

Three things it does that a plain `pandoc paper.md -o paper.pdf` does not:

  * embeds the figures. The manuscript's §Figures is a list of captions naming
    image stems, which is right for a repository and useless in a submission;
    each entry becomes the actual figure with its caption beneath.
  * adds the title page PLOS expects, with the affiliation and ORCID left as
    visible placeholders. A made-up affiliation on a submitted manuscript is
    worse than an obvious gap.
  * uses XeLaTeX and a font with Greek and combining marks, because the paper
    prints beta, tau, theta-hat, superscript nine and subscript zero, and
    pdflatex silently drops what it cannot set.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"
FIGDIR = ROOT / "docs" / "figures"
BUILD = ROOT / "build" / "submission"
OUT = BUILD / "PLOS_ONE_submission.pdf"

AUTHOR = "Ali Çetinkaya"
AFFIL = "[AFFILIATION — to be completed before submission]"
ORCID = "[ORCID — to be completed before submission]"

# Fonts are tried in order; the first one fontspec can load wins. Times New Roman
# and Helvetica ship with macOS; the two Latin Modern entries are the TeX
# fallbacks so the build still runs on a machine without them.
FONT_CANDIDATES = ["Times New Roman", "Latin Modern Roman", "TeX Gyre Termes"]
# The model equation is written in a code span, so it is set in the MONO font,
# and the default (Latin Modern Mono) has no Greek. That silently deleted the
# three coefficients from the one line that defines the estimand:
#   "log E[count_it] = year FE + γ·WB + τ·(WB × centred year) + β·(WB × post)"
# became "= year FE + ·WB + ·(WB × centred year) + ·(WB × post)".
MONO_CANDIDATES = ["Menlo", "DejaVu Sans Mono", "Courier New", "Latin Modern Mono"]

SUPER = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
         "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9"}
SUB = {"₀": "0", "₁": "1", "₂": "2", "₃": "3", "₄": "4",
       "₅": "5", "₆": "6", "₇": "7", "₈": "8", "₉": "9"}


def scripts_to_math(md: str) -> str:
    """Rewrite Unicode super/subscripts as LaTeX math.

    Times New Roman on macOS has no glyph for U+2079, so "2⁹ = 512" set with it
    silently becomes "2 = 512" — a claim about the bootstrap's support turning
    into an arithmetic falsehood, with no error anywhere in the build. The first
    version of this script shipped that PDF. LaTeX math needs no font coverage,
    so the substitution removes the dependency instead of hoping for it.
    """
    md = re.sub("[" + "".join(SUPER) + "]+",
                lambda m: "$^{" + "".join(SUPER[c] for c in m.group(0)) + "}$", md)
    md = re.sub("[" + "".join(SUB) + "]+",
                lambda m: "$_{" + "".join(SUB[c] for c in m.group(0)) + "}$", md)
    return md


def embed_figures(md: str) -> str:
    """Turn the caption list into real figures.

    Each entry reads

        - **Figure 1** — `fig1_composition`. <caption text, possibly wrapped>

    and the list runs to the horizontal rule that closes the section.
    """
    m = re.search(r"^## Figures\n(.*?)\n---\n", md, re.S | re.M)
    if not m:
        raise SystemExit("[pdf] refusing: no '## Figures' section to embed")

    block = m.group(1)
    entries = re.findall(
        r"- \*\*Figure (\d+)\*\* — `([a-z0-9_]+)`\.\s*(.*?)(?=\n- \*\*Figure |\Z)",
        block, re.S)
    if not entries:
        raise SystemExit("[pdf] refusing: '## Figures' matched no caption entries")

    out = ["## Figures", ""]
    for num, stem, caption in entries:
        src = FIGDIR / f"{stem}.pdf"
        if not src.exists():
            src = FIGDIR / f"{stem}.png"
        if not src.exists():
            raise SystemExit(f"[pdf] refusing: no image for {stem} in {FIGDIR}")
        caption = " ".join(caption.split())
        out += [f"![]({src}){{width=95%}}", "",
                f"**Fig {num}.** {caption}", "", r"\newpage", ""]
    body = "\n".join(out).rstrip() + "\n"
    return md[:m.start()] + body + "\n---\n" + md[m.end():]


def title_page(md: str) -> tuple[str, str]:
    """Split the H1 off and return (title, rest)."""
    first, rest = md.split("\n", 1)
    return first.lstrip("# ").strip(), rest


def probe_font(name: str, setter: str, sample: str) -> bool:
    """True if xelatex can load the font AND set every sample character in it.

    Loading is not coverage: xelatex loads Latin Modern Mono happily and then
    writes notdefs for Greek. So the probe renders the sample and reads the
    result back, which is the only check that answers the question asked.
    """
    probe = BUILD / "fontprobe.tex"
    # The sample has to be typeset IN the font under test. Setting monofont and
    # then writing the sample as body text measures the main font instead, which
    # is what the first version did: every mono candidate "failed" because the
    # probe never used one.
    body = f"\\texttt{{{sample}}}" if setter == "setmonofont" else sample
    probe.write_text("\\documentclass{article}\\usepackage{fontspec}"
                     f"\\{setter}{{{name}}}\\pagestyle{{empty}}"
                     f"\\begin{{document}}\\noindent {body}\\end{{document}}",
                     encoding="utf-8")
    (BUILD / "fontprobe.pdf").unlink(missing_ok=True)   # never read a stale probe
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                        probe.name], cwd=BUILD, capture_output=True)
    if r.returncode != 0:
        return False
    try:
        import fitz
    except ImportError:
        return True
    out = (BUILD / "fontprobe.pdf")
    if not out.exists():
        return False
    text = "".join(pg.get_text() for pg in fitz.open(out))
    return "\ufffd" not in text and "\uffff" not in text


GREEK_SAMPLE = "β τ γ θ α σ δ π ≥ × − §"


def pick_fonts() -> tuple[str, str]:
    main = next((f for f in FONT_CANDIDATES
                 if probe_font(f, "setmainfont", GREEK_SAMPLE + " θ̂")), None)
    mono = next((f for f in MONO_CANDIDATES
                 if probe_font(f, "setmonofont", GREEK_SAMPLE)), None)
    if not main or not mono:
        raise SystemExit(f"[pdf] refusing: no usable font "
                         f"(main={main}, mono={mono}). The sample includes Greek "
                         "because the manuscript's estimand is written in it.")
    return main, mono


def main() -> int:
    if not shutil.which("xelatex") or not shutil.which("pandoc"):
        raise SystemExit("[pdf] needs pandoc and xelatex on PATH")
    BUILD.mkdir(parents=True, exist_ok=True)

    md = PAPER.read_text(encoding="utf-8")
    title, rest = title_page(embed_figures(md))
    font, mono = pick_fonts()
    print(f"[pdf] fonts: text {font}, code {mono}")

    header = (
        "---\n"
        f'title: "{title}"\n'
        f'author: "{AUTHOR}"\n'
        f'date: "{AFFIL}\\\\newline {ORCID}"\n'
        "geometry: margin=2.4cm\n"
        f'mainfont: "{font}"\n'
        f'monofont: "{mono}"\n'
        "monofontoptions: Scale=0.85\n"
        "fontsize: 11pt\n"
        "linestretch: 1.15\n"
        "colorlinks: true\n"
        "urlcolor: black\n"
        "linkcolor: black\n"
        "header-includes:\n"
        "  - \\usepackage{longtable}\n"
        "  - \\usepackage{booktabs}\n"
        "  - \\AtBeginEnvironment{longtable}{\\footnotesize}\n"
        "  - \\usepackage{etoolbox}\n"
        "---\n\n"
    )
    # Pandoc reads ANY line of three dashes as the start of a YAML metadata
    # block, not just the one at the top, and this manuscript separates sections
    # with them. Left alone, pandoc tries to parse §2 as YAML and dies at line
    # 182 with a message that points at the header. `* * *` is an unambiguous
    # horizontal rule and renders identically.
    rest = re.sub(r"^---$", "* * *", rest, flags=re.M)
    rest = scripts_to_math(rest)
    src = BUILD / "submission.md"
    src.write_text(header + rest, encoding="utf-8")

    cmd = ["pandoc", str(src), "-o", str(OUT), "--pdf-engine=xelatex",
           "--from", "markdown+pipe_tables+tex_math_dollars",
           "--toc", "--toc-depth=2", "-V", "toc-title=Contents"]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=BUILD)
    if r.returncode != 0:
        sys.stderr.write(r.stdout + r.stderr)
        raise SystemExit("[pdf] pandoc failed")

    return verify(md)


def verify(source_md: str) -> int:
    """Read the built PDF back and refuse to call it done if a glyph is missing.

    XeLaTeX does not fail on a character the font cannot set; it writes a notdef,
    which extracts as U+FFFF and prints as nothing. So the only way to know the
    PDF says what the manuscript says is to read the PDF.
    """
    try:
        import fitz
    except ImportError:
        print("[pdf] WARNING: PyMuPDF not available, glyph check skipped")
        return 0

    doc = fitz.open(OUT)
    text = "".join(page.get_text() for page in doc)
    bad = text.count("\ufffd") + text.count("\uffff")
    if bad:
        ctx = [text[max(0, i - 30):i + 30].replace("\n", " ")
               for i, c in enumerate(text) if c in "\ufffd\uffff"][:5]
        sys.stderr.write("[pdf] REFUSING: %d unrenderable glyph(s):\n" % bad)
        for c in ctx:
            sys.stderr.write(f"    ...{c}...\n")
        return 1

    # A spot check that the numbers actually survived typesetting, not just that
    # nothing errored. These are the load-bearing figures of the three results.
    must = ["39.96", "22.97", "0.0142", "512", "0.16", "Fig 1.", "Fig 4."]
    missing = [m for m in must if m not in text]
    if missing:
        sys.stderr.write(f"[pdf] REFUSING: not in the built PDF: {missing}\n")
        return 1

    print(f"[pdf] wrote {OUT.relative_to(ROOT)}  "
          f"({OUT.stat().st_size/1024:.0f} KB, {doc.page_count} pages)")
    print(f"[pdf] glyph check clean; {len(must)} load-bearing strings present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
