"""Pin the PLOS ONE submission limits that the manuscript has to satisfy.

The abstract limit is the one that matters. It was 374 words against a stated
300 and nothing in the repository would have noticed, because until now nothing
measured it. Two tests, therefore: the manuscript passes, and the checker can
still fail. A compliance tool that cannot fail is a compliance tool that is not
being run.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "plos_compliance.py"
PAPER = ROOT / "docs" / "PAPER_DRAFT_v2.md"


def mutate_abstract(text: str, addition: str) -> str:
    """Append to the ABSTRACT, not to the first thing that looks like one.

    The manuscript opens with a preregistration note closed by its own `---`
    rule, so splitting on the first rule lands in the header and the padding
    never reaches the abstract at all. The first version of these two tests did
    that and then read the tool's clean verdict as the tool failing to notice —
    a broken negative control, which is worse than no negative control, because
    it makes an unexercised checker look exercised.
    """
    m = re.search(r"(^## Abstract\n.*?)(\n---\n)", text, re.S | re.M)
    assert m, "no abstract block"
    return text[:m.end(1)] + addition + text[m.end(1):]


def run(*args):
    return subprocess.run([sys.executable, str(TOOL), *args],
                          capture_output=True, text=True, timeout=120)


def test_manuscript_has_no_blockers_at_initial_submission():
    r = run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 blocker(s)" in r.stdout


def test_abstract_is_within_the_three_hundred_word_limit():
    r = run()
    line = next(l for l in r.stdout.splitlines() if "abstract" in l and "words" in l)
    n = int(line.split("abstract")[1].split("words")[0].strip())
    assert n <= 300, line


def test_checker_fails_on_an_over_length_abstract(tmp_path):
    """The guard on the guard. Pad the abstract past the limit and the tool must
    report a blocker; if it still passes, the passing result above means nothing.
    """
    fake = tmp_path / "over.md"
    fake.write_text(mutate_abstract(PAPER.read_text(encoding="utf-8"),
                                    " padding" * 120), encoding="utf-8")
    r = run(str(fake))
    assert r.returncode == 1, r.stdout
    assert "BLOCKER" in r.stdout


def test_checker_fails_on_a_citation_in_the_abstract(tmp_path):
    fake = tmp_path / "cited.md"
    fake.write_text(mutate_abstract(PAPER.read_text(encoding="utf-8"), " (2015)"),
                    encoding="utf-8")
    r = run(str(fake))
    assert r.returncode == 1, r.stdout
    assert "abstract citations: ['(2015)']" in r.stdout
