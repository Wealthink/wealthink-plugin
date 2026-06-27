---
name: understand-system
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Understand a customer's existing research system — a PDF/PPT report, a code
  snippet, a spreadsheet, or a pasted chat blob — and map it onto Wealthink
  artifacts (data sources, modules, events, templates, layout). Use when the user
  shares "here's the report we produce today / our current process" and wants to
  replicate or migrate it into Wealthink. Interactive and advisory; ends by
  handing off to plan-research.
---

# Understand a Customer's Research System

A prospect or new customer already produces research some other way — a weekly PDF,
a slide deck, an Excel model, a manual process. This skill **reverse-engineers
that system into Wealthink's building blocks** so it can be rebuilt on the
platform. It analyses and maps — it **does not create anything**; building happens
later via `plan-research` → the build skills.

## Step 1 — Gather context (ask)

Understand what you're looking at before parsing it:

- **What kind of system** — a finished report (PDF/PPT), a code/model, a
  spreadsheet, or a description/chat blob?
- **Agenda & audience** — what is it for, and who reads it?
- **Cadence** — how often is it produced?
- **Surface** — viewed on web or mobile? (affects the eventual layout.)

## Step 2 — Know the target shape

So the mapping lands on real Wealthink structures, recall the output shapes you're
mapping *into*:

- **Qualitative module output** — a structured analysis with named sections (e.g.
  *Market Overview*, *Key Drivers*, *Risks*, *Recommendation*). See `build-qual-module`.
- **Quantitative module output** — a configured chart over market/derivatives data
  (instrument, expiry, chart type). See `build-quant-chart`.
- **Template** — an ordered set of modules stitched into one report (`research-reports`).
- **Layout** — the report's visual design (`generate-layout`).

Also `discover` the customer's *current* Wealthink workspace (`list_all_modules`,
`list_templates`, `list_tags`, `list_data_sources`) so the mapping reuses anything
that already exists.

## Step 3 — Identify and parse the system

1. **Identify** the format (PDF / PPT / code / spreadsheet / chat blob).
2. **Parse it.** For a small artifact, read it inline.
   - **Large artifact (a long PDF/PPT/codebase):** spawn an isolated subagent to
     parse it and return a **structured extract**, so the raw dump never fills the
     main context (the same context-isolation principle as the `output-digest`
     agent). Give the subagent a complete task — "extract every section, its data
     inputs, and its cadence from this deck" — and have it return structured notes,
     not the raw file.

## Step 4 — Dissect into Wealthink artifacts (skill)

Walk the system section by section and map each piece to a Wealthink artifact:

- **A narrative/analysis section** → a **qualitative module** (capture its
  question, the news/sources it relies on, and its output sections).
- **A chart / price table / data exhibit** → a **quantitative chart module**
  (instrument, chart type, data window).
- **A "what happened this week" news roundup** → reads from **tracked events**
  under one or more **tags** (`market-news`); note which tags are needed.
- **The document as a whole** → a **template** (the section order) plus a **layout**.
- **External data feeding it** → a **data source** (note any source Wealthink
  doesn't yet have — that's a gap).

## Step 5 — Present the understanding (skill)

Show a clean mapping the user can sanity-check:

```
Their "Weekly Bullion Deck" → Wealthink

Section in deck          → Wealthink artifact
  Slide 1: Market recap  → Qual module (events: gold, silver, rupee)
  Slide 2: Gold chart    → Quant module (MCX gold candlestick, near-month)
  Slide 3: Silver chart  → Quant module (MCX silver candlestick)
  Slide 4: Outlook       → Qual module (SWOT-style, sections: drivers/risks/view)
  Whole deck             → Template (4 modules, weekly) + dashboard layout

Gaps
  • LBMA London fix feed not in current data sources.
  • "Client commentary" box is manual — no Wealthink equivalent; keep manual or drop.
```

## Step 6 — Hand off to planning (ask)

Ask whether to turn this understanding into a build plan. On yes, hand off to
`plan-research` (which will confirm intent, do gap analysis, and produce the
ordered build plan) → then the build skills.

## Notes

- Analyse and map only — never create modules/templates/tags here.
- If the customer's system needs a *new tracked topic*, event trackers are
  provisioned by Wealthink (app / account manager), not created through Claude.
- A large source document is exactly the case for an isolated parser subagent —
  keep the raw dump out of the main context.
- Everything maps into the user's own workspace — never imply cross-org data.
