import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s09a_imf_articleiv_frame import build_frame, parse_report_no

FIX = pd.DataFrame([
 {"title": "Republic of Korea: 2024 Article IV Consultation-Press Release; "
           "Staff Report; IMF Country Report No. 24/275",
  "url": "u1", "pub_date": "2024-08-28"},
 {"title": "The Gambia: 2023 Article IV Consultation and Fourth Review Under "
           "the Extended Credit Facility-Press Release; Country Report No. 23/311",
  "url": "u2", "pub_date": "2023-09-01"},
 {"title": "France: Selected Issues; IMF Country Report No. 24/122",
  "url": "u3", "pub_date": "2024-05-30"},
 {"title": "Eastern Caribbean Currency Union: 2024 Article IV Consultation; "
           "Country Report No. 24/300", "url": "u4", "pub_date": "2024-09-10"},
 {"title": "Ruritania: 2024 Article IV Consultation; Country Report No. 24/900",
  "url": "u5", "pub_date": "2024-03-01"},
 {"title": "Japan: 2020 Article IV Consultation; IMF Country Report No. 20/39",
  "url": "u6", "pub_date": "2020-02-10"},
 {"title": "Japan: 2020 Article IV Consultation (Corrigendum); "
           "IMF Country Report No. 20/39", "url": "u7", "pub_date": "2020-03-05"},
 {"title": "Germany: 2026 Article IV Consultation; Country Report No. 26/10",
  "url": "u8", "pub_date": "2026-01-20"},
 {"title": "Suisse: Consultation de 2024 au titre de l'article IV; No. 24/50",
  "url": "u9", "pub_date": "2024-06-01", "language": "French"},
])

def test_pipeline_statuses_and_flags():
    frame, audit = build_frame(FIX)
    st = audit.set_index("url")["status"].to_dict()
    assert st["u1"] == "included" and st["u2"] == "included"
    assert st["u3"] == "excluded_selected_issues"
    assert st["u4"] == "excluded_regional_multicountry"
    assert st["u5"] == "unmapped_country"
    assert st["u8"] == "excluded_after_cutoff"
    assert st["u9"] in ("excluded_language", "excluded_not_article_iv")
    inc = frame.set_index("url")
    assert inc.loc["u1", "country_iso3"] == "KOR"
    assert bool(inc.loc["u2", "combined_with_program"]) is True
    assert inc.loc["u1", "id"] == "CR2024-275"

def test_revision_resolution_keeps_corrigendum():
    frame, audit = build_frame(FIX)
    jp = frame[frame["country_iso3"] == "JPN"]
    assert len(jp) == 1 and jp.iloc[0]["url"] == "u7"
    assert (audit["status"] == "superseded_revision").sum() == 1

def test_report_no_parser():
    assert parse_report_no("IMF Country Report No. 98/7") == "CR1998-007"
    assert parse_report_no("Country Report No. 2015/123") == "CR2015-123"
    assert parse_report_no("no number here") is None


# ----------------------------- round-7: genuine SPROLL live-capture layer --
_PAGE1 = """
<div class="result-row"><a href="/en/pub/a1">Kenya: 2024 Article IV
Consultation; IMF Country Report No. 24/001</a>
<span class="date">July 10, 2024</span></div>
<div class="result-row"><a href="/en/pub/a2">Uganda: 2023 Article IV
Consultation; IMF Country Report No. 23/002</a>
<span class="date">March 3, 2023</span></div>
"""
_PAGE_EMPTY = "<div>No results found</div>"


class _FakeIMFSession:
    def __init__(self):
        self.urls = []
    def get(self, url, timeout=None):
        self.urls.append(url)
        class R:
            status_code = 200
        r = R()
        r.text = _PAGE1 if url.endswith("page=1") else _PAGE_EMPTY
        r.content = r.text.encode()
        return r


def test_parse_sproll_html_documented_structure():
    from s09a_imf_articleiv_frame import parse_sproll_html
    rows = parse_sproll_html(_PAGE1)
    assert len(rows) == 2
    assert rows[0]["pub_date"] == "2024-07-10"
    assert "article iv consultation" in rows[0]["title"].lower()


def test_fetch_live_sproll_archives_pages_and_stops(tmp_path):
    from s09a_imf_articleiv_frame import fetch_live_sproll
    sess = _FakeIMFSession()
    raw = tmp_path / "raw"
    df = fetch_live_sproll(sess, raw, raw / "request_log.csv", sleep=0.0)
    assert sorted(p.name for p in raw.glob("sproll_page_*.html")) == \
        ["sproll_page_0001.html", "sproll_page_0002.html"]
    log = (raw / "request_log.csv").read_text().strip().splitlines()
    assert len(log) == 3                       # header + 2 pages
    assert len(df) == 2 and len(sess.urls) == 2   # stopped on empty page
