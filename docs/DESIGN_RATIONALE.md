# Design rationale (D1–D12)

Every binding decision, its justification, and the evidence behind it. Deviations must be
logged here with a date. (Stage-0 numbers referenced below are in STAGE0_REPORT.md.)

## D1 — Genre-stratified corpus, never pooled
**Decision.** Sample and analyze four strata separately: Annual Reports, Project Appraisal
Documents (PADs), Implementation Completion (and Results) Reports (ICRs), and — phase 2 —
press releases. No pooled trend lines, ever.
**Why.** The Stage-0 micro-pilot showed genre dominates marker rates: Tier-2 bureaucratese
went 1.42 → 24.89 per 1k tokens between bins that differed in BOTH era and genre. A pooled
series would confound composition shifts with language change — the exact artifact that
would sink the paper in review. Moretti & Pestre used Annual Reports only; we keep that
stratum as the direct continuation and add operational genres for generality.

## D2 — Two research questions, two evidentiary standards
**Decision.** RQ1 (1946–2026 continuation of the Bankspeak feature series) is descriptive
time-series work. RQ2 (post-2022 discontinuity) uses ITS with placebo breakpoints and
pre-trend tests, framed as *convergent forensic description*, never causal proof.
**Why.** Attribution of a 2023 break to LLMs is fragile: Ajay Banga's presidency begins
June 2023, co-timed with ChatGPT-era adoption; style guides and thematic pivots
(climate/jobs) shift simultaneously. Claiming causality would be indefensible; claiming a
measured discontinuity consistent with documented internal LLM adoption (the Bank's IEG
described GPT experiments and an enterprise "mAI" deployment in 2023) is defensible.

## D3 — IMF comparator series (mandatory before RQ2 claims)
**Decision.** Build a parallel feature series on IMF documents (Article IV consultations
and/or Annual Reports) before publishing any RQ2 result.
**Why.** IMF leadership did not change at the breakpoint (Georgieva, 2019–), so the
WB-specific leadership confound is absent there. If the discontinuity appears in both
institutions, the LLM-era reading strengthens; if only at the WB, the Banga/style-guide
reading gains weight. Either result is publishable — the comparator converts a weakness
into a design feature. Implementation deferred to s09 stub (see D8).

## D4 — Classic Bankspeak features re-operationalized + internal replication check
**Decision.** s04 computes: nominalization density, acronym density, "and" frequency,
temporal-anchoring rate (explicit years/months/deictic time), mean sentence length,
management-vocabulary rate (small curated lexicon from the pamphlet's highlighted terms).
Before extending past 2012, the 1946–2012 Annual Report series must qualitatively
reproduce the pamphlet's published trajectories.
**Why.** The continuation claim only holds if our instruments see what theirs saw. A
failed internal replication is a stop-and-diagnose event, not a footnote.

## D5 — Two-tier lexical markers with recorded provenance
**Decision.** Tier-1 = strong LLM-associated words (delve, underscore, showcase, pivotal,
intricate, meticulous, boast, commendable, realm, testament, tapestry, seamless...);
Tier-2 = bureaucratese shared by Bankspeak and LLM style (foster, leverage, harness,
robust, resilient, transformative, unlock, bold...). Lists live in config with a source
tag per word; edits require provenance.
**Why.** Bankspeak was inflating Tier-2 long before 2022 (that is Moretti & Pestre's
finding). Only the tier split lets us separate "more Bankspeak" from "LLM fingerprint".
Tier-1 list follows the excess-word literature (Kousha & Thelwall's 12-term tracking;
Liang et al.'s distributional estimation); Tier-2 curated from the pamphlet + WB usage.

## D6 — Frozen pre-2022 SLMs as perplexity instruments
**Decision.** s06 uses small, locally pinned models whose training data predates ChatGPT
(GPT-2 2019; Pythia trained on the Pile). Model IDs + revisions pinned in config; API
models are never used as measuring instruments.
**Why.** Two reasons. (a) Epistemic: a model trained before 2022 cannot have absorbed
post-2022 LLM style, so its perplexity on new WB prose measures deviation from pre-LLM
institutional English — a clean instrument. (b) Reproducibility: API models drift across
versions; pinned local SLMs are frozen laboratory instruments (TAHRİC discipline). Runs
on a single consumer GPU (mps/cuda) or CPU with subsampling — fits the hardware budget.

## D7 — Power analysis gates Tier-1 claims (s07 before any annotation or RQ2 writing)
**Decision.** No Tier-1-based claim is drafted until s07 shows the harvested token count
per year×stratum cell gives ≥0.8 power for the plausible effect size.
**Why.** Stage-0 found Tier-1 = 0 in both micro-bins (2,091 tokens total) — expected:
even post-LLM academic rates put individual Tier-1 words at ~10⁻⁴–10⁻³ per token. The
null at micro-scale is uninformative; only a powered corpus makes absence meaningful.
This gate prevents the classic underpowered-null error.

## D8 — Staged scope: WB core first, IMF and press releases second
**Decision.** Phase 1 = three D&R strata (Annual Reports, PADs, ICRs), fully pipelined.
Phase 2 = IMF comparator (s09) and WB press releases (not in D&R; needs a news-site
fetcher). Phase 2 starts only after Phase-1 features exist end-to-end.
**Why.** Nine manuscripts are already in flight and MİSAK ramps in October 2026; scope
discipline is the binding constraint. Also, press releases are the one WB genre adjacent
to Liang et al.'s corpora (UN/corporate PRs) — keeping them out of Phase 1 keeps the
novelty boundary sharp.

## D9 — txturl-first ingestion
**Decision.** s02 prefers the API's `txturl` (server-side plain text) and falls back to
`pdfurl` + PyMuPDF extraction only when absent.
**Why.** Discovered in the API field table: plain-text copies exist for many documents.
This removes OCR/extraction noise from a large share of the corpus — extraction noise is
itself era-correlated (older PDFs are scans), which would otherwise bias features.
Fallback extraction is logged per document so era×extraction-method can be controlled.

## D10 — Write-once sampling artifacts, append-only manifest
**Decision.** s01 writes `data/meta/frozen_sampling_v<N>.csv` once and refuses to
overwrite; every download appends `sha256, url, path, date` to `manifest.tsv`.
**Why.** TAHRİC lesson (July 2026): deterministic generators are not stable across Python
versions; the artifact, not the generator, is the ground truth. Reviewers get hashes.

## D11 — English-only filter, volume-aware Annual Reports
**Decision.** `lang_exact=English`; Annual Report volumes deduplicated by report number,
concatenated per fiscal year.
**Why.** The pamphlet's construct is the English institutional register; translations
would import translator style. Multi-volume reports would otherwise double-count years.

## D12 — Venue and framing
**Decision.** GIQ (SSCI Q1) primary with an information-management framing (institutional
document quality, provenance, AI adoption); IP&M (SCIE Q1) alternate with a
measurement-methodology framing. Verify current quartiles on Clarivate before submission.
**Why.** GIQ is the natural home for IGO document-corpus work; IP&M already hosts the
ISNAD line and accepts measurement-validity papers. Doçentlik (Apr 2028) needs the
acceptance by late 2027 → submit Mar 2027; both venues' review latencies fit.

## Open items / deviations log
- [resolved 2026-08-06] `docty_exact` labels verified via s00 facets + 14 probe requests:
  - Annual Reports live under the facet **'World Bank Annual Report'** (331 English docs,
    1946–2025), NOT the generic 'Annual Report' facet (2,598 docs, 1976→; trust-fund/
    IEG/facility annual reports — wrong genre). Config corrected accordingly. Caveat:
    the correct label also carries MIGA/ICSID annual reports → title/repnb filter at
    the fiscal-year assembly step (extends D11).
  - Plain 'Implementation Completion Report' is **not** an API facet (probe total=0);
    the expected two-label OR was based on a false s00 substring match against
    'Implementation Completion Report Review' (an IEG review genre, excluded). The
    single label 'Implementation Completion and Results Report' spans 1994–2026
    (8,534 English docs) and absorbs the historical variant. Config corrected.
  - 'Project Appraisal Document' confirmed: 6,515 English docs, 1997–2026.
  - Noted for a future design decision (NOT adopted): historical predecessor genres
    'Project Completion Report' (1970→2017) for ICRs and 'Staff Appraisal Report'
    (1947→) for PADs exist as facets; extending strata backward would be a D1 change.
- [open] Press-release fetcher design (Phase 2).
- [deviation 2026-08-06, refines D9] Pilot v0 found documents.worldbank.org
  intermittently returns 403 on `/text/` (and sometimes `/pdf/`) paths — rate/WAF
  behaviour, not document-specific: 5 resumable s02 passes recovered 120 of 146
  initial failures (484/510 = 94.9% final; residue 24 persistent 403 + 1 hard 404 +
  1 record with no URL). s02 was hardened accordingly: per-document error handling
  (one bad URL no longer kills the run), pdfurl fallback now also on txturl *failure*
  (not only absence), failures logged to data/meta/download_failures.csv;
  utils.get_with_retry fails fast on permanent 4xx instead of retrying.
  Consequence to control for: transient txt-endpoint 403s convert those documents to
  PDF extraction permanently (manifest is append-only) — pilot delivery was 62% txt /
  38% pdf although 99.8% of sampled docs advertise a txturl. Full-run option (Ali to
  decide): txt-only first passes, pdf fallback pass only at the end; and verify PDF
  integrity (opens + has pages) BEFORE manifest_append — pilot has one corrupt PDF
  (IFC AR 2021, id 33464456, 0 tokens) that is now frozen-in by the append-only rule.
- [decision 2026-08-06, pre-v1-freeze; delegated to the assistant by Ali ("sen karar
  ver"), recorded for review] Three GO-gate items resolved before the real harvest:
  (1) IFC/MIGA/ICSID sibling reports inside the 'World Bank Annual Report' facet
  stay IN the v1 frozen sample (AR stratum has no cap, so they displace nothing);
  they are filtered at the fiscal-year assembly step with logged rules — keeps the
  frozen artifact broad and the exclusions revisable/human-reviewable.
  (2) s02 now integrity-checks content BEFORE manifest_append (pdf must open and
  have >=1 page; txt must be non-empty) — the append-only manifest can no longer
  freeze in a corrupt download.
  (3) s02 gained --no-pdf-fallback for txt-only early passes; pdf fallback runs only
  in the final pass(es), limiting era-correlated extraction-method mix (D9).
- [erratum 2026-08-07] Commit 0e9e8cf's message claims "server_txt >=89% in EVERY
  decade"; the verified figure for the 2010s is 88.54% (742/838). Correct statement:
  server_txt >=88.5% in every decade, >=89% in all decades except the 2010s.
  (Caught by the post-run verification pass; message is immutable, record stands here.)
- [decision 2026-08-07, delegated to the assistant by Ali ("sen karar ver"), recorded
  for review] The seven needs_review AR-facet documents are resolved (encoded in
  s10 RESOLVED_REVIEW): 1946 board-of-governors meeting proceedings EXCLUDED (genre
  mismatch: minutes/speeches, not the institutional report); the three IDA-only
  annual reports 1961-63 EXCLUDED (separate IDA series; the pamphlet-continuation
  line is IBRD, and combined WB+IDA reports enter from 1964); the 1990 "World Bank
  and the environment" first annual report EXCLUDED (thematic series); the 2018
  "Relatório Principal" EXCLUDED (translation; D11 English-register rule); the 2008
  "Summaries of Operations (Vol. 5)" INCLUDED as an Annual Report volume on repnb
  evidence (46256 = AR 2008's repnb, title pattern "Vol. 5" of 32) — it is currently
  download residue (no text), so it joins the assembly only if a later s02 pass
  retrieves it. Net effect on the assembled series today: none.
- [decision 2026-08-07, same delegation] RQ2 publication framing: D3 STANDS — no
  RQ2 claim is published before the IMF comparator series exists. The paper is not
  reframed around a "preliminary" RQ2; instead s09 Phase 2 (IMF Article IV / Annual
  Reports) is the next scheduled work block (target: autumn 2026), which the
  Mar 2027 submission window accommodates. RQ1 (continuation) and methods sections
  can be drafted now; RQ2 text stays descriptive until s09 lands.
- [deviation 2026-08-07, after third-eye editorial review — audit findings CONFIRMED
  against data] (1) FY2002 assembled AR unit had 12 tokens (cover-sheet-only server
  extractions) and FY2007 was a table/heading dump (46,723 tokens, 0.9% function-word
  share); both had passed every provenance control. New prespecified per-unit
  extraction-quality gate in config `assembly_qc` (min_tokens 5000, min_stopword_share
  0.15; calibrated: legitimate units >=17k tokens / >=0.20 share) -> assembled series is
  now 71 QC-gated units; per-unit QC logged to data/meta/ar_unit_qc.csv. Lesson recorded:
  provenance controls do not establish measurement validity. (2) AR breakpoint inference
  reduced to a LEVEL-ONLY spec (n_post=2 disclosed; post-break slope not identified);
  clean-series level shift is +0.070 (was +0.102 pre-QC with slope term). (3) s12
  robustness battery added (leave-one-year-out; empirical breakpoint ranking; median/
  trimmed aggregation; Tier-1 per-word decomposition). Ranking result: maximal cuts
  cluster 2022-2025 across series (AR top cut 2022; ICR/PAD 2024-25); headline wording
  changed from "discontinuity" to "post-2022 increase" accordingly. (4) Paper reframed to
  lead with genre-aware measurement discipline (review's recommendation); AR era labels
  corrected to 2023-2024. (5) All 25 reviewer-suggested references verified against
  Crossref/publisher records (25/25 VERIFIED, none corrected or fabricated).
- (log deviations below with dates)
