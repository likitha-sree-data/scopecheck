"""
One-off script: extract the StarHub PDF to a plain text file, so the
text can be copied into the app's paste box without going through
Streamlit's file uploader (which can't see files inside the Codespace,
only files on your local device).
"""

import pdfplumber

with pdfplumber.open("sample_reports/starhub_2025.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += (page.extract_text() or "") + "\n"

with open("starhub_extracted.txt", "w") as f:
    f.write(text)

print(f"Wrote {len(text)} characters to starhub_extracted.txt")