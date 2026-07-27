---
name: plan-research
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__test_run_quant
description: >
  Plan a Wealthink research report before building it — capture the user's
  intent, check which data sources and tracked news already cover it, find the
  gaps, and produce a concrete build plan (which modules to reuse vs create, which
  sources/tags/templates to use). Use when the user wants a *new* report or
  research workflow and isn't sure what to build yet — "I want to start tracking
  X", "help me set up research on Y", "what should my weekly pack contain?".
  Advisory and interactive; ends by handing off to the build skills.
---

# Plan a Research Report

This is the **front of the funnel**: turn a vague goal ("I want to track the gold
market for my clients") into a concrete, buildable plan, then hand off to
`build-qual-module` / `build-quant-chart` / `research-reports` to build it. This
skill **plans and advises — it does not create anything**; creation happens in the
build skills after the user approves the plan.

## Step 1 — Capture intent (ask)

Before looking at anything, understand the goal. Ask the few questions that change
the plan (batch them, don't interrogate):

- **Purpose** — internal research, or a deliverable distributed to clients/LPs?
- **Audience** — who reads it, and how sophisticated are they?
- **Coverage** — which instruments / topics / asset classes?
- **Cadence** — one-off, or recurring (daily / weekly / monthly)?
- **Shape** — a single analysis, or a multi-section report?

## Step 2 — Explore what the workspace already has (discover)

Never plan in a vacuum — see what's already there to reuse (via `discover`):

- `list_all_modules` — existing modules that may already cover part of the goal.
- `list_templates` — existing report templates to extend rather than duplicate.
  Pass `page_size: 5–10` or `q=<search>` to keep it tight; leave `include_layout`
  off, since layouts aren't part of planning.
- `list_tags` — which topics/instruments are already tracked as event tags.
- `list_data_sources` / `list_qual_data_sources` — the sources available to draw on.
- `list_events` (small limit, filtered by a candidate tag) — confirm the tracked
  news stream actually has coverage for the topic.

## Step 3 — Gap analysis (reasoning)

Compare the goal against what exists. Decide, per piece of the goal:

- **Already covered** — an existing module/template does this; reuse it.
- **Coverable now** — a data source and/or tracked-news tag exists; a *new* module
  over it will work.
- **Gap** — the data point isn't in any available source or tracked tag. Say so
  plainly. If it needs a *new tracked topic*, note that event trackers are
  provisioned by Wealthink (app / account manager), **not** created through Claude
  (see `market-news`).

## Step 3.5 — Look at one real payload per new source (step)

**Before you write a single module's `context` or classification rule, fetch one
real record from each data source the plan will use and read it.**

This is the cheapest step in the skill and the one that saves the most. Rules
written from an assumed schema get revised over and over once real data arrives —
and because sibling modules share those rules, every revision is paid N times. One
look up front replaces all of it.

For each source the plan introduces:

- `get_data_source_endpoints(source)` — what it actually exposes.
- Pull **one** real record: a small `run_quant_chart` / `test_run_quant` against
  the endpoint, or a narrow `list_events` for a news source. One row is enough;
  you are reading the schema, not the data. Use `data="both"` — you need field
  names *and* a couple of real values.

Then derive, and write down for the user:

- **Field names** — exactly as they come back, not as you'd expect them named.
- **Precision and units** — is a weight `0.0432` or `4.32`? A price in rupees or
  paise? Dates in what format?
- **Classification rules, grounded in a real value.** This is where assumptions
  cost most. If the plan needs "cash vs equity", find the field that actually marks
  it (for a holdings payload that is often `sector_name: "Unspecified"`) rather
  than inferring one from the fund's name or an absent field.
- **Nulls and edge rows** — what does a missing value look like, and is it a real
  category or an error?

Carry those into Step 4 as *stated* rules, so the user can correct them while it is
still a sentence in a plan rather than N modules that all encode the same mistake.

> If a payload contradicts the plan, say so now. A plan built on the wrong field is
> not a plan the user can approve meaningfully.

## Step 4 — Present the build plan (skill)

Lay out a concrete, ordered plan the user can approve:

```
Plan: Weekly Gold & Rupee Client Brief (weekly, client-facing)

Reuse (already in your workspace)
  • qm_abc…  Gold Market SWOT            → as-is
Data rules (from a real payload — confirm these)
  • Weights arrive as 0.0432 → render as 4.32%
  • Cash rows are marked sector_name "Unspecified", not a null sector
Create (fan out — rules proven against a real payload)
  • Qual:  "Rupee drivers digest"        → events, tag: rupee · source: news
  • Quant: "MCX Gold near-month 7D"      → candlestick, expiry from get_expiry_dates
  Acceptance: each returns its named sections, non-empty, for the current week
Assemble
  • Template "Weekly Gold & Rupee Brief" → order: news summary → gold chart → SWOT → rupee digest
  • Frequency: weekly · client-facing → plan to share via share-report

Gaps / notes
  • LBMA spot price not in current sources — would need a new data source or tracker.
```

Show: modules to reuse vs create (with fetch type / tags / sources for each), the
template and its section order, the cadence, and any gaps.

## Step 5 — Start building? (ask → handoff)

Ask whether to proceed. On yes, **hand off** — do not create here:

- New qualitative analyses → `build-qual-module`
- New charts → `build-quant-chart`
- Assemble the report → `research-reports`
- (Later) lay it out → `generate-layout`; share it → `share-report`

### Tell the build skills whether this batch can fan out

They build several modules **concurrently by default** — serialising them costs
2–4 minutes each. What they need from you is the one judgement you're better placed
to make: **does this batch rest on anything unproven?**

State it explicitly in the handoff, in one line:

- **"Fan out — rules proven."** The field/precision/classification rules in Step 3.5
  came from a real payload, each spec has acceptance assertions, and the sources
  have produced correct output here before. Build all of them at once.
- **"First contact — prove `<spec name>` first."** The batch shares something
  nothing has tested yet: a data source new to this workspace, a new classification
  rule, or a new shared output format. Name the most representative spec to
  test-run before the rest go out. This costs one round-trip **per source**, not
  per batch.

Nominate the representative spec yourself — you know which one exercises the risky
rule. And prefer a test-run to a build for the check: `test_run_qual` /
`test_run_quant` validate a spec without persisting anything.

## Notes

- This skill only reads and reasons; the confirm-before-create gate lives in the
  build skills. Don't create tags, sources, or modules here. Reading one real
  payload (Step 3.5) is a read, and it is the exception that pays for itself.
- `plan_required` / 402 on a read → relay it plainly and plan around what the
  workspace can access.
- Everything is scoped to the user's workspace — never imply cross-org data.
