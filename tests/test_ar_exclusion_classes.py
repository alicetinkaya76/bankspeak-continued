"""Pin the exclusion-class decomposition behind §6.1's Table 3c.

An external review objected that "the 195 excluded sibling-organisation volumes"
merged two methodologically different things: excluding IFC/MIGA/ICSID volumes is
a corpus-boundary decision, removing a duplicate record is data cleaning. The
objection was right about the category and wrong about the consequence — the
opposing trend is 94% sibling organisations, and the five duplicates have no
early-period observation at all — but the paper could not have known that until
it was computed.
"""
import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "meta" / "ar_assembly_log.csv"
FEATURES = ROOT / "data" / "features" / "classic.csv"

needs_data = pytest.mark.skipif(
    not (LEDGER.exists() and FEATURES.exists()),
    reason="needs data/meta/ar_assembly_log.csv and data/features/classic.csv "
           "(deposited, not in git)")

_spec = importlib.util.spec_from_file_location(
    "ar_exclusion_classes", ROOT / "tools" / "ar_exclusion_classes.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_the_classifier_separates_cleaning_from_a_boundary_decision():
    assert _mod.klass("IFC").startswith("sibling")
    assert _mod.klass("MIGA").startswith("sibling")
    assert _mod.klass("ICSID_nonlatin").startswith("sibling")
    assert _mod.klass("duplicate_repnb_volnb").startswith("duplicate")
    assert _mod.klass("resolved:IDA_separate_series").startswith("other")


@needs_data
def test_the_three_classes_account_for_every_excluded_file():
    """134 + 195 = 329, and the 195 split without remainder. An off-by-one here
    would put a document in no class and quietly out of the table."""
    led = {r["id"]: r for r in csv.DictReader(LEDGER.open(encoding="utf-8"))}
    docs = [r for r in csv.DictReader(FEATURES.open(encoding="utf-8"))
            if r["stratum"] == "annual_report"]
    asm = list(csv.DictReader(
        (ROOT / "data/features/ar_fy_features.csv").open(encoding="utf-8")))
    assembled = set()
    for r in asm:
        assembled.update(x for x in r["doc_ids"].split(";") if x)

    excluded = [r for r in docs if r["id"] not in assembled]
    assert len(docs) == 329 and len(excluded) == 195
    counts = {}
    for r in excluded:
        e = led.get(r["id"])
        k = _mod.klass(e["rule"]) if e else "other logged ruling"
        counts[k] = counts.get(k, 0) + 1
    assert sum(counts.values()) == 195, counts
    assert counts["sibling organisation (IFC/MIGA/ICSID)"] == 184, counts
    assert counts["duplicate volume record"] == 5, counts


@needs_data
def test_the_duplicates_cannot_drive_the_early_to_late_contrast():
    """Five duplicate records, none in the early era. The paper's mechanism
    cannot be an artifact of deduplication, and this is why."""
    led = {r["id"]: r for r in csv.DictReader(LEDGER.open(encoding="utf-8"))}
    docs = [r for r in csv.DictReader(FEATURES.open(encoding="utf-8"))
            if r["stratum"] == "annual_report"]
    dup_years = {int(r["year"]) for r in docs
                 if (e := led.get(r["id"])) and e["rule"] == "duplicate_repnb_volnb"}
    assert dup_years and min(dup_years) > _mod.EARLY[1], sorted(dup_years)


# --- the duplicate class is not a duplicate class -------------------------------

_adj_spec = importlib.util.spec_from_file_location(
    "companion_volume_adjudication", ROOT / "tools" / "companion_volume_adjudication.py")
_adj = importlib.util.module_from_spec(_adj_spec)
_adj_spec.loader.exec_module(_adj)


@needs_data
def test_most_of_the_duplicate_class_is_not_duplicates():
    """The frozen rule drops a record whose (repnb, volnb) key was already seen,
    which is content-blind. Four of the five it dropped carry different titles --
    two 2023 companions, a 2024 executive summary and a 2008 lending table."""
    led = list(csv.DictReader(LEDGER.open(encoding="utf-8")))
    real, companion = _adj.adjudicate(led)
    assert len(real) + len(companion) == 5
    assert len(companion) == 4, [r["display_title"][:60] for r in companion]


@needs_data
def test_restoring_the_companions_softens_but_does_not_reverse_the_headline():
    """Seven percentage points, and the direction holds. If a future change made
    the two series agree, Table 3d would be reporting a difference that no longer
    exists."""
    import json
    out = ROOT / "data" / "analysis" / "companion_volume_adjudication.json"
    if not out.exists():
        pytest.skip("run tools/companion_volume_adjudication.py first")
    d = json.loads(out.read_text())
    assert d["frozen"]["pct"] < d["restored"]["pct"] < 0
    assert abs(d["restored"]["pct"] - d["frozen"]["pct"]) > 3
