# Third-eye review instructions — Round 9 (post round-8 repair sprint)

Same auditor, same recompute-don't-trust standard, same BINARY ruling:
APPROVE FOR STAGE-A TIMESTAMPING or REJECT WITH REQUIRED CHANGES. Round 8
returned five blocking areas; this package claims to close all five with
regression tests that FAIL on the reviewed commit 56c972d.

## 0) Integrity (as round 8, plus)
Recompute zip identity against the freeze JSON; verify evidence/*.log,
evidence/rulings/*, evidence/repo.bundle as before. NEW mandatory evidence:
evidence/environment.json (machine-readable runtime record — check
python_version and every pin against .python-version / requirements.txt) and
evidence/calibration.json (the accepted calibration artifact; verify
calibration_sha256). The freeze JSON now aborts on null mandatory fields —
confirm none are null.

## 1) Verify your five round-8 probes now FAIL to reproduce
 (1) Acquisition: HTTP-500 SPROLL page, empty first page, anchors-without-
     rows page, and max-page exhaustion all RAISE (test_sproll_*); a
     legitimate anchor-free terminal page still works. WB raw archives are
     byte-verbatim transport bodies (rerun your re-serialization check);
     declared-total mismatch RAISES (test_fetch_declared_total_mismatch_
     raises). {} and probe-less docty JSONs are rejected
     (test_docty_schema_*).
 (2) MDE: rerun your IMF-invariance probe — changing --template-imf /
     --base-rate-imf MUST change the {P1,P2} outputs
     (test_imf_rate_changes_p1p2_simulation); defaults reproduce legacy
     draws exactly (test_imf_defaults_reproduce_legacy_draws; smoke
     unchanged). Missing template years RAISE. Rerun your crit_abs_z probe:
     the calibrated critical values now GOVERN Wald decisions and a
     calibration lacking crit_abs_z_half refuses the shortcut
     (test_calibrated_wald_crit_governs).
 (3) Event study: rerun your [1994..2025]-minus-{2002..2004} probe — the
     empty bin merges forward, every bin holds observations, and no
     near-zero-width interval appears (test_make_bins_interior_gap_merges_
     forward, test_event_study_interior_gap_estimable); all-zero and
     rank-deficient designs RAISE in passe_multi.
 (4) Standardization: every return path carries the full diagnostic set and
     a `failures` list; your masking construction now reports BOTH the zero
     post cell (primary, frozen order) and the support failure
     (test_std_simultaneous_failures_not_masked).
 (5) Packager: git-status failure aborts; --freeze-fields with
     --allow-dirty aborts; null mandatory freeze fields abort; environment
     and calibration evidence are validated and staged (test_git_status_
     failure_aborts, test_freeze_completeness_enforced, test_env_validation,
     test_calibration_staged_and_checked).

## 2) Rule on the amendments
PREREG_v0.7_AMENDMENTS.md (C13–C19) + STAGE_A_FREEZE_RECORD_v3.md (the
Stage-A object definition you required). C10 remains as you accepted it.

## 3) Runtime
python -m pytest tests/ -q (expect 116 passed), the five frozen selftest
lines bit-identical, make smoke unchanged. evidence/environment.json must
show Python 3.11.9 with the declared pins — this closes the pinned-stack
evidence obligation; state explicitly in your report whether you accept it.

## 4) Ruling
Binary, with ranked required changes if REJECT. The permitted-changes
boundary of your round-7/8 editor sections is unchanged.
