import hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from families import load_families, count_families, tokens

def test_mapping_shape_and_bijection():
    cfg = load_families()
    forms = [w for ws in cfg["families"].values() for w in ws]
    assert len(cfg["families"]) == 13 and len(forms) == 28 == len(set(forms))
    assert cfg["_form2fam"]["seamlessly"] == "seamless"       # the round-3 bug case
    assert cfg["_form2fam"]["intricacies"] == "intricate"     # the v1.0 stem-split case
    assert cfg["_form2fam"]["realms"] == "realm"
    assert cfg["_form2fam"]["meticulously"] == "meticulous"

def test_stopword_hash_matches_frozen_list():
    sw = sorted(["the","of","and","to","in","a","for","on","with",
                 "is","by","as","that","at","from"])
    h = hashlib.sha256(("\n".join(sw)).encode()).hexdigest()
    assert h == load_families()["stopword_gate"]["sha256_sorted_newline"]

def test_counting_families():
    r = count_families("The seamlessly delivered report underscores pivotal reforms.")
    assert r["fam_seamless"] == 1 and r["fam_underscore"] == 1 and r["fam_pivotal"] == 1
    assert r["tier1_count"] == 3 and r["eligible_tokens"] == 7

def test_matching_rule_edges():
    assert tokens("pivotal's") == ["pivotal's"]
    assert count_families("pivotal's")["tier1_count"] == 0     # frozen: does NOT count
    assert count_families("pivotal\u00e9")["tier1_count"] == 1 # 'pivotalé' -> 'pivotal'
    assert count_families("Delve delve DELVED")["fam_delve"] == 3
    z = count_families("")
    assert z["tier1_count"] == 0 and z["eligible_tokens"] == 0

def test_optional_repo_config_consistency():
    cfgy = Path(__file__).resolve().parents[1] / "config" / "config.yaml"
    if cfgy.exists():
        from families import verify_against_repo_config
        verify_against_repo_config(cfgy)
