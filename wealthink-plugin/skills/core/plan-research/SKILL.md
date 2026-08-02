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

## Step 3.5 — Look at one real payload per new source

One record from a source you haven't used before costs a single call, and it is
usually the difference between rules that hold and rules that get revised. Because
sibling modules share those rules, every revision is paid once per module — so
this is worth doing whenever the plan introduces a source nobody here has run.

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
  • qm_abc…  Gold Market SWOT            → as-is, also used by your Daily Bullion Brief
Data rules (from a real payload — confirm these)
  • Weights arrive as 0.0432 → render as 4.32%
  • Cash rows are marked sector_name "Unspecified", not a null sector
Create
  • Qual:  "Rupee drivers digest"        → events, tag: rupee · source: news
  • Quant: "MCX Gold near-month 7D"      → candlestick, expiry from get_expiry_dates
  Acceptance: each returns its named sections, non-empty, for the current week
Assemble
  • Template "Weekly Gold & Rupee Brief" → order: news summary → gold chart → SWOT → rupee digest
  • Frequency: weekly — confirm before I set it · client-facing → share via share-report

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

### Work out the build order here

This is the only skill that sees the whole graph — every report, every module,
which sources repeat and which modules are shared. The build skills each see one
module, so they can't work this out. Hand them an order.

**How the platform behaves**, which is all you need to derive one:

| | |
|---|---|
| **Pipeline** | data source → module → template → run → layout → share |
| **Costs** | a module build+run is 2–4 min; `list_*` calls are cheap; `test_run_*` costs a run and saves nothing |
| **Independent** | modules from each other; reports from each other |
| **Ordered** | a template can only be assembled once its modules exist |
| **Correlated** | modules on the same source share its field, precision and classification rules — they fail together |
| **Reusable** | one module can sit in many templates and they share its result — create it once |
| **Irreversible** | publishing, archiving, hard-deleting a source, and committing to a schedule |

Two consequences worth stating in the plan explicitly:

- **Group by source, not by report.** Modules sharing an untested source are the
  only ones where checking one tells you anything about the others. Four modules
  from four sources in one report are four independent risks; eight modules across
  three reports on one source are a single risk. Where a rule is unproven,
  `test_run_qual` / `test_run_quant` check it without saving anything — and those
  checks are independent of each other, so they run together too.
- **Deduplicate across reports before counting the work.** If three reports open
  with the same macro digest, that is one module, not three. Say so in the plan —
  it's usually the largest saving available.

Then state the order plainly, e.g.:

```
Build order
  1. Check 2 new sources           (2 test-runs, together)
  2. Create 9 modules              (together — 3 are shared across reports)
  3. Assemble 3 templates          (together, after step 2)
  4. Confirm schedules with the user, then set them
```

## Notes

- This skill only reads and reasons; the confirm-before-create gate lives in the
  build skills. Don't create tags, sources, or modules here. Reading one real
  payload (Step 3.5) is a read, and it is the exception that pays for itself.
- `plan_required` / 402 on a read → relay it plainly and plan around what the
  workspace can access.
- Everything is scoped to the user's workspace — never imply cross-org data.
