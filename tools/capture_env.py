"""Round-8: machine-readable runtime record. Run INSIDE the pinned venv
immediately before the evidence pytest run; pass the output to the packager
via --env. Records the exact interpreter and the installed versions of every
declared pin."""
import json, platform, sys, datetime
from importlib import metadata

PKGS = ["numpy", "pandas", "statsmodels", "scipy", "PyYAML", "requests",
        "pytest", "matplotlib", "PyMuPDF", "tqdm"]


def main() -> None:
    pkgs = {}
    for name in PKGS:
        try:
            pkgs[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            pkgs[name] = None
    rec = {"python_version": platform.python_version(),
           "implementation": platform.python_implementation(),
           "platform": platform.platform(),
           "executable": sys.executable,
           "packages": pkgs,
           "captured_utc": datetime.datetime.now(datetime.timezone.utc)
                                   .isoformat(timespec="seconds")}
    out = sys.argv[1] if len(sys.argv) > 1 else "environment.json"
    with open(out, "w") as f:
        json.dump(rec, f, indent=2)
    print(f"[env] {rec['python_version']} -> {out}")


if __name__ == "__main__":
    main()
