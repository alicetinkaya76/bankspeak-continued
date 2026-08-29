# THIRD-EYE REVIEW PROMPT v10 (round-10)

You are the adversarial third eye for the Stage-A freeze of "Bankspeak,
Continued". Round-9 verdict was REJECT with four areas; this package
answers it. Deliver a BINARY verdict: **APPROVE FOR STAGE-A TIMESTAMP**
or **REJECT WITH REQUIRED CHANGES**. Recompute everything; trust nothing.

## 1. Integrity gate (as before)
Zip sha256/bytes/entry count; SHA256SUMS and MANIFEST full verification;
freeze-field JSON cross-check; git bundle ↔ commit; requirements pins;
ruling-chain hashes (round2,3,4,7,8,9 — round6 remains a declared pending
textual item); logs; environment; calibration.

## 2. Independent execution (pinned env)
`python -m pytest tests/ -q` → expect **141 passed** (116 + 25 round-9
regressions). `python src/bootstrap_engine.py --selftest` → five lines,
bit-identical to logs/selftest.log. `make smoke` → see §4.

## 3. Round-9 probes — verify each FLIPS (11/11 were reproduced pre-repair)
| Round-9 probe | Now expected | Regression test |
|---|---|---|
| UTF-16 transport ≠ archive bytes | byte-identical, hook pre-parse | test_utf16_transport_archived_byte_identical |
| malformed body lost before archive | archived, then parse error propagates | test_malformed_body_archived_before_parse_failure |
| `{}` schemaless → zero-record success | RAISES | test_schemaless_payload_raises |
| total 3→1 drift silent | RAISES | test_declared_total_drift_raises |
| rerun overwrites raw file | write-once RAISES, bytes intact | test_rerun_raw_archive_write_once |
| anchor-free interstitial = terminal | interstitial marker RAISES | test_sproll_interstitial_marker_raises |
| unmarked blank page = terminal | positive marker required | test_sproll_unmarked_blank_page_raises |
| probe_sha256 format-only | artifact hash RECOMPUTED; required | test_docty_probe_hash_recomputed / _required |
| P2-invariant calibration | pooled family null; P2 inputs bind | test_p1p2_calibration_binds_p2_inputs |
| unbound reuse opens Wald in p0 | binding mismatch REFUSED | test_cross_family_reuse_refused |
| banner claims wald then refuses | engine resolved before single banner | test_engine_banner_tells_truth_when_refusing |
Also: template extra-years / non-positive tokens abort; event-study
failure propagation (test_event_study_*); packager junk/pilot-B/
single-key-ruling/bundle/provenance (test_stage_calibration_*,
test_required_ruling_chain_enforced, test_env_runs_crosscheck,
test_freeze_requires_bundle_flagpair). Old-commit check: the 25 new
tests on 7fb89a5 should fail except the behavior-preservation ones
(test_sproll_positive_terminal_ok, test_event_study_healthy_still_ok,
and the step-down semantics test).

## 4. DECLARED smoke-signature change (C25)
Family pooling changes ONLY the smoke calibrate block: crit_abs_z =
crit_abs_z_half ≈ 5.8208103823388075 (relative platform band ≤ 1e-12),
boot_size_at_null = 0.1, wald_boot_concordance = 0.8, calibration_ok =
false, plus family/binding fields. The smoke curve decision and
`family MDE80 = 0.9` are UNCHANGED; the selftest is untouched.

## 5. Evidence provenance (C23)
`evidence/environment.json` must carry `runs[]`; verify each staged log's
sha256 equals a zero-exit recorded run, and `evidence/calibration.json`
is production-shaped (ncal=200, B=9999, strict types, binding block) with
`binding.git_commit` EQUAL to the packaged commit. calibration_ok=false
is a legitimate outcome: it permanently refuses the Wald shortcut and
production runs full nested PASS-P.

## 6. Report
Amendment table C10, C13→C20, C14→C21, C15→C22, C16, C17→C23, C18→C24,
C19, C25; list any remaining blockers with reproducible probes.
