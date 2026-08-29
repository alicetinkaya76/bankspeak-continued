<!-- Round 15. Six independent reviewers, one lens each, every top finding then
handed to a skeptic instructed to refute it by default. Six findings survived,
none was withdrawn. What follows is the report verbatim; the response and what
was actually verified before acting is in ROUND15_RESPONSE.md. -->

# Pre-submission report — *Reconstructing Bankspeak* (PLOS ONE)

## 1. Verdict

**No — do not submit as it stands, but the blockers are packaging, not science.** The confirmatory design, the preregistered null, and the reporting discipline around it hold up: I re-fitted the frozen model from `06_machine_output/cells_P1.csv` and reproduced β̂ = 0.5856046402232642, the exact 512-pattern enumeration (8/512 on P1, 50/512 on P2), and the block statistic independently, and the manuscript's §7/§8 are candid about the things that actually threaten the result. What is not ready is everything a PLOS ONE editor touches before a reviewer does: the Data Availability field still contains a literal bracketed author choice, the deposit it points to does not exist, the archived code as published runs **zero** tests, and two numbers printed in the manuscript are contradicted by the code that is supposed to have generated them. Fix the four findings below — a day's clerical work plus one re-cut release — and I would submit.

## 2. Must fix before submission

### F1. The data-availability package is not submittable as written

Four defects in one story, all verified:

| where | what |
|---|---|
| `third_eye_kit/09_submission/SUBMISSION_DATA_AVAILABILITY.md:63` | The evidence deposit "is **[deposited at DOI … / to be deposited before publication]**" — a bracketed placeholder in a file whose own line 3 calls it "Submission-ready. Paste into the journal's Data Availability field." |
| `third_eye_kit/01_manuscript/PAPER_DRAFT_v2.md:1016–1018` | The "**Evidence deposit.**" entry lists contents and stops. No repository, no DOI, no verb, no "to be deposited" caveat — while the adjacent "Code and design record" entry (line 1007) does carry a DOI, so the silence reads as a dropped locator. |
| `PAPER_DRAFT_v2.md:262` (§3.4) | Asserts in the present tense that "The Zenodo deposit therefore carries the World Bank raw captures and all derived artifacts in full." A reader of the paper alone is told a deposit exists that the DAS says has not been made. §7 does not disclose this. |
| `third_eye_kit/01_manuscript/PAPER_SUPPLEMENT_v1.md:9` | Cites the code archive as `10.5281/zenodo.22152945`. That is v1.0.0 (`git tag v1.0.0` = 907d2a7), and `git ls-tree -r --name-only v1.0.0` contains **no** `data/meta/imf_document_index.csv` — the supplement is the one document sending readers to the release that lacks the IMF access index. Every other document (draft §9:1007, DAS:53, cover letter:58, README:123) is on v1.1.0 / 22158882. |

Separately, `SUBMISSION_DATA_AVAILABILITY.md:40` cites `data/meta/imf_retrieval/_manifest.csv` as the record "of the route and the URL used for every document," but `prepare_zenodo_deposit.py` puts that file in `HASH_ONLY_FILES` — its bytes never travel, and no deposited artifact carries a per-document route (the deposited index has exactly report_no, year, country_iso3, doi, sha256). `PAPER_DRAFT_v2.md:181` cites `docs/IMF_RETRIEVAL_20260820.md` and `docs/IMF_ACCESS_COMPLIANCE_20260820.md` by repository path; neither exists in `bankspeak-public/docs/`. Worth knowing *why*: `tools/build_public_repo.py:85` lists both by name in `PROSE_OK` as files that "legitimately discuss the IMF in prose and carry no document data," but the path `DENY` (`^docs/IMF_`, and the broader `(^|/)imf(?!_document_index)`) rejects them before the scanner runs, so all three `PROSE_OK` entries are unreachable dead code. These two were meant to be published.

**Edits.** (i) Mint the evidence deposit and put its DOI in the DAS and in §9, or state "to be deposited before publication" in §9 and soften §3.4 to the future tense. (ii) Change the supplement to the concept DOI `10.5281/zenodo.22152944`, as the DAS and README already do. (iii) In the DAS, say the retrieval manifest is deposited by hash only, or publish a route column stripped of IMF URLs. (iv) Move the two `docs/IMF_*` prose files past the DENY filter after a content check, or drop the path citations. (v) `data/meta/imf_access_probe.json`, cited at §9 for the 16/4/0 probe, appears in no INCLUDE list either — same choice applies.

### F2. The archived code does not run, and the deposit cannot regenerate Table 1

I built a clean venv from the repo's own pinned `requirements.txt` (numpy 1.26.4 / statsmodels 0.14.2 / pytest 8.2.2) and ran the README's headline command in `bankspeak-public`:

```
$ python -m pytest tests/ -q
!!!!!!!!!!!!!!!!!!! Interrupted: 12 errors during collection !!!!!!!!!!!!!!!!!!!
12 errors in 3.16s
```

Zero tests run, against README:79's "341 tests, no corpus needed." Cause: 11 of the 12 errors are `ModuleNotFoundError: No module named 's09a_imf_articleiv_frame'` and one is a missing `tools/imf_corpus_to_pipeline.py`. Both were stripped by `tools/build_public_repo.py:62–72` — `re.compile(r"(^|/)imf(?!_document_index)", re.I)` and `re.compile(r"articleiv", re.I)` match the *filenames* of two of the project's own source modules, one of which (`src/s09b_wb_p0_frame.py:34`) imports it at module scope. Ignoring the 12 uncollectable modules, 133 pass, 1 skips, and 5 more fail on `docs/IMF_permission_sample_list_1064.csv` and `data/meta/frozen_sampling_imf_v1.csv` — legitimately withheld files that should gate a `pytest.skip`, not a failure.

Second half: `tools/make_paper_tables.py:47–72` reads `data/meta/frozen_sampling_v2.csv`, `data/meta/extraction_log.csv`, `data/meta/ocr_log.csv` and `data/features/family_counts.csv`; `make_paper_figures.py:54` reads `data/features/classic.csv`. `grep` finds **none** of the five anywhere in `tools/prepare_zenodo_deposit.py` — not in `INCLUDE_FILES`, `INCLUDE_TREES`, or the hash-only lists (it stages `frozen_sampling_v1.csv`, not v2). Because `rows()` returns `[]` for a missing path and Table 1's denominator comes only from `frozen_sampling_v2.csv`, the generator dies rather than warns:

```
File "tools/make_paper_tables.py", line 112, in t1_corpus
    f"({tot['extracted']/tot['sampled']:.1%}), "
ZeroDivisionError: division by zero
```

So DAS's "Each numbered table and figure in the manuscript is regenerated by a named command" would be false even after the deposit is uploaded.

**Edits.** Add `src/s09a_imf_articleiv_frame.py` and `tools/imf_corpus_to_pipeline.py` to an allowlist in `build_public_repo.py` (they are the project's own code; the DENY comment "request/permission lists: IMF titles" describes `IMF_permission_sample_list_1064.csv`, not these), skip-guard the 5 permission-gated tests, add the five missing files to `INCLUDE_FILES`, re-cut a release, and update every DOI reference to it in one pass.

### F3. Two printed numbers the code contradicts

**(a) Block-origin sensitivity — wrong shift, and the reported case is the unrepresentative one.** `PAPER_DRAFT_v2.md:618`: "Shifting the origin of the same three-year partition by two years, however, gives P1 = 164/512 = **0.3203**." I enumerated all 512 sign patterns on the real P1 and P2 restricted score vectors, using the frozen `bootstrap_engine.build_design` / `_fit`:

| offset | P1 exact p | P2 exact p |
|---|---|---|
| 0 (preregistered) | 8/512 = 0.0156 | 50/512 = 0.0977 |
| 1 | **164/512 = 0.3203** | 78/512 = 0.1523 |
| 2 | 8/512 = 0.0156 | **18/512 = 0.0352** |

The 0.3203 figure is a **one**-year shift. A two-year shift leaves P1 exactly where the preregistered origin puts it. Only three distinct nine-block partitions of 27 years exist, and the paper reports the single one that inflates P1 while omitting the one under which P2's exact p drops to 0.0352 — below the 0.05 Holm threshold P2 would face. §8:964's take-away ("one word family, one post-period year, and one block origin") rests on that one case.

**Edit.** Print the full 3 × 2 table above at §6.2 and correct "two years" to "one year." The honesty argument survives the correction and is stronger for being complete; the "twentyfold" phrasing should be attached to the offset that actually produces it.

**(b) IMF retrieval routes sum to 1,069, not 1,064.** `SUBMISSION_DATA_AVAILABILITY.md:38` and `PAPER_DRAFT_v2.md:1028` both print "**710 came from static paths, 354 were resolved through a public web archive, and five through media or sequence paths**" as a partition of the corpus. `09_submission/imf_document_index.csv` has 1,064 data rows. The frozen SAP (`02_frozen_design/SAP_FINAL_DRAFT_20260820.md:83–84`) gives the disjoint tally: L1 static 705, L1b media 4, L1c sequence 1, L2/L2b archive 354 = 1,064. 710 = 705 + 4 + 1 is the *non-archive total*, so the five media/sequence documents are counted twice.

**Edit.** "705 came from static paths, four through a media tree, one through a bounded verification-gated sequence, and 354 through a public web archive." One line, two files.

## 3. Worth fixing

### F4. Two calibration sentences the code does not support

`tools/passp_calibration.py:103–104` draws `shock = rng.normal(0, SIGMA_DELTA, size=len(uy))` over unique **years** and adds `shock[searchsorted(uy, v)]` to every row of that year — both institutions get the same δ_t — while `bootstrap_engine.build_design` carries a saturated set of year dummies (27 years, 26 dummies + constant, 30 columns on 54 cells). The shock is absorbed. Two readers independently reproduced this: empirical size with the shock (0.0530 P1 / 0.0430 P2 at n=3000) is statistically indistinguishable from pure Poisson with no shock at all (0.0480 / 0.0443), and on P2 the shocked arm is the *smaller*. The project already knows why: `docs/PREREG_DRAFT_v0.5.md:346` and `src/mde_sim.py:8` both say "the previous common year shock was absorbed by C(year) and generated no identifying dependence," which is why `mde_sim` replaced it with a WB-specific differential shock. So supplement §S1's rationale — "A pure Poisson null would understate the variance the design actually faces and would flatter the test" — is unsupported by its own script's output, and §6.2:623's "a null carrying the design's own year-level shock" describes a shock the preregistration had retired.

Second: Table 4 (`PAPER_DRAFT_v2.md:505`) labels the PASS-E percentile intervals "95% CI." Two independent coverage harnesses put actual coverage of the true β=0 at 0.855 ± 0.035 (P1) / 0.868 ± 0.033 (P2) under a correctly specified Poisson null, and 0.815 / 0.790 under the differential shock; `sd_boot` runs 0.71–0.81× the true sampling SD, which is what transplanting unstandardized Pearson residuals does at n=54, p=30, mean leverage 0.556. §7:887 says only that no coverage study was run.

Both are reporting defects, not verdict defects, and I want to be explicit about direction: the intervals reach C2 and C3 only through `_excludes_zero`, where being too narrow is *permissive*, and both conditions failed anyway — C3 on its `_same_sign` conjunct (guard β −0.067 on P1, −0.439 on P2 against +0.586 / +0.332), C2 on an infeasible standardized arm. Correct calibration would only harden the preregistered null.

**Edits.** Relabel S1 as a Poisson-null size check, add a differential-shock arm (it is one function call to `mde_sim.simulate_joint` at θ=0), correct §6.2:623, and either report the measured coverage in S1 or relabel Table 4's column "percentile bootstrap interval (nominal 95%; coverage not established, see §7)."

## 4. Looked at and cleared

Nothing was withdrawn wholesale, but the skeptic pass killed six specific over-claims that reached me. Recording them so they are not re-raised:

- **"§9 carries a stale DOI"** — false. §9:1007 cites 22158882 = v1.1.0, which is current; `PLOS_SUBMISSION_CHECKLIST.md:156–163` correctly says so and asks only for a re-cut because the repo has moved past that release.
- **"Nothing flags the missing evidence-deposit DOI"** — false. `PLOS_SUBMISSION_CHECKLIST.md:123` tracks it explicitly, and the author raised it to reviewers himself in `docs/THIRD_EYE_PROMPT_v3_20260829.md:84`.
- **"An unresolvable DOI"** — no. 22158882, 22152944 and 22152945 are all minted; 22152945 is superseded, not dead, and the evidence deposit has no DOI because it does not yet exist.
- **"Nothing in the paper is regenerable"** — overstated. From the archived repo alone a reader can run `plos_compliance.py`, `make_vancouver_refs.py`, `build_submission_pdf.py`, and hash-verify the comparator corpus against the deposited index.
- **"PASS-P over-rejects by ~70% under the differential shock"** — refuted. `mde_sim.simulate_joint` at θ=0 with the same σ_δ=0.3205, ρ=0.5 gives marginal size 0.0473 (P1) / 0.0440 (P2) at nominal 0.05, consistent with the MDE doc's own θ=0 family type-I of 0.039. The ~0.09 figure appears only when the shock is layered on the real fitted null, and zeroing `WB_cyear` drops it to 0.062 — the driver is the fitted differential trend the paper already flags, not the shock. Every value cited also sits inside PREREG §8's own acceptance band [0.025, 0.10].
- **"PASS-E intervals gate C2 and C3"** — the Table 4 intervals do not; `_variant_ok` and `cond3` test different objects (the NB2/standardized arms and the guard refit), and neither failure is width-sensitive.
- **"PASS-E is the narrowest of four routes"** — true on P1, false on P2, where the paper's own HAC(3) route returns the narrower [0.074, 0.534].

## 5. Unverified

These were reported by a single reader and fell below the verification cap. I did **not** check them; treat each as a lead, not a finding. Three that I did happen to confirm in passing are marked ✓ and are folded into F1–F3 above; the rest are unchecked.

- Frozen `mom_alpha` (no d.o.f. correction, 30 parameters on 54 cells) cannot detect overdispersion, so C2's NB2 arm cannot fail and its reported pass carries no information. *(`bootstrap_engine.py:30–33`; the most consequential unverified item — it would hollow out a passing stability check.)*
- ✓ Block-origin p of 0.3203 is a one-year shift — **confirmed and elevated to F3(a)**.
- §6.4:801 / Abstract:36 compare P1's 2020–22 event-study bin (+0.661, a cumulative level contrast) against β̂ = 0.586 (a deviation from trend) — the conflation the paper elsewhere forbids.
- H-SHARED's interval clears zero by +0.0029 after 1,607 of 9,999 draws are discarded; neither the discard rate nor the margin is stated.
- Both Liang citations mis-described (§2:131–133); neither analyses peer review, and the peer-review study supplying three Tier-1 families is uncited.
- §2:129–138 / §4:278–282 invoke excess-vocabulary estimation to license an *imported* fixed lexicon where every cited work derives its word set from the corpus under study; the promised per-word provenance is said not to exist.
- §2:152–155 cites Bai & Perron (1998) for what is actually a ranking of candidate cuts by coefficient magnitude.
- §2:123 attributes "Studies of Bank and Fund documents" to three works, none of which studies the IMF.
- ✓ Public repo does not import / pytest collects nothing — **confirmed and elevated to F2**.
- ✓ Deposit omits Table 1's inputs — **confirmed and elevated to F2**.
- Abstract's 374→300-word cut deleted the three rising pamphlet features, leaving the Tier-2 bureaucratese register — which §1 says is *not* one of the five features Moretti and Pestre named — as the only quantified increase supporting "The trajectories reproduce."
- §6.2:689 / S7:154's "ten times the bootstrap SD" holds for P1 prevalence only; the other three validation outcomes sit at 2.0×–6.5×.
- §6.2:676 "did not begin at the boundary the design placed it at" states an onset fact the design cannot establish, two sentences before conceding diffusion "could plausibly lag by a year."
- §6.4's `placebo_sig_frac` denominator appears nowhere; the values imply six placebo cuts, making "every false breakpoint" six of six.
- Five numbers could not be checked at all because their source CSVs are outside both permitted directories: the 22.23/33.53 excluded-file rates, the τ-deleted refit β = 1.042, Table 6's rank source, the OCR 1.012× calibration, and the "61 replaced, 4 kept, of 65" spacing ledger.

## 6. The single largest remaining risk

The paper's entire warrant is that it is more careful than the work it reconstructs — `PAPER_DRAFT_v2.md:109` commits that "every count, rate and coefficient reported here is regenerated from `data/` by committed code" — and that warrant is what a PLOS ONE editor will test first and cheapest. Right now the test fails in public: the Data Availability field carries an unfilled bracket, the deposit it names does not exist, the archived code runs no tests on a clean install of its own pinned requirements, and two numbers in the manuscript disagree with the code that allegedly produced them, one of them (0.3203 at a one-year, not two-year, offset) inside the very sensitivity analysis offered as proof of candour. None of that touches the confirmatory null, which is sound — but PLOS ONE screens data availability before peer review, and an editor who finds a placeholder in the DAS, follows the DOI to a repository with no data, and then runs `pytest` and gets zero tests will not reach §6 at all. The risk is not that a reviewer rejects the science; it is that the paper never gets a reviewer. Every one of these is fixable in a day, and they should all be fixed in one pass, ending with a fresh tagged release whose DOI is then propagated to the manuscript, supplement, DAS, cover letter and README together.