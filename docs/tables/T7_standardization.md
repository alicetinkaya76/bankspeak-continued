**Table 7 — The composition-standardized arm of condition 2, under the grouping used and the grouping preregistered.** The right-hand block is a POST-HOC SENSITIVITY, not condition 2: PREREG §6 requires a year-matched income classification and this one is current. See `docs/DEVIATION_20260827_c2_standardization.md`.

| Panel | Grouping | π groups | Post token support (WB / IMF) | Floor | Primary reason |
|---|---|---|---|---|---|
| P1 | `<stratum>:<year>` (as run) | 0 | 0.000 / 0.000 | 0.80 | `no_common_support_groups` |
| P1 | country → region × income (repaired) | 12 | 0.889 / 0.785 | 0.80 | `post_token_support_below_0.80` |
| P2 | `<stratum>:<year>` (as run) | 0 | 0.000 / 0.000 | 0.80 | `no_common_support_groups` |
| P2 | country → region × income (repaired) | 12 | 0.834 / 0.744 | 0.80 | `post_token_support_below_0.80` |

Under the grouping actually used, π retained no group at all and support was 0.000 on both sides — the estimator could not have run whatever the corpora looked like. Under the repaired grouping it retains 12 groups and the arm is still infeasible, but now because the Fund's post-2022 documents concentrate in country groups where the Bank has little presence: IMF post-period token support falls just below the preregistered 0.80 floor. That is a measurement about composition rather than about our code, and it is close enough to the floor that the year-matched version could fall either side of it.
