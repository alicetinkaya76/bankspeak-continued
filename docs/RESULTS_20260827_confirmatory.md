# Confirmatory results — no confirmatory claim

Date: 2026-08-27. SAP frozen and timestamped **before** any of this was
computed: `10.5281/zenodo.22098259`, sha256 `4aa12279…2677`, published
2026-08-25T15:01:07Z. Every number below is regenerable by
`tools/run_after_sap.py` with that DOI and hash.

Reported under SAP §S7, which requires the power bound, `placebo_sig_frac`, the
series label and the prior-inspection disclosure to travel *with* every result
rather than sit in an appendix. They are all here.

## The governing verdict

`s13_validation_battery family`, Holm over the two panels, α = 0.05:

```
family_pass ......... false
passing_panels ...... []
headline_template ... null
```

**No confirmatory claim is made for either panel.** PREREG §5: failure of any
condition means the panel is reported descriptively with the failed condition
named. Both fail, and the reasons differ.

### P1 — WB ICR against the IMF Article IV comparator (α_holm = 0.025)

| | |
| --- | --- |
| θ (WB:post, log points) | **0.586** |
| PASS-P p | **0.0142** |
| C1 Holm | **passes** |
| C2 stability (NB2) | passes |
| C2 stability (standardized) | **infeasible** — see below |
| **C3 concentration guard** | **FAILS** |
| **C4 leave-one-post-year-out** | **FAILS** |

**C3 is the one that matters.** Refit with the `underscore` family removed, as
PREREG §3 mandates: β = **−0.067**, CI **[−0.509, 0.398]**. The effect does not
merely shrink — it **vanishes and changes sign**. The entire P1 signal is one
word family, which is exactly the failure mode §3 anticipated when it fixed
`underscore` as the mandatory guard *before* the data existed, on the disclosed
ground that it "already dominates on the WB side (43.48% of post-period hits)".
The guard was set for this, and it caught it.

**C4** deleting each post year in turn: 2023 → p = 0.0103, **2024 → p = 0.1815
(β 0.207 against 0.586)**, 2025 → p = 0.0142. The result rests on 2024.

### P2 — WB PAD against the same comparator (α_holm = 0.05)

θ = **0.332**, p = **0.0929**. C1 fails at its own α; the remaining conditions
fail with it.

## What the descriptive picture shows, and why the comparator earns its place

Tier-1 rate per 1,000 eligible tokens, pre-2023 against post-2023:

| panel | institution | pre | post | ratio |
| --- | --- | --- | --- | --- |
| P1 | WB (icr) | 0.0416 | 0.1359 | **×3.26** |
| P2 | WB (pad) | 0.0218 | 0.0635 | **×2.91** |
| both | **IMF (comparator)** | 0.1153 | 0.1332 | **×1.16** |

The World Bank panels rise roughly threefold; the IMF rises 16%. That gap is
what produces a positive θ. But two facts sit next to it:

**H-SHARED (the §2 descriptive companion): the IMF moved too.** Its own pre/post
change is **+0.145 log points, CI [0.003, 0.356]** — small, but its interval
excludes zero. The comparator is not a flat baseline.

**And the IMF's pre-period rate is nearly three times the WB's** (0.1153 against
0.0416). The two institutions were never on the same level, which is what §2
means by a *non-equivalent* comparator with institution and genre confounded,
and why interpretation was capped in advance.

## The three things that must accompany any reading of the above

**1. Power (SAP §S6, measured before any outcome existed).** MDE₈₀ is
unreachable on the preregistered θ grid under every companion setting. At
θ = 0.60 — the design's own G4 threshold, and almost exactly P1's point estimate
of 0.586 — family power is **0.159–0.216** where 0.80 was required. So a real
effect of this size would have been missed four times in five, and a rejection
at this size carries severe winner's-curse inflation. **A null here is
uninformative and is not reported as absence of effect.**

**2. Placebo.** From `its_results.csv`, `placebo_sig_frac` on the Tier-1
breakpoint: annual_report **1.00**, icr **1.00**, imf_article_iv 0.67, pad 0.33.
On the P1 panel's own stratum, *every* placebo breakpoint tried on pre-2022 data
is also significant. The panel-level placebo at 2016 is cleaner — P1 p = 0.1674,
P2 p = 0.4782 — so the two disagree, and both are reported.

**3. Series and prior inspection.** All ITS figures above are the `doc_level`
series; `ar_assembled` and `ar_assembled_levelonly` also exist and disagree in
sign on the same quantity, so no number is quoted without its series.
`docs/RULING_20260820_prior_inspection.md` stands: **748 of 2,738 (27.3%)** of
the Stage-B WB sample are documents whose outcomes were inspected at Stage-A,
while the IMF half of the contrast had never been computed before today.

## Corpus, and what was excluded

3,786 documents entered; **3,391** in the confirmatory window, 395 dropped —
382 outside 1999-2025, **10 by rulings D-8/D-11** (non-English and bilingual),
3 ineligible under §7. Full per-document ledger:
`data/meta/intention_to_sample_exclusions.csv`.

The IMF corpus is 1,064/1,064 retrieved, verified and — after OCR of 12,273
pages — clean on every quality class.

## Two limitations that are data, not verdicts

- **C2's standardized variant is infeasible**, not failed: the WB frozen samples
  carry no country field while the IMF sample does, so the two share no
  standardization stratum. Recorded rather than worked around.
- **The exclusions are pre-period-weighted.** Eighteen ICR documents leave P1,
  all of them pre-2023. Removing pre-period documents from one arm is not
  neutral to a pre/post contrast, and the per-year counts are in the ledger.

## What this licenses

The paper may say: a preregistered differential test was specified, externally
timestamped before the data were touched, and run. It yields **no confirmatory
claim**. The apparent WB rise does not survive removal of a single word family;
it depends on one post year; the comparator institution rose as well; and the
design's own power analysis, fixed in advance, says an effect of the observed
size would have been detected roughly one time in five.

That is a bounded, informative negative — and every part of the bound was set
before the outcome was visible.

---

# RQ1 — the spine, rebuilt and re-replicated

Measured on the same rebuilt corpus, after OCR, the D-7 refetch and every ruling.

## The D4 gate reproduces

D4 makes internal replication a **gate**: "Before extending past 2012, the
1946–2012 Annual Report series must qualitatively reproduce the pamphlet's
published trajectories. A failed internal replication is a stop-and-diagnose
event, not a footnote." On the assembled series, 1946–65 against 2020–26:

| feature | 1946–65 | 2020–26 | |
| --- | --- | --- | --- |
| temporal anchoring /1k | **39.96** | **22.97** | **falls** ✓ |
| nominalizations /100 | 5.98 | 7.71 | rises ✓ |
| management vocabulary /1k | 1.11 | 4.47 | rises ✓ |
| **Tier-2 bureaucratese /1k** | **0.252** | **7.631** | **×30** |
| Tier-1 /1k | 0.009 | 0.094 | ×10 |

The temporal figure is the sharp one: the third-eye review recorded the
pamphlet's trajectory as "~40 → ~24 per 1k tokens", and the rebuilt series gives
**39.96 → 22.97**. The gate passes on a corpus that has since been re-extracted,
OCR'd, refetched and pruned by ruling — which is a stronger replication than the
first one, because none of those repairs was made with this comparison in view.

## The series is materially more complete than it was

| | before | after |
| --- | --- | --- |
| Annual Report fiscal years | 71 | **76** |
| missing years | 7 | **2** (2000, 2010) |

**2002** was two un-OCR'd scans totalling 12 tokens and failed assembly QC; it is
now 73,917 tokens at 0.234 function-word share and passes. **2007** was 46,723
tokens of mojibake at 0.009; it is now 50,807 tokens at 0.254 and passes. Both
returned exactly as ruling D-9 predicted they would. The other three came back
with the Stage-B download of documents Stage-A never fetched.

## What RQ1 licenses that RQ2 does not

RQ1's claim needs no differential and no comparator: it is a measured,
replication-validated extension of a widely cited but methodologically loose
pamphlet, across eighty years, on a corpus whose every defect class was found,
ruled and recorded before the numbers were read. Tier-2 bureaucratese rising
thirtyfold is a finding in its own right and does not depend on any LLM
hypothesis.

That is the spine the paper should lead with — a recommendation made on
2026-08-20 on other grounds, and unchanged by today's results except that it is
now the part that survived.

---

# SAP §S9 discharged — the OCR method effect is small

§S9 made this binding: the 1999–2004 IMF block does not enter any comparison
until the OCR-versus-native method effect has been estimated **with era held
fixed**, on documents carrying both. Twenty native-text documents were OCR'd and
compared against their own native extraction, whole document against whole
document.

| statistic | native | OCR | ratio |
| --- | --- | --- | --- |
| mean token length | 5.484 | 5.515 | **1.006** |
| token recovery (median) | — | — | **1.012** (min 0.996, max 1.172) |
| hyphen breaks /1k tokens | 2.479 | 2.070 | 0.835 |
| single-char tokens /1k | 37.01 | 34.80 | 0.940 |
| non-ASCII fraction | 0.0020 | 0.0022 | 1.124 |

**OCR is close to equivalent to native extraction on this corpus.** Token counts
land within ~1% and mean token length within 0.6%; if anything OCR recovers
slightly *more* tokens and slightly *fewer* single-character fragments. The
collinearity §S9 identified is real in structure — every OCR'd document is IMF
and pre-period, so method cannot be controlled against era — but the quantity it
would confound with is small enough to bound rather than assume.

That is what the 1999–2004 block needed to enter the comparison, and it now has
it. The block is in the confirmatory cells above.

## A correction, because the first calibration was invalid

The calibration run on 2026-08-26 compared the first five pages of native text
against the OCR of the **whole** document. Every count metric was therefore a
page-count ratio wearing a method effect's clothes — chars 21×, tokens 25×,
hyphen breaks 80× — and only the two scale-free ratios meant anything. It was
reported here in passing as "mean token length falls 4.8% under OCR". **That was
wrong in magnitude and in sign**: measured like for like it rises 0.6%.

The tool now reads the whole document on both sides and emits per-1k-token rates
alongside the raw counts, so a count can no longer be mistaken for a rate. The
obligation §S9 imposes is discharged by the corrected numbers above, not by the
first ones.
