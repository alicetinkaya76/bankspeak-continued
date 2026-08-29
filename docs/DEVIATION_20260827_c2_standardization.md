# Deviation and repair: condition 2's standardized arm was computed on the wrong variable

**Date:** 2026-08-27. **Status:** the confirmatory artifacts are unchanged; a
labelled sensitivity is added beside them. **Governing verdict is unaffected.**

## What was frozen

PREREG v0.5 §6 fixes the standardization stratifier exactly:

> **Common ontology (fixed at Stage-B, metadata only):** country (ISO3) mapped to
> region × income group (WB groupings, year-matched), calendar year. […] the
> ICR/PAD group is the D&R primary-country field mapped to (region × income);
> regional/multi-country projects and documents with a missing field go to an
> explicit `unknown` group that counts as unsupported (conservative).

π is then built over groups with support **in both institutions in both
periods**, and the arm is infeasible if support falls below the declared floors.

## What was run

`tools/build_panel_cells.py` supplied `group = "<stratum>:<year>"` — `icr:2019`,
`imf_article_iv:2019`. Its own comment records the reason: *"the finest key
available on both sides without a country field for WB"*.

That premise was false. The D&R **`count` field carries the primary country**, it
is present on 2,406 of the 2,407 sampled ICR/PAD documents, and it has been
sitting in the write-once API capture (`data/meta/wb_p1p2_raw/`) since the Stage-B
harvest. It was never carried into `wb_p1p2_frame.csv`, so by the time the panel
builder looked for it, it was not where anyone would look. No request was needed
to recover it; the bytes were already on disk.

## Why the resulting output is not a finding

A stratum:year key is institution-specific by construction: `icr:2019` can never
have IMF support, `imf_article_iv:2019` can never have WB support. `build_pi`
therefore retained **zero** groups and the battery reported

    reason: no_common_support_groups
    pi_groups: 0
    excluded_token_share: 1.0   (every institution × period cell)
    post_token_support: {IMF: 0.0, WB: 0.0}

Read at face value, that says the two corpora share no common support — a strong
substantive claim about the World Bank and the Fund. It is not what happened.
Every cell was excluded because the key could not match across institutions, not
because the documents fail to overlap. PREREG §6 does say infeasible ⇒ condition 2
fails, so the verdict line is right; the *reason* recorded under it is not, and
publishing it as a property of the corpora would have been a misdescription.

This is the same failure mode already logged twice in this project — a ruling
that is recorded but never applied — appearing a third time, now in a
preregistered condition rather than a remedy.

## What the repair does, and what it deliberately does not do

`tools/build_country_ontology.py` builds the §6 ontology offline from the
write-once capture plus one new metadata call to the World Bank's own country
endpoint (captured write-once to `data/meta/wb_country_api_raw.json`). WB names
are matched against WB names — the same authority that wrote the `count` field —
rather than against a third-party gazetteer. Resolution: exact normalised name →
alias file → single-country prefix → comma-split. Aggregates are not countries,
so `Senegal,World` and `Mongolia,East Asia and Pacific` each resolve to their one
country while a value naming two or more distinct countries goes to `unknown`.
**94.9% of the sampled ICR/PAD documents resolve to a region x income group**, and 97.8% (P1) / 96.3% (P2) of the documents entering the panels carry one. (An earlier version of this record quoted 91.0%, which is the share over all kept documents in every stratum, not the panel population the sentence was about.) The residue
is written by name and count to `data/meta/country_unresolved.csv` (60 documents,
27 distinct values — regions, aggregates, and three territories the current
classification no longer lists). Tuning stopped there deliberately: continuing to
extend the map against a visible residue is how a mapping becomes
results-dependent.

**One element of §6 is NOT met.** Income group here is the **current**
classification, not year-matched. The year-matched series is the Bank's OGHIST
workbook — an `.xlsx` the pinned environment cannot read without adding a
dependency, and it was not assembled at Stage-B. Substituting a different income
variable after seeing results is exactly the researcher degree of freedom this
study is built to refuse, so the substitution is not smuggled into the condition.

Consequently:

- **The frozen confirmatory artifacts in `data/analysis/panels/` are not
  touched, and not re-run.** `--group-source stratum_year` remains the default so
  the 2026-08-27 run stays reproducible byte-for-byte, defect included.
- The repaired grouping is written to `data/analysis/panels_country/` and is
  reported as a **post-hoc, non-preregistered sensitivity**, labelled as such
  wherever it appears.
- **Condition 2 continues to fail as recorded.** What changes is what the paper
  is entitled to say about *why*: not "the corpora share no common support" but
  "the arm was supplied a stratifier that could not have common support, and the
  preregistered stratifier was not assembled in time."

## Why this could not have changed the verdict

`family_pass = false` is driven by conditions that were evaluated on their
merits: C3 fails in **both** panels (P1 β = −0.067, CI [−0.509, 0.398]; P2
β = −0.439, CI [−0.934, 0.051]), and C1 fails in P2 (p = 0.0929). A panel passes
only if all four conditions hold. No behaviour of C2 could lift either panel, so
nothing in this repair is capable of moving the headline — which is the reason it
could be carried out and reported openly rather than becoming a decision.

## Files

- `tools/build_country_ontology.py`, `data/meta/country_ontology.csv`,
  `data/meta/country_unresolved.csv`, `data/meta/wb_country_api_raw.json`
- `tools/build_panel_cells.py --group-source country`
- `data/analysis/panels_country/` (sensitivity only)
- alias additions in `config/wb_country_aliases.yaml`
