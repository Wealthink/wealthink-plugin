---
name: plan-research
allowed-tools: mcp__plugin_wealthink_mcp__*
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

## Step 4 — Present the build plan (skill)

Lay out a concrete, ordered plan the user can approve:

```
Plan: Weekly Gold & Rupee Client Brief (weekly, client-facing)

Reuse (already in your workspace)
  • qm_abc…  Gold Market SWOT            → as-is
Create (new modules)
  • Qual:  "Rupee drivers digest"        → events, tag: rupee · source: news
  • Quant: "MCX Gold near-month 7D"      → candlestick, expiry from get_expiry_dates
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

If the user approved several modules at once, the build step can fan them out in
parallel (one `module-builder` agent per approved spec) — see `build-qual-module`.

## Notes

- This skill only reads and reasons; the confirm-before-create gate lives in the
  build skills. Don't create tags, sources, or modules here.
- `plan_required` / 402 on a read → relay it plainly and plan around what the
  workspace can access.
- Everything is scoped to the user's workspace — never imply cross-org data.
