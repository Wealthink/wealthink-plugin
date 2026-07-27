---
name: run-research
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__run_module
  - mcp__plugin_wealthink_mcp__run_qual_stream
  - mcp__plugin_wealthink_mcp__run_quant_chart
  - mcp__plugin_wealthink_mcp__run_quant_module
  - mcp__plugin_wealthink_mcp__test_run_qual
  - mcp__plugin_wealthink_mcp__test_run_quant
  - Agent(output-digest)
  - Agent(run-verify)
description: >
  Run a Wealthink research module and present the result — either a qualitative
  module (LLM analysis like a SWOT, market summary, or news digest) or a
  quantitative module (a chart such as an MCX futures candlestick or price table).
  Use when the user says "run", "execute", "generate the chart for", or "show me
  the latest" for a module, or wants the output of an analysis.
---

# Run Research & Present Results

Wealthink runs are asynchronous, but the connector gives you **blocking wrapper
tools** that trigger the run, wait for it, and hand back the finished result.
Prefer those — they save you from managing a polling loop.

## Step 1 — Identify the module

You need the module's ID and its type (qualitative vs quantitative). If the user
named it ("run my gold SWOT"), resolve the ID via `discover` —
`list_module_options` is the cheapest lookup (id + name across both types), with
`list_qual_modules` / `list_quant_configs` when you need more detail. If several
match, ask which one.

**Run an unsaved spec instead?** If the user is describing something that doesn't
exist yet rather than naming a module they have, don't create one to run it —
`test_run_qual` / `test_run_quant` execute a spec without saving. See
`build-qual-module` / `build-quant-chart`.

## Step 2 — Run it (one call, waits for the result)

**Qualitative module** → `run_module(module_id)`
- Triggers the LLM analysis, polls until done, returns the final status with the
  analysis output. Default wait is 120s; pass `timeout_s` higher for known-slow
  modules.

**Quantitative chart module** → `run_quant_chart(config_id)`
- Streams chart generation (data fetch → chart code → execution) and returns
  `{ status, run_id, result, summary }` where `result` is the Plotly figure JSON.

> Streaming alternative for qualitative runs: `run_qual_stream(module_id)`
> returns `{ status, run_id, output }` over the live stream. Use it only if the
> user wants the streamed variant; `run_module` is the simpler default.

## Step 3 — If you have a run_id instead of waiting

If a run was already triggered (or a wrapper timed out and gave you a `run_id`),
fetch status/result directly:
- Qualitative run → `get_qual_run_status(run_id)`
- Latest chart for a quant module → `get_quant_result(config_id)`
- Past qualitative results → `list_qual_results(...)`

Statuses flow `pending → running → completed | failed`. Treat only `completed`
and `failed` as terminal. If a wrapper times out, the job is still running
server-side — give the user the `run_id` and offer to check again with
`get_qual_run_status`.

**Size the response to the question.** These calls take `data`:
`data="schema"` returns a JSON Schema of `result` instead of the rows,
`data="both"` gives you both, `data="full"` the raw data. Checking *whether* a run
produced output, or *what shape* it produced, does not need the rows — and a quant
result can be thousands of them. Use `full` when the user is reasoning over the
numbers, `schema` when you are reasoning over the structure.

## Runs the user didn't start

Modules can carry a `run_frequency` cron, and those schedules **now execute** — so
a module may have recent results nobody triggered by hand. Two consequences:

- When a result's timing looks unexplained, check the module's `run_frequency`
  before treating it as a mystery.
- A schedule can be **auto-paused** after repeated credential failures. It looks
  live except for `schedule_status`, `schedule_paused_reason` and
  `schedule_paused_at`. If a user says "my daily report stopped arriving", read
  those three fields first — the usual cause is a data-source credential that
  needs re-adding in the Wealthink app, which is a human action.

## Step 4 — Present the result

**Qualitative output** — the analysis lives in the run's output field (often
`module_output`). If it's structured JSON (sections like *Market Overview*,
*Key Drivers*, *Risks*, *Recommendation*), render it as a clean markdown report
with those headings. If it's plain text/markdown, render as-is. Always note the
module name and when it completed.

**Quantitative output** — summarise what was produced: instrument/symbol,
expiry, chart type, and status. The Plotly figure is in the result (`result` /
`module_output.figure`); describe the chart and key readings (last price, range,
notable moves) — **do not paste the raw figure JSON** into the chat. If the
surface can render Plotly, offer to display it.

## Running several modules, or handling a huge output

- **Several modules at once (run + verify):** this is the UC2 flow. Discover the
  targets, then **fan out one `run-verify` agent per module** — each runs its
  module (blocking wrapper), judges the output, and returns a compact verdict plus
  the best `run_id`. The large run output dies inside the agent; only the verdict
  reaches the main thread. Then review the verdicts **with the user** and decide
  what (if anything) to publish via `share-report`. The agent **recommends, never
  publishes**. Sequential fallback if the harness can't fan out.
- **One run, but the output is too big to hold/render:** spawn an `output-digest`
  agent on the `run_id` and present its tight summary instead of pulling the raw
  payload into the main context.

## Errors

- `status = failed` → surface the run's `error` field plainly and stop. Do not
  silently retry; a failure usually means a data or configuration issue.
- `plan_required` / 402 → relay the upgrade message; don't treat as a crash.
- Missing/wrong ID → re-run discovery and confirm the module with the user.

## After the run

Offer the obvious next step: re-run with different inputs, add this module to a
report (`research-reports`), or run a related module on the same news.
