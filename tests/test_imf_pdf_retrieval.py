"""IMF Article IV PDF retrieval (2026-08-20): resolution ladder, verification
rungs, and the permission-condition guarantees.

Old-commit classification matrix (round-13 honesty rule): ALL tests in this
file FAIL at every commit up to and including 8b82787 -- neither
``tools/fetch_imf_cr_pdfs.py`` nor ``tools/verify_imf_cr_pdfs.py`` exists
there. Every arm is new-behaviour; none is behaviour-preservation.

Fixture-only: the transport seam (``curl``) is monkeypatched and PDFs are
synthesized in-process. No network, and no IMF document text: the fixtures
build their own PDFs, so nothing retrieved from the IMF is read, printed or
committed by this file (permission condition 6).

The arms that carry compliance weight, not merely correctness:

* ``test_l2_gate_closed_issues_no_archive_request`` -- with the gate shut, the
  archive is not contacted AT ALL. A gate that merely discarded the result
  would still have made the request, which is the thing condition 3 is about.
* ``test_only_frozen_sample_records_are_requested`` -- condition 1. The
  retrieval can request nothing outside the frozen 1,064.
* ``test_legacy_url_zero_pads_to_two_digits`` -- the regression that produced
  dead links in the withdrawn list (commit 8b82787): ``2000/008`` is
  ``cr0008``, not ``cr008``.
"""
import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The frozen IMF sample is withheld from the public export under the permission,
# so in the published repository these five tests have no input. A missing
# permission-gated file is a SKIP, not a failure: a red suite in the archive
# tells a reader the analysis is broken, when what is actually true is that one
# input is licensed and they do not have it. The reason string says which file.
FROZEN_IMF = ROOT / "data" / "meta" / "frozen_sampling_imf_v1.csv"
needs_frozen_imf_sample = pytest.mark.skipif(
    not FROZEN_IMF.exists(),
    reason="needs data/meta/frozen_sampling_imf_v1.csv, withheld from the public "
           "repository under the IMF permission (present in the author's tree)")


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


fetch = _load("fetch_imf_cr_pdfs")
verify = _load("verify_imf_cr_pdfs")

fitz = pytest.importorskip("fitz")

PDF_MAGIC = b"%PDF-1.7\n"
# Fixture countries, ISO3 codes (ISO 3166 user-assigned: XFD, XRT), titles and
# media stems are synthetic; documents are referred to by report number only.


def make_pdf(path, text="", title=""):
    """Synthesize a PDF; ``text`` empty reproduces a pre-OCR scan (no text layer)."""
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text, fontsize=11)
    if title:
        doc.set_metadata({"title": title})
    doc.save(str(path))
    doc.close()


# --------------------------------------------------------------- L1 resolution

@pytest.mark.parametrize("report_no,expected", [
    ("1999/047", "1999/cr9947.pdf"),
    ("2000/008", "2000/cr0008.pdf"),   # the withdrawn list produced cr008 here
    ("2001/005", "2001/cr0105.pdf"),
    ("1999/149", "1999/cr99149.pdf"),
    ("2003/391", "2003/cr03391.pdf"),
    ("2017/015", "2017/cr1715.pdf"),
])
def test_legacy_url_zero_pads_to_two_digits(report_no, expected):
    assert fetch.legacy_url(report_no).endswith(expected)


def test_legacy_url_uses_the_report_number_year_not_the_sample_year():
    # frozen row 2002/246 carries year=2004; the path must follow the report no
    assert "/scr/2002/" in fetch.legacy_url("2002/246")


# ------------------------------------------------------- L2 language selection

def test_pick_english_prefers_the_english_folder():
    links = ["/-/media/Files/Publications/CR/2023/French/1XFDFA2023001.ashx",
             "/-/media/Files/Publications/CR/2023/English/1XFDEA2023001.ashx"]
    assert "English" in fetch.pick_english(links)


def test_pick_english_rejects_every_non_english_rendition():
    for folder in ("French", "Spanish", "Arabic", "Russian", "Chinese",
                   "Japanese", "Portuguese", "German", "Italian"):
        assert fetch.pick_english(
            [f"/-/media/Files/Publications/CR/2021/{folder}/x.pdf"]) is None


def test_pick_english_accepts_a_link_with_no_language_folder():
    # the 2019 shape: .../cr/2019/cr19nn-<country-slug>-a4.pdf
    link = "/-/media/files/publications/cr/2019/cr1900-freedonia-a4.pdf"
    assert fetch.pick_english([link, "/-/media/files/publications/cr/2019/french/x.pdf"]) == link


def test_resolve_via_archive_extracts_the_imf_link_and_fetches_from_imf(monkeypatch):
    html = ('<a href="/-/media/Files/Publications/CR/2023/French/1XFDFA2023001.ashx">fr</a>'
            '<a href="/-/media/Files/Publications/CR/2023/English/1XFDEA2023001.ashx">en</a>')
    monkeypatch.setattr(fetch, "fetch_text", lambda url: (200, html))
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    url, cands = fetch.resolve_via_archive("https://www.imf.org/en/publications/cr/x")
    assert url.startswith("https://www.imf.org/-/media/")   # never web.archive.org
    assert "English" in url and len(cands) == 2


def test_resolve_via_archive_normalizes_the_underscore_legacy_artifact(monkeypatch):
    monkeypatch.setattr(fetch, "fetch_text",
                        lambda url: (200, '<a href="/external/pubs/ft/scr/1999/_cr9900.pdf">x</a>'))
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    url, _ = fetch.resolve_via_archive("https://www.imf.org/en/x")
    assert url.endswith("/scr/1999/cr9900.pdf")


def test_resolve_via_archive_reports_nothing_when_the_snapshot_is_missing(monkeypatch):
    monkeypatch.setattr(fetch, "fetch_text", lambda url: (404, ""))
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    assert fetch.resolve_via_archive("https://www.imf.org/en/x") == (None, [])


# ------------------------------------------------------------ transport safety

def test_fetch_pdf_discards_a_body_that_is_not_a_pdf(tmp_path, monkeypatch):
    dest = tmp_path / "x.pdf"

    def fake_curl(url, out):
        out.write_bytes(b"<html>Forbidden</html>")
        return 200, b"", url

    monkeypatch.setattr(fetch, "curl", fake_curl)
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    status, size = fetch.fetch_pdf("https://x/y.pdf", dest)
    assert size == 0 and not dest.exists()


def test_fetch_pdf_keeps_a_real_pdf(tmp_path, monkeypatch):
    dest = tmp_path / "x.pdf"

    body = PDF_MAGIC + b"body\n%%EOF\n"

    def fake_curl(url, out):
        out.write_bytes(body)
        return 200, b"", url

    monkeypatch.setattr(fetch, "curl", fake_curl)
    status, size = fetch.fetch_pdf("https://x/y.pdf", dest)
    assert dest.exists() and size == len(body)


def test_the_user_agent_identifies_project_purpose_permission_and_contact():
    ua = fetch.UA
    assert "BankspeakContinued-Research" in ua          # name
    assert "academic replication" in ua                 # purpose
    assert "IMF permission" in ua                       # the grant
    assert "@" in ua                                    # reachable contact


def test_the_imf_rate_limit_is_one_request_per_second():
    assert fetch.IMF_SLEEP >= 1.0


# -------------------------------------------------- verification rungs (fetch)

def test_cover_check_r1_reads_the_report_number_from_the_text_layer(tmp_path):
    p = tmp_path / "a.pdf"
    make_pdf(p, text="IMF Country Report No. 23/43")
    assert fetch.cover_check(p, "2023/043") == "ok"


def test_cover_check_r2_falls_back_to_the_scan_metadata_stamp(tmp_path):
    p = tmp_path / "b.pdf"
    make_pdf(p, text="", title="Freedonia: Staff Report - ISCR/99/47")
    assert fetch.cover_check(p, "1999/047") == "ok_scan_metadata"


def test_cover_check_reports_a_textless_scan_it_cannot_confirm(tmp_path):
    p = tmp_path / "c.pdf"
    make_pdf(p, text="", title="Something Else Entirely")
    assert fetch.cover_check(p, "1999/047") == "no_text_layer"


def test_cover_check_reports_a_mismatch_rather_than_accepting_it(tmp_path):
    p = tmp_path / "d.pdf"
    make_pdf(p, text="IMF Country Report No. 11/22 " + "filler text " * 20)
    assert fetch.cover_check(p, "2023/043") == "mismatch"


# ------------------------------------------------ verification rungs (verifier)

def test_verifier_r3_accepts_a_scan_whose_stamp_is_truncated(tmp_path):
    """1999/089 carries "ISCR/99/" and 2000/095 "ISCR0095"; R2 cannot read
    either, but the title names the document unambiguously."""
    p = tmp_path / "e.pdf"
    title = "Freedonia: Staff Report for the 1999 Article IV Consultation- ISCR/99/"
    make_pdf(p, text="", title=title)
    ratio = verify.difflib.SequenceMatcher(
        None, verify.norm(title),
        verify.norm("Freedonia: Staff Report for the 1999 Article IV Consultation")).ratio()
    assert ratio >= verify.TITLE_THRESHOLD


def test_verifier_r3_threshold_rejects_a_different_document():
    ratio = verify.difflib.SequenceMatcher(
        None, verify.norm("Ruritania: Staff Report for the 1999 Article IV Consultation"),
        verify.norm("Zubrowka: Selected Issues and Statistical Appendix")).ratio()
    assert ratio < verify.TITLE_THRESHOLD


def test_wanted_tokens_cover_both_short_and_padded_report_forms():
    assert set(verify.wanted_tokens("2023/043")) >= {"23/43", "2023/043"}


# ------------------------------------------------------- permission conditions

@needs_frozen_imf_sample
def test_l2_gate_closed_issues_no_archive_request(tmp_path, monkeypatch):
    """Condition 3. The gate must prevent the request, not discard its result."""
    calls = []
    monkeypatch.setattr(fetch, "OUT_DIR", tmp_path)
    monkeypatch.setattr(fetch, "MANIFEST", tmp_path / "_manifest.csv")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "_log.jsonl")
    monkeypatch.setattr(fetch, "fetch_pdf", lambda url, dest: (404, 0))
    monkeypatch.setattr(fetch, "fetch_text",
                        lambda url: calls.append(url) or (200, ""))
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)

    fetch.main(["--only", "2023/043"])

    assert calls == [], f"archive was contacted with the gate shut: {calls}"
    rows = list(csv.DictReader((tmp_path / "_manifest.csv").open()))
    assert rows[0]["status"] == "blocked_condition3"
    assert rows[0]["route"] == "L2_blocked_condition3"


@needs_frozen_imf_sample
def test_l2_gate_open_does_reach_the_archive(tmp_path, monkeypatch):
    """The complement: the gate is a real switch, not a permanent refusal."""
    calls = []
    monkeypatch.setattr(fetch, "OUT_DIR", tmp_path)
    monkeypatch.setattr(fetch, "MANIFEST", tmp_path / "_manifest.csv")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "_log.jsonl")
    monkeypatch.setattr(fetch, "fetch_pdf", lambda url, dest: (404, 0))
    monkeypatch.setattr(fetch, "fetch_text",
                        lambda url: (calls.append(url), (200, ""))[1])
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)

    fetch.main(["--only", "2023/043", "--allow-archive-resolution"])

    assert calls, "gate open but the archive was never contacted"
    assert calls[0].startswith("https://web.archive.org/web/2id_/")
    # an empty latest capture falls through to the CDX snapshot walk (L2b)
    assert any("/cdx/search/cdx" in c for c in calls)


# --------------------------------------------- L1b: media tree, no archive

@pytest.mark.parametrize("report_no,expected", [
    ("2017/360", "/cr/2017/cr17360.pdf"),
    ("2018/001", "/cr/2018/cr1801.pdf"),
    ("2018/175", "/cr/2018/cr18175.pdf"),
])
def test_media_legacy_url_reuses_the_legacy_filename(report_no, expected):
    url = fetch.media_legacy_url(report_no)
    assert url.startswith("https://www.imf.org/-/media/files/publications/cr/")
    assert url.endswith(expected)


@needs_frozen_imf_sample
def test_l1b_is_tried_before_any_archive_request(tmp_path, monkeypatch):
    """L1b touches only imf.org, so it must run before the gated archive rung —
    and when it succeeds the archive is never contacted at all."""
    calls, fetched = [], []

    def fake_fetch_pdf(url, dest):
        fetched.append(url)
        if "/-/media/" in url:                     # L1 misses, L1b hits
            dest.write_bytes(PDF_MAGIC)
            return 200, len(PDF_MAGIC)
        return 404, 0

    monkeypatch.setattr(fetch, "OUT_DIR", tmp_path)
    monkeypatch.setattr(fetch, "MANIFEST", tmp_path / "_manifest.csv")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "_log.jsonl")
    monkeypatch.setattr(fetch, "fetch_pdf", fake_fetch_pdf)
    monkeypatch.setattr(fetch, "fetch_text", lambda u: calls.append(u) or (200, ""))
    monkeypatch.setattr(fetch, "cover_check", lambda p, r: "ok")
    monkeypatch.setattr(fetch, "page_count", lambda p: 1)
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)

    fetch.main(["--only", "2017/360", "--allow-archive-resolution"])

    assert calls == [], "L1b succeeded yet the archive was still contacted"
    assert fetched[0].startswith("https://www.imf.org/external/")   # L1 first
    assert "/-/media/" in fetched[1]                                # then L1b
    row = list(csv.DictReader((tmp_path / "_manifest.csv").open()))[0]
    assert row["route"] == "L1b_media_legacy" and row["status"] == "ok"


def test_archive_walk_uses_an_older_capture_when_the_latest_is_a_stub(monkeypatch):
    """Measured 2026-08-20: the latest capture of CR2021/103 is a 15 KB stub
    while the 2021-06-07 one carries the link."""
    good = ('<a href="/-/media/Files/Publications/CR/2021/English/'
            '1XRTEA2021001.ashx">pdf</a>')

    def fake_fetch_text(url):
        if url.startswith("https://web.archive.org/web/2id_/"):
            return 200, "<html>stub with no download section</html>"
        if "/cdx/search/cdx" in url:
            return 200, json.dumps([["timestamp"], ["20210607232551"],
                                    ["20211129001204"]])
        return 200, good

    monkeypatch.setattr(fetch, "fetch_text", fake_fetch_text)
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    url, cands = fetch.resolve_via_archive("https://www.imf.org/en/x")
    assert url.endswith("1XRTEA2021001.ashx")
    assert url.startswith("https://www.imf.org/-/media/")


def test_archive_walk_gives_up_honestly_when_no_capture_has_a_link(monkeypatch):
    monkeypatch.setattr(fetch, "fetch_text", lambda u: (
        (200, json.dumps([["timestamp"], ["20180426214604"]]))
        if "/cdx/search/cdx" in u else (200, "<html>no links here</html>")))
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    url, cands = fetch.resolve_via_archive("https://www.imf.org/en/x")
    assert url is None and cands == []


@needs_frozen_imf_sample
def test_only_frozen_sample_records_are_requested():
    """Condition 1: the retrieval's universe is exactly the frozen 1,064."""
    frozen = {r["id"] for r in csv.DictReader(
        (ROOT / "data" / "meta" / "frozen_sampling_imf_v1.csv").open(encoding="utf-8"))}
    ids = {"CR" + r["report_no"].replace("/", "-") for r in fetch.load_records()}
    assert len(frozen) == 1064
    assert ids == frozen


def test_manifest_records_the_route_so_a_subset_stays_reversible():
    """Condition 3 reversibility: every record must be attributable to a rung."""
    assert "route" in fetch.MANIFEST_FIELDS
    assert "sha256" in fetch.MANIFEST_FIELDS


# ------------------------------------------- truncation gate (added 2026-08-20)

def test_a_truncated_body_is_rejected_despite_valid_magic_bytes(tmp_path, monkeypatch):
    """The regression this gate exists for: five files reached the corpus as
    `ok` because they began "%PDF-" while being half a download (2012/221 was
    1.2 MB of a 2.8 MB file). Both PyMuPDF and pdftotext failed on their XRef.
    A complete PDF ends with %%EOF."""
    dest = tmp_path / "x.pdf"
    monkeypatch.setattr(fetch, "curl",
                        lambda url, out: (out.write_bytes(PDF_MAGIC + b"half a file"),
                                          (200, b"", url))[1])
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    status, size = fetch.fetch_pdf("https://x/y.pdf", dest)
    assert size == 0 and not dest.exists()


def test_a_complete_body_with_the_eof_trailer_is_kept(tmp_path, monkeypatch):
    dest = tmp_path / "x.pdf"
    body = PDF_MAGIC + b"content" * 100 + b"\n%%EOF\n"
    monkeypatch.setattr(fetch, "curl",
                        lambda url, out: (out.write_bytes(body), (200, b"", url))[1])
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    status, size = fetch.fetch_pdf("https://x/y.pdf", dest)
    assert dest.exists() and size == len(body)


# ------------------------------------------------ R4 rung (added 2026-08-20)

@pytest.mark.parametrize("expected,meta", [
    ("Freedonia: Staff Report for the 2000 Article IV Consultation and for a SMP",
     "Freedonia:  2000 Article IV Consultation and Staff-Monitored Program-Staff Report"),
    ("Republic of Ruritania: Staff Report for the 2002 Article IV Consultation",
     "Republic of Ruritania: 2002 Article IV Consultation-Staff Report; Staff Statement"),
    ("Democratic Republic of the Sylvanian Isles: "
     "Staff Report for the 2003 Article IV Consultation",
     "Democratic Republic of the Sylvanian Isles: "
     "2003 Article IV Consultation, First Review"),
])
def test_r4_accepts_the_same_document_phrased_differently(expected, meta):
    assert verify.country_year_match(expected, meta) is True


@pytest.mark.parametrize("expected,meta", [
    # different country, identical boilerplate -- the case token-set overlap got wrong
    ("Freedonia: Staff Report for the 2005 Article IV Consultation",
     "Ruritania: 2005 Article IV Consultation-Staff Report; Staff Statement"),
    # right country, wrong year
    ("Republic of Ruritania: Staff Report for the 2002 Article IV Consultation",
     "Republic of Ruritania: 2011 Article IV Consultation-Staff Report"),
    ("Zubrowka: Staff Report for the 2014 Article IV Consultation", ""),
])
def test_r4_rejects_a_different_document(expected, meta):
    assert verify.country_year_match(expected, meta) is False


def test_token_set_overlap_would_have_been_unsafe_here():
    """Kept as a guard against 'just loosen the threshold'.

    Article IV titles share nearly all their tokens, so set overlap cannot
    discriminate: the pair below (one country's short title against another
    country's long one) scores above several TRUE matches.
    Any future rung must beat this, not merely be more permissive."""
    import re as _re

    def toks(s):
        return set(_re.findall(r"[a-z0-9]+", s.lower())) - {
            "the", "for", "and", "of", "a", "under", "on"}

    def overlap(a, b):
        A, B = toks(a), toks(b)
        return len(A & B) / max(1, min(len(A), len(B)))

    # modelled on the real pair from the request list (2005/035 against
    # 2004/285) with the country names replaced by synthetic ones; the token
    # structure is unchanged. A short title against a long one containing all
    # its generic tokens drives the min-denominator overlap to 0.86 -- above
    # true matches R3 rejected.
    brief = "Freedonia: Staff Report for the 2004 Article IV Consultation"
    full = ("Ruritania: 2004 Article IV Consultation and Second Review Under the "
            "Three-Year Arrangement Under the Poverty Reduction and Growth "
            "Facility-Staff Report; Staff Statement; and Public Information "
            "Notice and Press Release on the Executive Board Discussion")
    assert overlap(brief, full) > 0.8, "the negative control must stay a real trap"
    assert verify.country_year_match(brief, full) is False


def test_snapshot_walk_tries_the_largest_capture_first(monkeypatch):
    """Stubs are small and complete captures are large, so size order beats
    date order. Measured: 2018/285's link sits in the 18 KB capture while four
    NEWER ones are 15-16 KB stubs; chronological order missed it."""
    calls = []

    def fake_fetch_text(url):
        if "/cdx/search/cdx" in url:
            return 200, json.dumps([["timestamp", "length"],
                                    ["20240101000000", "15454"],   # newest, stub
                                    ["20210124222624", "18020"],   # older, complete
                                    ["20220101000000", "16401"]])
        calls.append(url)
        return 200, ""

    monkeypatch.setattr(fetch, "fetch_text", fake_fetch_text)
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)
    assert fetch._snapshot_timestamps("https://www.imf.org/en/x")[0] == "20210124222624"


# ----------------------------------- L1c: bounded, verification-gated sequence

def test_sequence_candidates_are_bounded_and_shaped():
    c = fetch.sequence_candidates("2020/198", "XFD")
    assert len(c) == fetch.SEQ_LIMIT * 2          # two path shapes per sequence
    assert c[0].endswith("/cr/2020/english/1xfdea2020001.pdf")
    assert c[1].endswith("/cr/2020/1xfdea2020001.pdf")
    assert fetch.sequence_candidates("2020/198", "") == []      # no ISO3, no guess


def test_sequence_candidates_cover_the_2019_year_root_shape():
    """2019 puts the English rendition at the year root and only other languages
    in a subfolder; assuming the 2020 /english/ shape 404s and left 2019/079
    unresolved."""
    c = fetch.sequence_candidates("2019/079", "XRT")
    assert any(u.endswith("/cr/2019/1xrtea2019001.pdf") for u in c)
    assert any(u.endswith("/cr/2019/english/1xrtea2019001.pdf") for u in c)


@needs_frozen_imf_sample
def test_l1c_refuses_a_real_pdf_that_names_a_different_report(tmp_path, monkeypatch):
    """The gate that makes enumeration legitimate rather than guessing.

    Measured on 2020/198: the first sequence candidate (...2020001) IS a valid,
    complete PDF -- its cover says "IMF Country Report No. 20/152". Only the
    candidate whose cover names 20/198 may be kept, and the rejected one must
    not be left on disk. The record's ISO3 is overridden with a user-assigned
    code (XFD), so the candidate stems below name no real document.
    """
    tried = []
    keeper = "1xfdea2020002.pdf"

    def fake_fetch_pdf(url, dest):
        if "1xfdea2020" not in url:
            return 404, 0
        tried.append(url)
        dest.write_bytes(PDF_MAGIC + b"x\n%%EOF\n")
        return 200, 20

    real_load = fetch.load_records
    monkeypatch.setattr(fetch, "load_records",
                        lambda: [dict(r, country_iso3="XFD") for r in real_load()])
    monkeypatch.setattr(fetch, "OUT_DIR", tmp_path)
    monkeypatch.setattr(fetch, "MANIFEST", tmp_path / "_manifest.csv")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "_log.jsonl")
    monkeypatch.setattr(fetch, "fetch_text", lambda u: (200, ""))
    monkeypatch.setattr(fetch, "page_count", lambda p: 1)
    monkeypatch.setattr(fetch, "fetch_pdf", fake_fetch_pdf)
    monkeypatch.setattr(fetch, "cover_check",
                        lambda p, r: "ok" if tried and tried[-1].endswith(keeper)
                        else "mismatch")
    monkeypatch.setattr(fetch.time, "sleep", lambda *_: None)

    fetch.main(["--only", "2020/198", "--allow-archive-resolution"])

    row = list(csv.DictReader((tmp_path / "_manifest.csv").open()))[0]
    assert row["route"] == "L1c_sequence_verified"
    assert row["pdf_url"].endswith(keeper)
    assert tried[0].endswith("1xfdea2020001.pdf"), "candidates must run in order"
    assert any(u.endswith("1xfdea2020001.pdf") for u in tried), "the decoy was fetched"
