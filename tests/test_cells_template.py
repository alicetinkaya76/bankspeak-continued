import sys
from pathlib import Path
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from make_cells_template import build_template

def test_template_projects_docs_times_tpd():
    frame = pd.DataFrame({"year": [2019, 2019, 2021], "id": ["a", "b", "c"]})
    t = build_template(frame, tokens_per_doc=1000.0)
    assert t["year"].tolist() == [2019, 2021]
    assert t["docs"].tolist() == [2, 1]
    assert t["tokens"].tolist() == [2000.0, 1000.0]

def test_template_rejects_nonpositive_tpd():
    with pytest.raises(ValueError):
        build_template(pd.DataFrame({"year": [2020]}), 0.0)
