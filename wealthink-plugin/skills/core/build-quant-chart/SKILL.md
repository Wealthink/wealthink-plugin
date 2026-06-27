---
name: build-quant-chart
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Create, refine, or archive a quantitative chart module on Wealthink — a
  configured chart over market/derivatives data, such as an MCX commodity futures
  candlestick, a bhavcopy price table, or pivot levels. Use when the user wants
  to set up a new chart, change an instrument/expiry/chart type, or retire a
  chart module.
---

# Build a Quantitative Chart Module

A quantitative module ("quant config") is a saved chart specification: an
instrument, the data window, which data endpoints to pull, and which chart(s) to
render from them. Running it (see `run-research` → `run_quant_chart`) produces a
Plotly figure. Common for a multi-asset firm: MCX gold/silver/crude futures
charts, price tables, and pivot levels.

## Step 0 — Discover valid inputs (you cannot guess these)

Run these first (see `discover`):

- `list_data_sources` — the data source ID to pull from.
- `list_quant_chart_types` — the chart types the platform supports (e.g.
  candlestick, line, table, bar).
- `get_expiry_dates(...)` — the **valid expiry codes** for the instrument (e.g.
  `25JUN2026`). Always fetch these — never hand-type an expiry; an invalid expiry
  fails the run.
- `get_quant_config(id)` — when refining, read the current config first.

## Step 1 — Create the chart module

Call `create_quant_config` with:

- **name** — e.g. "Silver MCX Near-Month 7D".
- **asset class** — e.g. commodity.
- **data source** — from `list_data_sources`.
- **symbol / instrument** — e.g. `SILVER`.
- **expiry** — one or more codes from `get_expiry_dates` (repeatable for
  multi-expiry charts).
- **instrument type** — e.g. futures (`FUTCOM`), options, or all.
- **span** — the data window (e.g. `7d`, `30d`).
- **endpoints** — which data feeds to pull (e.g. bhavcopy, OHLC, pivot levels);
  repeatable.
- **charts** — each chart as `type : data_key : title`
  (e.g. `candlestick:ohlc:Silver OHLC`, `table:bhavcopy:Silver Price Table`);
  repeatable. The `data_key` ties a chart to one of the endpoints you pulled.

Example shape (a multi-chart config):
```
endpoints:  bhavcopy, ohlc
charts:     table:bhavcopy:Silver Price Table
            candlestick:ohlc:Silver OHLC (near month)
```

## Step 2 — Confirm, then test

Read the config back, summarise it (instrument, expiry, charts), and offer to
generate it once via `run-research` (`run_quant_chart`) so the user sees the real
chart before saving it into a report.

## Building several charts at once (approve-then-fan-out)

When the user wants **several** chart modules built together (the UC1 flow, often
arriving from `plan-research`): discover valid inputs and **get the user's
approval of every spec on the main thread** (Step 0–2, including a test render of
anything uncertain), then **fan out one `module-builder` agent per approved spec**.
Each agent creates its config, renders it once, and returns a compact summary —
hand it a complete spec with the data source, symbol, and **fresh expiry codes**
already resolved, since it cannot ask questions. Review the summaries with the
user afterwards. If the harness can't fan out, build the approved specs
sequentially inline with the same tools.

## Refine an existing config

`update_quant_config(config_id, ...)` — partial update.

> **Two rules that bite:**
> - If you change the **symbol**, you must also send a valid **expiry** — they
>   travel together (fetch fresh expiries via `get_expiry_dates`).
> - **expiry / endpoints / charts are replaced**, not appended. Send the full
>   intended list each time.

## Retire a config

`archive_quant_config(config_id)` — soft-delete (recoverable). No hard-delete via
the connector. **Confirm with the user first** — in Claude Code the archive-gate
hook also forces an explicit confirmation on `archive_*`; the confirmation is the
rule, the hook is the backstop.

## Notes

- Expiries roll: a code valid last month may be gone. Re-fetch with
  `get_expiry_dates` whenever you (re)build a config.
- Don't paste raw Plotly JSON into chat — describe the chart and key readings.
- All configs are workspace-scoped. If a write returns `plan_required` / 402,
  relay the upgrade message plainly.
