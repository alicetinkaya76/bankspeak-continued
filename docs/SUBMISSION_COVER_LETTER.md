# Cover letter — PLOS ONE

*Submission-ready draft. Bracketed fields are the author's to complete. The
letter deliberately does not cite PLOS ONE's soundness criteria as though they
compel acceptance; an editor reads that as pressure, not as fit.*

---

Dear PLOS ONE Editors,

Please consider my manuscript, **"Reconstructing Bankspeak: Eight Decades of
World Bank Language, a Corpus-Selection Effect, and an Unconfirmed Post-2022
Break,"** for publication as a Research Article.

**The manuscript reports a preregistered test that returned no confirmed effect.
I say so in the first line because an editor who discovers it in paragraph four
is entitled to read the first three as concealment.** What the paper offers is
two positive empirical results and a carefully bounded negative one.

First, it independently reconstructs Moretti and Pestre's widely cited
*Bankspeak* (2015) analysis from primary World Bank documents and extends the
assembled Annual Report series through fiscal 2024. The original corpus, feature
definitions and assembly rules were never released, so the finding has been
discussed far more often than checked. The qualitative trajectories reproduce.

Second, rebuilding the archive produced a measurement result I did not go
looking for and initially got wrong. Over the same fiscal years the same archive
yields a 43% decline in temporal anchoring or a 14% decline, and decomposing that
gap assigns **all** of it to which files count as Annual Reports — the excluded
sibling-organisation volumes trend upward while the Bank's own volumes fall.
Concatenating volumes into fiscal-year units, the operation one would expect to
matter, contributes nothing: for a token-normalised rate it is arithmetically
identical to a token-weighted mean. Earlier drafts attributed the gap to that
concatenation. The correction is in the paper because it is the more useful
finding: the unit of analysis can be inert while document selection is worth a
factor of three.

Third, the reconstructed corpus supports a preregistered comparative interrupted
time-series test of whether Tier-1 LLM-associated vocabulary shows a post-2022
World Bank discontinuity relative to an International Monetary Fund comparator.
No panel satisfies the prespecified decision rule. One panel produces a nominally
small *p*-value and then fails the concentration guard fixed in advance, fails a
leave-one-post-year-out check, loses significance under one preregistered
secondary inference route and falls short of its own Holm threshold under the
other, and shows a pre-period event-study bin exceeding the estimate itself. **An ex ante power analysis, computed before any outcome existed, shows
that an effect of the observed size would have been detected about one time in
five.** That figure is a disclosed design parameter, not a post-hoc excuse, which
is why it appears here rather than only in the discussion.

I therefore report the result as a bound on what this design can establish. It
is not evidence that LLM use had no effect, and it is not document-level AI
detection. No causal attribution to any model or vendor is made anywhere.

**On auditability.** The Stage-A registration (`10.17605/OSF.IO/5C9J8`) and the
separately timestamped Stage-B analysis plan (`10.5281/zenodo.22098259`, sha256
`4aa12279…2677`, published 2026-08-25T15:01:07Z) were both sealed before any
reported outcome was computed. The analysis code, test suite and complete
decision record are archived at `10.5281/zenodo.22158882`. Every table and figure
regenerates from deposited artifacts by a named command, and the manuscript
reports every preregistered sensitivity, including two that earlier drafts had
omitted and one that disagrees with the primary test about which panel is
significant.

**On the restricted corpus, stated here rather than discovered at revision.** The
1,064 IMF Article IV staff reports were obtained under written permission from
the International Monetary Fund that forbids redistributing the documents or
extracted text. I therefore deposit no IMF text. **The IMF publishes these reports
itself**, so access does not run through me: any reader can obtain them from the
Fund's website by country and report number, and the deposit lists all 1,064
documents by report number, year, country, DOI and SHA-256 so that a retrieved
file can be hashed against the copy analysed. I note in the manuscript that the
site is bot-protected and that my own automated collection needed a documented
ladder, including a public web archive for 354 documents; a reader scripting the
same collection should expect that, and a reader opening reports in a browser will
not. I am not a gatekeeper and can neither grant nor withhold access.

**What a reader should do differently.** The transferable result is not the null.
It is that a nominally significant aggregate lexical break can rest on one word
family, one post-period year and one arbitrary block origin, while a sealed
multi-condition rule correctly withholds the claim. Single-family lexicon
indicators of LLM influence are not robust, and a design without a preregistered
concentration check would have reported *p* = 0.0142 as a discovery.

The manuscript is original, is not under consideration elsewhere, and has a
single author. **[Funding, competing interests, preprint and ethics statements as
applicable.]**

Thank you for considering it.

Sincerely,

**[Name, affiliation, ORCID, email]**
