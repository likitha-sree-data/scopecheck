"""
app.py

Streamlit interface for ScopeCheck. Paste or upload a sustainability
report, run it through extraction and scoring, and see every flagged
claim with its full per-criterion reasoning, not just a color.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pdfplumber
from extraction import extract_claims
from scoring import score_claim
from rubric import CRITERIA

st.set_page_config(page_title="ScopeCheck", layout="wide")

TIER_COLORS = {"green": "#1a7f37", "yellow": "#9a6700", "red": "#cf222e"}
TIER_LABELS = {
    "green": "Well-substantiated",
    "yellow": "Partially substantiated",
    "red": "Weak / unverifiable as written",
}
STATUS_LABELS = {
    "met": "MET",
    "partially_met": "PARTIAL",
    "not_met": "NOT MET",
    "not_applicable": "N/A",
}

st.markdown(
    """
    <style>
        h1 { font-weight: 700; letter-spacing: -0.02em; margin-bottom: 0; }
        .tier-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.06em;
            color: white;
            vertical-align: middle;
        }
        .claim-meta { font-size: 12px; color: #6b7280; margin: 4px 0 10px 0; }
        .claim-text { font-size: 15px; font-weight: 600; margin: 10px 0 6px 0; }
        .source-quote {
            font-size: 13px; color: #4b5563; font-style: italic;
            border-left: 3px solid #e5e7eb; padding-left: 12px; margin: 10px 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("ScopeCheck")
st.caption(
    "Reads a sustainability report and flags emissions or net-zero claims "
    "that are written in a way that can't actually be verified, citing the "
    "exact sentence for every flag."
)

with st.expander("What this does and doesn't do"):
    st.markdown(
        "- Flags **how a claim is written**, not whether the underlying numbers are true.\n"
        "- Only covers emissions-reduction and net-zero claims, not water, DEI, or supply chain claims.\n"
        "- Scored by an LLM against a 7-criterion rubric, not a certified auditor. Treat results as a triage signal.\n"
        "- Claim count can vary slightly between runs on the same report."
    )

tab1, tab2 = st.tabs(["Paste text", "Upload PDF"])
report_text = None

with tab1:
    pasted = st.text_area("Paste report text here", height=200)
    if st.button("Analyze pasted text", type="primary"):
        report_text = pasted

with tab2:
    uploaded = st.file_uploader("Upload a sustainability report (PDF)", type="pdf")
    if uploaded and st.button("Analyze PDF", type="primary"):
        with pdfplumber.open(uploaded) as pdf:
            report_text = ""
            for page in pdf.pages:
                report_text += (page.extract_text() or "") + "\n"

if report_text:
    if not report_text.strip():
        st.error("No text found to analyze.")
    else:
        with st.spinner("Extracting claims..."):
            claims = extract_claims(report_text)

        if not claims:
            st.info("No quantified emissions or net-zero claims were found in this text.")
        else:
            st.success(f"Found {len(claims)} claim(s). Scoring each against the rubric...")

            tier_counts = {"green": 0, "yellow": 0, "red": 0}
            scored_claims = []

            progress = st.progress(0)
            for i, claim in enumerate(claims):
                scored = score_claim(claim)
                scored_claims.append(scored)
                tier_counts[scored["tier"]] += 1
                progress.progress((i + 1) / len(claims))
            progress.empty()

            col1, col2, col3 = st.columns(3)
            col1.metric("Well-substantiated", tier_counts["green"])
            col2.metric("Partially substantiated", tier_counts["yellow"])
            col3.metric("Weak / unverifiable", tier_counts["red"])

            st.divider()

            for i, sc in enumerate(scored_claims, 1):
                color = TIER_COLORS[sc["tier"]]
                label = TIER_LABELS[sc["tier"]]

                with st.container(border=True):
                    st.markdown(
                        f"<span class='tier-badge' style='background-color:{color};'>{sc['tier'].upper()}</span>"
                        f"<span class='claim-meta'>&nbsp;&nbsp;{label} &middot; "
                        f"{sc['ratio']*100:.0f}% of applicable criteria met</span>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"<div class='claim-text'>{sc['claim_summary']}</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='source-quote'>&ldquo;{sc['source_sentence']}&rdquo;</div>",
                        unsafe_allow_html=True,
                    )

                    with st.expander("Full rubric breakdown"):
                        for a in sc["assessments"]:
                            criterion = next((c for c in CRITERIA if c["id"] == a["criterion_id"]), None)
                            name = criterion["name"] if criterion else a["criterion_id"]
                            status = STATUS_LABELS.get(a["status"], a["status"].upper())
                            st.markdown(f"**{name} — {status}.** {a['reasoning']}")