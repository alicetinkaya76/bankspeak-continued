# Researcher degrees of freedom: what was fixed before the WB outcomes were seen

Date: 2026-08-20. Discharges the obligation queued in
`docs/RULING_20260820_prior_inspection.md` ("Consequent obligation, not yet
discharged"). Method: git history against a timestamp, not recollection.

## The boundary

WB outcomes were first computed **2026-08-07 09:13–09:14** — `classic.csv`
09:13, `markers.csv` 09:14, and `its_results.csv` 09:14, i.e. the ITS ran the
same minute the features landed. The last commit before that boundary is
`a7a5f72` (2026-08-06 22:50); the repository's first commit is `bcdb76b`
(2026-08-06 21:05).

Every analytic choice below is classified by whether it existed, unchanged, at
`a7a5f72`.

## Fixed before — verified by diff, not by memory

| degree of freedom | where | verdict |
| --- | --- | --- |
| **Outcome definition** (Tier-1 marker list) | `config.yaml: markers` | **byte-identical** at `a7a5f72` and today |
| **Marker extraction code** | `src/s05_features_markers.py` | **one commit only** — the 08-06 scaffold; never touched since |
| **ITS model specification** | `config.yaml: its` | identical |
| **Classic feature code** | `src/s04_features_classic.py` | zero post-boundary commits |
| Sampling design, seed, strata, year window | `config.yaml: sampling/seed/strata/years` | identical |

This is the load-bearing result: **the thing the confirmatory claim is measured
in — which words count, and how — was frozen before any WB outcome existed, and
has not moved since.**

## Changed after the boundary, with what it touches

| change | date | reaches the confirmatory family? |
| --- | --- | --- |
| `config: assembly_qc` (min_tokens 5000, min_stopword_share 0.15) | post | **No.** Used only by `s10_assemble_ar.py`, i.e. the Annual Report stratum, which §2 makes descriptive only |
| `config/families.yaml` (28→13 mapping) materialised | 2026-08-09 | **No.** PREREG §3: "the total is invariant to family relabeling". It affects per-family reporting, not the primary outcome |
| `config: perplexity` | post | **No.** NLL is exploratory only, and §7.4 already defers its regeneration |
| `config: imf_coveo` | 2026-08-19 | No. Stage-B transport |
| `src/s08_its_analysis.py` | 2026-08-09 | **Substance unchanged.** The diff replaces approximate p-values with exact ones (`p_b2` → `p_b2_exact`) and *strengthens* a caveat (scans "do not identify a unique break date, trajectory shape, or mechanism"). No model-form change |
| `src/s13_validation_battery.py` (×4), `s12_robustness.py`, `s10_assemble_ar.py` (×3) | 08-10 … 08-12 | Every commit is labelled "round-N repairs" — the adversarial review process, dated and documented in `docs/ROUND*_THIRD_EYE_REVIEW.md` |

## The one genuinely outcome-informed choice, and it is already disclosed

The **concentration-guard family is `underscore`**, and PREREG §3 states the
reason in the frozen document: it is "already known to dominate on the WB side
(43.48% of post-period hits)". That figure could only come from seeing the
outcomes. The preregistration handles it the only way that works — by *fixing*
the guard in advance and disclosing the basis, rather than selecting it later —
and by closing the adjacent hatch: "switching to breadth/prevalence now would
itself be an outcome-informed primary change is adopted: occurrence count stays
primary."

## Conclusion

The prior-inspection exposure is narrower than the ruling had to assume. The
outcome definition, the extraction code and the model specification predate the
outcomes and are unchanged. Everything altered afterwards either lands outside
the confirmatory family (annual-report QC, perplexity, Stage-B transport), is
provably neutral to the primary outcome (the 28→13 mapping), or is an
adversarial-review repair with a dated public trail. The single outcome-informed
choice is the guard family, and the preregistration discloses it in its own
text.

**What this does not do.** It does not audit choices that were never written
down — a decision taken in conversation and never committed leaves no trace, and
git can only certify what it holds. The claim here is bounded accordingly:
*every analytic degree of freedom that the repository records* was fixed before
the outcomes, except the ones tabled above.
