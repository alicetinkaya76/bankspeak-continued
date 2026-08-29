# Third-eye prompt, round 6 (paste everything below the line into the external model; attach round6_package zip)

Round 6 is a NARROW round. Round-5's three method defects (null-imposed draws inside the
basic-CI formula; the structurally-zero floored-share diagnostic; the unimplemented MDE
calibration) were accepted, reproduced on the authors' engine, and repaired in code and
in PREREG v0.4. This round has one central deliverable: **the binary Stage-A freeze
ruling on `docs/PREREG_DRAFT_v0.4.md`** — APPROVE AS WRITTEN / APPROVE WITH LISTED LINE
EDITS / REJECT WITH REQUIRED CHANGES. Do not re-audit what rounds 3–5 already verified
(corpus numbers, provenance, family counts, pins) unless a checksum fails.

---

## Step 0 — Package integrity

Run `sha256sum -c SHA256SUMS` (zero failures required), then confirm these MUST-EXIST
files; on any failure STOP and output only the failure list:

    docs/PREREG_DRAFT_v0.4.md            docs/PREREG_v0.4_AMENDMENTS.md
    docs/PREREG_DRAFT_v0.3.md            docs/STAGE_A_FREEZE_RECORD.md
    docs/round5_method_defect_evidence.json
    docs/round5_verification_summary.json
    src/bootstrap_engine.py              src/mde_sim.py
    tests/test_bootstrap_smoke.py        config/families.yaml

## Role 1 — Repair verifier

1. Run `python -m pytest tests/ -q` (expected: 22 passed) and
   `python src/bootstrap_engine.py --selftest`. Authors' results on two platforms:
   null-large β=−0.137, p=0.117, CI [−0.300, 0.011]; effect β=+0.765, p=0.003,
   CI [0.623, 0.898]; null-small floored=0.0316 — seeded quantities should reproduce
   exactly on your platform.
2. Confirm each round-5 defect is dead **in code**: (a) the CI now comes from a
   full-model estimation pass and contains β̂ in your reruns (your own θ=0.9
   configuration from `round5_method_defect_evidence.json` is the natural test);
   (b) `true_floored_share` measures actual reconstruction flooring — your 22%
   configuration should now report ≈22%; (c) `mde_sim.py --mode calibrate` emits
   `boot_size_at_null`, `wald_boot_concordance`, `calibration_ok` and the fallback
   rule.
3. Verify `src/bootstrap_engine.py` implements PREREG v0.4 §4.2 exactly (PASS-P
   partialled-score construction, block-sum studentization, seeds; PASS-E transplant,
   percentile CI, escalation thresholds). Any code–prereg divergence is blocking.

## Role 2 — Stage-A freeze ruling on v0.4 (primary role)

1. Diff v0.4 against v0.3 (both included) and rule whether the change log's four items
   fully implement your round-5 findings — and, **since only your JSON evidence reached
   the authors (your report text did not), explicitly list anything from your round-5
   report that v0.4 leaves unaddressed.** If nothing remains, say so in one line.
2. Stress-test what v0.4 introduced that round 5 never saw:
   - the PASS-P construction: partialled score with QML weights, block-sum
     studentization T* = Ση_B S_B/√(ΣS_B²), contiguous non-overlapping blocks;
   - the deliberate block-scheme asymmetry (fixed partition for wild weights vs
     circular moving blocks for the transplant) and its one-line rationale;
   - the PASS-E escalation ladder (>1% failures → Wald-boot CI; >50% → condition
     fails; floored share >5% → dual-CI reporting);
   - the governance sentence (PASS-P decides condition 1; PASS-E CI decides the CI
     clauses of conditions 2–4; near-boundary disagreement reported, not adjudicated);
   - the reuse map (NB2 / standardized / guard / LOPO);
   - the §8 acceptance rule (boot_size ∈ [α/2, 2α] AND concordance ≥ 0.95, else full
     nested).
3. End with the binary ruling: **APPROVE AS WRITTEN / APPROVE WITH LISTED LINE EDITS /
   REJECT WITH REQUIRED CHANGES** — exact line edits if applicable.

## Role 3 — Editor

(a) `docs/STAGE_A_FREEZE_RECORD.md` is the freeze artifact template. Confirm its field
list is sufficient for an externally timestamped Stage-A record, and state exactly what
may still change between an APPROVE and the timestamp (Stage-B-fill placeholders only?).
(b) Confirm the 31 October 2026 go/no-go and the fallback trigger survive unchanged.
(c) Confirm the deferred step-4 list (full s12 diagnostics, NLL regeneration, QC grid,
method interactions) still contains no hidden Stage-A blocker.

## Output format

Three headed sections — **Repairs / Stage-A ruling / Editor** — each ending with a
ranked action list, blocking items first. The Stage-A section MUST end with the binary
ruling. English. Recompute what you assert or label it NOT RECOMPUTABLE. No praise;
review. No new literature unless strictly required (then authors, year, venue, DOI,
confidence).
