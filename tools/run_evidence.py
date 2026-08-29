"""Round-9 (C23): execution provenance. Runs the evidence commands INSIDE
the pinned venv, captures each command's exit code, timing and log hash,
and writes a single machine-readable environment record binding the runtime
to the exact logs the packager will stage. Usage:

    python tools/run_evidence.py environment.json

writes pytest.log, selftest.log and environment.json in the CWD."""
import datetime
import hashlib
import json
import platform
import subprocess
import sys
from importlib import metadata

PKGS = ["numpy", "pandas", "statsmodels", "scipy", "PyYAML", "requests",
        "pytest", "matplotlib", "PyMuPDF", "tqdm"]
def build_steps(sigma_delta: str):
    """Round-10 (C26): the provenance harness covers ALL freeze evidence —
    tests, selftest, smoke AND the production calibration. The calibrate
    step also records its artifact's sha256."""
    return [
        ("pytest.log", [sys.executable, "-m", "pytest", "tests/", "-q"],
         None),
        ("selftest.log", [sys.executable, "src/bootstrap_engine.py",
                          "--selftest"], None),
        ("smoke.log", [sys.executable, "src/mde_sim.py", "--mode", "smoke",
                       "--theta-grid", "0.0:0.9:0.9",
                       "--sigma-delta", "0.1"], None),
        ("calibrate.log", [sys.executable, "src/mde_sim.py", "--mode",
                           "calibrate", "--sigma-delta", sigma_delta,
                           "--ncal", "200", "--B", "9999",
                           "--out", "calibration_pinned.json"],
         "calibration_pinned.json"),
    ]


def _utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(
        timespec="seconds")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default="environment.json")
    ap.add_argument("--sigma-delta", default="0.1",
                    help="sigma_delta for the production calibrate step "
                         "(must equal the value the production curve "
                         "will bind)")
    a = ap.parse_args()
    out = a.out
    pkgs = {}
    for name in PKGS:
        try:
            pkgs[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pkgs[name] = None
    runs, worst = [], 0
    for log_name, cmd, artifact in build_steps(a.sigma_delta):
        started = _utc()
        with open(log_name, "wb") as lf:
            r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT)
        ended = _utc()
        digest = hashlib.sha256(open(log_name, "rb").read()).hexdigest()
        rec = {"command": " ".join(cmd), "exit_code": r.returncode,
               "log_file": log_name, "log_sha256": digest,
               "started_utc": started, "ended_utc": ended}
        if artifact:
            try:
                rec["artifact"] = artifact
                rec["artifact_sha256"] = hashlib.sha256(
                    open(artifact, "rb").read()).hexdigest()
            except OSError:
                rec["artifact_sha256"] = None
        runs.append(rec)
        worst = max(worst, abs(r.returncode))
        print(f"[run] {log_name}: exit={r.returncode} sha={digest[:16]}")
    rec = {"python_version": platform.python_version(),
           "implementation": platform.python_implementation(),
           "platform": platform.platform(),
           "executable": sys.executable,
           "packages": pkgs, "runs": runs, "captured_utc": _utc()}
    with open(out, "w") as f:
        json.dump(rec, f, indent=2)
    print(f"[env] {rec['python_version']} + {len(runs)} bound run(s) "
          f"-> {out}")
    sys.exit(worst)


if __name__ == "__main__":
    main()
