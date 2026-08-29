# Sprint-2 kit notes (2026-08-10) — round-7 readiness

Round-7 gate status (ROUND6_BUILD_PLAN.md):
(a) item-5 builders + item-8 orchestration with green fixtures — DONE
    (s09b_wb_p0_frame, s13_validation_battery, make_cells_template; suite 50 passed);
(b) full PREREG v0.5 assembled from v0.4 + amendments — DONE
    (docs/PREREG_DRAFT_v0.5.md, change log at top);
(c) freeze-record v2 fields populated by the packager — DONE
    (tools/build_audit_package.py v2, --freeze-fields; MANIFEST.tsv now real).

Engine v3.1: the WB_cyear coefficient is recorded from the SAME PASS-E draws
(trend_beta_hat / trend_ci_percentile). The edit is purely additive; the frozen
selftest numbers are bit-identical before/after and are now PINNED as a test
(test_selftest_values_pinned_cross_platform).

Frozen seed-offset registry (PREREG v0.5 SS10): PASS-P seed+b; PASS-E
seed+500000+b; event-study PASS-E seed+600000+b; H-SHARED seed+700000+b.

Declared-open items carried to round 7 (none blocks the freeze, authors' view):
wb_p0_docty.yaml labels pending verbatim s00 confirmation at Stage-B (pipeline is
label-agnostic; live layer gated); the environment pins are the recovered scaffold
requirements.txt / requirements-ppl.txt (Python 3.11.9) — the authors' full-suite
rerun on that pinned stack is a standing pre-freeze obligation; external-timestamp
channel (OSF primary / fallback); the SS6
ESS_tok rendering is DECLARED for round-7 stress-testing; the SS7 NLL filter is a
deferred step-4 patch.

Freeze discipline unchanged: no WB outcome analysis before the SAP timestamp
(s13 CLI gate --i-am-post-sap; battery development was fixture-only), no live
metadata capture outside Stage-B (--i-am-in-stage-b gates in s09a/s09b), UNGDC
firewall intact.
