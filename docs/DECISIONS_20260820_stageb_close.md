# Stage-B closing decisions

Date: 2026-08-20. Taken under Ali's standing instruction to decide as much as
possible with a publishable GIQ/IP&M paper as the criterion. Each is marked
reversible; none edits a frozen artifact.

## D-1. The §11.5 fallback is NOT triggered

§11.5: "The RQ1/measurement-paper fallback triggers **iff neither branch ({P0}
nor {P1, P2}) survives the Stage-B gates** by that date; P0 failing its gates
alone is not a fallback trigger (the family is then {P1, P2})."

That sentence describes exactly the present situation. G1–G4 are **P0
candidate-selection** gates — §2.3 makes {P1, P2} the family that obtains *when
no candidate passes*, not a candidate that must itself pass. {P1, P2} is
therefore not gated, and the fallback condition is not met.

The purposive reading is available and was considered: G4 encodes what the
design means by "can support a confirmatory claim", the P1/P2 family now misses
that standard by four to five times, and one could argue a family that would
fail the design's own power gate has not "survived the Stage-B gates".

**It is rejected, and for the project's own reason.** That reading would
reinterpret a frozen rule *after* measuring an inconvenient quantity. Adopting
it would be an outcome-adjacent change to the decision structure — the exact
failure mode preregistration exists to foreclose, and the one this repository
polices everywhere else. The literal text governs.

Consequence: **the confirmatory P1/P2 analysis runs as preregistered**, after
the SAP freeze. Declining to run one's own preregistered test upon discovering
it is underpowered is a worse position than running it and reporting the bound —
scientifically and to a reviewer.

## D-2. The power bound travels with every confirmatory result

Not a footnote and not an appendix. Every H-DIFF estimate is reported adjacent
to: 80% family power is unreachable on the preregistered θ grid under all three
companion settings; at θ = 0.60, the design's own G4 threshold, power is
0.159–0.216. A null is reported as uninformative rather than as absence of
effect; a rejection is reported with its winner's-curse caveat.

## D-3. Paper framing is a separate decision from D-1, and was previously conflated

`docs/PAPER_STRATEGY_20260820.md` recommends RQ1 as the spine and RQ2 as a
bounded result. That is a **presentation** choice about what leads the paper. It
does **not** require the §11.5 fallback and does not reduce the confirmatory
analysis's status. Earlier framing in this session ran the two together; they are
separated here. The analysis runs; the paper leads with the eighty-year series.

## D-4. §7.4 does not gate the SAP freeze

The deferred step-4 patch to `s06` must precede any NLL reporting. But §12 puts
NLL confirmatory claims out of scope and §2 makes NLL exploratory only, so it
constrains no SAP constant. **Decision:** the SAP states that no NLL number
appears in any output until the §7.4 regeneration has run, and the freeze does
not wait on it.

## D-5. The A11 SAR arm stays a population-definition sensitivity, and cannot rescue power

A5.4 declares it: the operational-genre analysis repeated with Staff Appraisal
Reports appended to the PAD stratum under the same per-year cap, reported
alongside the frozen-definition result and never in place of it.

Worth stating explicitly now that power is measured: **the SAR arm cannot
improve the confirmatory power.** SAR is PAD's predecessor series and covers the
period *before* 1997, while the confirmatory contrast is bounded below at
**1999** by the IMF Article IV frame's own start (the Fund published no Article
IV staff reports before the April 1999 pilot). SAR therefore contributes no year
inside the common window. And within the window, adding documents was measured
not to help — tripling every panel moved power at θ = 1.2 from 0.48 to 0.53.

The arm keeps exactly the role A5.4 gave it and acquires no new one.

## D-6. The 2027-01-15 descriptive snapshot

Stated as a constant, not work: the §11.4 descriptive update uses a second frame
snapshot on **2027-01-15**, covering all 2026-dated records indexed at that
snapshot, reported in an appendix and never pooled into any confirmatory
analysis.

## What remains, and is not mine

**The SAP freeze itself.** Its content is now complete —
`docs/SAP_READINESS_20260820.md` carries every Stage-B constant with its value
and hash, and the three items that were open this morning are closed. What
remains is an external timestamp from Ali's OSF/Zenodo account and the final
authorship wording. One action, not a work item.

Until it happens, `s03` and everything downstream stay unrun, OCR of the 194
scans included, per `docs/DEVIATION_20260820_stageb_retrieval.md` D1.

---

## Addendum (same day, later): rulings D-7 to D-10 — the flagged documents

Taken under the same standing instruction, after
`docs/EXTRACTION_DEFECTS_20260820.md` put four questions to the operator and the
operator delegated them back. All four are reversible; none computes or is
informed by any study outcome — every input to these rulings is an extraction-
quality measurement.

## D-7. The 70 spacing-loss documents: take D9's own fallback, verified

Re-extract from `pdfurl` via PyMuPDF (`tools/refetch_server_txt_defects.py`),
which is D9's second branch applied to exactly the documents whose first branch
failed — no new rule. A re-extraction replaces the text only when it measures
better on the statistic that condemned it; a document that fails to improve is
**excluded and counted** in the §7 intention-to-sample table, never silently
kept. The refetch is text download and waits behind the SAP freeze.

## D-8. Language: exclude whole, under existing precedent

- `pad/2005/6336275` (wholly French) is **excluded under D11**. This follows the
  repository's own precedent exactly: `s10`'s resolved-review list already
  excludes `30458125` as `resolved:translation_D11`.
- The **11 bilinguals** (English report + French/Spanish annexes, ten in `icr`)
  are **excluded whole as the primary rule**, with an include-whole sensitivity
  arm reported alongside. Segmenting out the annexes would preserve more signal,
  but a segmentation rule drafted after inspecting these specific documents
  invites the post-hoc objection even though no outcome informed it; whole-
  document exclusion is the conservative, preregistrable line. One of the
  eleven (`icr/2026/40113264`) is outside the confirmatory window anyway
  (§11.4), so the confirmatory cost is ten documents in P1's pre-period —
  disclosed, not hidden.

## D-9. The 2 mojibake documents: OCR, same verification

`pad/2018/29809040` and `annual_report/2007/8514715` go through the OCR path —
rasterising bypasses the broken ToUnicode CMap — under the same accept-only-if-
it-measures-better criterion. The 2002 and 2007 Annual Report units are then
reassembled, returning two years to the RQ1 series.

## D-10. No new automatic gate for icr/pad; the scan becomes a mandatory diagnostic

Adding an exclusion gate to the confirmatory panels *after* inspecting the
corpus would itself be the researcher degree of freedom this project polices,
even with clean hands on outcomes. Instead:

1. `tools/corpus_quality_scan.py` is a **mandatory diagnostic**: it runs before
   features on every corpus (the IMF corpus included, once `s03` exists for it),
   and every flag is resolved by an explicit, recorded ruling — this addendum
   being the ruling for everything currently flagged.
2. The 12 `low_prose_borderline` documents are **kept**: they are genuine
   English prose diluted by tables (en_share 0.09–0.15, all above the 0.05
   alarm). Four of the twelve are moot (already excluded by `s10`'s title
   rules), and the two `pad` borderlines are also in D-7's refetch set, whose
   remedy should lift them out of the borderline band — verified by re-running
   the scan after the refetch.
3. The scan re-runs after D-7/D-9 remedies; any *new* flag gets a dated ruling
   before the analysis proceeds.

---

## Addendum 2026-08-27: rulings D-11 to D-13 — the flags the gate stopped on

The quality gate halted the post-SAP run, which is what D-10 built it to do:
the corpus grew by 2,806 extracted documents (the Stage-B redraw that Stage-A
never downloaded) and brought 12 hard-class flags no ruling covered. All twelve
are fresh instances of classes already ruled; none is a new phenomenon, and the
existing criteria decide them without amendment. Recorded as new numbers rather
than folded into D-8/D-9 so the dated record shows what was known when.

**The IMF corpus is clean.** All 1,064 documents scanned, zero flags of any
class. The OCR path did its work: the era whose extraction was the study's
worst structural threat now reads as ordinary prose.

## D-11. Eight more bilingual ICRs — excluded whole, as D-8

`icr/1997/731789`, `icr/1997/731935`, `icr/1998/731648`, `icr/2000/888115`,
`icr/2001/1089542` (Spanish), `icr/2001/1552041`, `icr/2005/6050764`,
`icr/2005/6067516`. Each is an English Implementation Completion Report with
French or Spanish annexes appended, French/Spanish function-word share above
English in every case. D-8's reasoning applies unchanged, including its reason
for preferring exclusion over segmentation, and its include-whole sensitivity
arm now covers nineteen documents rather than eleven.

Confirmatory cost, disclosed: **eighteen ICR documents excluded from P1**, all
of them pre-period. That direction matters and is stated plainly — removing
pre-period documents from one panel is not neutral to a pre/post contrast, so
the intention-to-sample table carries the per-year counts.

## D-12. Three more broken-CMap documents — OCR, as D-9

`icr/2014/18923059`, `pad/2018/29947076`, `pad/2018/30375008`. The two 2018
PADs carry the same substitution as `pad/2018/29809040` already ruled
(`ŽĐƵŵĞŶƚŽĨ dŚĞtŽƌůĚĂŶŬ` for "Document of The World Bank"), which makes four
documents from one year sharing one broken font encoding — a World Bank
production artifact, not a random fault. `icr/2014/18923059` is a different
substitution again. All three go to the OCR path under D-9's criteria and are
added to `ocr_overrides.csv`.

## D-13. The 2008 lending-data table — kept, and the reason is D-10's

`annual_report/2008/34063917`, 427 tokens of a lending table. It is not a
defect: it is a genuine annex volume of the Annual Report, and the assembled
2008 unit passes QC with it (measured: the flagged volumes are 14.8% of that
unit's tokens, and every other QC-passing year is 0.0%). D-10 keeps such
material rather than pruning the corpus after inspecting it; the assembly gate
is the preregistered instrument for deciding what a fiscal-year unit contains,
and it has already decided.

Its `table_dump_suspected` flag is therefore ruled **not a defect** and enters
`d13_kept.csv` so the gate stops re-raising it.

## A defect in the D-7 remedy, found and repaired before it spread

Recorded here because the tool's own docstring named this failure mode and then
committed it. D-7 replaced text only when the re-extraction improved on the
statistic that condemned it — **one-sided**. Mojibake tokens are SHORT, so
replacing readable text with garbage passes both tests: mean token length falls
and the long-token share falls to zero.

It happened once. `annual_report/2007/8514626` was replaced at mean token length
**3.05** against a corpus median of 5.56 — ten standard deviations below, not an
improvement but a different failure. Measured across all 62 replacements, that
was the only one outside the healthy band (the other 61 landed 4.8–6.4, median
5.31), so the damage was contained and is now undone: the raw `server_txt` was
intact and the original extraction regenerated from it.

The criterion is now two-sided — a re-extraction must improve **and** land
inside the band the corpus itself defines — with the band derived at runtime
rather than hardcoded, a `kept_original_outside_band` outcome distinct from
`no_improvement`, and a regression test that builds mojibake, confirms it passes
both one-sided tests, and asserts the band is what refuses it.

## Addendum 2026-09-03: ruling D-14 — the three IMF-derived aggregates

**Question.** May `data/analysis/imf_frame_publication.json`,
`imf_frame_publication.csv` and `imf_cadence_balance.json` be redistributed in
the public code mirror, as they already are in the evidence deposit?

**Basis.** The written permission of 2026-08-20 (`docs/IMF_ACCESS_COMPLIANCE_
20260820.md`, items 5 and 6): no redistribution of the documents or of
extracted text; derived outputs only. The three files hold, per fiscal year,
listing-hit counts, eligible counts, sampled counts, inclusion probabilities,
the cap flag and the per-cell seed, and a cadence tally. None holds a title, a
URL or a sentence of any document. The public build's content scan reads every
byte of them and refuses on an IMF identifier.

*Correction, same day.* As first written this ruling said none of the three
held a report number. The content scan then refused `imf_frame_publication.json`
for 78 of them: the within-cell fragility check had written the report number
of each unselected document it dropped, and none of those 78 is among the
1,064 in the published index. A report number is a catalogue identifier and
not extracted text, but the compliance record describes an identifier footprint
of exactly the analysed documents, and this would have widened it to documents
never retrieved. The tool now withholds the id (the fragility estimate is what a
reader needs), the file was regenerated, the evidence deposit was rebuilt from
it, and the ruling stands on the corrected file. The scan did what it is for.

**Ruling.** They are derived, non-substitutive outputs of the kind the
permission allows, and are redistributable. They join the mirror's include
list; the deny rule is narrowed to exempt exactly these three paths; the
content scan still runs on them. Made by the author on the instruction that the
remaining open items be closed, and recorded here so it is a ruling and not a
default.

