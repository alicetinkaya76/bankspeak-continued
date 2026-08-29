"""Audit packaging (v2, round-6/round-7 upgrade).

v1 (round-5) staged the file set, wrote SHA256SUMS and ran the s11
regeneration check. v2 adds, per round-6 blocker 9 and the round-7 gate:
 - MANIFEST.tsv is actually written (path, bytes, sha256; the v1 docstring
   promised it and the code did not deliver -- doc-code mismatch fixed);
 - junk exclusion: .DS_Store, __pycache__/, *.pyc never enter the package
   (deliberate audit artifacts like *.bak-round4 are KEPT);
 - the environment is declared by the recovered scaffold pin files
   requirements.txt / requirements-ppl.txt (on the include list and hashed
   into the freeze fields); a transitive pip-freeze lock
   (requirements.lock.txt) is hashed additionally when present;
 - --freeze-fields OUT.json emits the Stage-A freeze-record v2
   archive-binding fields: zip sha256 + byte size + entry count, SHA256SUMS
   and MANIFEST digests, .python-version content + hash, dependency-lock
   hash, git commit, hashes of supplied test/selftest/calibration logs
   (--log name=path, repeatable) and of the round-ruling artifact (--ruling).

Usage:
    python tools/build_audit_package.py --out round7_package.zip \
        [--freeze-fields freeze_fields.json] [--log tests=pytest.log] \
        [--log selftest=selftest.log] [--ruling docs/ROUND6_RULING.md]
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["config", "src", "tests", "tools", "docs",
           "data/analysis", "data/features",
           "Makefile", "requirements.txt", "requirements-ppl.txt",
           ".python-version"]
META = ["ar_unit_qc.csv", "extraction_log.csv", "extraction_log_v2.csv",
        "ar_assembly_log.csv", "frozen_sampling_v1.csv",
        "download_failures.csv", "manifest.tsv"]   # data/meta manifest: REQUIRED
EXCLUDE_NAMES = {".DS_Store"}
EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_SUFFIXES = {".pyc"}


def _keep(p: Path) -> bool:
    if p.name in EXCLUDE_NAMES or p.suffix in EXCLUDE_SUFFIXES:
        return False
    return not any(part in EXCLUDE_DIRS for part in p.parts)


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stage_tree(root: Path, stage: Path) -> None:
    if stage.exists():
        shutil.rmtree(stage)
    for rel in INCLUDE:
        src = root / rel
        if not src.exists():
            print(f"[pkg] skip missing {rel}")
            continue
        dst = stage / rel
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                *EXCLUDE_NAMES, *EXCLUDE_DIRS, "*.pyc"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for f in META:
        src = root / "data" / "meta" / f
        if not src.exists():
            sys.exit(f"[pkg] ABORT -- required data/meta/{f} missing "
                     f"(round-4: s11 needs manifest.tsv)")
        dst = stage / "data" / "meta" / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def regeneration_check(stage: Path, runner=subprocess.run) -> None:
    """Round-7 editor blocker: a freeze builder FAILS CLOSED — a failed
    regeneration aborts packaging instead of degrading to a warning."""
    print("[pkg] regeneration check: python src/s11_paper_artifacts.py --check")
    try:
        runner([sys.executable, "src/s11_paper_artifacts.py"],
               cwd=stage, check=True, timeout=600)
    except Exception as e:
        sys.exit(f"[pkg] ABORT -- regeneration check failed: {e}")


def validate_and_stage_env(stage: Path, env_path: Path, root: Path) -> Path:
    """Round-8: machine-readable proof of the EXACT runtime. Validates the
    capture_env.py record against .python-version and every parseable pin in
    requirements.txt, then stages it to evidence/environment.json."""
    if not env_path.exists():
        sys.exit(f"[pkg] ABORT -- --env {env_path}: file missing")
    try:
        env = json.loads(env_path.read_text())
    except Exception as e:
        sys.exit(f"[pkg] ABORT -- --env is not valid JSON: {e}")
    want_py = (root / ".python-version").read_text().strip()
    got_py = str(env.get("python_version", ""))
    if got_py != want_py:
        sys.exit(f"[pkg] ABORT -- environment python_version {got_py!r} != "
                 f"declared {want_py!r}")
    pins = {}
    for line in (root / "requirements.txt").read_text().splitlines():
        line = line.strip()
        if "==" in line and not line.startswith("#"):
            name, ver = line.split("==", 1)
            pins[name.strip().lower()] = ver.strip()
    pkgs = {str(k).lower(): str(v)
            for k, v in (env.get("packages") or {}).items()}
    bad = [f"{n} (env {pkgs.get(n)!r} != pin {v!r})"
           for n, v in pins.items() if n in pkgs and pkgs[n] != v]
    missing = [n for n in pins if n not in pkgs]
    if bad or missing:
        sys.exit("[pkg] ABORT -- environment/pin mismatch: "
                 + "; ".join(bad + [f"{m} absent from env record"
                                    for m in missing]))
    runs = env.get("runs")
    if not (isinstance(runs, list) and runs):
        sys.exit("[pkg] ABORT -- environment record carries no execution "
                 "provenance (runs[]); produce it with tools/"
                 "run_evidence.py so the logs are bound to the recorded "
                 "session (round-9)")
    for r in runs:
        for k in ("command", "exit_code", "log_sha256", "started_utc",
                  "ended_utc"):
            if k not in r:
                sys.exit(f"[pkg] ABORT -- environment runs[] entry lacks "
                         f"{k!r}")
    ev = stage / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    dst = ev / "environment.json"
    shutil.copy2(env_path, dst)
    return dst


PRODUCTION_NCAL = 200
PRODUCTION_B = 9999
CAL_BINDING_KEYS = ("family", "years", "alpha", "rho", "sigma_delta",
                    "companion", "seed", "p2_start_year", "base_rates",
                    "templates", "tokens_per_doc", "git_commit")


def _num(x):
    """Round-10: a number is finite by definition here — NaN/Inf are
    forgeries, not values."""
    import math
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))


def stage_calibration(stage: Path, cal_path: Path) -> Path:
    """Round-9 (C23): the packaged calibration must BE the prespecified
    production calibration — strictly typed, at the preregistered sizes,
    and bound to its decision inputs. Anything else aborts."""
    if not cal_path.exists():
        sys.exit(f"[pkg] ABORT -- --calibration {cal_path}: file missing")
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from calib_schema import (validate_calibration,
                              reject_nonstandard_constants)
    try:
        cal = json.loads(cal_path.read_text(),
                         parse_constant=reject_nonstandard_constants)
    except Exception as e:
        sys.exit(f"[pkg] ABORT -- calibration is not valid strict JSON: "
                 f"{e}")
    schema_errs = validate_calibration(cal)
    if schema_errs:
        sys.exit("[pkg] ABORT -- calibration schema (round-11): "
                 + "; ".join(schema_errs))
    errs = []
    if cal.get("ncal") != PRODUCTION_NCAL:
        errs.append(f"ncal={cal.get('ncal')!r} != preregistered "
                    f"{PRODUCTION_NCAL}")
    if cal.get("B") != PRODUCTION_B:
        errs.append(f"B={cal.get('B')!r} != preregistered {PRODUCTION_B} "
                    "(a pilot calibration is not freeze evidence)")
    if errs:
        sys.exit("[pkg] ABORT -- calibration rejected: " + "; ".join(errs))
    ev = stage / "evidence"
    ev.mkdir(parents=True, exist_ok=True)
    dst = ev / "calibration.json"
    shutil.copy2(cal_path, dst)
    return dst


MANDATORY_FREEZE_FIELDS = [
    "zip_sha256", "zip_bytes", "zip_entry_count", "sha256sums_entries",
    "manifest_rows", "sha256sums_sha256", "manifest_sha256",
    "python_version", "python_version_sha256", "requirements_sha256",
    "requirements_ppl_sha256", "git_commit", "environment_sha256",
    "calibration_sha256",
]


REQUIRED_RULINGS = ("round2", "round3", "round4", "round7", "round8",
                    "round9", "round10", "round11", "round12", "round13")


def enforce_freeze_completeness(ff: dict) -> None:
    """Round-8/9: null mandatory fields ABORT instead of warning
    (requirements_lock_sha256 remains the one declared-optional field);
    the ruling chain must cover every available round (C19/C23) and the
    git bundle is mandatory freeze evidence."""
    nulls = [k for k in MANDATORY_FREEZE_FIELDS if not ff.get(k)]
    if not (ff.get("logs") or {}).get("tests"):
        nulls.append("logs.tests")
    if not (ff.get("logs") or {}).get("selftest"):
        nulls.append("logs.selftest")
    if not (ff.get("logs") or {}).get("smoke"):
        nulls.append("logs.smoke (round-10: smoke is bound evidence)")
    rl = ff.get("rulings") or {}
    miss = [k for k in REQUIRED_RULINGS if not rl.get(k)]
    if miss:
        nulls.append(f"rulings[{','.join(miss)}]")
    if not ff.get("git_bundle_sha256"):
        nulls.append("git_bundle_sha256 (bundle is mandatory freeze "
                     "evidence)")
    if nulls:
        sys.exit("[pkg] ABORT -- freeze fields incomplete (null/missing): "
                 + ", ".join(nulls))


def crosscheck_calibration_run(env_staged: Path, cal_staged: Path) -> None:
    """Round-10 (C26): the staged calibration must be the byte-exact
    artifact of a zero-exit calibrate step recorded in the environment's
    execution provenance."""
    env = json.loads(env_staged.read_text())
    cal_sha = _sha256(cal_staged)
    ok = any(r.get("artifact_sha256") == cal_sha and r.get("exit_code") == 0
             for r in env.get("runs", []))
    if not ok:
        sys.exit("[pkg] ABORT -- the staged calibration is not bound to "
                 "any zero-exit calibrate run in the environment record; "
                 "regenerate evidence with tools/run_evidence.py")


def crosscheck_env_runs(env_staged: Path, ff_logs: dict) -> None:
    """Round-9 (C23): every staged log must be the byte-exact product of a
    zero-exit run recorded in the environment's execution provenance."""
    env = json.loads(env_staged.read_text())
    ok_hashes = {r.get("log_sha256") for r in env.get("runs", [])
                 if r.get("exit_code") == 0}
    bad = [name for name, h in (ff_logs or {}).items() if h not in ok_hashes]
    if bad:
        sys.exit("[pkg] ABORT -- log(s) "
                 + ", ".join(bad)
                 + " are not bound to any zero-exit run in the environment "
                   "record; regenerate evidence with tools/run_evidence.py")


def copy_evidence(stage: Path, logs: dict, rulings: dict, root: Path,
                  git_bundle: bool = False, runner=subprocess.run) -> dict:
    """Round-7 editor blocker: the claimed evidence must be verifiable from
    INSIDE the package. Copies every referenced log to evidence/{name}.log
    and every round ruling to evidence/rulings/{name}.md BEFORE the manifest
    is written (so they are hashed into MANIFEST/SHA256SUMS/zip), and
    optionally creates evidence/repo.bundle (git bundle --all) so the
    recorded commit is independently retrievable. Missing paths abort."""
    ev = stage / "evidence"
    staged_logs, staged_rulings, bundle = {}, {}, None
    for name, p in (logs or {}).items():
        if not Path(p).exists():
            sys.exit(f"[pkg] ABORT -- --log {name}={p}: file missing")
        ev.mkdir(parents=True, exist_ok=True)
        dst = ev / f"{name}.log"
        shutil.copy2(p, dst); staged_logs[name] = dst
    for name, p in (rulings or {}).items():
        if not Path(p).exists():
            sys.exit(f"[pkg] ABORT -- --ruling {name}={p}: file missing")
        (ev / "rulings").mkdir(parents=True, exist_ok=True)
        dst = ev / "rulings" / f"{name}.md"
        shutil.copy2(p, dst); staged_rulings[name] = dst
    if git_bundle:
        ev.mkdir(parents=True, exist_ok=True)
        bundle = ev / "repo.bundle"
        try:
            runner(["git", "bundle", "create", str(bundle), "--all"],
                   cwd=root, check=True, timeout=300)
        except Exception as e:
            sys.exit(f"[pkg] ABORT -- git bundle failed: {e}")
    return {"logs": staged_logs, "rulings": staged_rulings, "bundle": bundle}


def require_clean_tree(root: Path, allow_dirty: bool,
                       runner=subprocess.run) -> None:
    """Freeze-fields runs demand a clean, committed working tree. Round-8:
    a git failure is itself a FAILURE — never silently treated as clean."""
    try:
        r = runner(["git", "status", "--porcelain"], cwd=root,
                   capture_output=True, text=True, timeout=10)
    except Exception as e:
        sys.exit(f"[pkg] ABORT -- git status could not be executed ({e}); "
                 "a freeze run cannot proceed without a verifiable tree")
    if r.returncode != 0:
        sys.exit("[pkg] ABORT -- git status failed (exit "
                 f"{r.returncode}); refusing to assume a clean tree")
    if r.stdout.strip() and not allow_dirty:
        sys.exit("[pkg] ABORT -- working tree not clean; commit first "
                 "(freeze runs must never be dirty)")


def write_manifest_and_sums(stage: Path):
    files = sorted(p for p in stage.rglob("*") if p.is_file() and _keep(p))
    man = stage / "MANIFEST.tsv"
    with open(man, "w") as fh:
        fh.write("path\tbytes\tsha256\n")
        for p in files:
            fh.write(f"{p.relative_to(stage)}\t{p.stat().st_size}\t"
                     f"{_sha256(p)}\n")
    sums = stage / "SHA256SUMS"
    with open(sums, "w") as fh:
        for p in files + [man]:
            fh.write(f"{_sha256(p)}  {p.relative_to(stage)}\n")
    return man, sums


def zip_stage(stage: Path, out: Path) -> int:
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(stage.rglob("*")):
            if p.is_file() and _keep(p):
                z.write(p, p.relative_to(stage))
                n += 1
    return n


def _git_commit(root: Path):
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                           capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def freeze_fields(zip_path: Path, sums_path: Path, manifest_path: Path,
                  entry_count: int, root: Path, logs=None, rulings=None,
                  bundle=None) -> dict:
    """Stage-A freeze-record archive-binding fields, v3 (round-7): logs and
    rulings are hashed from their in-package evidence/ copies; disambiguated
    zip_entry_count / sha256sums_entries / manifest_rows; optional
    git_bundle_sha256 makes the commit independently verifiable."""
    pv = root / ".python-version"
    req = root / "requirements.txt"
    reqp = root / "requirements-ppl.txt"
    lock = root / "requirements.lock.txt"
    out = {
        "zip_sha256": _sha256(zip_path),
        "zip_bytes": zip_path.stat().st_size,
        "zip_entry_count": entry_count,
        "sha256sums_entries": sum(1 for _ in open(sums_path)),
        "manifest_rows": sum(1 for _ in open(manifest_path)) - 1,
        "sha256sums_sha256": _sha256(sums_path),
        "manifest_sha256": _sha256(manifest_path),
        "python_version": (pv.read_text().strip() if pv.exists() else None),
        "python_version_sha256": (_sha256(pv) if pv.exists() else None),
        "requirements_sha256": (_sha256(req) if req.exists() else None),
        "requirements_ppl_sha256": (_sha256(reqp) if reqp.exists() else None),
        "requirements_lock_sha256": (_sha256(lock) if lock.exists() else None),
        "git_commit": _git_commit(root),
        "logs": {name: _sha256(p) for name, p in (logs or {}).items()},
        "rulings": {name: _sha256(p) for name, p in (rulings or {}).items()},
        "git_bundle_sha256": (_sha256(bundle) if bundle else None),
        "built_utc": datetime.datetime.now(datetime.timezone.utc)
                     .isoformat(timespec="seconds"),
    }
    missing = [k for k in ("requirements_sha256", "git_commit")
               if out[k] is None]
    if missing:
        print(f"[pkg] freeze-fields WARNING: null fields {missing} -- the "
              f"freeze record cannot be finalized until these exist")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--freeze-fields",
                    help="write the freeze-record v2 archive-binding fields "
                         "to this JSON path")
    ap.add_argument("--log", action="append", default=[], metavar="NAME=PATH",
                    help="machine-readable log to hash into the freeze "
                         "fields (repeatable), e.g. --log tests=pytest.log")
    ap.add_argument("--ruling", action="append", default=[],
                    metavar="NAME=PATH",
                    help="round-ruling artifact copied into evidence/rulings "
                         "and hashed (repeatable), e.g. "
                         "--ruling round7=docs/ROUND7_THIRD_EYE_REVIEW.md")
    ap.add_argument("--git-bundle", action="store_true",
                    help="embed evidence/repo.bundle (git bundle --all) so "
                         "the recorded commit is independently verifiable")
    ap.add_argument("--allow-dirty", action="store_true",
                    help="skip the clean-tree gate (FORBIDDEN with "
                         "--freeze-fields)")
    ap.add_argument("--env", help="machine-readable environment record from "
                                  "tools/capture_env.py; validated against "
                                  ".python-version and requirements.txt, "
                                  "copied to evidence/environment.json "
                                  "(REQUIRED with --freeze-fields)")
    ap.add_argument("--calibration", help="accepted MDE calibration JSON; "
                                          "copied to evidence/"
                                          "calibration.json (REQUIRED with "
                                          "--freeze-fields)")
    a = ap.parse_args()
    logs, rulings = {}, {}
    for item in a.log:
        name, _, path = item.partition("=")
        logs[name] = Path(path)
    for item in a.ruling:
        name, _, path = item.partition("=")
        rulings[name] = Path(path)
    if a.freeze_fields and a.allow_dirty:
        sys.exit("[pkg] ABORT -- --freeze-fields and --allow-dirty are "
                 "mutually exclusive (round-8): freeze evidence may never "
                 "be built from a dirty tree")
    if a.freeze_fields and not a.git_bundle:
        sys.exit("[pkg] ABORT -- --freeze-fields requires --git-bundle "
                 "(round-9): the bundle is mandatory freeze evidence")
    if a.freeze_fields:
        require_clean_tree(ROOT, a.allow_dirty)
    stage = ROOT / "_pkg_stage"
    stage_tree(ROOT, stage)
    regeneration_check(stage)
    ev = copy_evidence(stage, logs, rulings, ROOT, a.git_bundle)
    env_staged = cal_staged = None
    if a.env:
        env_staged = validate_and_stage_env(stage, Path(a.env), ROOT)
    if a.calibration:
        cal_staged = stage_calibration(stage, Path(a.calibration))
    man, sums = write_manifest_and_sums(stage)
    out = Path(a.out)
    n = zip_stage(stage, out)
    print(f"[pkg] wrote {a.out} ({n} files)")
    if a.freeze_fields:
        ff = freeze_fields(out, sums, man, n, ROOT, ev["logs"],
                           ev["rulings"], ev["bundle"])
        ff["environment_sha256"] = _sha256(env_staged) if env_staged else None
        ff["calibration_sha256"] = _sha256(cal_staged) if cal_staged else None
        enforce_freeze_completeness(ff)
        crosscheck_env_runs(env_staged, ff.get("logs") or {})
        crosscheck_calibration_run(env_staged, cal_staged)
        cal_doc = json.loads(cal_staged.read_text())
        cal_commit = (cal_doc.get("binding") or {}).get("git_commit")
        if cal_commit != ff.get("git_commit"):
            sys.exit(f"[pkg] ABORT -- calibration binding commit "
                     f"{str(cal_commit)[:12]!r} != packaged commit "
                     f"{str(ff.get('git_commit'))[:12]!r}; the production "
                     "calibration must be generated at the packaged HEAD "
                     "(evidence outputs are .gitignored so the tree stays "
                     "clean)")
        Path(a.freeze_fields).write_text(json.dumps(ff, indent=2))
        print(f"[pkg] freeze fields -> {a.freeze_fields}")
    shutil.rmtree(stage)


if __name__ == "__main__":
    main()
