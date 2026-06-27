---
name: venture
allowed-tools: mcp__plugin_wealthink_wealthink__*
description: >
  Set up and run venture-capital research on Wealthink — deal-pipeline tracking,
  investment-thesis monitoring, and portfolio-update reports. Use when the user
  talks like a VC: "track my pipeline", "monitor my thesis on space X", "build my
  portfolio update". A persona lens (scaffold): it maps VC vocabulary onto
  Wealthink artifacts and hands off to the core build/run/report skills — it does
  not re-implement any mechanics.
---

# Venture-Capital Research Lens *(scaffold)*

A **thin persona adapter** for a VC firm. It translates VC language into Wealthink
building blocks and **hands off to the core skills**; mechanics live in core. This
is a scaffold — extend defaults and starter templates as demand appears, but keep
it an adapter.

## Vocabulary map (VC → Wealthink)

| You say… | Wealthink artifact | Core skill |
|----------|--------------------|-----------|
| "Track my deal pipeline / a space" | a qual module over news tagged to that theme | `build-qual-module` |
| "Monitor my thesis on X" | a qual module framed around the thesis + its signals | `build-qual-module` |
| "Portfolio update" | a **template** of portfolio + thesis modules, run monthly | `research-reports` |
| "What's new in my spaces?" | tracked events filtered by theme/company tags | `market-news` |
| "Send the update to my LPs/partners" | publish a report run to a link | `share-report` |

## Default parameters for this persona

- **Tags** — one per investment theme/space and per portfolio company.
- **Cadence** — **monthly** for portfolio updates; weekly for active theses.
- **Qual output shape** — *Thesis Status*, *Signals This Period*, *Portfolio
  Moves*, *Watch / Risks*.

## Starter templates (suggest, then build via `research-reports`)

- **Thesis Monitor** — one section per active thesis with supporting signals.
- **Portfolio Update** — portfolio company news → thesis status → pipeline notes.
- **Space Scan** — a theme deep-dive over tracked news.

## How a request flows

Map intent → if open-ended, `plan-research` → build via `build-qual-module` /
`build-quant-chart` (approve-then-fan-out) → assemble/run via `research-reports`
→ lay out (`generate-layout`) → distribute (`share-report`, confirm before public).

## Composing with other connectors (defensive)

If a **CRM** (deal/pipeline) or **mail** connector is present, offer to enrich the
update from it or send it out — **only if available**; otherwise return the link.
Core never depends on a non-Wealthink connector.

## Stay in lane

Vocabulary, defaults, and starter shapes only — **all mechanics live in core**.
Don't write `create_*` / `run_*` sequences here; hand off to the core skill.
Sign-in, `plan_required`/402, and tenant scope are handled by core.
