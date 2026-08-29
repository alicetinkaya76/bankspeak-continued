# THIRD-EYE REVIEW PROMPT v14 (round-14)

Adversarial third eye, Stage-A freeze of "Bankspeak, Continued".
Round-13 verdict: REJECT with three package/record blockers; the C33/C34
method repairs were explicitly confirmed and are UNTOUCHED here. BINARY
verdict: **APPROVE FOR STAGE-A TIMESTAMP** or **REJECT WITH REQUIRED
CHANGES**. Recompute everything.

## 1. Integrity gate
TEN rulings (round2,3,4,7,8,9,10,11,12,13 — round6 declared pending).
Record v3.4 is the ONLY `STAGE_A_FREEZE_RECORD*.md` in the package —
the versionless fossil and v3.3 are removed; the frozen-object
definition explicitly includes PREREG_v0.11 (C33–C35) and PREREG_v0.12
(C36–C38); a literal rulings.round13 row exists.

## 2. Independent execution (pinned env)
`python -m pytest tests/ -q` → **183 passed** (182 + the reproducer
regression). Selftest bit-identical; smoke numbers AND shape unchanged
(crit ≈ 5.8208103823388075, relative ≤ 1e-12; nested; MDE80 = 0.9).

## 3. Round-13 blockers — verify each closes
1. Fossil/template: glob ALL STAGE_A_FREEZE_RECORD*.md — exactly one
   file, v3.4, carrying PREREG_v0.11_AMENDMENTS, C33, C35,
   PREREG_v0.12 and rulings.round12 + rulings.round13
   (test_freeze_record_covers_current_schema, now fossil-inclusive).
2. Classification record: module headers now state the recomputed
   matrices — r11: 16 = 13 old-commit failures + 3 named,
   docstring-marked preservation arms; r12: 9 = 7 + 2 with per-arm
   reference commits (canonical-ids preserves on both;
   sproll-forged-text preserves on 1b71b4f, flips vs 10266ba). Verify
   by porting the current files onto the old commits with your
   audit-compatibility shims.
3. Reproducer: run docs/reproduce_round12_blockers.sh (rebuilt on YOUR
   corrected script, archived verbatim next to it as
   reproduce_round12_blockers_round13_audit.sh; portability shim:
   shasum fallback) against this package's bundle +
   evidence/calibration.json — expect A1 NOT REPRODUCED, A2 NOT
   REPRODUCED, both id fixtures REJECTED. The regression
   test_archived_reproducer_prints_all_four_verdicts executes the
   archived script itself and asserts all four verdict lines; it FAILS
   on d9ddef5 (the set -e script dies on the first correct ABORT).

## 4. Evidence provenance
Unchanged: four-run harness; log and calibration byte-binding; staged
calibration schema-valid with binding.git_commit == packaged commit;
calibration_ok=false legitimate; Stage-B curve runs pass
--calib-expected-sha256 = the frozen calibration_sha256 and their logs
carry the verified-hash line.

## 5. Report
Amendment table C10, C34, C27, C22, C16, C33, C32→C36, C35→C37,
reproducer→C38, C19, C25; remaining blockers with reproducible probes.
