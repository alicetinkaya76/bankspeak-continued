# Audit record v1.3 — append-only addendum (2026-08-09)

v1.2 is unchanged; this addendum registers rounds 5–6 per the round-6
audit-trail requirement.

- Round 5: verification fully green incl. the 775/775 post-period
  reconciliation; three method defects demonstrated (null-imposed basic-CI,
  vacuous floored-share, uncalibrated MDE shortcut) — all reproduced by the
  authors and repaired (engine v2, two-pass inference). Ruling: REJECT.
- Round 6: repairs A/B confirmed dead by independent rerun (θ=0.9 CI contains
  β̂; independent floor share 0.2251 measured); nine blockers issued — all
  accepted; the two checkable ones reproduced by the authors (duplicate-cell
  acceptance; standardization counterexample (0.90, 0.10)). Ruling: REJECT.
  Repairs: engine v3 + mde v3 + standardize.py (19 tests green); [BUILD]
  remainder and round-7 gate in ROUND6_BUILD_PLAN.md.
- Evidence-packaging lesson adopted: every demonstrated-defect JSON must carry
  its full generating configuration (tokens, θ, seeds, years, B).
- Platform statement of record: deterministic seeded outputs reproduce exactly
  on three stacks so far; continuous outputs carry a ≤1e-13 tolerance outside
  the pinned environment; an exact pinned-environment rerun remains an
  author-side obligation before any freeze.
