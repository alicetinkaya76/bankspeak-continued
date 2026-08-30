"""Pin the safety properties of the evidence-deposit uploader.

The token is the author's: it goes in `.env`, the script reads it, and nothing
else. These tests hold that shape in place, because the failure modes are quiet
ones — a secret in a URL ends up in a server log, and a publish that happens by
default cannot be undone.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "upload_evidence_deposit.py"
SRC = TOOL.read_text(encoding="utf-8")


def test_it_refuses_and_explains_when_no_token_is_configured():
    env = {k: v for k, v in os.environ.items() if "ZENODO" not in k}
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True,
                       text=True, env=env, timeout=120)
    assert r.returncode != 0
    out = r.stdout + r.stderr
    assert "no ZENODO_TOKEN" in out
    assert "never prints it" in out


def test_the_token_travels_in_a_header_and_never_in_a_url():
    """A bearer header stays out of server logs and error messages; a query
    parameter does not. Zenodo's API accepts both, so this is a choice."""
    assert "Bearer {tok}" in SRC or 'f"Bearer {tok}"' in SRC
    for bad in ("access_token=", "?token=", "&token="):
        assert bad not in SRC, f"the token would appear in a URL via {bad!r}"


def test_the_token_is_never_printed_or_written():
    """No print/write of the token variable, however it is spelled."""
    for line in SRC.splitlines():
        s = line.strip()
        if s.startswith("#") or s.startswith('"'):
            continue
        if ("print(" in s or "write_text(" in s or "sys.stdout" in s):
            assert "tok" not in s.replace("token(", "").replace("ZENODO_TOKEN", ""), s


def test_publishing_is_opt_in():
    """A published Zenodo record cannot be deleted, only superseded. The
    irreversible step must never be the default."""
    assert '"--publish", action="store_true"' in SRC
    assert "if not a.publish:" in SRC
    assert "NOT published" in SRC


def test_a_checksum_mismatch_refuses_instead_of_publishing():
    assert "REFUSING" in SRC and "checksum" in SRC


def test_sandbox_is_available_so_the_real_record_can_be_rehearsed():
    assert "sandbox.zenodo.org" in SRC
    assert '"--sandbox", action="store_true"' in SRC


def test_dot_env_is_gitignored():
    """The uploader tells the author to put a secret in .env. Until this was
    written, .gitignore did not cover it."""
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in [l.strip() for l in ignore]
