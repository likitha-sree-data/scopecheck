"""
scoring.py

Step 2 of the ScopeCheck pipeline: given one extracted claim, score it
against the 7-criterion credibility rubric (see rubric.py), one
criterion at a time, with reasoning for each.

This step does NOT re-read the whole report, it works only from what
extraction.py already pulled out: the source sentence and claim type.
Keeping this input small is also what keeps this step cheap.
"""

import json
import os
from anthropic import Anthropic
from rubric import CRITERIA, score_tier

SCORING_MODEL = "claude-haiku-4-5-20251001"

SCORING_TOOL = {
    "name": "record_assessment",
    "description": "Record the credibility assessment for one emissions/net-zero claim against the rubric.",
    "input_schema": {
        "type": "object",
        "properties": {
            "assessments": {
                "type": "array",
                "description": "One assessment per rubric criterion, in the same order the criteria were given.",
                "items": {
                    "type": "object",
                    "properties": {
                        "criterion_id": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["met", "partially_met", "not_met", "not_applicable"],
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "One sentence explaining the status, referencing the claim's actual wording.",
                        },
                    },
                    "required": ["criterion_id", "status", "reasoning"],
                },
            }
        },
        "required": ["assessments"],
    },
}

SCORING_PROMPT = """You are scoring one claim from a corporate sustainability report against a credibility rubric.

Claim (type: {claim_type}):
"{source_sentence}"

For EACH of the following criteria, decide if the claim, AS WRITTEN, meets it, partially meets it, does not meet it, or if the criterion doesn't apply to this type of claim at all.

{criteria_block}

Judge only the sentence given. Do not assume missing information exists elsewhere in the report. If a criterion doesn't apply to this claim type (for example, offset disclosure doesn't apply to a claim that never mentions "net" anything), mark it not_applicable rather than not_met.

Call record_assessment with one entry per criterion listed above, in order."""


def _format_criteria_block() -> str:
    lines = []
    for c in CRITERIA:
        lines.append(f"- {c['id']}: {c['name']}\n  {c['question']}")
    return "\n".join(lines)


def score_claim(claim: dict, model: str = SCORING_MODEL) -> dict:
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    prompt = SCORING_PROMPT.format(
        claim_type=claim["claim_type"],
        source_sentence=claim["source_sentence"],
        criteria_block=_format_criteria_block(),
    )

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=0,
        tools=[SCORING_TOOL],
        tool_choice={"type": "tool", "name": "record_assessment"},
        messages=[{"role": "user", "content": prompt}],
    )

    assessments = []
    for block in response.content:
        if block.type == "tool_use":
            assessments = block.input["assessments"]
            break

    points = 0.0
    applicable_count = 0
    for a in assessments:
        if a["status"] == "not_applicable":
            continue
        applicable_count += 1
        if a["status"] == "met":
            points += 1.0
        elif a["status"] == "partially_met":
            points += 0.5

    ratio = points / applicable_count if applicable_count else 0.0

    return {
        **claim,
        "assessments": assessments,
        "applicable_count": applicable_count,
        "met_points": points,
        "ratio": round(ratio, 2),
        "tier": score_tier(ratio),
    }


if __name__ == "__main__":
    from extraction import extract_claims

    sample_text = """
    In 2025, we achieved a 22% reduction in Scope 1 and Scope 2 emissions
    compared to our 2019 baseline. We remain committed to sustainability
    and continue to explore new ways to reduce our environmental impact.
    Our goal is to reach net zero emissions across our operations.
    """

    claims = extract_claims(sample_text)
    for claim in claims:
        scored = score_claim(claim)
        print(json.dumps(scored, indent=2))
        print("---")
