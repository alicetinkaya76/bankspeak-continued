import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s09b_wb_p0_frame import build_frame, resolve_country, g2_coverage, load_wb_aliases

ROOT = Path(__file__).resolve().parents[1]
CEM, SCD, CPF = ("Country Economic Memorandum",
                 "Systematic Country Diagnostic",
                 "Country Partnership Framework")

FIX = pd.DataFrame([
 {"id":"D1","docty":CEM,"count":"Turkiye","display_title":"Turkiye - Country Economic Memorandum","docdt":"2019-05-10","repnb":"RPT100","volnb":1},
 {"id":"D2","docty":SCD,"count":"Ghana","display_title":"Ghana - Systematic Country Diagnostic","docdt":"2021-03-01","repnb":"RPT200","volnb":1},
 {"id":"D3","docty":CPF,"count":"Kenya","display_title":"Kenya - Country Partnership Framework","docdt":"2024-02-01","repnb":"RPT300","volnb":1},
 {"id":"D4","docty":CEM,"count":"Egypt, Arab Republic of","display_title":"Egypt CEM","docdt":"2018-06-01","repnb":"RPT400","volnb":1},
 {"id":"D5","docty":CEM,"count":"Congo, Democratic Republic of","display_title":"DRC CEM","docdt":"2017-02-01","repnb":"RPT450","volnb":1},
 {"id":"D6","docty":CEM,"count":"Western Africa","display_title":"Regional study","docdt":"2016-01-01","repnb":"RPT460","volnb":1},
 {"id":"D7","docty":CEM,"count":"Kenya;Uganda","display_title":"Two-country CEM","docdt":"2016-05-01","repnb":"RPT470","volnb":1},
 {"id":"D8","docty":CEM,"count":"","display_title":"No-country row","docdt":"2016-06-01","repnb":"RPT480","volnb":1},
 {"id":"D9","docty":"Project Appraisal Document","count":"India","display_title":"Wrong genre","docdt":"2016-07-01","repnb":"RPT490","volnb":1},
 {"id":"D10","docty":CEM,"count":"India","display_title":"India CEM","docdt":"2026-01-15","repnb":"RPT500X","volnb":1},
 {"id":"D11","docty":CEM,"count":"Nigeria","display_title":"Nigeria CEM (Vol. 1)","docdt":"2015-04-01","repnb":"RPT500","volnb":1},
 {"id":"D12","docty":CEM,"count":"Nigeria","display_title":"Nigeria CEM (Vol. 2)","docdt":"2015-04-01","repnb":"RPT500","volnb":2},
 {"id":"D13","docty":CEM,"count":"Brazil","display_title":"Brazil CEM","docdt":"2012-01-01","repnb":"RPT600","volnb":1},
 {"id":"D14","docty":CEM,"count":"Brazil","display_title":"Brazil CEM (Revised)","docdt":"2012-03-01","repnb":"RPT600","volnb":1},
 {"id":"D15","docty":CEM,"count":"France","display_title":"France CEM","docdt":"2011-01-01","repnb":"RPT700","volnb":1,"lang":"French"},
])

def test_statuses_and_country_rules():
    frame, audit = build_frame(FIX, root=ROOT)
    st = audit.set_index("doc_id")["status"].to_dict()
    assert st["D1"] == st["D2"] == st["D3"] == "included"
    assert st["D6"] == st["D7"] == "excluded_regional_multicountry"
    assert st["D8"] == "excluded_no_country"
    assert st["D9"] == "excluded_docty"
    assert st["D10"] == "excluded_after_cutoff"
    assert st["D15"] == "excluded_language"
    inc = frame.set_index("doc_id")
    assert inc.loc["D1", "country_iso3"] == "TUR"
    assert inc.loc["D4", "country_iso3"] == "EGY"      # comma inversion
    assert inc.loc["D5", "country_iso3"] == "COD"      # alias-map extension
    assert inc.loc["D1", "id"] == "RPT100"             # unit = repnb

def test_version_and_volume_resolution():
    frame, audit = build_frame(FIX, root=ROOT)
    ng = frame[frame["country_iso3"] == "NGA"]
    assert len(ng) == 1 and int(ng.iloc[0]["volnb"]) == 1
    br = frame[frame["country_iso3"] == "BRA"]
    assert len(br) == 1 and "Revised" in br.iloc[0]["title"]
    assert (audit["status"] == "superseded_version").sum() == 2

def test_resolve_country_unmapped_logs():
    aliases = load_wb_aliases(ROOT)
    iso, err = resolve_country("Ruritania", aliases)
    assert iso is None and err == "unmapped_country"

def test_g2_coverage_report():
    frame, _ = build_frame(FIX, root=ROOT)
    imf = pd.DataFrame({"year": list(range(1994, 2026))})
    rep = g2_coverage(frame, imf)
    assert rep["cem"]["common_pre_years_with_articleiv"] == 5
    assert rep["cem"]["g2_metadata_ok"] is False       # << 25 common pre years
    assert rep["cpf"]["post_years"] == [2024]


# ------------------------- round-7: page-level live-capture architecture --
class _FakeResp:
    def __init__(self, payload):
        import json as _json
        self._p = payload
        self.status_code = 200
        self.text = _json.dumps(payload)
        self.content = self.text.encode()     # the fake's VERBATIM bytes
    def json(self):
        return self._p


class _FakeSession:
    """Two-page WDS stratum: total=3, rows_per_page=2."""
    def __init__(self):
        self.calls = []
    def get(self, url, params=None, timeout=None):
        self.calls.append(dict(params))
        os_ = params.get("os", 0)
        if os_ == 0:
            docs = {"D1": {"id": "1", "docty": "X", "count": "5",
                           "display_title": "A", "docdt": "2024-01-01T00:00:00Z",
                           "repnb": "R1", "volnb": "1"},
                    "D2": {"id": "2", "docty": "X", "count": "6",
                           "display_title": "B", "docdt": "2024-02-01T00:00:00Z",
                           "repnb": "R2", "volnb": "1"},
                    "facets": {}}
        else:
            docs = {"D3": {"id": "3", "docty": "X", "count": "7",
                           "display_title": "C", "docdt": "2024-03-01T00:00:00Z",
                           "repnb": "R3", "volnb": "1"}}
        return _FakeResp({"total": 3, "documents": docs})


def _mini_cfg():
    return {"api": {"base_url": "http://fake", "rows_per_page": 2,
                    "format": "json", "lang_exact": "English",
                    "fields": ["id", "docty", "count", "display_title",
                               "docdt", "repnb", "volnb"],
                    "max_retries": 2, "timeout": 5, "backoff_base": 1,
                    "sleep_seconds": 0}}


def test_page_hook_archives_every_raw_page(tmp_path, monkeypatch):
    import s09b_wb_p0_frame as s9b
    import utils
    fake = _FakeSession()
    monkeypatch.setattr(utils, "session_for", lambda cfg: fake)
    raw = tmp_path / "raw"
    df = s9b.fetch_live(_mini_cfg(), [{"genre": "cem", "docty": "X"}],
                        2024, 2024, raw, raw / "request_log.csv")
    pages = sorted(p.name for p in raw.glob("cem_2024_os*.json"))
    assert pages == ["cem_2024_os0.json", "cem_2024_os2.json"]
    log = (raw / "request_log.csv").read_text().strip().splitlines()
    assert len(log) == 3 and log[0].startswith("utc,")     # header + 2 pages
    assert len(df) == 3                                    # combined records
    assert all("os" in c for c in fake.calls)
    # round-9: archived page bytes are the VERBATIM transport BYTES
    body0 = fake.get("http://fake", {"os": 0}, 1).content
    assert (raw / "cem_2024_os0.json").read_bytes() == body0


def test_docty_verification_overrides_and_logs(tmp_path, capsys):
    import json as _json
    from s09b_wb_p0_frame import apply_docty_verification
    v = tmp_path / "verified.json"
    import hashlib as _hl
    art = tmp_path / "probe_artifact.json"
    art.write_bytes(b"S00 PROBE ARTIFACT")
    v.write_text(_json.dumps({"verified_utc": "2026-11-01T00:00:00Z",
                              "source": "s00",
                              "probe_sha256":
                                  _hl.sha256(b"S00 PROBE ARTIFACT")
                                  .hexdigest(),
                              "labels": {"cem": "Country Economic "
                                                "Memorandum (verified)",
                                         "scd": "Systematic Country "
                                                "Diagnostic",
                                         "cpf": "Country Partnership "
                                                "Framework"}}))
    dm = apply_docty_verification(
        [{"genre": "cem", "docty": "Country Economic Memorandum"},
         {"genre": "scd", "docty": "Systematic Country Diagnostic"}], str(v), probe_artifact=str(art))
    assert dm[0]["docty"].endswith("(verified)")
    assert dm[1]["docty"] == "Systematic Country Diagnostic"
    assert "docty divergence" in capsys.readouterr().out
