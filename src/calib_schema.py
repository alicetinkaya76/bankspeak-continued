"""Round-11 (C31): ONE recursive strict schema for calibration artifacts,
shared by the runtime (mde_sim curve licensing) and the packager. Every
rule here is a freeze rule: violations return human-readable errors and
the caller fails closed.

Strictness contract:
- integers are REAL JSON integers (bool and float forms rejected);
- every number is finite (NaN/Infinity never validate);
- the year vector is unique and strictly increasing;
- enums are closed sets; key sets are EXACT (unknown decision-bearing
  fields are rejected);
- template identities have an exact inner shape.
"""
import math

TOP_KEYS = {"crit_abs_z", "crit_abs_z_half", "boot_size_at_null",
            "wald_boot_concordance", "calibration_ok", "ncal", "B",
            "sigma_delta", "family", "binding"}
BINDING_KEYS = {"family", "years", "alpha", "rho", "sigma_delta",
                "companion", "seed", "p2_start_year", "base_rates",
                "templates", "tokens_per_doc", "git_commit"}
RATE_KEYS = {"shared", "imf", "p1", "p2", "p0"}
TPL_KEYS = {"shared", "imf", "p1", "p2", "p0"}
FAMILIES = {"p0", "p1p2"}
COMPANIONS = {"zero", "half", "full"}
_HEX = set("0123456789abcdef")


def _is_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def _is_fin(x):
    return (isinstance(x, (int, float)) and not isinstance(x, bool)
            and math.isfinite(x))


def _tpl_ok(v):
    if v is None:
        return True
    if not isinstance(v, dict) or len(v) != 1:
        return False
    if "sha256" in v:
        h = v["sha256"]
        return (isinstance(h, str) and len(h) == 64
                and set(h) <= _HEX)
    if "flat_tokens_per_year" in v:
        t = v["flat_tokens_per_year"]
        return _is_fin(t) and t > 0
    return False


def validate_calibration(cal) -> list[str]:
    """Return a list of violations; empty means the artifact validates."""
    errs = []
    if not isinstance(cal, dict):
        return ["calibration artifact is not a JSON object"]
    extra = set(cal) - TOP_KEYS
    if extra:
        errs.append(f"unknown top-level field(s): {sorted(extra)}")
    for k in ("crit_abs_z", "crit_abs_z_half", "sigma_delta"):
        if not (_is_fin(cal.get(k)) and cal[k] > 0):
            errs.append(f"{k} must be a finite number > 0")
    for k in ("boot_size_at_null", "wald_boot_concordance"):
        if not (_is_fin(cal.get(k)) and 0.0 <= cal[k] <= 1.0):
            errs.append(f"{k} must be a finite number in [0,1]")
    if not isinstance(cal.get("calibration_ok"), bool):
        errs.append("calibration_ok must be a strict JSON boolean")
    for k in ("ncal", "B"):
        if not (_is_int(cal.get(k)) and cal[k] > 0):
            errs.append(f"{k} must be a REAL positive JSON integer "
                        "(float/bool forms rejected)")
    if cal.get("family") not in FAMILIES:
        errs.append(f"family must be one of {sorted(FAMILIES)}")
    b = cal.get("binding")
    if not isinstance(b, dict):
        errs.append("binding block missing or not an object")
        return errs
    missing = BINDING_KEYS - set(b)
    extra_b = set(b) - BINDING_KEYS
    if missing:
        errs.append(f"binding lacks {sorted(missing)}")
    if extra_b:
        errs.append(f"binding carries unknown field(s): {sorted(extra_b)}")
    if missing or extra_b:
        return errs
    if b["family"] not in FAMILIES:
        errs.append(f"binding.family must be one of {sorted(FAMILIES)}")
    ys = b["years"]
    if not (isinstance(ys, list) and len(ys) >= 2
            and all(_is_int(y) for y in ys)
            and all(ys[i] < ys[i + 1] for i in range(len(ys) - 1))):
        errs.append("binding.years must be a list of >=2 REAL integers, "
                    "unique and strictly increasing")
    for k in ("alpha", "rho", "sigma_delta"):
        if not _is_fin(b.get(k)):
            errs.append(f"binding.{k} must be a finite number")
    if _is_fin(b.get("alpha")) and not (0.0 < b["alpha"] < 1.0):
        errs.append("binding.alpha must lie in (0,1)")
    if _is_fin(b.get("rho")) and not (0.0 <= b["rho"] <= 1.0):
        errs.append("binding.rho must lie in [0,1]")
    if not _is_int(b.get("seed")):
        errs.append("binding.seed must be a REAL integer")
    if not (b.get("p2_start_year") is None or _is_int(b["p2_start_year"])):
        errs.append("binding.p2_start_year must be an integer or null")
    if b.get("companion") not in COMPANIONS:
        errs.append(f"binding.companion must be one of "
                    f"{sorted(COMPANIONS)}")
    br = b.get("base_rates")
    if not (isinstance(br, dict) and set(br) == RATE_KEYS
            and all(v is None or _is_fin(v) for v in br.values())):
        errs.append("binding.base_rates must map EXACTLY "
                    f"{sorted(RATE_KEYS)} to finite numbers or null")
    tp = b.get("templates")
    if not (isinstance(tp, dict) and set(tp) == TPL_KEYS
            and all(_tpl_ok(v) for v in tp.values())):
        errs.append("binding.templates must map EXACTLY "
                    f"{sorted(TPL_KEYS)} to null, {{sha256: 64-hex}} or "
                    "{flat_tokens_per_year: finite>0}")
    t = b.get("tokens_per_doc")
    if not (t is None or (_is_fin(t) and t > 0)):
        errs.append("binding.tokens_per_doc must be a finite number > 0 "
                    "or null")
    gc = b.get("git_commit")
    if not (isinstance(gc, str) and gc):
        errs.append("binding.git_commit must be a non-empty string")
    return errs


def reject_nonstandard_constants(s):
    """json.loads parse_constant hook: NaN/Infinity/-Infinity are never
    valid in a freeze artifact."""
    raise ValueError(f"nonstandard JSON constant {s!r} rejected "
                     "(round-11 freeze rule)")
