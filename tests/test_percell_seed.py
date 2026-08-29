import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from percell_seed import cell_seed, cell_rng

def test_deterministic_and_distinct():
    assert cell_seed("imf", "article_iv", 2001) == cell_seed("imf", "article_iv", 2001)
    assert cell_seed("imf", "article_iv", 2001) != cell_seed("imf", "article_iv", 2002)
    assert cell_seed("imf", "article_iv", 2001) != cell_seed("wb", "article_iv", 2001)

def test_isolation_from_other_cells():
    a1 = cell_rng("imf", "article_iv", 2001).sample(range(1000), 40)
    _ = cell_rng("wb", "cem", 1988).sample(range(500), 40)     # unrelated draw
    a2 = cell_rng("imf", "article_iv", 2001).sample(range(1000), 40)
    assert a1 == a2
