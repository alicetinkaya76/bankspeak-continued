# THIRD-EYE REVIEW PROMPT v12 (round-12)

You are the adversarial third eye for the Stage-A freeze of "Bankspeak,
Continued". Round-11 verdict was REJECT with four blockers (C28a/C26/
C28b/C24); this package answers it. Deliver a BINARY verdict: **APPROVE
FOR STAGE-A TIMESTAMP** or **REJECT WITH REQUIRED CHANGES**. Recompute
everything.

## 1. Integrity gate
As before, now with EIGHT rulings (round2,3,4,7,8,9,10,11 — round6
remains a declared pending textual item). The superseded freeze-record
v3.1 is REMOVED; v3.2 ships (v0.9+v0.10 normative, logs.smoke,
rulings.round10/11 rows — C32).

## 2. Independent execution (pinned env)
`python -m pytest tests/ -q` → expect **173 passed** (157 + 16 round-11
regressions). Selftest → five lines, bit-identical. Smoke → numbers AND
shape unchanged from round-11 (crit ≈ 5.8208103823388075, relative band
≤ 1e-12; nested engine; MDE80 = 0.9).

## 3. Round-11 probes — verify each FLIPS (6/6 reproduced pre-repair)
| Round-11 probe | Now expected | Regression test |
|---|---|---|
| forged production artifact + NO hash arg → Wald | external calibration REFUSED without --calib-expected-sha256 | test_external_calibration_without_hash_is_refused |
| — | correct hash licenses; verified hash printed to the run log | test_correct_hash_licenses_and_is_reported |
| `<a/>No results` passed as terminal | structural parser RAISES | test_self_closing_anchor_is_an_anchor (+variants) |
| id-less record met total=1 | canonical non-empty id required | test_record_without_id_raises / _blank_id |
| retried 5xx bodies never archived | every attempt archived from inside the retry layer | test_retried_bodies_reach_the_attempt_hook (+no-content abort) |
| SPROLL re-encoded via r.text | verbatim transport bytes archived; strict-UTF-8 parse fails closed AFTER archiving | test_sproll_archives_verbatim_transport_bytes / _non_utf8 |
| ncal=200.0 / dup years / typed-binding junk staged | shared recursive schema rejects (runtime AND packager); NaN literal rejected at parse | test_schema_rejects_* / test_packager_rejects_nonstandard_json_constants / test_curve_refuses_schema_broken_even_with_correct_hash |
| record template behind schema | v3.2 covers v0.9/v0.10 + smoke + round-10/11 rows | test_freeze_record_v32_covers_the_round11_schema |
Old-commit check: the 16 new tests on 10266ba should fail except
behavior-preservation (the schema-accepts-real-output arm, the
attribute-variant assertions on plain divs, and the correct-hash
licensing arm which exercises the r10 mechanism).

## 4. Evidence provenance
Unchanged four-run harness; verify log and calibration byte-binding as
in v11, plus: the staged calibration validates against
src/calib_schema.py, and `binding.git_commit` EQUALS the packaged
commit. calibration_ok=false remains legitimate (production runs full
nested); at Stage-B every curve run passes
--calib-expected-sha256 = the frozen calibration_sha256.

## 5. Report
Amendment table C10, C26→C30, C27, C22, C16, C28→C29+C31, C24→C32, C19,
C25; list any remaining blockers with reproducible probes.
