# Venue facts, verified against primary sources — 2026-08-28

Companion to `VENUE_RESEARCH_20260828.md`, which left five items explicitly
unverified. All five are now resolved. Each was looked up twice independently and
then adjudicated by a third pass that re-fetched the source; the ÜAK rule, being
the one that changes the plan, I also confirmed myself from the PDF.

**Retrieval date matters.** Everything below was read on 2026-08-28. ÜAK reissues
its criteria per application period and Springer Nature's fee page carries no
date stamp, so both must be re-checked at submission time.

---

## 1. ÜAK — the rule that changes the timetable

> **Only PUBLISHED counts. Accepted, in press, online-first and early access do
> not.**

From the 2026 Mart Dönemi FAQ, Q18, verbatim — I opened the PDF and read it:

> "Buna göre başvuru tarihinden önce elektronik ortamda erişilebilir olsa dahi ön
> basım, ön görünüm, çevrimiçi erken görünüm, "online published" ya da "early
> access", "early view", "available online", "upcoming issues", "in progress",
> "published (early access)", "gelecek sayılar" vb. ibareler içeren, değişiklik
> olma ihtimali bulunan çalışmalar yayımlanmış makale olarak değerlendirilemez."

Q17, same document: a DOI is **not** sufficient — the publication processes must
also be complete.

Source: `uak.gov.tr/documents/documents/6a07202a2ea5f.pdf` (2026 Mart Dönemi SSS).
Criteria table: `.../69affdf9bdbcc.pdf` (Tablo 11, Sosyal/Beşeri/İdari Bilimler).
Note: `uak.gov.tr` fails TLS chain verification in some clients; `curl -4` works.

**Points, Tablo 11 madde 1 (international article, not from the candidate's own
theses):** SCIE or SSCI — Q1 30, Q2 20, Q3 15, Q4 10 · AHCI 20 · **ESCI or Scopus
10** · other international indexes 5. Binding: at least 10 points from (a)–(d)
after the doctorate. Multi-author papers split the points equally; a
single-authored paper takes the full score.

**So a Scopus-only journal does count — at 10 points — and because this paper is
single-authored it clears the madde-1 minimum on its own.** A two-author Scopus
paper would yield 5 and would not.

**Unresolved, and it is the live risk:** the predatory-journal rule (YÖK Genel
Kurul 2021.18.643) classifies journals *only* by Web of Science quartile, so a
Scopus-indexed journal with no WoS quartile is not addressed by the text in
either direction. For a **fee-charging** Scopus-only venue that is an unquantified
risk worth settling in writing before paying anything. It does not arise for a
diamond-OA venue that charges nothing.

---

## 2. Humanities and Social Sciences Communications — APC settled

> **£1,390 / $1,990 / €1,590**, plus VAT or local taxes where applicable.

Both earlier figures were wrong: ~£1,240 is stale and too low, ~£3,500 belongs to
other Nature Portfolio titles. The fee page states a single APC for the journal
and does not break it out by article type.

> "The APC price will be determined from the date on which the article is
> accepted for publication."

So the price is pinned at acceptance, not submission. Three waiver or discount
routes exist on the same page: country-based waivers keyed to the **corresponding**
author, institutional/transformative agreements, and the Springer Nature APC
waivers policy. The page carries **no date stamp** — the only dated text is a 2026
copyright footer — so re-check before submitting.

---

## 3. PLOS ONE — the third-party gate is open in policy

The baseline is strict:

> "PLOS journals require authors to make all data necessary to replicate their
> study's findings publicly available without restriction at the time of
> publication."

But the exception is explicit:

> "For studies involving third-party data, we encourage authors to share any data
> specific to their analyses that they can legally distribute. PLOS recognizes,
> however, that authors may be using third-party data they do not have the rights
> to share."

That is the route this corpus needs: derived counts and a SHA-256 manifest are
distributable, the documents are not. **What cannot be verified in advance is
whether a given submission is accepted under it** — that is an editorial judgement
on the data availability statement, not a policy fact. The statement must name the
restriction, the source, and how another researcher would obtain the same access.

---

## 4. Digital Scholarship in the Humanities — both indexes, contradiction resolved

Clarivate's Master Journal List, ISSN 2055-7671, exact match, coverage field:

> "Web of Science Core Collection: Social Sciences Citation Index | Arts &
> Humanities Citation Index"

> **SSCI yes, AHCI yes.** ESCI no, SCIE no. Stated 2025 JIF 1.0.

The earlier contradiction was not a contradiction: the OUP About page lists only
SSCI, which is an omission on the publisher's side. Clarivate owns the decision.

Under Tablo 11 this is worth 20 points via AHCI, or 10–30 via SSCI depending on
quartile — better standing than the earlier research assumed.

---

## 5. Journal of Cultural Analytics — Scopus yes, Web of Science no, and free

Clarivate MJL, ISSN 2371-4549, all four Core Collection filters active:
**"Found 0 results."** The same session returned an exact match for DSH as a
positive control, so the zero is a real negative rather than a broken query.

Scopus source record 21101046167: **indexed, 2019–2026**, CiteScore 2025 = 1.8,
SJR 0.373, rank #31/1186 in Literature and Literary Theory. Articles before 2019
are not covered.

Fees, from the journal's own policies page:

> "There are no author processing charges (APCs) or submission charges to publish
> with JCA."

Diamond open access, CC BY 4.0, authors retain copyright, archived by Portico.

**So JCA scores 10 points, costs nothing, and carries none of the fee-charging
predatory-rule risk** — the unresolved gap in §1 does not bite here.

---

## What this changes

The earlier research treated March 2027 as a deadline for *acceptance*. It is a
deadline for **publication**, and every queue on the shortlist now has to be
judged on submission-to-publication rather than submission-to-decision. That
sharpens the ranking rather than reversing it:

- **DSH** gains on standing (SSCI **and** AHCI, 20+ points) and loses on the only
  axis that now binds. OUP humanities queues plus a published-not-accepted rule is
  the worst possible combination for this window.
- **PLOS ONE** and **HSSC** keep their positions; both publish quickly after
  acceptance, and HSSC's fee is a third of the worst-case figure that was feared.
- **JCA** rises. It was set aside on the assumption that Scopus-only might not
  count. It does count, it is single-authored so it clears the madde-1 gate alone,
  it is free, and it is the fastest and best intellectual fit on the list. Its
  cost is standing: 10 points against 20–30, and no Web of Science listing.

**None of this is a recommendation.** The trade is between points and probability
of being *published* by March 2027, and only Ali can price that.

## Still to check before acting

1. Whether ÜAK reissues Tablo 11 for the 2026 Ekim period before the application.
2. HSSC's fee page at submission time — it is undated.
3. The predatory-rule status of any fee-charging Scopus-only venue, in writing,
   if one is ever considered. Not needed for JCA.
4. Actual submission-to-publication times for the shortlisted venues, which no
   policy page states and which the author may be able to estimate from recent
   articles' received/accepted/published dates.
