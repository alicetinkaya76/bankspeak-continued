"""SAP addendum A1/A2/A3 (2026-08-19): Coveo transport for the s09a live
Article IV listing.

Old-commit classification matrix (round-13 honesty rule): ALL tests in this
file FAIL at 20af74e71d7eedb0a23583d81982f816b645544f (fetch_live_coveo does
not exist there); the A2 arms additionally fail at a1b41ad (no catalog
fields) and the A3 arms at db71c15 (offset pagination). Every arm is
new-behaviour; none is behaviour-preservation.

Fixture-only: a scripted fake session; no network. Covers the write-once
guard (both page-file kinds), verbatim-byte archiving, non-200 and
JSON-decode fail-closed aborts, the A3 window contract (a window is accepted
only when returned entire; a truncated window splits year -> month -> day
and never paginates), split-sum integrity, the day floor, the global sum
check, permanentid uniqueness and presence, imfdate presence, the
missing-api-key refusal, body hygiene (no session analytics, catalog fields
requested, imflanguage never requested, firstResult always 0), the catalog
report number carried verbatim, provenance normalization, and the imfdate
epoch-ms conversion at an ET year boundary.
"""
import calendar
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s09a_imf_articleiv_frame import (_coveo_body, _coveo_scalar,
                                      _imfdate_ms_to_iso, fetch_live_coveo,
                                      parse_report_no)

CFG = {"contact_email": "ali.cetinkaya@selcuk.edu.tr",
       "imf_coveo": {"api_key": "xxTESTKEY", "page_size": 1000,
                     "sleep_seconds": 0.0, "year_lo": 2025, "year_hi": 2025}}

AUG10_2026_ET_MS = 1786334400000      # 2026-08-10 00:00 US-Eastern (EDT)
DEC31_2025_ET_MS = 1767157200000      # 2025-12-31 00:00 US-Eastern (EST)


def result(pid, title="T: 2025 Article IV Consultation", uri="https://x/1",
           ms=DEC31_2025_ET_MS, volno=None, iso=None, series=None,
           imftype=None):
    raw = {"permanentid": pid, "imfdate": ms}
    for k, v in (("seriesvolumeno", volno), ("imfisocode", iso),
                 ("imfseries", series), ("imftype", imftype)):
        if v is not None:
            raw[k] = v
    return {"title": title, "clickUri": uri, "raw": raw}


def page(total, results):
    return json.dumps({"totalCount": total, "results": results}).encode()


class FakeResp:
    def __init__(self, status, content):
        self.status_code, self.content = status, content


class FakeSession:
    """Pops scripted (status, body-bytes) responses; records request bodies."""

    def __init__(self, script):
        self.script, self.bodies = list(script), []

    def post(self, url, data=None, headers=None, timeout=None):
        self.bodies.append(json.loads(data.decode("utf-8")))
        status, content = self.script.pop(0)
        return FakeResp(status, content)


def run(tmp_path, script, cfg=CFG, **kw):
    raw = tmp_path / "raw"
    sess = FakeSession(script)
    df = fetch_live_coveo(sess, raw, raw / "request_log.csv", cfg, **kw)
    return df, sess, raw


def simple_script(n=2):
    """global(total=n) then year 2025 returning all n. Two responses: the
    measurement request does not collect its results."""
    rs = [result(f"p{i}") for i in range(n)]
    return [(200, page(n, rs[:1])), (200, page(n, rs))]


# ------------------------------------------------------------- happy path --
def test_happy_path_one_request_per_window(tmp_path):
    df, sess, raw = run(tmp_path, simple_script(2))
    assert list(df.columns) == ["title", "url", "pub_date", "report_no",
                                "src_imfisocode", "src_imfseries",
                                "src_imftype"]
    assert "language" not in df.columns          # A2: the imflanguage trap
    assert len(df) == 2
    assert len(sess.bodies) == 2                 # measurement + one year
    assert (raw / "coveo_page_0000.json").exists()
    log = (raw / "request_log.csv").read_text().strip().splitlines()
    assert len(log) == 1 + 2
    assert log[0].split(",")[:4] == ["utc", "page", "url", "window"]


def test_raw_files_are_verbatim_response_bytes(tmp_path):
    script = simple_script(2)
    _, _, raw = run(tmp_path, list(script))
    for i, (_, body) in enumerate(script):
        assert (raw / f"coveo_page_{i:04d}.json").read_bytes() == body


def test_empty_year_costs_one_request_and_no_rows(tmp_path):
    df, sess, _ = run(tmp_path, [(200, page(0, [])), (200, page(0, []))])
    assert len(df) == 0 and len(sess.bodies) == 2


# --------------------------------------------------- A3 window contract ----
def test_truncated_year_splits_into_months_and_never_paginates(tmp_path):
    """The year reports 3 but returns 2 -> split into 12 months; two months
    carry the items, the rest are empty. firstResult stays 0 throughout."""
    a, b, c = result("a"), result("b"), result("c")
    script = [(200, page(3, [a])),               # measurement
              (200, page(3, [a, b]))]            # year 2025: TRUNCATED
    for m in range(1, 13):
        if m == 3:
            script.append((200, page(2, [a, b])))
        elif m == 7:
            script.append((200, page(1, [c])))
        else:
            script.append((200, page(0, [])))
    df, sess, _ = run(tmp_path, script)
    assert len(df) == 3
    assert len(sess.bodies) == 2 + 12
    assert all(body["firstResult"] == 0 for body in sess.bodies)
    assert "(@imfdate>=2025/03/01 @imfdate<=2025/03/31)" in sess.bodies[4]["aq"]
    last = calendar.monthrange(2025, 2)[1]
    assert f"@imfdate<=2025/02/{last:02d}" in sess.bodies[3]["aq"]


def test_truncated_month_splits_into_days(tmp_path):
    a, b = result("a"), result("b")
    script = [(200, page(2, [a])),               # measurement
              (200, page(2, [a]))]               # year: truncated
    for m in range(1, 13):
        if m == 1:
            script.append((200, page(2, [a])))   # january: truncated
            for d in range(1, 32):
                if d == 5:
                    script.append((200, page(1, [a])))
                elif d == 9:
                    script.append((200, page(1, [b])))
                else:
                    script.append((200, page(0, [])))
        else:
            script.append((200, page(0, [])))
    df, sess, _ = run(tmp_path, script)
    assert len(df) == 2
    assert ("(@imfdate>=2025/01/05 @imfdate<=2025/01/05)"
            in sess.bodies[3 + 4]["aq"])


def test_truncated_day_is_a_hard_floor(tmp_path):
    a = result("a")
    script = [(200, page(2, [a])), (200, page(2, [a]))]
    for m in range(1, 13):
        if m == 1:
            script.append((200, page(2, [a])))
            for d in range(1, 32):
                script.append((200, page(2, [a])) if d == 1 else
                              (200, page(0, [])))
        else:
            script.append((200, page(0, [])))
    with pytest.raises(RuntimeError, match="cannot be split further"):
        run(tmp_path, script)


def test_child_windows_must_sum_to_the_parent(tmp_path):
    a, b = result("a"), result("b")
    script = [(200, page(5, [a])), (200, page(5, [a, b]))]
    for m in range(1, 13):                       # months sum to 2, not 5
        script.append((200, page(2, [a, b])) if m == 4 else
                      (200, page(0, [])))
    with pytest.raises(RuntimeError, match="children sum to"):
        run(tmp_path, script)


def test_window_sum_must_match_the_global_total(tmp_path):
    a = result("a")
    with pytest.raises(RuntimeError, match="window sum"):
        run(tmp_path, [(200, page(9, [a])), (200, page(1, [a]))])


def test_incoherent_response_more_results_than_total(tmp_path):
    a, b = result("a"), result("b")
    with pytest.raises(RuntimeError, match="results > totalCount"):
        run(tmp_path, [(200, page(2, [a])), (200, page(1, [a, b]))])


# ------------------------------------------------------- fail-closed arms --
def test_write_once_guard_refuses_stale_dirs(tmp_path):
    for stale in ("coveo_page_0001.json", "sproll_page_0001.html"):
        raw = tmp_path / f"raw_{stale}"
        raw.mkdir()
        (raw / stale).write_bytes(b"old")
        with pytest.raises(RuntimeError, match="write-once"):
            fetch_live_coveo(FakeSession([]), raw, raw / "log.csv", CFG)


def test_non_200_aborts_after_archiving(tmp_path):
    with pytest.raises(RuntimeError, match="HTTP 403"):
        run(tmp_path, [(403, b"denied")])
    assert (tmp_path / "raw" / "coveo_page_0000.json").read_bytes() == b"denied"


def test_invalid_json_aborts_after_archiving(tmp_path):
    with pytest.raises(RuntimeError, match="not valid UTF-8 JSON"):
        run(tmp_path, [(200, b"<html>not json</html>")])
    assert (tmp_path / "raw" / "coveo_page_0000.json").exists()


def test_schema_drift_aborts(tmp_path):
    with pytest.raises(RuntimeError, match="schema drift"):
        run(tmp_path, [(200, json.dumps({"results": []}).encode())])


def test_duplicate_permanentid_aborts(tmp_path):
    dup = result("SAME")
    with pytest.raises(RuntimeError, match="duplicate permanentid"):
        run(tmp_path, [(200, page(2, [dup])), (200, page(2, [dup, dup]))])


def test_missing_permanentid_aborts(tmp_path):
    bad = {"title": "T", "clickUri": "u", "raw": {"imfdate": DEC31_2025_ET_MS}}
    with pytest.raises(RuntimeError, match="without permanentid"):
        run(tmp_path, [(200, page(1, [bad])), (200, page(1, [bad]))])


def test_missing_imfdate_aborts(tmp_path):
    bad = {"title": "T", "clickUri": "u", "raw": {"permanentid": "p"}}
    with pytest.raises(RuntimeError, match="without imfdate"):
        run(tmp_path, [(200, page(1, [bad])), (200, page(1, [bad]))])


def test_missing_api_key_refuses(tmp_path):
    with pytest.raises(SystemExit, match="imf_coveo.api_key missing"):
        fetch_live_coveo(FakeSession([]), tmp_path / "raw",
                         tmp_path / "raw" / "log.csv",
                         {"contact_email": "x@y"})


# ----------------------------------------------------------- body hygiene --
def test_body_hygiene_and_requested_fields(tmp_path):
    _, sess, _ = run(tmp_path, simple_script(1))
    for b in sess.bodies:
        assert "actionsHistory" not in b and "analytics" not in b
        assert b["sortCriteria"] == "@imfdate descending"
        assert b["firstResult"] == 0
        for f in ("seriesvolumeno", "imfseries", "imfisocode", "imftype"):
            assert f in b["fieldsToInclude"], f
        assert "imflanguage" not in b["fieldsToInclude"]
    assert "@imfdate>=" not in sess.bodies[0]["aq"]      # measurement
    assert ("(@imfdate>=2025/01/01 @imfdate<=2025/12/31)"
            in sess.bodies[1]["aq"])


def test_coveo_body_is_the_page_query_minus_session_fields():
    b = _coveo_body(0, 100)
    assert "Article-iv-Consultation" in b["aq"]
    assert b["searchHub"] == "Search" and b["tab"] == "default"
    assert "analytics" not in b and "actionsHistory" not in b


# ------------------------------------------------------- A2 catalog fields --
def test_report_no_is_carried_verbatim_from_seriesvolumeno(tmp_path):
    pub = result("p1", "Freedonia: Staff Report for the 1999 Article IV "
                 "Consultation", volno="Country Report No.  1999/149",
                 iso=["COL"], series=["IMF Staff Country Reports"],
                 imftype="Issue Page")
    news = result("p2", "IMF Executive Board Concludes 2025 Article IV "
                  "Consultation with Ruritania", iso=["MNG"],
                  imftype="Press Release")
    df, _, _ = run(tmp_path, [(200, page(2, [pub])),
                              (200, page(2, [pub, news]))])
    assert df.iloc[0]["report_no"] == "Country Report No.  1999/149"
    assert df.iloc[1]["report_no"] == ""          # absent -> empty, no crash
    assert df.iloc[0]["src_imfisocode"] == "COL"  # single-element list
    assert df.iloc[0]["src_imfseries"] == "IMF Staff Country Reports"
    assert df.iloc[0]["src_imftype"] == "Issue Page"
    assert df.iloc[1]["src_imfseries"] == ""


def test_frozen_parser_turns_the_catalog_string_into_a_report_id():
    """The capture layer never interprets the string; parse_report_no does,
    and it already handles the catalog's spacing and 4-digit volume."""
    assert parse_report_no(" Country Report No.  1999/149") == "CR1999-149"
    assert parse_report_no(" Country Report No. 2026/221") == "CR2026-221"


def test_multi_country_isocode_is_preserved_not_collapsed(tmp_path):
    multi = result("p9", "Sylvania Union: 2025 Article IV Consultation",
                   iso=["DEU", "FRA"], imftype="Issue Page")
    df, _, _ = run(tmp_path, [(200, page(1, [multi])),
                              (200, page(1, [multi]))])
    assert df.iloc[0]["src_imfisocode"] == "DEU|FRA"


def test_coveo_scalar_normalization():
    assert _coveo_scalar(None) == ""
    assert _coveo_scalar([]) == ""
    assert _coveo_scalar(["X"]) == "X"
    assert _coveo_scalar(["X", "Y"], join=True) == "X|Y"
    assert _coveo_scalar("plain") == "plain"


def test_imfdate_conversion_is_utc_date_of_instant():
    assert _imfdate_ms_to_iso(AUG10_2026_ET_MS) == "2026-08-10"
    assert _imfdate_ms_to_iso(DEC31_2025_ET_MS) == "2025-12-31"
