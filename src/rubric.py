"""
rubric.py

The credibility rubric ScopeCheck uses to evaluate emissions-reduction
and net-zero claims found in corporate sustainability reports.

Design notes (why these 7 criteria and not others):

Each criterion below reflects a real, recognized weak point that shows
up again and again in corporate climate disclosures, drawn from how the
GHG Protocol, the Science Based Targets initiative (SBTi), and groups
that audit corporate net-zero pledges (e.g. the New Climate Institute's
Corporate Climate Responsibility Monitor) actually evaluate claims.
The point isn't "is this claim true," which no automated tool can
verify, it's "is this claim written in a way that COULD be verified."

Scope note: this rubric only covers emissions-reduction and net-zero
claims. It intentionally does not attempt to cover water use, DEI,
supply chain labor, or other ESG claim types. See README for why.
"""

RUBRIC_VERSION = "0.2.0"

CRITERIA = [
    {
        "id": "baseline_year",
        "name": "Baseline year specified",
        "question": "Does the claim state what year the reduction is measured against?",
        "why_it_matters": (
            "\"We cut emissions by 30%\" is meaningless without a base year. "
            "A 30% cut since 2005 (a common, favorable base year for many "
            "industries) is a very different claim than 30% since 2020. "
            "Cherry-picking a high-emissions base year is one of the most "
            "common ways to inflate a reduction percentage."
        ),
    },
    {
        "id": "scope_specificity",
        "name": "GHG Protocol scope specified",
        "question": (
            "Does the claim specify which scope(s) it covers: Scope 1 "
            "(direct emissions), Scope 2 (purchased energy), or Scope 3 "
            "(value chain, e.g. suppliers, product use, business travel)?"
        ),
        "why_it_matters": (
            "Scope 3 is usually 70-90% of a company's total footprint for "
            "non-industrial companies, and it's also the hardest to measure "
            "and the easiest to leave out."
        ),
    },
    {
        "id": "absolute_vs_intensity",
        "name": "Absolute vs. intensity-based reduction",
        "question": (
            "Is the reduction reported in absolute terms (total tons of "
            "CO2e) or intensity terms (emissions per unit of revenue, "
            "product, or output)? If intensity-based, is the absolute "
            "trend also disclosed?"
        ),
        "why_it_matters": (
            "A company can report an improving emissions intensity while "
            "its absolute emissions are still rising, simply by growing "
            "revenue or output faster than it improves efficiency."
        ),
    },
    {
        "id": "third_party_verification",
        "name": "Third-party verification or assurance",
        "question": (
            "Is there any mention of external assurance, e.g. a named "
            "auditor, ISO 14064 verification, limited or reasonable "
            "assurance, or a recognized standard-setter (SBTi validation, "
            "CDP disclosure)?"
        ),
        "why_it_matters": (
            "Self-reported, unaudited figures are the norm, not the "
            "exception, but a claim that names a specific verifier or "
            "standard is materially harder to fabricate or quietly revise "
            "later."
        ),
    },
    {
        "id": "time_bound_target",
        "name": "Time-bound target with interim milestones",
        "question": (
            "For forward-looking claims (net zero, carbon neutral, etc.), "
            "is there a specific target date AND at least one interim "
            "milestone, not just a distant end goal?"
        ),
        "why_it_matters": (
            "\"Net zero by 2050\" with no interim milestones lets a company "
            "defer all real action for decades while claiming climate "
            "leadership today."
        ),
    },
    {
        "id": "offset_disclosure",
        "name": "Offset/credit reliance disclosed",
        "question": (
            "If the claim involves \"net\" reductions, carbon neutrality, "
            "or net zero, does it disclose how much of the claim relies on "
            "purchased offsets or credits versus actual emissions cuts?"
        ),
        "why_it_matters": (
            "\"Net\" is doing a lot of work in \"net zero.\" A target that's "
            "60% offset-reliant is a fundamentally different, and much "
            "weaker, claim than one that's 90% real reduction."
        ),
    },
    {
        "id": "methodology_reference",
        "name": "Recognized methodology referenced",
        "question": (
            "Does the claim reference a recognized accounting standard or "
            "framework (GHG Protocol, SBTi, CDP, TCFD/ISSB) rather than an "
            "unstated or proprietary methodology?"
        ),
        "why_it_matters": (
            "Without a named standard, there's no way to compare this "
            "company's numbers to any other company's, or to know if the "
            "methodology changed between reporting years to flatter the "
            "trend line."
        ),
    },
]

RISK_TIERS = {
    "green": {"min_ratio": 0.8, "label": "Well-substantiated"},
    "yellow": {"min_ratio": 0.4, "label": "Partially substantiated"},
    "red": {"min_ratio": 0.0, "label": "Weak / unverifiable as written"},
}


def score_tier(ratio: float) -> str:
    """
    Map a met-points-to-applicable-criteria ratio (0.0-1.0) to a risk
    tier. Criteria marked not_applicable for a given claim are excluded
    from the ratio, so a claim isn't penalized for a criterion that
    never applied to it in the first place.
    """
    if ratio >= RISK_TIERS["green"]["min_ratio"]:
        return "green"
    if ratio >= RISK_TIERS["yellow"]["min_ratio"]:
        return "yellow"
    return "red"


if __name__ == "__main__":
    for c in CRITERIA:
        print(f"[{c['id']}] {c['name']}")
        print(f"  Q: {c['question']}")
        print()