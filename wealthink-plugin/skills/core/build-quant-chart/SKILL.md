---
name: build-quant-chart
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__create_quant_config
  - mcp__plugin_wealthink_mcp__run_quant_chart
  - mcp__plugin_wealthink_mcp__test_run_quant
  - mcp__plugin_wealthink_mcp__test_run_quant_stream
  - mcp__plugin_wealthink_mcp__update_quant_config
  - Agent(module-builder)
  - Agent(output-digest)
description: >
  Create, refine, or archive a quantitative chart module on Wealthink — a
  configured chart over market/derivatives data, such as an MCX commodity futures
  candlestick, a bhavcopy price table, or pivot levels. Use when the user
  says "generate a silver futures chart", "build me a candlestick for the
  near-month expiry", "change that chart to the next expiry", "switch it to a
  price table", or wants to retire a chart module.
---

# Build a Quantitative Chart Module

A quantitative module ("quant config") is a saved chart specification: an
instrument, the data window, which data endpoints to pull, and which chart(s) to
render from them. Running it (see `run-research` → `run_quant_chart`) produces a
Plotly figure. Common for a multi-asset firm: MCX gold/silver/crude futures
charts, price tables, and pivot levels.

## Step 0 — Discover valid inputs (you cannot guess these)

Run these first (see `discover`):

- `list_data_sources` — the data source ID to pull from. **You only ever see
  sources this workspace can actually run** — the connector pins agent callers to
  the enabled view. A source that isn't listed needs credentials added in the
  Wealthink app; that is a human action and you cannot do it (credential tools are
  deliberately not exposed to agents).
  The catalogue is broad, and several sources need no credentials at all — among
  them the Indian mutual-fund sources (`amfi`, `mfapi`, `groww_mf`) — so check the
  list before telling a user something isn't available.
- `list_quant_chart_types` — the chart types the platform supports (e.g.
  candlestick, line, table, bar).
- `get_expiry_dates(...)` — the **valid expiry codes** for the instrument, in the
  connector's own format (a code like `<DD><MON><YYYY>`). Always fetch these and
  pass one through verbatim — never hand-type an expiry or copy one out of an
  example. Expiries roll, so any literal written down here is wrong within weeks,
  and an invalid expiry fails the run.
- `get_quant_config(id)` — when refining, read the current config first. The
  generated **`ai_code`** is omitted unless you pass `include_code=true`; ask for
  it only when you actually need to inspect the code (it runs 6–9 KB). The same
  flag applies to `list_quant_configs` and to the response of
  `update_quant_config`.

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

## Step 2 — Render before you save

`test_run_quant` renders a spec **without creating a config**. Use it whenever the
instrument, endpoints or chart grammar are uncertain — it's how you find out that
a `data_key` doesn't match an endpoint, or an expiry is stale, without leaving a
broken config behind. (`test_run_quant_stream` is the streaming variant.)

Iterate on the spec until the render is right, *then* `create_quant_config`.

> **`DATA_SOURCE_KEY_MISSING` is not retryable.** A config against a source with no
> credentials **saves with a warning but hard-fails at run**. The fix is adding the
> key in the Wealthink app — a human action you cannot perform and retrying will
> never resolve. Say so plainly and stop; don't loop.

## Step 3 — Confirm

Read the config back (without `include_code` unless you need the generated code),
summarise it (instrument, expiry, charts), and offer to generate it once via
`run-research` (`run_quant_chart`) so the user sees the real chart before it goes
into a report.

When you only need to know a result's *structure* — which data keys came back,
what fields a layout could render — pass **`data="schema"`** to the result call
instead of pulling thousands of OHLCV rows.

## Building several charts at once (approve-then-fan-out)

When the user wants **several** chart modules built together (the UC1 flow, often
arriving from `plan-research`): discover valid inputs and **get the user's
approval of every spec on the main thread** (Steps 0–3, including a
`test_run_quant` render of anything uncertain), then **fan out one
`module-builder` agent per approved spec**.
Each agent creates its config, renders it once, and returns a compact summary —
hand it a complete spec with the data source, symbol, and **fresh expiry codes**
already resolved, since it cannot ask questions. Review the summaries with the
user afterwards. If the harness can't fan out, build the approved specs
sequentially inline with the same tools.

## Refine an existing config

`update_quant_config(config_id, ...)` — partial update.

> **Three rules that bite:**
> - If you change the **symbol**, you must also send a valid **expiry** — they
>   travel together (fetch fresh expiries via `get_expiry_dates`).
> - **expiry / endpoints / charts are replaced**, not appended. Send the full
>   intended list each time.
> - The update **response** omits `ai_code` unless you pass `include_code=true`.
>   Don't read its absence as "the code was wiped".

**Scheduling a config** works like a qual module: `run_frequency` is a live cron
that now actually fires, invalid expressions 400 at save, it can't combine with an
absolute time window, and repeated credential failures auto-pause the schedule —
read back `schedule_status` before telling the user it's running. See
`build-qual-module` for the full rules.

## Retire a config

`archive_quant_config(config_id)` — soft-delete (recoverable). No hard-delete via
the connector. **Confirm with the user first** — in Claude Code the removal-gate
hook also forces an explicit confirmation on `archive_*`; the confirmation is the
rule, the hook is the backstop.

## Notes

- Expiries roll: a code valid last month may be gone. Re-fetch with
  `get_expiry_dates` whenever you (re)build a config.
- Don't paste raw Plotly JSON into chat — describe the chart and key readings.
- All configs are workspace-scoped. If a write returns `plan_required` / 402,
  relay the upgrade message plainly.
