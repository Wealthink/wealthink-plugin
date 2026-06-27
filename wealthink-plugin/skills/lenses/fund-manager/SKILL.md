---
name: fund-manager
allowed-tools: mcp__plugin_wealthink_wealthink__*
description: >
  Set up and run fund-manager research on Wealthink — allocation and risk
  monitoring, mandate/compliance reporting, and client/board reporting packs. Use
  when the user talks like a fund or portfolio manager: "monitor my allocation",
  "build my mandate report", "risk update for the board". A persona lens
  (scaffold): it maps fund-management vocabulary onto Wealthink artifacts and
  hands off to the core report/share skills — it does not re-implement mechanics.
---

# Fund-Manager Research Lens *(scaffold)*

A **thin persona adapter** for a fund/portfolio manager. It translates
fund-management language into Wealthink building blocks and **hands off to the
core skills**; mechanics live in core. Scaffold — extend defaults and starter
templates as demand appears, but keep it an adapter. This persona leans on
`research-reports` and `share-report` more than on building bespoke modules.

## Vocabulary map (fund manager → Wealthink)

| You say… | Wealthink artifact | Core skill |
|----------|--------------------|-----------|
| "Monitor my allocation / sleeves" | qual + quant modules per asset class/sleeve | `build-qual-module` + `build-quant-chart` |
| "Risk update" | a qual module over risk-relevant tracked events | `build-qual-module` |
| "Mandate / board / client report" | a **template** of allocation + risk modules, scheduled | `research-reports` |
| "How are my asset classes doing?" | tracked events filtered by asset-class tags | `market-news` |
| "Send the report to the client/board" | publish a report run to a link | `share-report` |

## Default parameters for this persona

- **Tags** — one per asset class / sleeve / mandate theme.
- **Cadence** — **monthly/quarterly** for mandate/board packs; weekly for risk.
- **Qual output shape** — *Allocation Snapshot*, *Performance Drivers*, *Risk &
  Compliance Notes*, *Outlook*.

## Starter templates (suggest, then build via `research-reports`)

- **Mandate Report** — allocation snapshot → performance drivers → risk → outlook.
- **Risk Update** — risk-relevant developments across the book.
- **Board Pack** — high-level allocation + risk + outlook for governance.

## How a request flows

Map intent → if open-ended, `plan-research` → build any needed modules via the
`build-*` skills (approve-then-fan-out) → assemble/run via `research-reports` →
lay out (`generate-layout`) → distribute (`share-report`, confirm before public).

## Composing with other connectors (defensive)

If a **portfolio/custody** connector is present, offer to pull live allocation/AUM
into the pack; if a **mail** connector is present, offer to send it — **only if
available**; otherwise return the Wealthink report link. Core never depends on a
non-Wealthink connector.

## Stay in lane

Vocabulary, defaults, and starter shapes only — **all mechanics live in core**.
Don't write `create_*` / `run_*` sequences here; hand off to the core skill.
Sign-in, `plan_required`/402, and tenant scope are handled by core.
