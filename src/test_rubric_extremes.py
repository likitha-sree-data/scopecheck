"""
test_rubric_extremes.py

Sanity check: does the rubric score a maximally strong claim as green
and a maximally weak claim as red? This bypasses extraction entirely
and hand-constructs both claims directly, to test the scoring logic
in isolation from any messiness in real report text.

Run: python test_rubric_extremes.py
"""

from scoring import score_claim

STRONG_CLAIM = {
    "source_sentence": (
        "We achieved a verified 35% absolute reduction in Scope 1 and "
        "Scope 2 greenhouse gas emissions between our 2018 baseline and "
        "2024, calculated in accordance with the GHG Protocol Corporate "
        "Standard and independently assured by an external auditor under "
        "ISO 14064-3."
    ),
    "claim_summary": "35% absolute Scope 1+2 reduction since 2018, GHG Protocol methodology, third-party assured",
    "claim_type": "historical_reduction",
}

WEAK_CLAIM = {
    "source_sentence": "Our goal is to reach net zero emissions across our operations.",
    "claim_summary": "Commitment to reach net zero emissions",
    "claim_type": "net_zero_or_carbon_neutral",
}


def run_check(label, claim, expected_tier):
    print(f"\n{'=' * 60}")
    print(label)
    print("=" * 60)
    print(f"Claim: {claim['source_sentence']}")

    result = score_claim(claim)

    print(f"\nExpected tier: {expected_tier.upper()}")
    print(
        f"Actual tier:   {result['tier'].upper()} "
        f"({result['ratio'] * 100:.0f}% of {result['applicable_count']} applicable criteria met)"
    )

    print("\nPer-criterion breakdown:")
    for a in result["assessments"]:
        print(f"  [{a['status']:>15}] {a['criterion_id']}: {a['reasoning']}")

    passed = result["tier"] == expected_tier
    print(f"\n{'PASS' if passed else 'FAIL'}: expected {expected_tier}, got {result['tier']}")
    return passed


if __name__ == "__main__":
    results = []
    results.append(run_check("TEST 1: Maximally strong claim (should score GREEN)", STRONG_CLAIM, "green"))
    results.append(run_check("TEST 2: Maximally weak claim (should score RED)", WEAK_CLAIM, "red"))

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {sum(results)}/{len(results)} checks passed")
    print("=" * 60)
    