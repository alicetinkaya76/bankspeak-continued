# Third-eye prompt, round 2 (paste everything below the line into the external model)

Round-2 package: revised draft (PAPER_DRAFT_v0.md, v0.2), point-by-point response
(RESPONSE_TO_REVIEW.md), regenerated tables (tables/), robustness battery (robustness/),
figures, and aggregate feature data. No raw document text is included.

---

You are conducting a second-round evaluation of a revised manuscript package. Play THREE
roles in sequence and keep them clearly separated in your output. Be blunt in all three;
optimize for what would actually happen at an SSCI/SCIE venue, not for encouragement.

## Context

You (or a predecessor review you should treat as your own first round) previously found:
a defective 12-token fiscal-year unit (FY2002) and a suspect FY2007 inside the assembled
Annual-Report series; an unidentified post-break slope estimated from two post-break years;
a "2023–2026" label on evidence ending in 2024; placebo fractions of 0.50–1.00 undercutting
any 2023-specific "discontinuity" claim; Tier-1 circularity and concentration risk;
perplexity-validity concerns; untreated within-stratum composition; multiplicity; and a
recommendation to lead with genre-aware measurement discipline rather than a dated break.
The authors claim to have implemented most demands and documented the rest as planned work.
RESPONSE_TO_REVIEW.md is their point-by-point account; PAPER_DRAFT_v0.md is the revised
draft; robustness/ contains the new evidence (QC log, leave-one-year-out, empirical
breakpoint scan and ranking, median/trimmed aggregation, per-word decomposition).

## Role 1 — Handling editor

1. Give a disposition for the revised package as if it (plus a completed IMF comparator
   section) were submitted to Government Information Quarterly: desk-reject, major
   revision, minor revision, or conditionally acceptable — and the single sentence you
   would write to the authors explaining why.
2. State whether the reframing (measurement-discipline lead; "ramped post-2022 increase"
   instead of "2023 discontinuity") is now consistent with the evidence in the bundled
   tables. If any claim still outruns the data, quote it verbatim.
3. List what must exist in the manuscript BEFORE submission that is still missing
   (distinguish: blocking vs. cosmetic). The authors' own "NOT done" list is at the end of
   RESPONSE_TO_REVIEW.md — judge whether each deferred item is correctly deferred or
   actually blocking.

## Role 2 — Referee (methods)

4. Point-by-point: for each first-round demand (A1–A3, O3–O10 as labeled in
   RESPONSE_TO_REVIEW.md), verdict ADDRESSED / PARTIALLY / NOT ADDRESSED, with one line of
   justification grounded in the bundled files — spot-check the numbers in the response
   against tables/ and robustness/ wherever you can compute them from the CSVs.
5. Assess the NEW evidence on its own terms:
   - Does the breakpoint scan (breakpoint_scan_tier1.csv) support "maximal cuts cluster in
     2022–2025"? Note that later cuts mechanically have fewer post years — does the
     ranking's comparability caveat hold up, and what analysis would fix it?
   - Is the QC gate (min 5,000 tokens, min 15% function-word share) defensible as
     *prespecified*, given it was calibrated on the same 73 units it then filtered? What
     wording or sensitivity analysis would make it clean?
   - Does the leave-word-out result genuinely defuse the concentration concern, or does a
     43% underscore-family share still demand a redefined confirmatory lexicon?
6. Name the single weakest remaining link in the causal-adjacent chain and the cheapest
   analysis that would strengthen it.

## Role 3 — Reference auditor

7. The draft's reference section lists 25 entries with DOIs (plus two DOI-less proceedings
   entries). Independently verify EVERY entry: resolve each DOI (or locate the proceedings
   record) and confirm authors, year, venue, and scope match how the draft uses the work.
   Output a table: entry → VERIFIED / MISCITED (what's wrong) / UNVERIFIABLE. Do not let
   earlier verification claims substitute for your own check.
8. In-text fit: for each reference MODULE (a–f in Section 2), judge whether the cited works
   actually support the intended claims, and flag any work cited for something it does not
   contain.
9. Missing literature: suggest at most 8 additional must-cite works. HARD RULE: only works
   you are confident exist; give authors, year, venue, DOI when known, and a confidence
   label; if unsure, omit. Fabricated citations discredit the entire review — every entry
   you output will be checked against Crossref.

## Output format

Three clearly headed sections (Editor / Referee / Reference audit), each ending with a
ranked action list (blocking items first). English. Do not praise; review.
