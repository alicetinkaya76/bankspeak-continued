**Table 2 — Exclusions applied to the analysis corpus.** Each ledger is a committed CSV; `tools/build_panel_cells.py` is where they are enforced rather than merely recorded.

| Ledger | Rule | Documents | Strata touched |
|---|---|---|---|
| `d8_exclusions.csv` | D-8/D-11: non-English or bilingual documents | 20 | icr, pad |
| `intention_to_sample_exclusions.csv` | PREREG §7 intention-to-sample | 395 | annual_report, icr, pad |
| `d13_kept.csv` | D-13: flagged, adjudicated, KEPT (shown for completeness) | 1 | annual_report |
