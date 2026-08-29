# Round-2 audit completion (2026-08-09)

Internal completion of the round-2 third-eye review. The external reviewer received only
`PAPER_DRAFT_v0.2.docx`; every number below was recomputed directly from the CSVs in this
repository (`data/analysis/robustness/`, `data/analysis/paper/`, `data/features/`,
`data/meta/`). File this under `docs/` next to `RESPONSE_TO_REVIEW.md`.

## 1. Why round 2 returned "NOT AUDITABLE" — package failure, not evidence failure

The round-2 prompt promised: revised draft + `RESPONSE_TO_REVIEW.md` + `tables/` +
`robustness/` + figures + aggregate features. Only the docx reached the reviewer. All
eleven A/O verdicts of "NOT AUDITABLE" and every "current CSVs were not supplied" caveat
follow from that. Verified: the docx matches `docs/PAPER_DRAFT_v0.md` on every phrase the
reviewer quoted, so the review is of the real v0.2 text.

Two additional defects in the round-2 prompt itself, both caught or triggered by the reviewer:

1. **Reference count misstated.** Prompt: "25 entries with DOIs (plus two DOI-less
   proceedings entries)" = 27. Actual bibliography: 25 total = 23 with DOI + 2 without
   (Juzek & Ward COLING 2025; Mitchell et al. PMLR 202). Reviewer's count is correct.
2. **O9 does not exist in `RESPONSE_TO_REVIEW.md`.** The memo answers A1–A3, O3–O8, O10;
   the prompt instructs auditing "A1–A3, O3–O10". Either restore the missing O9 item or
   renumber, and archive the round-1 review text itself in `docs/` so labels are auditable.

Round-3 packaging rule: zip must physically contain the memo, `data/analysis/paper/`,
`data/analysis/robustness/`, `data/meta/ar_unit_qc.csv`, and this audit file; state the
exact file list in the prompt and count references correctly.

## 2. Completed A/O crosswalk (what round 2 could not verify, now verified)

| Label | Verdict (auditable now) | Ground truth from repo |
|---|---|---|
| A1 (FY2002/FY2007) | **ADDRESSED, wording wrong** | `ar_unit_qc.csv`: FY2002 = 2 docs, **12 tokens**, 0.0000 stopword share; FY2007 = 2 docs, **46,723 tokens**, 0.0094 share. All 71 retained units: ≥17,023 tokens, ≥0.2008 share. Gate values match the memo. "Prespecified" is chronologically false — see erratum E1. |
| A2 (level-only, n_post=2) | **ADDRESSED** | `NUMBERS.md` / `T2_its.csv`: ar_assembled_levelonly tier1 b2 = +0.0699, p<0.001, n_post = 2, placebo frac 0.00. LOYO base row confirms 0.0699. |
| A3 (2023–2024 label) | **ADDRESSED** | Draft and tables use 2023–2024 for AR; ICR/PAD run to 2026. Residual span issues are cosmetic (E7). |
| O3 (placebo → breakpoint scan) | **PARTIALLY** | Scan exists and ranks reproduce: 2023 = 2/72 (ar_assembled, top 2022 b2=0.0760), 3/27 (ICR), 4/25 (PAD), 27/74 (doc-level AR). But 72 candidates = only **65 unique partitions** (§4.1), inference is still raw ranking, and "ramped adoption" overreads it (E3). |
| O4 (Banga/IMF) | **NOT ADDRESSED (by design)** | s09 still a stub; D3 embargo holds. Controlled-contrast estimation is the round-3 gate. |
| O5 (Tier-1 concentration) | **PARTIALLY** | `tier1_decomposition.csv`, pooled post-2022: underscore family **43.5%**, pivotal **14.7%**, combined **58.2%** (memo's 43/15/58 confirmed). LWO ratios confirmed: ICR 2.22×, PAD 3.85×, AR doc-level 2.14×. New: family HHI 0.240, effective lexicon ≈ 4.2 families; AR post-period absolute mass = **20 hits total** (§4.3) — the reviewer's absolute-effects demand is justified. |
| O6 (perplexity) | **PARTIALLY** | `robust_aggregation.csv` medians confirmed: Pythia ICR 2.4004→2.5331, PAD 2.4503→2.5994; GPT-2 rises too; doc-level AR falls under every aggregator. Naming is wrong ("pre-LLM", "pre-2022 models") — E2. Assembled-unit NLL still missing. |
| O7 (within-stratum composition) | **NOT ADDRESSED** | Correctly disclosed; scheduled with comparator round. Blocking for submission, as reviewer says. |
| O8 (multiplicity) | **NOT ADDRESSED** | Declared-not-executed. Freeze estimand + FDR family in a PREREG file *before* any IMF result is inspected (§6, P2). |
| O9 | **UNDEFINED** | Missing from the memo (§1.2). |
| O10 (residue) | **ADDRESSED** | Recomputed from `frozen_sampling_v1.csv` vs `classic.csv`: residue = 65 unique ids = 61×HTTP-403 + 1×HTTP-404 + 3 no-URL (draft's "62 + 3" ✓). 6 zero-token docs in `classic.csv` ✓. Missingness-by-year/format model still pending. |

## 3. Independent recomputation of every quoted number

**All verified against the CSVs:** corpus totals (2,818 / 2,753 / 97.7% / 65 / 99.78%);
per-stratum rows of Table 1; ITS Table 3 (+0.070 / +0.056 p<0.001 / +0.027 p=0.010;
placebos 0.00 / 1.00 / 0.50); breakpoint ranks and candidate counts; LOYO range
0.041–0.099; decomposition shares and LWO ratios; robust-aggregation medians; QC values;
era means (temporal 39.96 → 26.10 [1986–2005] → 27.99 [2006–2012]; Tier-2 0.25 → 9.09 =
36.36×); 2020s Annual-Report plain-text share = **56.0%** (14/25 docs); overall
server-txt share 2,705/3,145 logged extractions.

**Discrepancies found (fix in v0.3):**

- **D-1.** Draft §5 says "27/71 assembled AR years below the token gate"; regenerated
  `T3_power.csv` says **26**/71. Trust the regenerated artifact; fix the prose.
- **D-2.** Draft/memo say "function-word share"; the artifact column is `stopword_share`
  and the config gate is computed on a stopword list (which includes "and", itself a
  reported outcome). Rename consistently and disclose the list (see §4.5).
- **D-3.** Table 2's first era is labeled "1946–1965" but the assembled series starts 1947
  (19 units = 1947–1965). Doc-level AR spans 1946–2025, assembled 1947–2024, ICR/PAD to
  2026 — one sentence should state all three spans (reviewer's title-span point).

## 4. New computations the reviewer demanded or predicted

### 4.1 Breakpoint scan: 72 calendar cuts = 65 unique designs (reviewer's suspicion confirmed)
Missing FYs inside the 1947–2024 assembled span: 1971, 1981, 1990, 2000, 2002, 2007, 2010.
Each produces a duplicate pre/post partition (cut at the missing year ≡ cut at the next
year); the scan CSV shows 7 exact-duplicate (n_post, b2, p) pairs. After deduplication:
**65 unique designs; 2023 still ranks 2nd** (2022: b2=0.0760, n_post=3; 2023: 0.0699,
n_post=2; 2021: 0.0497, n_post=4). Report unique designs, and add per-candidate
n_pre/n_post/SE/CI as the reviewer specifies.

**Endpoint caution is empirically live:** the maximal ICR and PAD cuts are **2025 — the
last admissible cut (n_post=2)** — and doc-level AR's maximum is 2024. "Maximal cuts
cluster late" is descriptively true; a ramp is not identified. Add trimmed candidate
interval (min post ≥3), sup-Wald/QLR with bootstrap critical values (Andrews 1993;
Bai–Perron 1998/2003), and an explicit no-change vs step vs slope vs ramp model comparison.

### 4.2 LOYO decomposition — actually favorable once n_post=1 fits are separated
The published range 0.041–0.099 mixes two regimes. Dropping a **pre** year: b2 ∈
[0.0680, 0.0746] — tight around 0.0699. Dropping a **post** year leaves n_post=1
(drop-2023 → 0.0412; drop-2024 → 0.0986), a structurally different, one-observation
level estimate. Report the pre-year LOYO band as the influence result and flag the two
post-year rows as n_post=1 sensitivity, not influence.

### 4.3 Absolute Tier-1 mass (the near-zero-baseline problem, quantified)
Post-2022 hits: AR **20**, ICR **417**, PAD **338** (pre: 348 / 812 / 673 over far larger
token bases). Assembled-AR post base = 72,823 tokens across two units (FY2023: 43,795;
FY2024: 29,028). Post-period family shares (pooled): underscore 43.5, pivotal 14.7,
seamless 10.8, showcase 9.9, multifaceted 6.5, commendable 4.0 (%). HHI = 0.240 →
effective ≈ 4.2 families. Consequence: report absolute rate differences with intervals and
document prevalence; define a family-collapsed, independently sourced confirmatory Tier-1
before the comparator; keep the current index explicitly exploratory.

### 4.4 Extraction-method check — headline estimate cleared, doc-level panels not
All three post-cut assembled units (FY2022, FY2023, FY2024) and 9 of 10 preceding units
are `server_txt` (FY2021: 1 of 3 docs pymupdf). The 56%-plain-text problem lives in the
**doc-level 2020s AR sample**, not in the assembled series → the +0.070 headline is not an
extraction-switch artifact; say so with the unit-level table. ICR/PAD 2020s txt shares are
83.5% / 76.7% vs ≥90% / 93% in the 1990s — era-correlated exactly as D9 anticipated, so the
promised method-sensitivity model (method covariate and txt-only re-estimation) is due.

### 4.5 QC gate: token-only sensitivity is NOT redundant
FY2007 (46,723 tokens) **passes** a token-count-only gate; only the share criterion — or an
independent indicator (alphabetic-character share, sentence yield, line-length structure)
— catches it. So the reviewer's sensitivity package is substantive: threshold grid,
token-only variant (retains FY2007 → re-estimate), independent-indicator variant, blind
manual audit of exclusions + lowest retained units, and application of the frozen rule
unchanged to the IMF corpus. Outcome-adjacency is real (gate share includes "and") but the
observed separation (≥20.1% vs ≤0.9%) should carry the argument once the grid is shown.

## 5. Errata for v0.3 (exact replacements)

- **E1** §3.3 "We therefore impose a prespecified per-unit gate" → "Following the blinded
  external audit, we defined and froze an audit-derived extraction-quality gate before
  re-estimating all outcome models." Same fix in RESPONSE memo A1.
- **E2** §4: drop "pre-LLM model surprise" and "frozen pre-2022 models" → "reference-model
  NLL under two frozen models whose training corpora predate ChatGPT-era text: GPT-2
  (2019) and Pythia-1.4b (released 2023; trained on the Pile, compiled 2020)." Aligns the
  paper with D6's own wording; document both corpus cutoffs.
- **E3** Abstract "consistent with ramped adoption rather than a single break" and Results
  "a ramped post-2022 increase, not a single sharp 2023 break" → "Several measures show a
  late-period increase, but the available annual series neither distinguish a unique
  breakpoint within 2022–2025 nor identify its mechanism." Keep "post-2022 increase" as
  the descriptive label; delete "ramp/adoption" as a process claim until the step-vs-ramp
  comparison and controlled contrast exist.
- **E4** "~35% (39.96 → ~26–28)" → "approximately 30–35% (39.96 → 26.10 by 1986–2005;
  27.99 by 2006–2012)".
- **E5** "27/71" → "26/71" (D-1). **E6** "function-word share" → "stopword share" +
  disclose list (D-2). **E7** spans (D-3). **E8** memo O9 (§1.2).
- **E9** References: split the Stanford pamphlet and NLR manifestations of Moretti/Pestre
  (DOI belongs to NLR); add the López Bernal corrigendum (10.1093/ije/dyaa118) and verify
  s08 uses the corrected centered-interaction form; run the reviewer's eight additions
  through the Crossref pipeline before integration — Andrews 1993 (10.2307/2951764),
  Bai–Perron 2003 (10.1002/jae.659), Linden 2015 (10.1177/1536867X1501500208), Bottomley
  et al. 2019 (10.1515/em-2018-0010), Benjamini–Hochberg 1995
  (10.1111/j.2517-6161.1995.tb02031.x), Grimmer–Stewart 2013 (10.1093/pan/mps028), Egami
  et al. 2022 (10.1126/sciadv.abg2652), Zuiderwijk et al. 2021 GIQ (10.1016/j.giq.2021.101577).

## 6. Merged ranked plan (reviewer demands × HANDOFF order × D1–D12)

- **P0 — text fixes, half a day.** E1–E9 above. No analysis needed.
- **P1 — s12 extensions on existing data, 1–2 days.** (a) dedup partitions + per-candidate
  n_pre/n_post/coef/SE/CI + trimmed interval + sup-Wald/QLR bootstrap + step/ramp model
  comparison [O3]; (b) LOYO split per §4.2 [A2]; (c) QC sensitivity package per §4.5 [A1];
  (d) family-collapsed Tier-1 + absolute effects + HHI + prevalence + leave-family-out
  [O5]; (e) extraction-method sensitivity (covariate + txt-only) and
  missingness-by-year×format model [O10/D9]; (f) concordance samples for top families
  (needs data/text/ on the workstation).
- **P2 — freeze before looking (do NOW, costs an hour).** Write `docs/PREREG.md`: one
  confirmatory estimand = institution×post interaction, composition-standardized Poisson
  QML with log-token offset, HAC/cluster inference; the FDR-controlled exploratory family
  enumerated; QC rule and Tier-1 confirmatory lexicon frozen. Commit before any IMF
  document is downloaded [O4, O8, D3].
- **P3 — comparator round (Sep–Oct 2026, as scheduled).** IMF harvest via s09; harmonized
  genres; metadata enrichment (region/sector/instrument/template era) for within-stratum
  composition [O7]; assembled-unit NLL [O6]; then the controlled contrast per PREREG.
- **P4 — manuscript completion (Nov 2026–Jan 2027).** Section 2 and Discussion around
  public-sector information governance (Zuiderwijk anchor); primary sources for WB LLM
  adoption with explicit scope statements; figures/captions/bibliography normalization.
- **P5 — round-3 review.** Fixed prompt + full package + this audit file; invite
  recomputation of §§3–4.

Timeline check: P0–P2 fit before the comparator work already scheduled for Sep–Oct; the
Mar 2027 GIQ submission target stands. The round-2 "desk-reject in submitted form" is the
expected verdict on a self-declared embargoed skeleton; the operative content is the
blocking list, which this plan absorbs in full.
