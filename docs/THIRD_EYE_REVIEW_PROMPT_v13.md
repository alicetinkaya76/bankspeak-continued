# THIRD-EYE REVIEW PROMPT v13 (round-13)

Adversarial third eye, Stage-A freeze of "Bankspeak, Continued".
Round-12 verdict was REJECT with two blockers (C29/C31 residue; C30
residue) and two test-quality findings; this package answers all four.
BINARY verdict: **APPROVE FOR STAGE-A TIMESTAMP** or **REJECT WITH
REQUIRED CHANGES**. Recompute everything.

## 1. Integrity gate
As before, now with NINE rulings (round2,3,4,7,8,9,10,11,12 — round6
remains a declared pending textual item). Freeze record v3.3 ships and is the ONLY record template in the package — every superseded template (v2, v3, v3.1, v3.2) is removed; one literal ruling row per completed round.

## 2. Independent execution (pinned env)
`python -m pytest tests/ -q` → expect **182 passed** (173 + 9 round-12).
Selftest → five lines, bit-identical. Smoke → numbers AND shape
unchanged (crit ≈ 5.8208103823388075, relative ≤ 1e-12; nested;
MDE80 = 0.9).

## 3. Round-12 blockers — verify each FLIPS
Run your own reproduce_round12_blockers.sh (archived at
docs/reproduce_round12_blockers.sh) against this package's bundle +
evidence/calibration.json: Blocker A1/A2 must print NOT REPRODUCED
(both runs now differ — the no-hash run ABORTS with exit≠0 and
"--calib-expected-sha256" on stderr; the correct-hash run prints
"[mde] calibration artifact sha256 verified: <sha>" and proceeds
nested), and Blocker B must print REJECTED for both id fixtures.
Regression names: test_false_artifact_without_hash_aborts,
test_false_artifact_with_hash_verifies_and_runs_nested,
test_schema_broken_false_artifact_aborts_despite_hash,
test_false_artifact_with_wrong_hash_aborts,
test_int_id_is_a_schema_failure,
test_whitespace_variant_id_is_a_schema_failure,
test_sproll_archive_ignores_forged_text,
test_sproll_log_bytes_column_counts_bytes. The provenance gate now
runs BEFORE calibration_ok (C33): every external-calibration run —
including the REAL ok=false frozen artifact — either aborts or carries
the verified-hash line. Earlier-round curve tests were evolved to the
abort contract (stderr assertions, exit≠0) — this evolution is
declared, not silent. One further declared evolution: the former
test_freeze_record_v32_covers_the_round11_schema is generalized to
test_freeze_record_covers_current_schema — it asserts EXACTLY ONE
record template ships and that it carries the full current schema, so a
superseded template can never satisfy it again.

## 4. Test-classification declaration (C35)
The round-11 file holds 16 tests whose old-commit (10266ba) result is
12 failed / 4 passed; the four passing arms are behavior-preservation /
layer-attribution (docstring-marked): the UTF-8 positive-archive arm
(UTF-8 round-trip is identity on the old path), the canonical-output
arms, and the schema-accepts-real arm. New in round-12: the NaN
packager fixture is a fully valid artifact whose ONLY defect is the NaN
literal (rejection attributable to the parse-layer ban, message
"strict JSON"), and a transport-forgery flip (content ≠ text) proves
byte-sourced SPROLL archiving. The request-log bytes column now counts
raw transport bytes (multi-byte fixture asserted).

## 5. Evidence provenance
Four-run harness unchanged; verify log and calibration byte-binding,
schema validity of the staged calibration, and binding.git_commit ==
packaged commit. calibration_ok=false remains legitimate; at Stage-B
every curve run passes --calib-expected-sha256 = the frozen
calibration_sha256 and its log must carry the verified-hash line.

## 6. Report
Amendment table C10, C30→C34, C27, C22, C16, C29/C31→C33, C32 (v3.3),
C19, C25, C35; remaining blockers with reproducible probes.
