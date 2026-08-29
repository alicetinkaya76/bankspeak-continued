# PREREG v0.12 AMENDMENTS (C36–C38) — round-13 required changes

Binding on top of v0.5–v0.11. Round-13 verdict: REJECT; three
package/record blockers (the C33/C34 method repairs were explicitly
confirmed and are untouched).

## C36 — Freeze-record integrity (closes the C32 blocker)
1. The versionless fossil `docs/STAGE_A_FREEZE_RECORD.md` (a v0.4-era
   template) is REMOVED from the package. The single-template rule now
   covers ALL `STAGE_A_FREEZE_RECORD*.md` names, versionless included,
   and the regression asserts exactly one ships.
2. Record v3.4 supersedes v3.3: the frozen-object definition explicitly
   includes `+ PREREG_v0.11_AMENDMENTS (C33–C35) + PREREG_v0.12_AMENDMENTS
   (C36–C38)` — no "it's inside the ZIP" indirection — and carries a
   literal `rulings.round13` row.

## C37 — Test-classification record corrected to the recomputed matrices (closes the C35 blocker)
1. Round-11 file: 16 tests = **13 old-commit (10266ba) failures + 3
   preservation/layer-attribution passes**, named in the module header
   and docstring-marked on the passing arms themselves
   (attribute-variants; UTF-8 positive archive — identity round-trip on
   the old path; schema-accepts-real-output). The strengthened NaN test
   is now a true old-commit failure (the old packager rejects for a
   different reason than the asserted "strict JSON" attribution), which
   is exactly why the former 12/4 claim became 13/3.
2. Round-12 file: 9 tests = **7 failures + 2 preservation passes on
   1b71b4f**, with the reference commit declared per arm:
   canonical-ids-still-pass preserves on both old commits;
   sproll-forged-text preserves on 1b71b4f and FLIPS against 10266ba
   (pre-C30 text-sourced archiving). "Every probe fails" headers are
   gone.

## C38 — Portable fail-closed reproducer, regression-guarded (closes the reproducer blocker)
The archived `docs/reproduce_round12_blockers.sh` is rebuilt on the
round-13 auditor's corrected script (archived verbatim alongside it as
`reproduce_round12_blockers_round13_audit.sh`): expected nonzero ABORTs
are captured in subshells, stdout/stderr are kept separate, verdicts
print unconditionally, and hashing falls back to `shasum -a 256` where
GNU sha256sum is absent (macOS). A new regression
(`test_archived_reproducer_prints_all_four_verdicts`) executes the
archived script against a fully valid production-shaped
calibration_ok=false artifact and asserts all four verdict lines
(A1/A2 NOT REPRODUCED; both id fixtures REJECTED).
