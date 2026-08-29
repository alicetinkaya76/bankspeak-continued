# THIRD-EYE REVIEW PROMPT v11 (round-11)

You are the adversarial third eye for the Stage-A freeze of "Bankspeak,
Continued". Round-10 verdict was REJECT with three areas (C20/C21/C23);
this package answers it. Deliver a BINARY verdict: **APPROVE FOR STAGE-A
TIMESTAMP** or **REJECT WITH REQUIRED CHANGES**. Recompute everything.

## 1. Integrity gate (as before)
Zip sha256/bytes/entries; SHA256SUMS + MANIFEST; freeze-field JSON;
bundle ↔ commit; pins; ruling chain now SEVEN entries (round2,3,4,7,8,9,
10 — round6 remains a declared pending textual item); logs now include
smoke; environment; calibration.

## 2. Independent execution (pinned env)
`python -m pytest tests/ -q` → expect **157 passed** (141 + 16 round-10
regressions). Selftest → five lines, bit-identical to logs/selftest.log.
Smoke → all NUMBERS unchanged from C25 (crit ≈ 5.8208103823388075,
relative band ≤ 1e-12; boot 0.1; concordance 0.8; ok=false; nested
engine; MDE80 = 0.9); the binding block now prints `years` as the full
integer vector (declared shape change, C27.4).

## 3. Round-10 probes — verify each FLIPS (7/7 reproduced pre-repair)
| Round-10 probe | Now expected | Regression test |
|---|---|---|
| SPROLL rerun overwrote page + truncated log | run-immutable + write-once; bytes and log survive | test_sproll_rerun_raises_and_preserves |
| request log opened in "w" | append-only, history preserved | test_sproll_log_is_append_only |
| `<a>No results found</a>` accepted as terminal | semantic anchor regex RAISES | test_sproll_bare_anchor_terminal_raises (+ newline variant) |
| duplicate id across pages met total=2 | unique-id completeness RAISES | test_duplicate_ids_across_pages_raise |
| file-based template → NameError: Path | works; binding carries template sha256 | test_file_based_template_binding_works |
| years endpoint-only; gaps unrepresentable | gap-aware parser; full vector in binding | test_years_with_calendar_gaps, test_binding_carries_full_year_vector |
| tokens_per_doc absent from binding | bound; doubled exposure ≠ same identity | test_tokens_per_doc_enters_binding |
| forged pilot (ncal=1/B=19/ok=true/crit=0) opened Wald | production-size + positive-finite licensing REFUSES | test_forged_pilot_cannot_open_wald |
| — | file-hash pinning available for Stage-B | test_calib_expected_sha_pins_the_artifact |
| packager accepted NaN / -1 / Inf; untyped binding; no p2_start_year | finite/positive/typed v6 REJECTS | test_packager_rejects_* / test_packager_requires_p2_start_year_key |
| provenance covered only pytest+selftest | 4-step harness; calibration byte-bound to a zero-exit run; logs.smoke mandatory | test_run_evidence_covers_all_four_steps, test_calibration_bound_to_recorded_run |
Old-commit check: the 16 new tests on f24e0ef should fail except
behavior-preservation (the well-typed staging arm and the years-parser
accept cases).

## 4. Evidence provenance (C28)
`evidence/environment.json` carries FOUR runs (pytest, selftest, smoke,
calibrate). Verify: every staged log hash equals a zero-exit run's
log_sha256; the staged calibration's sha256 equals the calibrate run's
artifact_sha256; the calibration is production-sized (ncal=200, B=9999),
strictly typed, and its binding.git_commit EQUALS the packaged commit.
calibration_ok=false remains a legitimate outcome (production runs full
nested PASS-P); at Stage-B, curve runs pass
--calib-expected-sha256 = the frozen calibration_sha256, making the
packaged artifact the ONLY licensed calibration.

## 5. Report
Amendment table C10, C20→C26, C21→C27, C22, C16, C23→C28, C24, C19, C25,
C27.4 shape note; list any remaining blockers with reproducible probes.
