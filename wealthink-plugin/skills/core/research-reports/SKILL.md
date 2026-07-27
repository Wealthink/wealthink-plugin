---
name: research-reports
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__create_template
  - mcp__plugin_wealthink_mcp__run_template
  - mcp__plugin_wealthink_mcp__update_template
  - Agent(output-digest)
description: >
  Build, run, and fetch Wealthink research report templates — a template bundles
  several qualitative and quantitative modules into one multi-section report that
  can run on a schedule (e.g. a weekly multi-asset briefing). Use when the user
  says "build my weekly research report", "run my morning pack now", "add a
  section to that report", "reorder the sections", "make it run daily", or
  "show me last week's report".
---

# Research Report Templates

A **template** is the user's report definition: an ordered set of modules (qual
analyses + quant charts) plus a run schedule. Running it executes every child
module and stitches the outputs into one report. This is the firm's deliverable —
e.g. "Weekly Macro + Commodity Briefing", "Daily Bullion Brief".

## Create a report template

1. **Pick the modules** (via `discover`: `list_module_options` is the cheapest way
   to see everything available). Decide their order — **module order is the section
   order in the report.** A typical flow: a macro/news summary, then charts, then
   instrument SWOTs, then a conclusion.
2. **Create it** with `create_template`:
   - **name** and (optional) **description**.
   - **module IDs** — ordered list of the modules to include.
   - **frequency** — `daily` | `weekly` | `monthly`.
   - optional **report title / objectives** and **active** flag.
3. Read it back with `get_template_by_id(id)` and confirm the section order with
   the user.

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

- **`list_template_reports(template_id=<id>)`** — the runs for one template.
  `template_id` is **required**; there is no "all reports across all templates"
  listing. The response is **metadata only** — `id`, `run_id`, `date`, `status`,
  `is_public`, `public_link` — which is exactly what you want when hunting for a
  `run_id`. Pass `show_result=true` only if you actually need the payloads inline.
- **`get_template_report_by_run_id(template_id, run_id)`** — one historical run.
- **`get_template_run_status(run_id)`** — a run's status and stitched result.

**Control the payload with `data`** on any of the result-returning calls:

| `data` | Returns | Use when |
|---|---|---|
| `schema` | a Draft-7 JSON Schema of `result` | you need the *shape* — which sections/fields exist, building or debugging a layout |
| `both` | schema **and** values | you want structure plus a look at real numbers |
| `full` | the raw rows | the user is reasoning over the data itself |

Present it as a clean, sectioned research report — one section per module, in
order. Render qual sections as headed markdown; for quant sections, describe the
chart and key readings (don't paste raw Plotly JSON). Lead with the report title
and run date.

> **A full stitched report can be too big to hold or render.** Reach for
> `data="schema"` *first* — it often removes the problem outright. If you still
> need the values, spawn an `output-digest` agent on the `run_id`: it absorbs the
> whole report and returns a tight, sectioned summary (naming any section that
> failed), so the raw payload never floods the main context. Pull full text only
> for the one section a user explicitly asks to see.

## Refine a template

`update_template(template_id, ...)` — partial update.

> **Replace-not-append:** the module list you send *replaces* the whole list. To
> reorder, add, or remove a section, send the complete intended ordered list.

Change frequency, title/objectives, or active flag the same way.

## Retire a template

`archive_template(template_id)` — soft-delete (recoverable), but the template
disappears from active lists and its scheduled runs stop. **Always confirm with
the user before archiving** — and in Claude Code the removal-gate hook enforces
this by requiring an explicit confirmation on `archive_*` calls. The confirmation
is the rule; the hook is the backstop, and it only runs in Claude Code.

Archived runs already published to a client link keep serving — revoke those via
`share-report` separately if that's the intent.

## Natural next steps

- **Share it with a client** → `share-report` (publish the run to a public link).
- **Lay it out visually** → `generate-layout` (design a branded dashboard layout for the report).

## Notes

- A report is only as good as its modules — if a section reads poorly, fix the
  module (`build-qual-module` / `build-quant-chart`) and re-run.
- Everything is workspace-scoped. `plan_required` / 402 on a write → relay the
  upgrade message plainly.
