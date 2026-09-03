"""No IMF document title may appear in any file the project ships.

The data-permission record treats titles as verbatim IMF content, and the
deposit's own redaction rule drops the title column from the frame. Yet an
audit of the staged deposit found about sixteen real titles, and five real
IMF-published PDF filenames, sitting in test fixtures under tests/ -- files that
both the public code mirror and the evidence deposit copy wholesale. The
mirror's density rule tolerated them (few per file); the deposit's scanner
never looked at .py files.

This test uses the one thing only this machine has: the unpublished frame with
its titles. It skips, not passes, when the frame is absent. It never prints a
title: a failure names the file, the line and a character count.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FRAME = ROOT / "data" / "meta" / "imf_articleiv_frame.csv"
SHIPPED = [ROOT / "tests", ROOT / "tools", ROOT / "src", ROOT / "docs", ROOT / "config"]
MEDIA_STEM = re.compile(r"1[0-9a-z]{3}ea\d{7}|/-/media/files/publications/cr/", re.I)


def _titles() -> list[str]:
    if not FRAME.exists():
        pytest.skip("unpublished frame not present on this machine")
    with FRAME.open(encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh))
    col = next((c for c in rows[0] if c.lower() in ("title", "display_title")), None)
    if col is None:
        pytest.skip("frame carries no title column here")
    # long enough that a verbatim hit cannot be boilerplate alone
    return sorted({r[col].strip() for r in rows if len(r[col].strip()) >= 40})


def _shipped_text_files():
    """Files that actually leave this machine: what the public mirror would
    stage (its DENY and PROSE_OK rules decide) plus what the deposit copies.
    The IMF request lists under docs/IMF_* carry titles by design and are
    denied by the mirror; scanning them would only report the rule working."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bp", ROOT / "tools" / "build_public_repo.py")
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
    for base in SHIPPED:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix not in (".py", ".md", ".yaml", ".yml", ".txt", ".json", ".csv"):
                continue
            if "__pycache__" in p.parts:
                continue
            rel = p.relative_to(ROOT).as_posix()
            if bp.denied(rel) and p.name not in bp.PROSE_OK:
                continue
            yield p


def test_no_frame_title_appears_verbatim_in_shipped_text():
    titles = _titles()
    # whole titles, and the first sixty characters of long ones so a
    # near-verbatim substring is caught; never a bare country-name prefix,
    # which the first version of this test reported as a title
    # A title is caught whole, or by its head up to and including the "Article
    # IV Consultation" boilerplate (entity name plus year plus consultation):
    # that is specific to one document. A bare entity-name prefix is not, and
    # a design document must be free to discuss a mapping rule by naming the
    # entity; the first version of this rule flagged exactly that.
    cores = set()
    for t in titles:
        cores.add(t)
        m = re.search(r"^.{20,}?\b(?:19|20)\d{2}\s+Article\s+IV\s+Consultation", t)
        if m and len(m.group(0)) < len(t):
            cores.add(m.group(0))
    hits = []
    for p in _shipped_text_files():
        text = p.read_text(encoding="utf-8", errors="replace")
        for c in cores:
            i = text.find(c)
            if i >= 0:
                line = text.count("\n", 0, i) + 1
                hits.append(f"{p.relative_to(ROOT)}:{line} ({len(c)} chars)")
                break
    assert not hits, "verbatim IMF titles in shipped files: " + "; ".join(hits)


def test_no_imf_media_filename_appears_in_shipped_text():
    """The /-/media/ link components are IMF-published URL parts; the
    compliance record treats them as such. Report numbers are fine."""
    hits = []
    for p in _shipped_text_files():
        if p.name in ("fetch_imf_cr_pdfs.py",) and p.parent.name == "tools":
            # the fetcher must describe the pattern; it must not name a document
            pass
        for m in MEDIA_STEM.finditer(p.read_text(encoding="utf-8", errors="replace")):
            frag = m.group(0)
            # a schematic pattern with x placeholders is documentation, not a document
            # documentation placeholders (x) and stems built on ISO 3166 user-assigned
            # codes (XAA to XZZ) cannot name a real document; the fixtures use XFD/XRT
            if ("xxx" in frag.lower() or frag.lower().endswith("/cr/")
                    or frag.lower().startswith("1x")):
                continue
            line = p.read_text(encoding="utf-8", errors="replace").count("\n", 0, m.start()) + 1
            hits.append(f"{p.relative_to(ROOT)}:{line}")
            break
    assert not hits, "IMF media filenames in shipped files: " + "; ".join(hits)
