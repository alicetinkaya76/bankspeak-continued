# Third-eye prompt, round 7 (USE ONLY after the sprint-2 kit is green and committed;
# paste everything below the line into the external model; attach the round7_package
# zip and, alongside it, the freeze_fields JSON emitted at packaging)

Round 7 is the **Stage-A freeze round**. All nine round-6 required changes were
accepted; the two independently checkable defects were reproduced on the authors'
stack before repair; the [CODE] items shipped in the round-6 kit and the [BUILD] items
(WB-P0 frame builder, validation/interpretive orchestration, full v0.5 assembly,
freeze-field emission) shipped in sprint 2. The central deliverable of this round is
**the binary Stage-A freeze ruling on `docs/PREREG_DRAFT_v0.5.md`** — APPROVE AS
WRITTEN / APPROVE WITH LISTED LINE EDITS / REJECT WITH REQUIRED CHANGES. Do not
re-audit what rounds 3–6 already verified (corpus numbers, provenance, family counts,
pins, the round-5 two-pass repair) unless a checksum fails.

Declared-open items (state whether each blocks the freeze; the authors assert none
does): (i) the `config/wb_p0_docty.yaml` strings are the EXPECTED facet labels and are
verified verbatim by the s00 probe only at Stage-B — the s09b pipeline is
label-agnostic and its live layer is gated; (ii) the environment is declared by the
pinned scaffold files `requirements.txt` / `requirements-ppl.txt` (hashed into the
freeze record; Python 3.11.9 per `.python-version`), and the authors' full-suite
rerun on that pinned stack is a standing pre-freeze obligation — confirm the record
fields suffice; (iii) the external-timestamp channel (OSF
primary; Zenodo/OpenTimestamps fallback) is an author-side logistics item; (iv) the §6
ESS floor's executable rendering (ESS_tok = 1/Σ_g(π̃_g²/tok_g) against a 0.50 ×
total-token floor) is DECLARED for your stress-test in this round; (v) the §7 NLL
≥100-token filter is disclosed as a deferred step-4 patch, not yet applied to archived
s06 outputs.

---

## Step 0 — Package integrity

Run `sha256sum -c SHA256SUMS` (zero failures required) and confirm `MANIFEST.tsv`
agrees with the tree (spot-check ≥5 rows). Then confirm these MUST-EXIST files; on any
failure STOP and output only the failure list:

    docs/PREREG_DRAFT_v0.5.md            docs/PREREG_v0.5_AMENDMENTS.md
    docs/PREREG_DRAFT_v0.4.md            docs/ROUND6_BUILD_PLAN.md
    docs/STAGE_A_FREEZE_RECORD_v2.md     docs/ROUND7_KIT_NOTES.md
    src/bootstrap_engine.py              src/mde_sim.py
    src/standardize.py                   src/s09a_imf_articleiv_frame.py
    src/s09b_wb_p0_frame.py              src/g1_audit.py
    src/s13_validation_battery.py        src/make_cells_template.py
    tools/build_audit_package.py         Makefile
    requirements.txt                     requirements-ppl.txt
    .python-version                      config/wb_p0_docty.yaml

The zip must contain no `.DS_Store`, `__pycache__`, or `*.pyc` entries (the `*.bak*`
files are deliberate audit artifacts and belong there).

## Role 1 — Sprint verifier

1. Run `python -m pytest tests/ -q` (expected: **50 passed**) and
   `python src/bootstrap_engine.py --selftest`. Authors' results, reproduced
   bit-identically on macOS/arm64 (Python 3.11.9) and Linux/x86-64 (numpy 2.4.4,
   pandas 3.0.2):
   null-large β=−0.137, p=0.117, CI [−0.300, 0.011];
   effect β=+0.765, p=0.003, CI [0.623, 0.898];
   null-small β=+1.104, p=0.193, CI [0.157, 2.02], floored=0.0316;
   nb2-overdispersed β=−0.310, p=0.257, α̂=0.035;
   duplicate-rejection OK on ('WB', 1994).
   Seeded quantities should reproduce exactly on your platform
   (`tests/test_bootstrap_smoke.py::test_selftest_values_pinned_cross_platform` pins
   them).
2. `python src/mde_sim.py --mode smoke --theta-grid 0.0:0.9:0.9 --sigma-delta 0.1`
   must print `calibration_ok: false` and `curve decision engine: full_nested_pass_p`
   (the smoke itself demonstrates the round-6 blocker-1 fallback firing; smoke MDE
   numbers are smoke-scale only).
3. Verify the sprint-2 modules implement their prereg sections exactly; any
   code–prereg divergence is blocking:
   - `s13_validation_battery.py` vs §5 conditions 1–4, §3 validation algorithms, §9
     event-study/placebo/H-SHARED, the §10 seed-offset registry, and the §4.2
     escalation ladder as consumed via `governing_ci`;
   - the trend CI: `bootstrap_engine.py` records `WB_cyear` from the SAME PASS-E
     draws (no separate simulation) — confirm in code and in
     `tests/test_bootstrap_smoke.py::test_trend_ci_from_same_passe_draws`;
   - `s09b_wb_p0_frame.py` vs Appendix B.10 (unit, version, single-ISO3 with the
     inversion-suffix rotation, cutoff, raw-page archiving obligation, Stage-B gate);
   - `make_cells_template.py` vs the §8 P0 projection;
   - `tools/build_audit_package.py --freeze-fields` vs the §11.6 archive-binding
     field list (run it yourself on the unpacked tree if convenient).
4. Battery fixtures: `tests/test_battery.py` runs a θ=0.9 world through all four
   conditions and a null world through condition-1 failure, plus the §6 hard-fail and
   ESS-floor paths and the B6 four-state Holm logic. Re-run and, if you wish,
   perturb θ to check the conditions move the right way.

## Role 2 — Stage-A freeze ruling on v0.5 (primary role)

1. Diff v0.5 against v0.4 + `PREREG_v0.5_AMENDMENTS.md` (all included) and rule
   whether the weave fully implements the nine round-6 required changes. **The full
   round-6 report reached the authors this time; explicitly list anything from that
   report v0.5 leaves unaddressed.** If nothing remains, say so in one line.
2. Stress-test what v0.5 introduced that round 6 never saw in executable/exact form:
   - the §6 ESS_tok rendering (declared-open item iv): is
     1/Σ_g(π̃_g²/tok_g) ≥ 0.50 × total tokens a faithful executable reading of "ESS
     floor on cell token masses under π", and are its failure modes (thin-cell
     concentration) the right ones to guard against?
   - the four-state family logic of §2/§5 as implemented in `holm_family`
     (singleton level α, no promotion, fallback state);
   - the §9 event-study bin constructor (anchor, backward bins, <2-year merge,
     reference bin) and the per-bin PASS-E transplant;
   - the H-SHARED estimator (pooled log-rate difference, +0.5 continuity, IMF-only
     circular block-3, empty-period draws counted as failures);
   - the 2016 placebo construction (≤2022 subset, WB×post16 column substitution into
     the frozen design);
   - the seed-offset registry (§10) — any collision or unintended draw-sharing?
   - Appendix B.10 (WB-P0 protocol) — determinism and auditability of the country,
     unit and version rules;
   - §11.6 archive binding — does the field list, as emitted by `--freeze-fields`,
     bind the archive tightly enough that a post-timestamp edit is detectable?
3. End with the binary ruling: **APPROVE AS WRITTEN / APPROVE WITH LISTED LINE EDITS /
   REJECT WITH REQUIRED CHANGES** — exact line edits if applicable.

## Role 3 — Editor

(a) `docs/STAGE_A_FREEZE_RECORD_v2.md` + the attached freeze_fields JSON: confirm the
record's fields are fully populated or placeholder-marked, that the JSON's non-null
fields match the package you hold (recompute zip SHA-256 and entry count), and state
exactly what may still change between an APPROVE and the timestamp (Stage-B-fill
placeholders only). (b) Confirm the 31 October 2026 go/no-go and the fallback trigger
survive v0.5 unchanged. (c) Confirm the deferred step-4 list (full s12 diagnostics,
NLL regeneration incl. the §7 filter, QC grid, method interactions) still contains no
hidden Stage-A blocker. (d) Note any doc-code mismatch you find anywhere in the
package (one was fixed this round: the packager now actually writes MANIFEST.tsv).

## Output format

Three headed sections — **Sprint verification / Stage-A ruling / Editor** — each
ending with a ranked action list, blocking items first. The Stage-A section MUST end
with the binary ruling. English. Recompute what you assert or label it NOT
RECOMPUTABLE. No praise; review. No new literature unless strictly required (then
authors, year, venue, DOI, confidence).
