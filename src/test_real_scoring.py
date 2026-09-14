"""
One-off test: run extraction AND scoring against the real report, to
see the full pipeline's output distribution on real, messy claims
before building the interface on top of it.
"""

import pdfplumber
from extraction import extract_claims
from scoring import score_claim

PDF_PATH = "../sample_reports/starhub_2025.pdf"

with pdfplumber.open(PDF_PATH) as pdf:
    full_text = ""
    for page in pdf.pages:
        full_text += (page.extract_text() or "") + "\n"

print(f"Extracted {len(full_text)} characters from {PDF_PATH}")
claims = extract_claims(full_text)
print(f"Found {len(claims)} claims, scoring each against the rubric...\n")

tier_counts = {"green": 0, "yellow": 0, "red": 0}

for i, claim in enumerate(claims, 1):
    scored = score_claim(claim)
    tier_counts[scored["tier"]] += 1
    print(f"{i}. [{scored['tier'].upper()} - {scored['ratio']}] {claim['claim_summary']}")

print("\n--- Summary ---")
for tier, count in tier_counts.items():
    print(f"{tier}: {count}")
