"""
Quick one-off script to sanity check what pdfplumber pulls out of a
real PDF report, before running it through the extraction pipeline.
Not part of the final app, just a scratch check, safe to delete later.
"""

import pdfplumber

with pdfplumber.open("sample_reports/starhub_2025.pdf") as pdf:
    print(f"Total pages: {len(pdf.pages)}")
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text() or ""
        full_text += text + "\n"

    print(f"Total characters extracted: {len(full_text)}")
    print("--- First 1000 characters ---")
    print(full_text[:1000])
