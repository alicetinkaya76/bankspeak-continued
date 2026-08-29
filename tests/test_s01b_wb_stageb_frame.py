"""s01b — WB Stage-B metadata frame capture (A6, 2026-08-20).

Old-commit classification matrix (round-13 honesty rule): ALL tests in this file
FAIL at every commit up to and including 8b82787 — `src/s01b_wb_stageb_frame.py`
does not exist there. Every arm is new-behaviour; none is behaviour-preservation.

Fixture-only: a scripted fake session, no network. Covers the Stage-B refusal,
the write-once guards (raw directory and frame output), verbatim-byte archiving
of both ordinary pages and retried 429/5xx bodies, the append-only request log
and its schema, the `s09_frame_sampler` input contract, cross-genre id
uniqueness, and the PREREG §11.4 confirmatory cutoff — including that the cutoff
is read off each record's own `docdt` rather than off the query year.
"""
import csv
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import s01b_wb_stageb_frame as s01b  # noqa: E402
import utils  # noqa: E402


def _cfg():
    return {
        "contact_email": "x@y.z",
        "api": {"base_url": "https://api.test/wds", "format": "json",
                "rows_per_page": 2, "lang_exact": "English",
                "fields": ["id", "docdt"], "max_retries": 3, "timeout": 5,
                "backoff_base": 1.0, "sleep_seconds": 0.0},
        "years": {"start": 2024, "end": 2025},
        "strata": {"icr": {"docty_exact": ["ICR"], "per_year_cap": 40},
                   "pad": {"docty_exact": ["PAD"], "per_year_cap": 40}},
    }


def _doc(i, docdt="2024-05-05T00:00:00Z"):
    return {"id": str(i), "docdt": docdt, "repnb": f"R{i}",
            "display_title": f"T{i}", "txturl": f"t{i}", "pdfurl": f"p{i}"}


class _Resp:
    def __init__(self, status, payload):
        self.status_code = status
        self.content = json.dumps(payload).encode("utf-8")

    def json(self):
        return json.loads(self.content)

    def raise_for_status(self):
        raise RuntimeError(f"HTTP {self.status_code}")


class _FakeSession:
    """Serves one page per (genre-ish docty, year); `script` may inject retries."""

    def __init__(self, pages=None, script=None):
        self.pages = pages or {}
        self.script = list(script or [])
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append(dict(params))
        if self.script:
            status, payload = self.script.pop(0)
            return _Resp(status, payload)
        key = (params["docty_exact"], params["strdate"][:4], params.get("os", 0))
        payload = self.pages.get(key, {"total": 0, "documents": {}})
        return _Resp(200, payload)


def _pages_one_each():
    """One document per (docty, year) across 2024-2025, ids kept unique."""
    out, n = {}, 0
    for docty in ("ICR", "PAD"):
        for year in ("2024", "2025"):
            n += 1
            out[(docty, year, 0)] = {
                "total": 1,
                "documents": {f"D{n}": _doc(n, f"{year}-05-05T00:00:00Z")}}
    return out


@pytest.fixture
def patched(monkeypatch):
    monkeypatch.setattr(utils.time, "sleep", lambda *_: None)
    return monkeypatch


# ------------------------------------------------------------- Stage-B refusal

def test_refuses_to_run_without_the_stage_b_flag(tmp_path):
    with pytest.raises(SystemExit) as e:
        s01b.main(["--frame-out", str(tmp_path / "f.csv"),
                   "--raw-dir", str(tmp_path / "raw")])
    assert "--i-am-in-stage-b" in str(e.value)


def test_refuses_to_overwrite_an_existing_frame(tmp_path):
    out = tmp_path / "f.csv"
    out.write_text("already here")
    with pytest.raises(SystemExit) as e:
        s01b.main(["--frame-out", str(out), "--raw-dir", str(tmp_path / "raw"),
                   "--i-am-in-stage-b"])
    assert "write-once" in str(e.value)
    assert out.read_text() == "already here"


# --------------------------------------------------------- write-once archives

def test_refuses_a_raw_directory_that_already_holds_archives(tmp_path, patched):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "icr_2024_os0.json").write_text("{}")
    with pytest.raises(RuntimeError, match="write-once"):
        s01b.fetch_live(_cfg(), {"icr": {"docty_exact": ["ICR"]}},
                        2024, 2024, raw, session=_FakeSession(_pages_one_each()))


def test_archives_every_page_verbatim_and_logs_it(tmp_path, patched):
    raw = tmp_path / "raw"
    sess = _FakeSession(_pages_one_each())
    s01b.fetch_live(_cfg(), {"icr": {"docty_exact": ["ICR"]}}, 2024, 2025, raw,
                    session=sess)
    names = sorted(p.name for p in raw.glob("*.json"))
    assert names == ["icr_2024_os0.json", "icr_2025_os0.json"]
    # verbatim: the archived bytes parse back to the served payload
    served = json.loads((raw / "icr_2024_os0.json").read_bytes())
    assert served["total"] == 1
    log = list(csv.reader((raw / "request_log.csv").open()))
    assert log[0] == s01b.LOG_HEADER
    assert len(log) == 3                               # header + 2 pages
    assert log[1][1] == "icr" and log[1][2] == "2024"


def test_retried_5xx_bodies_are_archived_and_logged(tmp_path, patched):
    raw = tmp_path / "raw"
    page = {"total": 1, "documents": {"D1": _doc(1)}}
    sess = _FakeSession(script=[(503, {"err": "busy"}), (200, page)])
    s01b.fetch_live(_cfg(), {"icr": {"docty_exact": ["ICR"]}}, 2024, 2024, raw,
                    session=sess)
    attempts = sorted(p.name for p in raw.glob("*attempt*"))
    assert attempts == ["icr_2024_os0_attempt1_status503.json"]
    assert json.loads((raw / attempts[0]).read_bytes()) == {"err": "busy"}
    rows = list(csv.DictReader((raw / "request_log.csv").open()))
    assert any(r["rows_returned"] == "attempt:503" for r in rows)


def test_the_request_log_is_append_only(tmp_path, patched):
    raw = tmp_path / "raw"
    log = tmp_path / "request_log.csv"
    s01b.fetch_live(_cfg(), {"icr": {"docty_exact": ["ICR"]}}, 2024, 2024, raw,
                    log, session=_FakeSession(_pages_one_each()))
    first = log.read_text()
    s01b.fetch_live(_cfg(), {"pad": {"docty_exact": ["PAD"]}}, 2024, 2024,
                    tmp_path / "raw2", log, session=_FakeSession(_pages_one_each()))
    after = log.read_text()
    assert after.startswith(first)                     # nothing rewritten
    assert after.count("\n") > first.count("\n")


# --------------------------------------------------- s09_frame_sampler contract

def test_frame_carries_the_columns_the_sampler_requires():
    from s09_frame_sampler import REQUIRED
    assert set(REQUIRED) <= set(s01b.FRAME_FIELDS)


def test_frame_shape_institution_genre_year_id(tmp_path, patched):
    captured = s01b.fetch_live(_cfg(), _cfg()["strata"], 2024, 2025,
                               tmp_path / "raw",
                               session=_FakeSession(_pages_one_each()))
    rows = s01b.build_frame(captured)
    assert len(rows) == 4
    assert {r["institution"] for r in rows} == {"wb"}
    assert {r["genre"] for r in rows} == {"icr", "pad"}
    assert {r["year"] for r in rows} == {2024, 2025}
    assert len({r["id"] for r in rows}) == 4          # ids unique across cells
    assert rows == sorted(rows, key=lambda x: (x["genre"], x["year"], x["id"]))


def test_build_frame_refuses_a_duplicate_id_across_cells():
    captured = [{"genre": "icr", "year": 2024, "record": _doc(7)},
                {"genre": "pad", "year": 2025, "record": _doc(7)}]
    with pytest.raises(RuntimeError, match="duplicate document id"):
        s01b.build_frame(captured)


def test_build_frame_refuses_an_empty_id():
    with pytest.raises(RuntimeError, match="empty id"):
        s01b.build_frame([{"genre": "icr", "year": 2024, "record": {"id": " "}}])


# ------------------------------------------------ PREREG §11.4 calendar cutoff

@pytest.mark.parametrize("docdt,expected", [
    ("2025-12-31T00:00:00Z", True),
    ("2026-01-01T00:00:00Z", False),
    ("2025-06-30T00:00:00Z", True),
    ("2026-08-20T00:00:00Z", False),
    ("", False),                     # unknown date is never treated as early
    ("not-a-date", False),
])
def test_confirmatory_cutoff_is_read_off_the_publication_date(docdt, expected):
    assert s01b.confirmatory_eligible(docdt) is expected


def test_cutoff_uses_docdt_not_the_query_year(tmp_path):
    """A 2026-dated record captured in the 2025 cell must still be excluded;
    deriving the flag from the cell year would wrongly admit it."""
    captured = [{"genre": "icr", "year": 2025,
                 "record": _doc(1, "2026-02-02T00:00:00Z")}]
    row = s01b.build_frame(captured)[0]
    assert row["year"] == 2025
    assert row["confirmatory_eligible"] is False
    assert row["docdt_year_matches_cell"] is False


def test_2026_is_captured_not_dropped(tmp_path):
    """A6: the window is 1946-2026 and 2026 is flagged, never omitted."""
    captured = [{"genre": "icr", "year": 2026,
                 "record": _doc(1, "2026-03-03T00:00:00Z")}]
    rows = s01b.build_frame(captured)
    assert len(rows) == 1 and rows[0]["confirmatory_eligible"] is False


# --------------------------------------------------------- decision-logic line

def test_s01b_does_not_reimplement_the_frozen_fetch_rules():
    """The line: s01b is transport/archiving/shaping. The rules that decide what
    a document IS stay in the frozen s01 stack.

    Checked structurally on the AST, not by grepping the source: the module must
    IMPORT `fetch_stratum_year` and must not define its own paging/validation
    twin. A prose mention of a frozen rule is documentation, not duplication,
    and must not fail this arm.
    """
    import ast
    tree = ast.parse((ROOT / "src" / "s01b_wb_stageb_frame.py").read_text())
    imported = {alias.name for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
                for alias in node.names}
    assert "fetch_stratum_year" in imported
    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "fetch_stratum_year" not in defined
    assert defined >= {"fetch_live", "build_frame", "confirmatory_eligible"}


def test_schema_failures_from_s01_propagate(tmp_path, patched):
    """A payload lacking 'total'/'documents' must abort the capture, not be
    absorbed as an empty year."""
    sess = _FakeSession(script=[(200, {"documents": {}})])
    with pytest.raises(RuntimeError, match="schema failure"):
        s01b.fetch_live(_cfg(), {"icr": {"docty_exact": ["ICR"]}}, 2024, 2024,
                        tmp_path / "raw", session=sess)
