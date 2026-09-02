# Note on the data-availability statement — NOT for submission

Kept out of `docs/SUBMISSION_DATA_AVAILABILITY.md` so it cannot be pasted into a
journal form by accident. (The filename was missing from this sentence, which
made the instruction unfollowable.)

The hash manifest establishes **identity, not availability**, which is why
`data/meta/imf_document_index.csv` and the retrieval routes described in the
statement matter more than the hashes do. (This note used to say "the publisher
route above", which points at nothing in a standalone file.)

If PLOS's data-availability check asks for a named contact rather than a
publication service, the IMF's Communications Department is the correct
addressee. That is a fallback, not the primary claim. The primary claim is that
these documents are published and are served without credentials from
`www.imf.org`, which is how all 1,064 analysed here were obtained — every one at
HTTP 200 from that host, none from a web archive.

What the statement deliberately does **not** say is that access is frictionless.
Our own measurements contradict that: the CMS returned 403 to an identified
research client, `doi.org` and `elibrary.imf.org` returned 202 with an empty
body, and a byte-checked probe of 20 documents found the static path serving a
real PDF for 16 and the DOI serving a document for none. Every measurement was
made by a non-browser client, so the statement does not assert what a human
reader with a browser meets — we did not test that, and an earlier draft asserted
it anyway.
