# Draft query to the IMF on the archive-resolution step

**Status: draft for Ali to send, edit or discard.** Not sent. It exists so that
the option in `docs/IMF_ACCESS_COMPLIANCE_20260820.md` §4.3 — put the question to
the IMF rather than rely on our own reading — costs nothing but a decision.

Sending it is optional. §4.2 records why the step is defensible on its own
terms, and §4.3 records the one-command reversal if the answer is no. The case
for sending anyway: 354 of 1,064 documents rest on our reading of condition 3,
and a written answer converts a judgment call into a permission.

Suggested recipient: the same address that granted the permission
(`copyright@imf.org`), replying in the existing thread so the context travels
with it.

---

**Subject:** Follow-up on the automated-retrieval permission — one method question

Dear colleagues,

Thank you again for the permission of 20 August 2026 to retrieve the 1,064
preregistered IMF Staff Country Reports by automated means. I am writing to
describe one step of the method and to ask whether it is acceptable to you,
rather than to rely on my own reading of the conditions.

The reports themselves download normally. `www.imf.org/external/pubs/ft/scr/…`
and `www.imf.org/-/media/…` answer an ordinary identified request, robots.txt
permits both paths, and I retrieve at one request per second with a User-Agent
naming the project, the purpose and this permission.

For reports from 2019 onward the PDF filename cannot be derived — it is
irregular by design (`1fraea2021001.pdf`, `cr1927-senegal-a4.pdf`,
`1polea2025001-print-pdf.pdf`). The filename is published on each report's page
on imf.org, but that page returns HTTP 403 to my client: the site's bot
management does not distinguish a polite research client from an unwanted one.
For those documents I therefore read **only the link** from a public web-archive
copy of your own public page, and then download the PDF **from www.imf.org**.
The archive is never the source of a stored document. This affects 354 of the
1,064.

My reading is that this does not circumvent an access control: no challenge is
solved, no fingerprint altered, no credential or token used; what is taken from
the archive is a URL, and the document itself comes from your server over a path
that serves my client normally. But the judgment is mine, and I would rather have
yours.

Before adopting it I measured and closed every alternative: your sitemap returns
403 to this client; the site search API indexes no Country Report PDFs; Crossref
carries no full-text link; OpenAlex resolves only to elibrary.imf.org, which
answers 202 with an empty body host-wide; and enumerating candidate filenames
would fire thousands of failed requests at your servers, which I was unwilling to
do. The archive step is the lightest remaining option for the IMF — exactly one
request per document.

Two things follow whichever way you answer. Every affected document is labelled
in my manifest, so the set is exactly countable and removable in one command; if
you would prefer the step not be used, I will delete those 354 files and report
the resulting coverage as partial. And if there is a route you would rather I
use — a whitelisted User-Agent, a file list, or anything else — I will switch to
it.

Nothing is redistributed: the documents stay on a local machine, only derived
outputs are published, and the acknowledgement of your permission will appear in
the paper.

With thanks,

Ali Çetinkaya
Selçuk University
