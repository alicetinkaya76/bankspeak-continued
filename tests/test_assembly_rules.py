"""Offline tests for the s10 sibling filter. Titles below are real display_title
patterns from the harvested metadata (facts, not shipped document text)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from s10_assemble_ar import classify

def test_wb_annual_reports_included():
    for t in [
        "The World Bank Annual Report 2020 : Supporting Countries in Unprecedented Times",
        "World Bank annual report 1974",
        "World Bank Annual Report 2004 (Vol. 1 of 2) : Year in Review",
        "World Bank and IDA annual report 1963 - 1964",
        "World Bank, International Development Association annual report 1968",
        "World Bank, IDA annual report 1973",
        "International Bank for Reconstruction and Development annual report 1950",
    ]:
        decision, rule = classify(t)
        assert decision == "include", (t, rule)

def test_sibling_org_reports_excluded():
    for t, expected in [
        ("International Finance Corporation (IFC) annual report 1994", "IFC"),
        ("IFC Annual Report 2021 : Meeting the Moment", "IFC"),
        ("Multilateral Investment Guarantee Agency (MIGA) Annual Report 2024", "MIGA"),
        ("International Centre for Settlement of Investment Disputes (ICSID) 2019 Annual Report", "ICSID"),
        ("CIADI informe anual 1994 : International Centre for Settlement", "ICSID"),
    ]:
        decision, rule = classify(t)
        assert decision == "exclude" and rule == expected, (t, decision, rule)

def test_unit_qc_separates_prose_from_degenerate_extractions():
    from s10_assemble_ar import unit_qc
    qc = {"min_tokens": 50, "min_stopword_share": 0.15}
    prose = ("The report of the board describes the lending program for the year "
             "and the projects approved in the region, with details of the loans "
             "made to the member countries and the results of the operations. ") * 4
    ok, n, share = unit_qc(prose, qc)
    assert ok and n >= 50 and share >= 0.15
    stamps = "Public Disclosure Authorized " * 30          # FY2002 failure mode
    ok, _, share = unit_qc(stamps, qc)
    assert not ok and share < 0.05
    table_dump = "Revenue Expenses Assets Liabilities Total " * 40  # FY2007 mode
    ok, _, _ = unit_qc(table_dump, qc)
    assert not ok
    ok, _, _ = unit_qc("short text", qc)                   # below min_tokens
    assert not ok

def test_resolved_review_covers_known_borderline_ids():
    from s10_assemble_ar import RESOLVED_REVIEW
    assert set(RESOLVED_REVIEW) == {"438429", "1561354", "25251052", "1561253",
                                    "439284", "34063779", "30458125"}
    for decision, rule in RESOLVED_REVIEW.values():
        assert decision in {"include", "exclude"}
        assert rule.startswith("resolved:")

def test_borderline_titles_go_to_review_not_auto_resolved():
    for t in [
        "First annual meeting of the board of governors of the International Bank",
        "The World Bank and the environment : first annual report, fiscal 1990",
        "Relatório Principal",
        "Summaries of Operations Approved during Fiscal 2008 : East Asia and Pacific (Vol. 5)",
        "International Development Association annual report 1962",
    ]:
        decision, _ = classify(t)
        assert decision == "review", (t, decision)
