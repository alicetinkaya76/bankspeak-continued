# Extraction defects: five classes, two of them nested in the pre-period

Date: 2026-08-20. Artifacts: `data/meta/corpus_quality_flags.csv`,
`data/meta/ocr_inventory.csv`. Tools: `tools/corpus_quality_scan.py`,
`tools/ocr_prepass.py`. **Nothing is excluded** — this is the adjudication
dossier for a ruling that belongs in the SAP, not in a tool.

## The headline

Two extraction defects are **nested inside the pre-2023 period of a
confirmatory panel**, which is the one placement that manufactures a result:

| defect | where | pre/post |
| --- | --- | --- |
| **Lost word spacing** | **65 of 70 in `pad` (P2)**, 2 icr | 2003–2009; **0 from 2010 on** |
| **No text layer (scans)** | 192 IMF Article IV, 2 WB AR | 1999–2004; **0 post-2023** |

Both depress measurement in the pre-period only. A marker count that is
systematically too low before 2023 and correct after it **is** a post-2022
increase, with no language change required.

## 1. Lost word spacing — the one that was nearly missed

Found by mean-token-length, not by the function-word gate, which is why the
stopword scan saw only 2 of the 70. Median mean token length across 3,125
documents is 5.56; the affected documents run 6.3 to **10.9**, with up to
**17.3%** of tokens ≥ 18 letters — words glued together by the PDF's own text
layer (`PROJECTAPPRAISALDOCUMENT`, `FOROFFICIALUSEONLY`).

Distribution, and it is not uniform:

| period | affected |
| --- | --- |
| 1998–2001 | ~1% |
| **2003–2009** | **7–20%** (2004 peaks at 20%) |
| **2010 onward** | **0.0%** |
| overall <2010 vs ≥2010 | **5.3% vs 0.0%** |

**Measured consequence, without computing any study outcome.** Six common words
were chosen that are confirmed *not* in the Tier-1/Tier-2 lists
(`development`, `project`, `government`, `financial`, `component`,
`institutional`), and their whole-word matches compared against their true
occurrences:

| document | whole-word | actual | **missed** |
| --- | --- | --- | --- |
| `pad/2001/10792808` | 159 | 728 | **78.2%** |
| `pad/2005/5606130` | 625 | 1,215 | **48.6%** |
| `pad/2004/3925662` | 798 | 1,372 | **41.8%** |

Marker families are counted by whole-word matching. In these documents 40–78%
of any such matching is invisible.

**The diagnosis inverted on measurement, and the remedy is clean.** The first
assumption was that our PDF extraction was at fault. It is not:

| extraction method | affected |
| --- | --- |
| `pymupdf` (PDF path) | **0 of 437 — 0.0%** |
| `server_txt` (`txturl` path) | **70 of 2,688 — 2.6%** |

Every affected document came through `txturl`. The defect is in the World Bank's
own plain-text copies; our PDF path is clean.

That is awkward for **D9**, which chose `txturl`-first precisely to avoid
extraction noise, reasoning that such noise "is itself era-correlated (older PDFs
are scans), which would otherwise bias features". The server text carries its own
era-correlated defect, in the opposite direction — 2003–2009, absent from 2010 on,
65 of 70 in P2. **D9's premise holds for scans and fails for spacing.**

The remedy needs no new rule: D9 already specifies `pdfurl` + PyMuPDF as the
fallback, **all 70 affected documents carry a `pdfurl`**, and that path has a
0.0% defect rate. `tools/refetch_server_txt_defects.py` takes exactly that
branch for exactly these documents, replaces text **only when the re-extraction
measures better on the same statistic that condemned it**, and refuses a partial
pass rather than silently skipping. It is gated behind the SAP freeze because
re-fetching is text download (§11.3).

## 2. Scans without a text layer

192 IMF Article IV documents (1999–2004) and 2 WB Annual Reports, 12,055 pages.
Covered in SAP §S9: extraction method is collinear with the estimand, so
`--calibrate` must estimate the OCR-versus-native effect with era held fixed
before the block enters any comparison.

## 3. Mojibake — broken ToUnicode CMaps

Two documents, two *different* substitutions:

- **`pad/2018/29809040`** — 57,439 tokens, **P2**. `ŽĐƵŵĞŶƚŽĨ dŚĞtŽƌůĚĂŶŬ` is
  "Document of The World Bank".
- **`annual_report/2007/8514715`** — 44,516 tokens. `GHS8` is "NOTE",
  `4RTFF4QX` is "A SUMMARY", `4hhxwfpi` is "Accumulated". English prose head,
  garbled body.

Both are OCR-recoverable: rasterising bypasses the CMap entirely.

## 4. Language — one violation and eleven bilinguals

The class is **not** twelve non-English documents. Reading them apart:

- **Wholly non-English (1):** `pad/2005/6336275` — "Document de La Banque
  mondiale … Traduction non officielle du texte en anglais". A clean D11
  violation.
- **Bilingual (11):** English report with French or Spanish annexes appended —
  `icr/1997/731876`, `icr/1998/728010`, `icr/2000/729077`, `icr/2001/1089440`,
  `icr/2001/1552084` (Spanish), `icr/2004/11309689`, `icr/2004/5527314`,
  `icr/2004/6457585`, `icr/2008/10975080`, `icr/2017/29259198`,
  `icr/2026/40113264`. Ten of the eleven are in **`icr` (P1)**.

All arrived through the API's own `lang_exact: English` filter, so the defect is
inherited from World Bank metadata rather than introduced here.

The remedies differ, which is why the split matters: exclusion for the first;
for the eleven, either exclusion or a language-segmentation rule that keeps the
English report and drops the annexes. **Segmenting after seeing the corpus is a
researcher degree of freedom** — the rule has to be preregistered, or the
documents excluded whole.

## 5. Non-prose annexes — mostly already handled

Ten Annual Report documents flagged; **four are already excluded** by
`s10_assemble_ar`'s title rules (the 1996–1998 IFC Investment Portfolios and the
2007 MIGA report). The existing machinery works.

Six remain inside assembled units: the 2007 pair (contents page + the mojibake
volume — together **100%** of that unit's tokens, which is why 2007 correctly
fails QC) and four 2008 table/list annexes (**14.8%** of the 2008 unit).

**A threat that was tested and refuted.** Annex dilution varying by year would
confound the RQ1 trend. Measured across every QC-passing year: **2008 is 14.8%
and every other year is 0.0%.** It is one year's problem, not a trend artifact.

## Two years the AR series can recover

Of the 7 years missing from 1947–2024, five have no documents in the frame at
all. **2002** is two un-OCR'd scans totalling 12 tokens; **2007** is mojibake.
Both come back with OCR — two years returned to the eighty-year series RQ1
rests on.

## What the SAP must settle, before the analysis runs

1. **The 70 spacing-loss documents.** The remedy exists and is D9's own fallback
   (`tools/refetch_server_txt_defects.py`, all 70 have a `pdfurl`, the PDF path
   is 0.0% defective). What the SAP must state is that it will be taken, and the
   verification criterion for accepting a re-extraction.
2. **The 12 language cases** — exclude the one, and rule on the eleven
   bilinguals as a class.
3. **The 2 mojibake documents** — OCR, or exclude.
4. **Whether `icr`/`pad` get a prose gate at all.** `s10`'s covers only Annual
   Reports; §7's "tokens ≥ 1" is what stands behind P1 and P2 today.

Every count above is regenerable from the two tools. None of it required
computing a study outcome, and none was.
