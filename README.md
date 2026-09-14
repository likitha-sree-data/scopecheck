# ScopeCheck

An AI agent that reads corporate sustainability reports and flags
emissions-reduction and net-zero claims that are written in a way that
can't actually be verified, citing the exact sentence for every flag.

Built for the AI Builders Hackathon (Sep 2026).

## The problem

Sustainability reports are full of claims like "we reduced our carbon
footprint by 30%" or "we're committed to net zero." Some of these are
backed by real, auditable numbers. Many are marketing language dressed
up as a metric: no baseline year, no scope definition, no third-party
check, no distinction between an actual cut and a purchased offset.

Investors, journalists, and regulators (increasingly under frameworks
like the EU's CSRD and the SEC's climate disclosure rules) need a fast
way to tell which claims in a 100+ page report deserve a closer look.
Reading every report by hand doesn't scale. ScopeCheck is a first pass:
not a verdict on whether a company is lying, but a flag on which
specific sentences are too vague to check.

## How it works

1. **Extract**: an LLM call reads the report and pulls out every
   quantified emissions-reduction or net-zero claim, along with the
   exact sentence it came from.
2. **Score**: a second LLM call evaluates each claim against a 7-point
   credibility rubric (see below), one criterion at a time, with
   reasoning for each.
3. **Report**: results are shown in a web interface, each claim colored
   green / yellow / red by how many rubric criteria it meets, with the
   source sentence and reasoning visible for every flag.

Extraction and scoring are deliberately separate steps rather than one
prompt, so each step can be checked and debugged independently, and so
the reasoning behind a score is traceable rather than a single opaque
output.

## The rubric

Full detail and reasoning for each criterion lives in
[`src/rubric.py`](src/rubric.py). Summary:

| Criterion | What it checks |
|---|---|
| Baseline year specified | Is there a stated year the reduction is measured against? |
| Scope specificity | Does it say Scope 1, 2, or 3 (GHG Protocol), or just "emissions"? |
| Absolute vs. intensity | Is this a real cut in total emissions, or just per-unit efficiency? |
| Third-party verification | Is there any external audit or standard-setter named? |
| Time-bound target | Is there a specific date and interim milestone, not just an end goal? |
| Offset disclosure | For "net" claims, is offset reliance vs. real reduction disclosed? |
| Methodology reference | Is a recognized standard (GHG Protocol, SBTi, CDP) cited? |

This rubric deliberately covers **emissions and net-zero claims only**,
not water use, DEI, or supply-chain labor claims, which each need a
different rubric. Depth on one claim type beats shallow coverage of
all of them.

## Example

Tested against a hand-built maximally-strong claim and a maximally-weak
one, to validate the rubric independent of any single report's mess:

**Strong claim** (scores GREEN, 100% of 5 applicable criteria met):
> "We achieved a verified 35% absolute reduction in Scope 1 and Scope 2
> greenhouse gas emissions between our 2018 baseline and 2024,
> calculated in accordance with the GHG Protocol Corporate Standard and
> independently assured by an external auditor under ISO 14064-3."

Hits baseline year, scope specificity, absolute framing, third-party
verification, and named methodology. Time-bound target and offset
disclosure are correctly marked not applicable, since this is a
historical claim, not a forward-looking or net-zero one.

**Weak claim** (scores RED, 0% of 6 applicable criteria met):
> "Our goal is to reach net zero emissions across our operations."

Fails every applicable criterion: no baseline, no scope, no
verification, no date, no offset disclosure, no methodology. Note that
a claim can be entirely true and still score red here, this rubric
scores verifiability, not honesty.

Also tested against a real 83-page corporate sustainability report,
where it correctly caught a claim (a 19.1% Scope 3 *increase*) that
was stated in body text but absent from the report's own highlights
page.

## Setup

1. Clone this repo and open it in a Codespace, or any environment with Python 3.11+
2. `pip install -r requirements.txt`
3. Get an API key from [console.anthropic.com](https://console.anthropic.com/), then set it as an environment variable: `export ANTHROPIC_API_KEY=your-key-here` (or add it as a Codespaces secret)
4. Run the interface: `streamlit run app.py`

## Status

Built and validated during the hackathon window (Aug 21 to Sep 15, 2026): rubric, extraction, scoring, and interface are complete, tested against hand-built edge cases and a real 83-page corporate sustainability report. See commit history for the full build process.

## Limitations

- This tool flags **how a claim is written**, not whether the underlying numbers are true. A well-written claim can still be based on fabricated data; this tool can't catch that.
- Rubric scoring is done by an LLM, not a certified auditor. Treat output as a triage signal, not a final judgment.
- Extraction and scoring work sentence by sentence. If a report states a claim on one page and its third-party assurance statement 60 pages later, this tool can't connect the two, so a genuinely verified claim can still score lower than it deserves.
- The Anthropic Messages API no longer exposes a temperature or sampling-control parameter, so exact claim counts can vary slightly between runs on the same report. Tier outcomes on well-defined claims have stayed consistent in testing; borderline claims near a rubric boundary are the ones most likely to shift.
- Extraction occasionally includes claims outside its intended scope, most often renewable-energy-mix percentages that resemble emissions claims but measure a different thing. The prompt explicitly excludes these, but exclusion isn't perfect.
- When a report states the same fact in more than one place (a stats callout and body prose, for example), extraction can pull it out twice as separate claims.