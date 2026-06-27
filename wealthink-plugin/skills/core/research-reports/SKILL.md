---
name: research-reports
allowed-tools: mcp__plugin_wealthink_wealthink__*
description: >
  Build, run, and fetch Wealthink research report templates — a template bundles
  several qualitative and quantitative modules into one multi-section report that
  can run on a schedule (e.g. a weekly multi-asset briefing). Use when the user
  wants to create a report, change which modules/sections it contains or how
  often it runs, generate a report now, or fetch a generated report.
---

# Research Report Templates

A **template** is the user's report definition: an ordered set of modules (qual
analyses + quant charts) plus a run schedule. Running it executes every child
module and stitches the outputs into one report. This is the firm's deliverable —
e.g. "Weekly Macro + Commodity Briefing", "Daily Bullion Brief".

## Create a report template

1. **Pick the modules** (via `discover`: `list_all_modules` / `list_qual_modules`
   / `list_quant_configs`). Decide their order — **module order is the section
   order in the report.** A typical flow: a macro/news summary, then charts, then
   instrument SWOTs, then a conclusion.
2. **Create it** with `create_template`:
   - **name** and (optional) **description**.
   - **module IDs** — ordered list of the modules to include.
   - **frequency** — `daily` | `weekly` | `monthly`.
   - optional **report title / objectives** and **active** flag.
3. Read it back and confirm the section order with the user.

## Run a report (and get it back)

`run_template(template_id)` — triggers the run, waits for all child modules, and
returns the final status. Template runs are longer than single modules (the
default wait is 180s; raise `timeout_s` for big reports).

- If it times out, the run is still going server-side. Use
  `get_template_run_status(run_id)` to check later.
- Treat only `completed` / `failed` as terminal. A template can **partially
  fail** (one module errored while others succeeded) — inspect the run status and
  tell the user which section is missing rather than declaring total failure.

## Fetch a generated report

- `list_template_reports(...)` — list generated report runs (find the run_id you
  want).
- `get_template_run_status(run_id)` — the run's status and stitched result.

Present it as a clean, sectioned research report — one section per module, in
order. Render qual sections as headed markdown; for quant sections, describe the
chart and key readings (don't paste raw Plotly JSON). Lead with the report title
and run date.

> **A full stitched report can be too big to hold or render.** When it is, spawn
> an `output-digest` agent on the `run_id` — it absorbs the whole report and
> returns a tight, sectioned summary (and names any section that failed), so the
> raw payload never floods the main context. Pull the full text only for the one
> section a user explicitly asks to see in full.

## Refine a template

`update_template(template_id, ...)` — partial update.

> **Replace-not-append:** the module list you send *replaces* the whole list. To
> reorder, add, or remove a section, send the complete intended ordered list.

Change frequency, title/objectives, or active flag the same way.

## Retire a template

`archive_template(template_id)` — soft-delete (recoverable). No hard-delete via
the connector. Confirm first.

## Natural next steps

- **Share it with a client** → `share-report` (publish the run to a public link).
- **Lay it out visually** → `generate-layout` (design a branded dashboard layout for the report).

## Notes

- A report is only as good as its modules — if a section reads poorly, fix the
  module (`build-qual-module` / `build-quant-chart`) and re-run.
- Everything is workspace-scoped. `plan_required` / 402 on a write → relay the
  upgrade message plainly.
