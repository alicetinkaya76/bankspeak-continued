"""Landing the IMF corpus in the pipeline layout, and the OCR pre-pass (A8/A9).

Old-commit classification matrix (round-13 honesty rule): ALL tests in this file
FAIL at every commit up to and including 8b82787 — neither
``tools/imf_corpus_to_pipeline.py`` nor ``tools/ocr_prepass.py`` exists there.
Every arm is new-behaviour; none is behaviour-preservation.

Fixture-only: PDFs are synthesized in-process, paths are redirected to tmp_path,
and no IMF document is read. No network; tesseract is never invoked.

The arms carrying more than correctness:

* ``test_year_comes_from_the_frozen_sample_not_the_report_number`` — frozen row
  2002/246 carries year 2004. Binning by the report number would silently move
  documents between cells that the per-cell seed and every downstream key use.
* ``test_a_document_outside_the_frozen_sample_is_refused`` — permission
  condition 1, enforced at the point files enter the pipeline.
* ``test_sap_gate_refuses_feature_stage_modes`` — PREREG §11.3.
* ``test_fidelity_computes_no_study_outcome`` — calibration must measure
  extraction quality without computing a Tier-1 rate.
"""
import csv
import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


land = _load("imf_corpus_to_pipeline")
ocr = _load("ocr_prepass")
fitz = pytest.importorskip("fitz")


def make_pdf(path, text=""):
    doc = fitz.open()
    page = doc.new_page()
    if text:
        for i in range(40):                       # enough chars to clear the probe
            page.insert_text((50, 40 + i * 15), text, fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    doc.close()


def _manifest(rows):
    return {r["report_no"]: r for r in rows}


def _frozen(rows):
    return {r["id"]: r for r in rows}


# ------------------------------------------------------ landing: cell integrity

def test_year_comes_from_the_frozen_sample_not_the_report_number(tmp_path, monkeypatch):
    monkeypatch.setattr(land, "SRC_DIR", tmp_path)
    monkeypatch.setattr(land, "DEST_ROOT", tmp_path / "dest")
    (tmp_path / "CR2002-246.pdf").write_bytes(b"%PDF-1.7\n%%EOF\n")
    moves = land.plan(
        _manifest([{"report_no": "2002/246", "status": "ok", "sha256": "x"}]),
        _frozen([{"id": "CR2002-246", "year": "2004"}]))
    doc_id, src, dest, _ = moves[0]
    assert dest.parent.name == "2004", "binned by the report year, not the sample year"


def test_a_document_outside_the_frozen_sample_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(land, "SRC_DIR", tmp_path)
    with pytest.raises(RuntimeError, match="not in the frozen sample"):
        land.plan(_manifest([{"report_no": "1999/999", "status": "ok", "sha256": "x"}]),
                  _frozen([{"id": "CR1999-047", "year": "1999"}]))


def test_only_ok_records_are_landed(tmp_path, monkeypatch):
    monkeypatch.setattr(land, "SRC_DIR", tmp_path)
    monkeypatch.setattr(land, "DEST_ROOT", tmp_path / "dest")
    (tmp_path / "CR1999-047.pdf").write_bytes(b"%PDF-1.7\n%%EOF\n")
    moves = land.plan(
        _manifest([{"report_no": "1999/047", "status": "ok", "sha256": "x"},
                   {"report_no": "1999/048", "status": "unresolved", "sha256": ""}]),
        _frozen([{"id": "CR1999-047", "year": "1999"},
                 {"id": "CR1999-048", "year": "1999"}]))
    assert [m[0] for m in moves] == ["CR1999-047"]


def test_a_missing_file_behind_an_ok_row_aborts(tmp_path, monkeypatch):
    monkeypatch.setattr(land, "SRC_DIR", tmp_path)
    with pytest.raises(RuntimeError, match="missing"):
        land.plan(_manifest([{"report_no": "1999/047", "status": "ok", "sha256": "x"}]),
                  _frozen([{"id": "CR1999-047", "year": "1999"}]))


def test_s02_csv_carries_the_columns_s02_reads(tmp_path, monkeypatch):
    monkeypatch.setattr(land, "S02_CSV", tmp_path / "s02.csv")
    n = land.write_s02_csv(
        _manifest([{"report_no": "1999/047", "status": "ok",
                    "pdf_url": "https://www.imf.org/external/x.pdf", "sha256": "x"}]),
        _frozen([{"id": "CR1999-047", "year": "1999", "pub_date": "1999-07-01",
                  "title": "Aruba: Staff Report"}]))
    row = list(csv.DictReader((tmp_path / "s02.csv").open()))[0]
    assert n == 1
    for c in ("id", "stratum", "year", "txturl", "pdfurl"):
        assert c in row
    assert row["stratum"] == "imf_article_iv"
    assert row["pdfurl"].startswith("https://www.imf.org/")
    assert row["txturl"] == ""          # the IMF serves no plain-text copy


# ------------------------------------------------------------- OCR: classification

def test_a_text_layer_pdf_is_classified_native(tmp_path):
    p = tmp_path / "a.pdf"
    make_pdf(p, text="IMF Country Report No. 23/43 staff report text")
    native, chars, pages = ocr.has_text_layer(p)
    assert native is True and chars > 0 and pages == 1


def test_an_image_only_pdf_is_classified_scan(tmp_path):
    p = tmp_path / "b.pdf"
    make_pdf(p, text="")                          # no text layer at all
    native, chars, _ = ocr.has_text_layer(p)
    assert native is False and chars == 0


def test_an_unreadable_file_is_classified_scan_rather_than_crashing(tmp_path):
    p = tmp_path / "c.pdf"
    p.write_bytes(b"not a pdf")
    assert ocr.has_text_layer(p) == (False, 0, 0)


# --------------------------------------------------------------- OCR: the gates

@pytest.mark.parametrize("mode", ["--run", "--calibrate"])
def test_sap_gate_refuses_feature_stage_modes(mode):
    with pytest.raises(SystemExit) as e:
        ocr.main([mode])
    assert "SAP freeze" in str(e.value)


def test_scan_is_allowed_without_the_gate(tmp_path, monkeypatch):
    """--scan classifies only; it extracts no text and computes no feature."""
    raw = tmp_path / "raw"
    make_pdf(raw / "imf_article_iv" / "1999" / "CR1999-047.pdf", text="")
    make_pdf(raw / "imf_article_iv" / "2024" / "CR2024-011.pdf", text="text here")
    monkeypatch.setattr(ocr, "RAW", raw)
    monkeypatch.setattr(ocr, "META", tmp_path / "meta")
    assert ocr.main(["--scan"]) == 0
    rows = list(csv.DictReader((tmp_path / "meta" / "ocr_inventory.csv").open()))
    by_id = {r["id"]: r for r in rows}
    assert by_id["CR1999-047"]["native_text"] == "False"
    assert by_id["CR2024-011"]["native_text"] == "True"
    assert by_id["CR1999-047"]["year"] == "1999"


# ----------------------------------------------------- OCR: calibration hygiene

def test_fidelity_computes_no_study_outcome():
    """Calibration measures extraction quality. It must not compute a Tier-1
    rate or any other outcome, or it would be an outcome peek wearing a
    diagnostic's clothes."""
    f = ocr.fidelity("delve underscore showcase pivotal tapestry")
    assert set(f) == {"chars", "tokens", "mean_token_len", "hyphen_breaks",
                      "nonascii_frac", "single_char_tokens"}
    assert not any("tier" in k or "family" in k or "rate" in k for k in f)


def test_fidelity_detects_the_damage_ocr_actually_does():
    native = "the intricate and meticulous assess-\nment of macroeconomic policy"
    mangled = "the intric ate a nd meti culous assess- ment of rnacroeconornic p olicy"
    fn, fo = ocr.fidelity(native), ocr.fidelity(mangled)
    assert fo["tokens"] > fn["tokens"]                    # spurious word splits
    assert fo["mean_token_len"] < fn["mean_token_len"]
    assert fo["single_char_tokens"] >= fn["single_char_tokens"]


# ------------------------------------------------- Zenodo deposit: the invariant

zen = _load("prepare_zenodo_deposit")


def test_no_imf_corpus_or_raw_archive_is_ever_deposited(tmp_path, monkeypatch):
    """The invariant, stated as the permission states it: no IMF document bytes
    and no IMF raw archive leave the machine. A path-substring check cannot
    express that — `template_imf.csv` holds year/docs/projected-tokens and no
    IMF content at all, and is a derived non-substitutive output §5 permits.
    The real rule is about TREES."""
    root = tmp_path
    for rel in ("data/raw/imf_article_iv/1999", "data/meta/imf_articleiv_raw",
                "data/meta/wb_p0_raw"):
        (root / rel).mkdir(parents=True, exist_ok=True)
        (root / rel / "f.bin").write_bytes(b"x")
    monkeypatch.setattr(zen, "ROOT", root)
    monkeypatch.setattr(zen, "INCLUDE_TREES", [("data/meta/wb_p0_raw", "wb")])
    monkeypatch.setattr(zen, "INCLUDE_FILES", [])
    monkeypatch.setattr(zen, "HASH_ONLY_TREES",
                        [("data/raw/imf_article_iv", "corpus"),
                         ("data/meta/imf_articleiv_raw", "listing")])
    monkeypatch.setattr(zen, "HASH_ONLY_FILES", [])

    zen.main(["--out", str(root / "dep"), "--copy"])
    rows = list(csv.DictReader((root / "dep" / "MANIFEST.csv").open()))
    deposited = {r["path"] for r in rows if r["disposition"] == "deposited"}

    assert deposited == {"data/meta/wb_p0_raw/f.bin"}
    for r in rows:
        if r["path"].startswith(("data/raw/imf_article_iv",
                                 "data/meta/imf_articleiv_raw")):
            assert r["disposition"] == "hash_only_not_deposited"
            assert r["sha256"]                     # verifiability is preserved
    # and nothing from those trees was staged on disk
    staged = {p.relative_to(root / "dep" / "payload").as_posix()
              for p in (root / "dep" / "payload").rglob("*") if p.is_file()}
    assert not any(s.startswith("data/raw/imf_article_iv") for s in staged)
    assert not any(s.startswith("data/meta/imf_articleiv_raw") for s in staged)


@pytest.mark.skipif(
    not (ROOT / "zenodo_deposit" / "MANIFEST.csv").exists(),
    reason="needs a built zenodo_deposit/MANIFEST.csv; run "
           "tools/prepare_zenodo_deposit.py first (build artifact, not in git)")
def test_excluded_files_still_carry_a_hash_so_they_stay_verifiable():
    """Excluding bytes must not cost verifiability: §5 permits publishing
    SHA-256 hashes, and the manifest is how a holder of the originals checks."""
    rows = list(csv.DictReader(
        (ROOT / "zenodo_deposit" / "MANIFEST.csv").open(encoding="utf-8")))
    excluded = [r for r in rows if r["disposition"] == "hash_only_not_deposited"]
    assert excluded, "the real manifest should exclude the IMF material"
    assert all(len(r["sha256"]) == 64 for r in excluded)


def test_real_deposit_config_never_names_an_imf_tree():
    """The test above proves the MECHANISM keeps IMF trees out. This proves the
    CONFIGURATION does, which is the part a later edit can quietly break: the
    deposit list grew on 2026-08-27 to carry the confirmatory outputs, and the
    next such edit is the one that could add an IMF path by hand. Checked against
    the module's real lists, not a monkeypatched pair."""
    imf_trees = [t for t, _ in zen.HASH_ONLY_TREES]
    assert imf_trees, "the IMF trees must stay declared hash-only"
    named = [t for t, _ in zen.INCLUDE_TREES] + list(zen.INCLUDE_FILES)
    for rel in named:
        for tree in imf_trees:
            assert not rel.startswith(tree), (
                f"deposit list names {rel!r}, which lives under the hash-only "
                f"tree {tree!r}")


# ------------------------------------- D9: the log downstream actually reads

def test_ocr_writes_the_extraction_log_not_only_its_own(tmp_path, monkeypatch):
    """D9 requires the extraction method logged per document so era x method can
    be controlled. Writing only to ocr_log.csv satisfied the letter and not the
    function: s05b_family_counts — which produces the CONFIRMATORY outcome —
    iterates extraction_log.csv, so 192 OCR'd documents (the whole 1999-2004 IMF
    block) were absent from the Tier-1 counts while present in classic.csv and
    markers.csv, which walk data/text directly."""
    raw, text, meta = tmp_path / "raw", tmp_path / "text", tmp_path / "meta"
    meta.mkdir(parents=True)
    (meta / "ocr_inventory.csv").write_text(
        "path,id,stratum,year,native_text,probe_chars,pages\n"
        "icr/2001/x.pdf,x,icr,2001,False,0,3\n", encoding="utf-8")
    (meta / "extraction_log.csv").write_text("id,path,method\n", encoding="utf-8")
    (meta / "ocr_log.csv").write_text("", encoding="utf-8")
    make_pdf(raw / "icr" / "2001" / "x.pdf", text="")

    monkeypatch.setattr(ocr, "RAW", raw)
    monkeypatch.setattr(ocr, "TEXT", text)
    monkeypatch.setattr(ocr, "META", meta)
    monkeypatch.setattr(ocr, "ocr_pdf", lambda p, **k: "the report of the bank " * 60)
    monkeypatch.setattr(ocr.shutil, "which", lambda n: "/usr/bin/tesseract")

    ocr.main(["--run", "--i-have-frozen-the-sap", "--utc", "2026-08-27T00:00:00Z"])

    rows = list(csv.DictReader((meta / "extraction_log.csv").open()))
    assert [(r["id"], r["method"]) for r in rows] == [("x", "ocr_tesseract")]
    assert (text / "icr" / "2001" / "x.txt").exists()
