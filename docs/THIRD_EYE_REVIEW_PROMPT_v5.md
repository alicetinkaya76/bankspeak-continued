# Third-eye prompt, round 5 (paste everything below the line into the external model; attach round5_package zip)

Round 5 closes the Stage-A loop. Since round 4: PREREG v0.3 was produced implementing
all twelve required changes; the audit record was corrected to v1.2; and the six
"must-complete-before-Stage-A" code preconditions were EXECUTED on the authors' pinned
environment. This round has one central deliverable: **the binary Stage-A freeze ruling
on `docs/PREREG_DRAFT_v0.3.md`** — APPROVE AS WRITTEN / APPROVE WITH LISTED LINE
EDITS / REJECT WITH REQUIRED CHANGES. Everything else supports that ruling.

---

## Step 0 — Package integrity

This package was machine-built (`tools/build_audit_package.py`) with a standard
checksum file. First run `sha256sum -c SHA256SUMS` (or equivalent) and confirm zero
failures. Then confirm these MUST-EXIST files are present; if any is missing or any
checksum fails, STOP and output only the failure list:

    docs/PREREG_DRAFT_v0.3.md          docs/ROUND2_AUDIT_COMPLETION_v1.2.md
    docs/ROUND4_THIRD_EYE_REVIEW.md    docs/round2_external_review.md
    config/families.yaml               config/config.yaml
    data/features/family_counts.csv    data/meta/extraction_log_v2.csv
    data/meta/manifest.tsv             src/families.py
    src/bootstrap_engine.py            src/mde_sim.py
    src/percell_seed.py                src/s09_frame_sampler.py
    src/apply_patches.py               src/s08_its_analysis.py.bak-round4
    tests/test_families.py             tests/test_bootstrap_smoke.py

## Executed preconditions — verifiable claims (Role 1 checks each)

1. **Environment:** full test suite passes 20/20 under pinned Python 3.11.9
   (round-4's environment condition). Rerun `python -m pytest tests/ -q` yourself.
2. **Patches applied:** s08 (full-precision placebo thresholds `p_b2_exact`/`p_b3_exact`;
   E3-aligned output language) and s06 (hardware-invariant NLL population). Diff the
   live files against the shipped `.bak-round4` backups.
3. **Machine-readable outcome:** `config/families.yaml`
   (sha256 `79b381ef190bbbb5ec51db6889be62487510c60737e4df4e9012c354db0d6c50`) +
   `src/families.py` + unit tests covering the seamlessly/intricacies/pivotal's/pivotalé
   cases. Verify the 28→13 mapping equals PREREG Appendix A and `config.yaml
   markers.tier1`.
4. **Exact integer counts:** `data/features/family_counts.csv` — 2,753 docs,
   missing_text=0, zero_token=6, **tier1_total=2608**. Cross-checks to run:
   (a) reconstruct the expected total from `markers.csv` rates × `classic.csv` tokens
   (≈2608.0); (b) sum the post-period (year ≥ 2023) family counts and reconcile against
   the 775 pooled post-period hits in `tier1_decomposition.csv`, explaining any delta;
   (c) confirm per-family columns sum to `tier1_count` row-wise.
5. **Provenance:** `data/meta/extraction_log_v2.csv` — 3,145 rows = 2,753 `v1` +
   392 `v0_pilot_only`; `analysis_eligible=2747` (exactly tokens>0 = 2,753−6);
   `nll_eligible=2743` (exactly tokens≥100; the four 1–99-token docs are 2017572
   AR-2002/12, 34063941 AR-2008/32, 10752676 ICR-2009/14, 10508321 PAD-2009/14).
6. **Immutable model revisions:** `config.yaml` now pins
   gpt2 `607a30d783dfa663caf39e06633721c8d4cfcd7e` and EleutherAI/pythia-1.4b
   `fedc38a16eea3bd36a96b906d78d11d2ce18ed79` (no `revision: main` remains — grep it).
7. **Cross-platform determinism:** `python src/bootstrap_engine.py --selftest` produced
   bit-identical results on Linux x86-64 and macOS arm64
   (null: beta=−0.137, p=0.065; effect: beta=+0.974, p=0.005; method=block), and the
   MDE smoke calibration gave crit |z| = 1.8734642040310812 on both. Run the selftest
   on your platform and report whether you reproduce the identical numbers (a third
   platform).

## Declared open items — rule only on placement, do not re-flag

- Round-1 review archive / O9 crosswalk: still pending author-side; per round-4's own
  ruling this is a final-audit documentation blocker, not a Stage-A blocker.
- External timestamps (OSF or fallback): execute AFTER this round's APPROVE.
- Raw text (`data/text/`, 2.4 GB) excluded: `s05b`/`s12` end-to-end runs are NOT
  RECOMPUTABLE here; totals ARE cross-checkable via item 4 above.
- Full `s12` locked-robustness implementation (dedup scan, sup-Wald, step/ramp, QC
  grid, method interactions) is scheduled for the post-SAP locked-robustness step per
  round-4's own sequencing.
- The MDE smoke output in logs is smoke-sized (`ncal=10`); production constants
  (`--ncal 200 --B 9999`, `--reps 1000`) are frozen in PREREG §8.

## Role 1 — Precondition verifier

Walk round-4's six "must be complete before Stage-A freeze" items and rule each
**DONE / NOT DONE** with package evidence (run the tests and selftest; recompute the
item-4 cross-checks). Flag any claim above you can refute.

## Role 2 — Stage-A freeze ruling on PREREG v0.3 (primary role)

1. Walk the twelve round-4 required changes; rule each **RESOLVED / PARTIALLY /
   UNRESOLVED** with the v0.3 section that answers it.
2. Stress-test what v0.3 introduced that round 4 never saw: the fixed CEM>SCD>CPF
   priority and the recorded "effectively CEM-or-nothing" consequence; the G1 blind
   title/abstract audit (≥16/20); the pseudo-count construction
   `y* = max(0, round(μ̂⁰ + √μ̂⁰·r*))` and its floored-share report; the basic-bootstrap
   CI choice; the >1% failure sign-flip fallback; the MDE studentized shortcut with
   its 200-run calibration; the 2016 pre-period placebo; the quasi-binomial breadth
   model; the +0.5 zero-count rule; Appendix B's `combined_with_program` flag and
   single-ISO3 country rule; the 2023–2025 confirmatory window with the 2027-01-15
   descriptive-2026 snapshot.
3. End the section with the binary ruling: **APPROVE AS WRITTEN / APPROVE WITH LISTED
   LINE EDITS / REJECT WITH REQUIRED CHANGES** — with exact line edits if applicable.

## Role 3 — Editor

(a) If the ruling is APPROVE (either form): list exactly what may still change between
this ruling and the OSF timestamp (Stage-B-fill placeholders only?) and what may not.
(b) Confirm or amend the 31 October 2026 go/no-go and the fallback trigger.
(c) Confirm nothing in the step-4 deferred list has silently become a Stage-A blocker.

## Output format

Three headed sections — **Preconditions / Stage-A ruling / Editor** — each ending with
a ranked action list, blocking items first. The Stage-A section MUST end with the
binary ruling. English. Recompute what you assert or label it NOT RECOMPUTABLE. No
praise; review. No new literature unless strictly required (then authors, year, venue,
DOI, confidence).
