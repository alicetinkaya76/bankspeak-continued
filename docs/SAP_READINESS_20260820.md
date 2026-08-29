# SAP freeze readiness — Stage-B constants inventory (2026-08-20)

PREREG §11.3 ends Stage-B with "the final SAP (this document, every Stage-B
constant filled), externally timestamped. Only then: text download and feature
processing." §11.5 makes 31 October 2026 the hard Stage-B deadline. This
inventory exists so the freeze is a review, not an excavation.

**The freeze itself is not the assistant's to perform:** it needs an external
timestamp from Ali's OSF/Zenodo account, and the final analysis-plan wording is
an authorship decision. Everything below is the material that decision needs.

## Filled — value and hash on record

| Stage-B constant | Value | Artifact / sha256 |
| --- | --- | --- |
| Stage-A seal | commit `20af74e7` | `round14_package_20260814.zip` `0ca03b60…21114` |
| OSF registration | `10.17605/OSF.IO/5C9J8`, `2026-08-16T04:21+00:00` | GATE 0 closed |
| Calibration (Wald unlicensed) | `calibration_ok=false` | `cf033e2f…3203` |
| Branch decision (write-once) | family `{P1P2}` | `d9ddbaec8a6e38dd1db5abe7913c9c40840224170a5e4a56d72193ad3aa5c985` |
| G2 measured, all candidates | cem 22, cpf 24, scd 8 vs threshold 25 | `data/meta/g2_metadata_report.json` |
| G3 metadata support | 1.0 for all three (13/13, 13/13, 19/19) | same |
| IMF Article IV frame | 2,788 units, 1999–2025 | `5e465df668a8d940…6ae3` |
| WB P0 candidate frame | 491 units | `c25ae6002ba37f95…370a` |
| IMF frozen sample | 1,064 units | `baa91fa7fa4b92af…3d7e` |
| **WB Stage-B frame (A6)** | 15,385 rows, 1946–2026, captured 2026-08-20 | `d98424163dbe3c92…74d2` |
| **WB frozen sample — annual_report** | 331 (P-A descriptive) | `77f1855cc4a31a7f…e13a` |
| **WB frozen sample — icr** | 1,246 (P1) | `1b0c1698840fd5e5…abed` |
| **WB frozen sample — pad** | 1,161 (P2) | `948f4ee1a559b171…9111` |
| **IMF corpus retrieval** | 1,064/1,064 downloaded and verified | manifest `adc0ecdd…7e39`, verification `92b5d742…5118` |
| Confirmatory cutoff | publication date ≤ 2025-12-31; 2026 flagged, 315 WB rows | §11.4 |
| Prior-inspection overlap | 748 of 2,738 (27.3%) | `docs/A7_FRAME_DRIFT_20260820.md` |
| Seeds | global 20260806; per-cell `SHA256("20260806\|inst\|genre\|year")` | `src/percell_seed.py` |
| Suite | 279 passed, 1 warning | — |

## Open — the SAP cannot be frozen until these are settled

1. ~~**MDE / §8 power constants for P1P2.**~~ **MEASURED 2026-08-20** —
   `docs/MDE_P1P2_20260820.md`. It was run rather than argued about, because a
   reviewer will ask and a post-hoc power analysis is worthless.

   **MDE₈₀ is unreachable: 80% family power is not attained anywhere on the
   preregistered θ grid (0.00–1.20), under ANY of the three companion settings.**
   Final at full precision (1,000 reps, B = 9,999, all curves complete): at
   θ = 0.60 — the very threshold G4 sets — power is **0.159 / 0.158 / 0.216**
   for companion zero / half / full. Held to its own standard the family misses
   by a factor of four to five. Type-I behaviour is
   sound (0.03 at θ=0 against α=0.05), so the engine is fine and the design is
   underpowered. σ_δ = 0.3205 is the whole story: at σ_δ = 0 the same setup
   gives MDE₈₀ = 0.65. Tripling every panel's documents moves power at θ=1.2
   from 0.48 to 0.53, so **sampling more documents is not a fix** — the binding
   constraint is a year-level shock and there are only three post years.

   The SAP constant is therefore not a number but a statement, and it must be in
   the SAP *before* the analysis runs. What remains open is the consequence, not
   the measurement: whether this triggers the §11.5 fallback is a
   preregistration reading and Ali's call.

2. ~~**The §7.4 regeneration.**~~ **DECIDED** (`DECISIONS_20260820_stageb_close.md` D-4): does not gate the freeze; the SAP states that no NLL number appears until it has run. Original text: The sealed `ppl.csv` must be regenerated before any
   NLL reporting (five bad GPT-2 records purged, the hardware-dependent CPU
   subsample abolished). NLL is exploratory only, so this may not gate the SAP —
   but the SAP should say which.

3. ~~**The unlocked-degrees-of-freedom audit.**~~ **DISCHARGED 2026-08-20** —
   `docs/AUDIT_20260820_researcher_dof.md`, done against git history rather than
   recollection. The outcome definition (`config.yaml: markers`) is
   byte-identical across the 2026-08-07 09:13 boundary and
   `s05_features_markers.py` has one commit ever. Everything altered afterwards
   lands outside the confirmatory family, is provably neutral to the primary
   outcome, or is a dated adversarial-review repair. The single outcome-informed
   choice is the guard family, which the preregistration discloses itself.

4. ~~**A11 SAR sensitivity arm**~~ **DECIDED** (D-5): keeps A5.4's role, and cannot rescue power — SAR precedes 1997 while the confirmatory window is bounded below at 1999 by the IMF frame, so it adds no year inside it.

5. ~~**The 2027-01-15 descriptive snapshot**~~ **STATED** (D-6).

## Also open, and outside the SAP

- **OCR**: 194 documents / 12,004 pages, bounded to 1999–2004. An `s03`-stage
  act, deferred behind the freeze per `docs/DEVIATION_20260820_stageb_retrieval.md`
  D1, and unbudgeted in every version of the plan so far.
- **Zenodo mirror** for the raw archives (`wb_p1p2_raw/` 33 MB, `imf_articleiv_raw/`,
  `wb_p0_raw/`, and the 2.47 GB IMF corpus is licensed and stays local).
- Small debts carried from the handover: round-6 report export into the ruling
  chain, round-1 review text, git history cleanup, two R14 maintenance notes, and
  the runbook ordering correction (PHASE 4 consumes PHASE 5's `mde_p0.json`).
