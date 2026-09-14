"""
One-off test: run the extraction step against a real, full-length
sustainability report instead of the two-sentence toy example, to see
whether extraction holds up on messy real-world PDF text (jumbled
headers, pull-quote boxes, table of contents, etc.).

Not part of the final app, safe to delete once we've seen the result.
"""

import pdfplumber
from extraction import extract_claims

PDF_PATH = "../sample_reports/starhub_2025.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"

print(f"Extracted {len(full_text)} characters from {PDF_PATH}")
print("Calling Claude to extract claims, this is a bigger input than the toy example, may take a bit longer...")

claims = extract_claims(full_text)

print(f"\nFound {len(claims)} claims:\n")
for i, c in enumerate(claims, 1):
    print(f"{i}. [{c['claim_type']}] {c['claim_summary']}")
    print(f"   Source: {c['source_sentence']}")
    print()
