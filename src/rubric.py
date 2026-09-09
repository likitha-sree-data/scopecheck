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
A claim that fails most of these criteria isn't necessarily false, but
it's unfalsifiable as written, which is the definition of a weak claim.

Scope note: this rubric only covers emissions-reduction and net-zero
claims. It intentionally does not attempt to cover water use, DEI,
supply chain labor, or other ESG claim types. See README for why.
"""

RUBRIC_VERSION = "0.1.0"

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
        "met_example": "\"a 42% reduction in Scope 1 and 2 emissions since our 2019 baseline\"",
        "weak_example": "\"we've significantly reduced our emissions over the years\"",
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
            "and the easiest to leave out. A claim that says \"emissions\" "
            "with no scope breakdown is very often a Scope 1+2 only claim "
            "wearing a bigger number's clothing."
        ),
        "met_example": "\"a 15% reduction in Scope 1 and Scope 2 emissions; Scope 3 reporting begins next fiscal year\"",
        "weak_example": "\"our total emissions are down 15%\"",
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
            "revenue or output faster than it improves efficiency. "
            "Intensity-only claims, with no absolute figure alongside, are "
            "a well-documented way to describe worsening climate impact "
            "using improving-sounding numbers."
        ),
        "met_example": "\"emissions intensity improved 12% per unit of revenue; absolute Scope 1+2 emissions grew 3% due to production expansion\"",
        "weak_example": "\"our carbon intensity improved 12% this year\"",
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
            "later than an unverified internal number."
        ),
        "met_example": "\"verified by [Auditor] under ISO 14064-3; targets validated by the Science Based Targets initiative\"",
        "weak_example": "\"we are proud of the progress we've made\" (no verification mentioned anywhere in the report)",
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
            "leadership today. A credible target has near-term checkpoints "
            "that make backsliding visible before it's too late to matter."
        ),
        "met_example": "\"net zero by 2040, with a 50% absolute reduction target by 2030\"",
        "weak_example": "\"committed to achieving net zero emissions\"",
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
            "weaker, claim than one that's 90% real reduction. Reports that "
            "use \"net zero\" or \"carbon neutral\" without ever mentioning "
            "offsets are usually hiding a heavy reliance on them."
        ),
        "met_example": "\"85% of the reduction comes from operational changes; the remaining 15% is addressed through verified carbon removal credits\"",
        "weak_example": "\"we achieved carbon neutrality across our operations\" (no mention of offsets anywhere)",
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
        "met_example": "\"calculated in accordance with the GHG Protocol Corporate Standard\"",
        "weak_example": "\"using our internal sustainability tracking methodology\"",
    },
]

RISK_TIERS = {
    "green": {"min_met": 6, "label": "Well-substantiated", "max_met": 7},
    "yellow": {"min_met": 3, "label": "Partially substantiated", "max_met": 5},
    "red": {"min_met": 0, "label": "Weak / unverifiable as written", "max_met": 2},
}


def score_tier(criteria_met_count: int) -> str:
    """Map a count of criteria met (0-7) to a risk tier key."""
    if criteria_met_count >= RISK_TIERS["green"]["min_met"]:
        return "green"
    if criteria_met_count >= RISK_TIERS["yellow"]["min_met"]:
        return "yellow"
    return "red"