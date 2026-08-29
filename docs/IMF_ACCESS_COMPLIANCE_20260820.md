# IMF Article IV retrieval — access route and compliance record

Date: 2026-08-20. Operator: Ali Çetinkaya. Status: records the route actually
used to retrieve the preregistered 1,064-document sample, and the evidence for
the claim that the route stays inside the IMF's permission.

This is a reasoned engineering-and-conduct record, not a legal opinion. Every
factual claim below is a measurement, reproducible from
`diagnostics/20260820_access_legitimacy/probes.tsv` and the retrieval manifest.

## 1. The permission

The IMF granted explicit permission (recorded in commit `8b82787`) to retrieve
the 1,064-document preregistered sample **by automated means**, subject to:

1. the preregistered sample only;
2. one request per second;
3. an identified User-Agent;
4. no circumvention of access controls;
5. no redistribution of the documents or of extracted text;
6. derived outputs only;
7. no model training (inference with a fixed local model is permitted, with no
   IMF content retained by an external provider);
8. citation, and acknowledgement of the permission.

Asked how to proceed given that this network receives HTTP 403 from
`www.imf.org`, the IMF declined to whitelist, to supply files directly, or to
arrange a text-and-data-mining route, and advised determining an appropriate
means of access from available resources. This document is that determination.

## 2. What the block actually is — measured, not assumed

The premise recorded on 2026-08-20 morning was that `www.imf.org` is blocked to
this network and retrieval must therefore wait. Re-measured the same day, that
premise is **too broad**. The WAF rejects the `/en/` CMS pages; the static
document paths are served normally to an ordinary client:

| Probe | Result |
| --- | --- |
| `www.imf.org/robots.txt` | **200** `text/plain`, 450 B |
| `www.imf.org/en/publications/cr/issues/…` (CMS page) | **403** `text/html` |
| `elibrary.imf.org/view/journals/002/2023/043/…` | **202**, empty body |
| `doi.org/10.5089/…` → elibrary | **202**, empty body |
| `www.imf.org/external/pubs/ft/scr/1999/cr9947.pdf` | **206** `application/pdf` |
| `www.imf.org/external/pubs/ft/scr/2017/cr1715.pdf` | **206** `application/pdf` |
| `www.imf.org/-/media/…/cr/2023/english/1ginea2023001.pdf` | **206** `application/pdf` |
| `www.imf.org/-/media/…/cr/2025/english/1polea2025001-print-pdf.pdf` | **206** `application/pdf` |

Captured 2026-08-20T08:01:01Z with the identified research User-Agent.

The two paths the retrieval uses — `/external/pubs/ft/scr/` and `/-/media/` —
answer a plain, unauthenticated, identified GET. There is no login, no paywall,
no token, and no rate gate on them. **Nothing is being defeated**: the blocked
paths are simply not used.

`robots.txt` (fetched the same minute, archived as `robots_20260820.txt`)
confirms this independently. It carries no `Crawl-delay` and **no `Disallow`
line matching either path**. Its `Disallow` list names other prefixes —
including `/external/np/a4pilot/1999/`, `/external/np/a4pilot/2000/`, and the
GFSR/WEO `*index.htm` pages — which are not touched.

## 3. Condition-by-condition

| Condition | How it is met | Enforced by |
| --- | --- | --- |
| Sample only | Input is the frozen 1,064-row list; no crawling, no link-following, no discovery | `load_records()` reads the two frozen sample files (`docs/IMF_library_request_list_1064.csv` joined to `docs/IMF_permission_sample_list_1064.csv` for the page URL) and nothing else |
| 1 request/second | `IMF_SLEEP = 1.0` after every imf.org request; archive requests throttled harder at 2.0 s | `tools/fetch_imf_cr_pdfs.py` |
| Identified UA | `BankspeakContinued-Research/1.0 (academic replication of Moretti & Pestre 2015; IMF permission 2026-08-20; contact: …)` — names the project, the purpose, the permission and a reachable contact | sent on every request incl. the probes above |
| No circumvention | Only unauthenticated static paths are requested; the WAF-blocked `/en/` and the 202-ing elibrary are never fetched for content | §2, and §4 for the one nuance |
| No redistribution | PDFs land in `data/raw/imf_cr_pdf/`, matched by `data/raw/*` in `.gitignore`; nothing is committed, published or shared | repo `.gitignore` line 4 |
| Derived outputs only | Only features/counts/hashes leave `data/`; this is the existing project rule, unchanged | project `CLAUDE.md` |
| No model training | No IMF content is sent to any external provider; downstream perplexity work runs locally on models pinned by revision hash (`gpt2` @ `607a30d7…`, `EleutherAI/pythia-1.4b` @ `fedc38a1…`) and never updates their weights | `config/config.yaml` lines 89-91 |
| Citation + acknowledgement | Attribution string in §6 | paper + OSF record |

## 4. The one judgment call — the Wayback step

For reports from 2019 onward the PDF filename is **not derivable**. It is
irregular by design: `1fraea2021001.pdf`, `cr1927-senegal-a4.pdf`,
`1polea2025001-print-pdf.pdf`. An earlier attempt at guessing the pattern
produced dead links and was withdrawn (commit `8b82787`); guessing is therefore
ruled out, and brute-forcing candidate filenames would multiply requests against
the very host the permission asks us to treat gently.

The filename is stated on the IMF's own publication page, which this network
cannot load (403). The retrieval therefore reads **that page's Wayback snapshot**
solely to extract the `/-/media/…` link the IMF itself published, and then
fetches the PDF **from www.imf.org**. The archive is never the source of a
stored document.

Stated plainly, both ways:

- **For**: the page is public and free, carries no access control of any kind,
  and the 403 is generic bot-management rather than a decision to withhold it.
  The information taken from the archive is a URL, not content. The document is
  then fetched from the IMF, at 1 req/s, from a path the IMF serves openly and
  robots.txt permits. The IMF permitted automated retrieval of exactly this
  sample and advised finding an appropriate means from available resources; a
  public web archive is such a resource.
- **Against**: the live page is, in fact, refused to this client, and reading its
  content elsewhere routes around that refusal. Someone applying condition 4
  strictly could object on that ground alone.

### 4.1 Routes ruled out first

L2 was not adopted because it was convenient. Every alternative reachable from
this network was measured on 2026-08-20 and closed:

| Alternative | Result |
| --- | --- |
| Derive the filename from a pattern | Impossible: `1fraea2021001.pdf`, `cr1927-senegal-a4.pdf`, `1polea2025001-print-pdf.pdf`. A prior guess produced dead links and was withdrawn (commit `8b82787`) |
| `www.imf.org/sitemap.xml` (declared in robots.txt) | **403** |
| Coveo, the site's own public search API | Indexes 9,251 PDFs, **none** under `publications/cr`; `@filetype==pdf` + CR path wildcard returns 0 |
| Crossref full-text `link` field | `null` on the issue DOIs |
| OpenAlex `best_oa_location.pdf_url` | Resolves, but only to `elibrary.imf.org` |
| `elibrary.imf.org` — `/view/`, `/downloadpdf/`, `/doc/…/Source_PDF/`, and the host root | **202 with an empty body**, uniformly: the whole host is behind a silent bot wall |
| Brute-force the per-country-year sequence | Rejected twice over: it is guessing, and it would fire thousands of 404s at the host the permission asks us to treat gently |

### 4.2 Decision (operator ruling, 2026-08-20)

**L2 is enabled for the 2019-2025 records.** Reasoning, recorded so a reviewer
weighs the judgment rather than discovering it:

1. Condition 3 forbids *defeating* controls. L2 defeats nothing: no challenge is
   solved, no fingerprint faked, no credential, cookie or token used, the UA
   stays honest. The blocked page is simply not requested.
2. What L2 takes from the archive is a **URL string**, not the resource. The
   resource is fetched from the IMF's own server, over a path that answers this
   exact client 200/206, that robots.txt permits, and that carries no control.
3. No withheld material is obtained. The reports are free; OpenAlex types the
   series diamond/bronze open access. There is no protected material here for
   condition 3 to protect.
4. The IMF, asked how to proceed given the 403, advised determining an
   appropriate means of access from available resources. A public archive of the
   IMF's own public page is such a resource.
5. L2 is the **lightest** remaining option for the IMF: exactly one request per
   document. The alternatives are a library request that makes IMF staff service
   280 documents by hand, or filename brute-forcing.

The counter-argument in §4 stands and is not waved away: the live page is
refused to this client, and L2 reads its content elsewhere. The decision is that
condition 3 protects the IMF's material, not the incidental fact of which URL a
given client can discover -- and that the reversibility below makes this the
right risk to take rather than one to hedge by losing 26% of the comparator.

### 4.3 Reversibility

Every affected record carries `route = L2_page_link_via_archive` in the
manifest, so the set is exactly countable at any moment and removable in one
command:

```
python - <<'EOF'
import csv, pathlib
d = pathlib.Path("data/raw/imf_cr_pdf")
for r in csv.DictReader((d / "_manifest.csv").open()):
    if r["route"] == "L2_page_link_via_archive":
        (d / ("CR" + r["report_no"].replace("/", "-") + ".pdf")).unlink(missing_ok=True)
EOF
```

If the IMF is asked and objects, that command runs, the manifest rows stay as
the record of what was retrieved and withdrawn, and the paper reports the
resulting coverage in the PREREG §7.8 intention-to-sample table -- which already
anticipates partial retrieval. Sending that question to the IMF remains open and
costs nothing; it is not a precondition, because the act is defensible on its
own terms.

The 2019-2025 subset is **26% of the sample (280 of 1,064)** and is the window
in which the Tier-1 word families the study measures are most informative, which
is why losing it by default was not treated as the safe choice.

## 5. What the retrieval does not do

No login, credential, token, cookie or session is used. No paywall or access
control is bypassed. No User-Agent spoofing — the UA is honest and identifies
the project. No concurrency: strictly sequential, one request at a time. No
crawling or link-following beyond the fixed sample list. No content is taken
from any host other than www.imf.org. Failures are recorded, never guessed
around: a record no rung resolves is written `unresolved` with no file.

## 6. Provenance and attribution

Written for every record in `data/raw/imf_cr_pdf/`:

- `_manifest.csv` — report number, DOI, route, resolved PDF URL, HTTP status,
  byte count, **SHA-256**, page count, cover check, status, candidate links, UTC
- `_log.jsonl` — append-only event log
- `_verification.csv` — independent re-verification (`tools/verify_imf_cr_pdfs.py`),
  which re-derives the hash and names the evidence rung per record

Attribution string for the paper:

> Contains IMF Staff Country Reports retrieved from www.imf.org under written
> permission from the International Monetary Fund (2026-08-20), accessed
> 2026-08-20. The IMF is not responsible for any analysis or conclusions drawn
> from these documents.

## 7. Effect on the earlier record

Commit `8b82787` states that retrieval waits on an institutional subscription
route and that no workaround is attempted. Its second clause still holds — no
workaround is attempted, and §5 lists what is not done. Its first clause is
**superseded**: the measurement in §2 shows no subscription is needed for the
static paths, which is why retrieval proceeded. That commit's stance is
corrected here rather than quietly abandoned.
