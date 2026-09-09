"""
extraction.py

Step 1 of the ScopeCheck pipeline: given the raw text of a sustainability
report, extract every quantified emissions-reduction or net-zero claim,
along with the exact sentence it came from.

This step does NOT judge the claims, that's scoring.py's job.
"""

import json
import os
from anthropic import Anthropic

EXTRACTION_MODEL = "claude-haiku-4-5-20251001"

EXTRACTION_TOOL = {
    "name": "record_claims",
    "description": "Record every quantified emissions or net-zero claim found in the report text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "claims": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source_sentence": {
                            "type": "string",
                            "description": "The exact sentence from the report containing the claim, verbatim.",
                        },
                        "claim_summary": {
                            "type": "string",
                            "description": "A short, plain-language restatement of what is being claimed.",
                        },
                        "claim_type": {
                            "type": "string",
                            "enum": [
                                "historical_reduction",
                                "future_target",
                                "net_zero_or_carbon_neutral",
                            ],
                            "description": (
                                "historical_reduction: a reduction already achieved. "
                                "future_target: a forward-looking goal with a date. "
                                "net_zero_or_carbon_neutral: any claim using the words "
                                "net zero, carbon neutral, or carbon negative."
                            ),
                        },
                    },
                    "required": ["source_sentence", "claim_summary", "claim_type"],
                },
            }
        },
        "required": ["claims"],
    },
}

EXTRACTION_PROMPT = """You are helping audit a corporate sustainability report for specificity.

Read the report text below and find every sentence that makes a QUANTIFIED claim about greenhouse gas emissions or a net-zero / carbon-neutral commitment. This includes:
- Reported reductions ("we cut emissions by X%")
- Future targets ("we will reduce emissions by X% by [year]")
- Net zero, carbon neutral, or carbon negative commitments, even without a specific percentage

Do NOT include:
- Vague statements with no number and no target date ("we care about the environment")
- Claims about water, waste, biodiversity, DEI, or other non-emissions topics
- General mission statements
- Renewable energy adoption or energy-mix percentages ("X% of our electricity comes from renewable sources") UNLESS that sentence also states a specific emissions reduction number, since renewable energy share is a different metric from emissions themselves

For each claim found, extract it exactly as it appears (source_sentence must be a verbatim quote from the text below, not a paraphrase), plus a short plain-language summary and a claim_type.

Report text:
---
{report_text}
---

Call the record_claims tool with everything you find."""


def extract_claims(report_text: str, model: str = EXTRACTION_MODEL) -> list[dict]:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=0,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "record_claims"},
        messages=[
            {"role": "user", "content": EXTRACTION_PROMPT.format(report_text=report_text)}
        ],
    )

    for block in response.content:
        if block.type == "tool_use":
            return block.input["claims"]

    return []


if __name__ == "__main__":
    sample_text = """
    In 2025, we achieved a 22% reduction in Scope 1 and Scope 2 emissions
    compared to our 2019 baseline. We remain committed to sustainability
    and continue to explore new ways to reduce our environmental impact.
    Our goal is to reach net zero emissions across our operations.
    """

    claims = extract_claims(sample_text)
    for c in claims:
        print(json.dumps(c, indent=2))
