**Table 5 — Why the raw ratio and the fitted interaction disagree.** Both columns are computed from `cells_P*.csv` by `tools/make_paper_tables.py`. Rates are Tier-1 counts per 1,000 eligible tokens, pooled within period; the ratio of ratios is descriptive and was never the estimand.

| Panel | Family | WB pre→post | IMF pre→post | WB×/IMF× |
|---|---|---|---|---|
| P1 | all Tier-1 | 0.0416 → 0.1359 (×3.26) | 0.1153 → 0.1332 (×1.16) | 2.83 |
| P1 | minus `underscore` | 0.0321 → 0.0861 (×2.68) | 0.0238 → 0.0368 (×1.55) | 1.74 |
| P2 | all Tier-1 | 0.0218 → 0.0635 (×2.91) | 0.1153 → 0.1332 (×1.16) | 2.52 |
| P2 | minus `underscore` | 0.0161 → 0.0374 (×2.32) | 0.0238 → 0.0368 (×1.55) | 1.50 |

The descriptive ratio of ratios stays above 1 in every row. The preregistered quantity is the fitted interaction in Table 4, which carries year effects and the differential shock structure the bootstrap resamples; it does not survive the same removal. Only the fitted quantity was registered.
