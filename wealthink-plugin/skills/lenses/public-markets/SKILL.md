---
name: public-markets
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Set up and run public-markets / equity research on Wealthink — stock and sector
  coverage, morning notes and daily wraps, earnings previews and reviews, and
  sector-rotation monitors. Use when the user talks like a sell-side or buy-side
  equity analyst: "initiate coverage on X", "build my morning note", "earnings
  preview for next week's prints", "which sectors are rotating?". A persona lens:
  it maps equity-desk vocabulary onto Wealthink artifacts and hands off to the
  core build/run/report skills — it does not re-implement any mechanics.
---

# Public-Markets (Equity) Research Lens

This is a **thin persona adapter** for an equity desk. It translates how an equity
analyst talks into Wealthink's building blocks, supplies sensible defaults, and
then **hands off to the core skills** to do the actual work. It never invents its
own MCP call sequence — if a step needs mechanics, that's a core skill's job.

## Vocabulary map (equity desk → Wealthink)

| You say… | Wealthink artifact | Core skill |
|----------|--------------------|-----------|
| "Initiate coverage on TICKER" | a qual module (thesis) + quant chart(s) for the name | `build-qual-module` + `build-quant-chart` |
| "Morning note / daily wrap" | a **template** of coverage modules, run **daily** | `research-reports` |
| "Earnings preview / review" | a qual module over earnings-tagged events for the name | `build-qual-module` |
| "Sector monitor / rotation" | quant charts (relative performance) + a qual read | `build-quant-chart` + `build-qual-module` |
| "What's moving my names today?" | tracked events filtered by ticker/sector tags | `market-news` |
| "Send the note to the desk/clients" | publish a report run to a link | `share-report` |

## Default parameters for this persona

Use these as starting points (confirm, don't impose):

- **Tags** — one per covered ticker/sector (`reliance`, `nifty-bank`, `it-sector`),
  plus a cross-cutting `earnings` tag for results-season items.
- **Cadence** — **daily** for morning notes/wraps; **weekly** for sector reviews;
  ad-hoc for earnings around print dates.
- **Qual output shape** — equity-note sections: *View / Rating*, *Catalysts*,
  *Earnings & Estimates*, *Risks*, *Valuation*. A structured output makes the
  morning-note layout predictable.
- **Quant defaults** — price/relative-performance charts over a 30–90d span;
  for derivatives names, near-month futures via `get_expiry_dates`.

## Starter templates (suggest, then build via `research-reports`)

- **Morning Note** — macro/overnight recap (events) → index charts → top-3 coverage
  updates → flagged catalysts. Daily.
- **Earnings Preview Pack** — one section per name reporting this week:
  estimates, setup, what to watch. Weekly during the season.
- **Sector Monitor** — relative-performance charts + a rotation read across the
  sectors the desk follows. Weekly.

## How a request flows

1. **Recognise the persona intent** and map it with the table above.
2. **Plan if it's open-ended** ("set up my coverage") → hand to `plan-research`
   to confirm scope, reuse vs create, and gaps.
3. **Build** the mapped modules → `build-qual-module` / `build-quant-chart`
   (approve-then-fan-out for several names at once).
4. **Assemble & run** the note/pack → `research-reports`.
5. **Lay out** for the desk's surface (web/mobile) → `generate-layout`.
6. **Distribute** → `share-report` (publish the run; confirm before making public).

## Composing with other connectors (defensive)

The payoff of the equity desk's toolset is the cross-tool flow — "build the
morning note and send it out". Compose **only if the other connector is present**,
and degrade gracefully if not:

- If a **mail/Slack connector** is available, offer to send the published note's
  link to the desk distribution; **otherwise just return the link**.
- Never hard-fail because a connector the firm didn't install is missing. Core
  Wealthink work never depends on any non-Wealthink connector.

## Stay in lane

- This lens only maps vocabulary, defaults, and starter shapes — **all mechanics
  live in core**. If you find yourself writing `create_*` / `run_*` call sequences
  here, move that logic to the core skill and hand off instead.
- `plan_required` / 402 and sign-in are handled by core; relay/login as usual.
- Everything is the user's own workspace — never imply cross-org data.
