**Table 4 — The confirmatory verdict.** From `data/analysis/panels/family_verdict.json` and the two panel batteries. A panel passes only if all four conditions hold; the family verdict is Holm over the panels.

| | P1 (ICR × IMF) | P2 (PAD × IMF) |
|---|---|---|
| β̂ (differential, log-rate) | 0.586 | 0.332 |
| 95% CI | [0.267, 0.921] | [0.017, 0.622] |
| p (two-sided) | 0.0142 | 0.0929 |
| C1 — Holm-adjusted significance | pass | **fail** |
| C2 — specification stability | **fail** (standardized arm infeasible: no_common_support_groups) | **fail** (standardized arm infeasible: no_common_support_groups) |
| C3 — concentration guard | **fail** | **fail** |
| C4 — leave-one-post-year-out influence | **fail** | **fail** |
| Panel verdict | **fail** | **fail** |
| τ̂ — WB differential trend (log points/yr) | 0.0371 [0.019, 0.055] | 0.0483 [0.033, 0.064] |
| PREREG §9 extrapolation trigger | 0.445 vs β̂ 0.586 — **fires** | 0.579 vs β̂ 0.332 — **fires** |
| H-SHARED (IMF own change) | 0.145 [0.003, 0.356] | 0.145 [0.003, 0.356] |
| Placebo cut (2016) | p = 0.1674 | p = 0.4782 |

**Family verdict: `family_pass = false`, `headline_template = None`.**
