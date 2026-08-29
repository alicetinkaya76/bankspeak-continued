# Stage-0 report — 6 Aug 2026 — verdict: GO (conditional)

## Gate 1 — Novelty: PASS
No published extension of Moretti & Pestre's series past 2012; no LLM-trace study of
World Bank *reports*. Nearest neighbors, each distinguishable:
- Liang et al., "Widespread adoption of LLM-assisted writing across society": consumer
  complaints, corporate press releases, job postings, **UN press releases** (~14% by late
  2024). Not WB, not report genres, not diachronic, no Bankspeak construct.
- Kousha & Thelwall: 12 LLM-associated terms across scholarly databases (delve +1,500%,
  underscore +1,000%, intricate +700%, 2022→2024). Academic register; our Tier-1 source.
- IMF WP 2025/109: LLMs *as analysts* of central-bank communication — inverse question.
- Context asset: WB's own IEG (2023) documented GPT experiments and the enterprise
  "mAI" (GPT-3.5) deployment → institutional adoption of the "treatment" is on record.
- Detector-reliability caveat on record (2026 false-positive controversies, e.g. the
  Commonwealth Prize / Pangram case) → D2's signals-not-proof framing.

## Gate 2 — Access: PASS
`https://search.worldbank.org/api/v3/wds` live, unauthenticated, JSON; returns
`abstracts`, `docdt`, `docty`, `display_title`, `pdfurl`, `txturl`, `guid`; `strdate`/
`enddate` date filters; `rows`/`os` paging; facet enumeration via `fct`. Repository
coverage 1946–present (matches the Bankspeak start year). Single test query: 592 hits.

## Gate 3 — Parametric micro-pilot: CONDITIONAL PASS
Bins: PRE = 1,408 tokens (2006–2021 abstracts + one 2021 press release); POST = 683
tokens (Jun–Jul 2026 press releases). Results:

| metric | PRE | POST |
|---|---|---|
| Tier-1 per 1k tokens | 0.00 | 0.00 |
| Tier-2 per 1k tokens | 1.42 | 24.89 |
| nominalizations /100 | 7.1 | 8.5 |
| "and" /100 | 3.34 | 5.71 |
| mean sentence length | 28.2 | 32.5 |

Reading: large measurable stylistic differences exist and the pipeline works end-to-end,
BUT the bins confound era with genre (→ D1) and Tier-1 needs corpus scale (→ D7). The
micro-pilot's job was to prove measurability and surface design constraints; it did both.

## Binding conditions attached to GO
Genre stratification (D1); IMF comparator before RQ2 claims (D3); internal 1946–2012
replication check (D4); tiered markers with provenance (D5); power gate on Tier-1 (D7);
UNGDC firewall (CLAUDE.md rule 1).

## Timeline
Corpus Sep–Oct 2026 → analysis Nov–Dec 2026 → draft Jan–Feb 2027 → submit Mar 2027.
Kill criteria: detectors disagree beyond preset threshold → RQ2 downgrades to
descriptive; ITS pre-trends violated → trends reported without breakpoint claims.
