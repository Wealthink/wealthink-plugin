---
name: private-equity
allowed-tools: mcp__plugin_wealthink_wealthink__*
description: >
  Set up and run private-equity research on Wealthink — portfolio-company
  monitoring, deal/sector screens, and LP reporting packs. Use when the user talks
  like a PE professional: "monitor my portfolio companies", "screen this sector
  for deals", "build my quarterly LP pack". A persona lens (scaffold): it maps PE
  vocabulary onto Wealthink artifacts and hands off to the core build/run/report
  skills — it does not re-implement any mechanics.
---

# Private-Equity Research Lens *(scaffold)*

A **thin persona adapter** for a PE firm. It translates PE language into Wealthink
building blocks and **hands off to the core skills**. It never invents its own MCP
call sequence — mechanics live in core. This is a scaffold: extend the defaults
and starter templates as real demand appears, but keep it an adapter.

## Vocabulary map (PE → Wealthink)

| You say… | Wealthink artifact | Core skill |
|----------|--------------------|-----------|
| "Monitor portfolio company X" | a qual module over news tagged to that company | `build-qual-module` |
| "Deal / sector screen" | a qual module (+ charts) over a sector's tracked news | `build-qual-module` + `build-quant-chart` |
| "Quarterly LP pack" | a **template** of portfolio + market modules, run **monthly/quarterly** | `research-reports` |
| "What's happening with my portfolio?" | tracked events filtered by company/sector tags | `market-news` |
| "Send the pack to LPs" | publish a report run to a link | `share-report` |

## Default parameters for this persona

- **Tags** — one per portfolio company and per watched sector.
- **Cadence** — **monthly/quarterly** for LP packs; weekly for active deal screens.
- **Qual output shape** — *Company Update*, *Key Developments*, *Risks/Watch
  Items*, *Valuation/Exit Considerations*.

## Starter templates (suggest, then build via `research-reports`)

- **Portfolio Monitor** — one section per portfolio company + a market backdrop.
- **LP Quarterly Pack** — portfolio updates → sector context → outlook. Quarterly.
- **Deal Screen** — a sector scan with charts and a qualitative read.

## How a request flows

Map intent → if open-ended, `plan-research` → build via `build-qual-module` /
`build-quant-chart` (approve-then-fan-out) → assemble/run via `research-reports`
→ lay out (`generate-layout`) → distribute (`share-report`, confirm before public).

## Composing with other connectors (defensive)

If a **portfolio/custody** or **mail** connector is present, offer to pull current
AUM/holdings into the pack or email it to LPs — **only if available**; otherwise
return the Wealthink report link. Core never depends on a non-Wealthink connector.

## Stay in lane

Vocabulary, defaults, and starter shapes only — **all mechanics live in core**. If
you start writing `create_*` / `run_*` sequences here, move them to core and hand
off. Sign-in, `plan_required`/402, and tenant scope are handled by core.
