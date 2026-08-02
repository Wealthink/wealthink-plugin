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
analyses + quant charts) plus a run schedule. This is the firm's deliverable —
e.g. "Weekly Macro + Commodity Briefing", "Daily Bullion Brief".

## How a template actually works

**A template assembles its modules' latest published results — it does not run
the modules itself.** Almost everything surprising about templates follows from
this one fact, so it's worth holding onto:

- **One module can sit in several templates**, and they share its result. Three
  reports that all open with the same macro digest cost **one** module run, not
  three. So when several reports need the same analysis, **create the module once
  and reference it from each template** — don't build near-duplicates per report.
- **A template run either succeeds or fails; there is no partial status**, because
  assembly is all it does.
- **A scheduled template pauses only when *no* module has a new published result**
  — there is nothing to assemble. That makes a *running* template weak evidence of
  health, and a *paused* one a sign that everything stalled some time ago.

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

### Reuse before you build

Check whether a module the user needs **already exists** (`list_module_options`)
before sending them to `build-qual-module` / `build-quant-chart`. A module in
another template can be referenced directly — same module, shared result, no
second build and no second run. This is the cheapest win available when someone
is setting up their second or third report.

## Setting the schedule is the point

For most users the report is meant to arrive **without them** — they approve it
once, it runs on its schedule, and they read the output in the Wealthink app. The
schedule is therefore the deliverable, not a setting.

- **Confirm the frequency explicitly before setting it.** "Weekly" in conversation
  is not consent to a recurring job. Say what will run, how often, and from when.
- **`daily` | `weekly` | `monthly`** — those are the options. If the user asks for
  something else (quarterly is a common ask), say so plainly and offer the nearest
  fit plus a manual run when they need it.
- **After approval, tell the user what happens next** — the report will run on its
  own and they'll be notified when it's ready; they don't need to keep a session
  open.
- **A schedule can stop quietly.** If a user says *"my weekly report stopped
  arriving"*, don't start by re-running it. Check each module's latest result date
  first (see above) — a template pauses only once *every* module has gone stale,
  so by the time the report visibly stops, the underlying cause is usually old.

## Run a report (and get it back)

`run_template(template_id)` — triggers the run, waits for all child modules, and
returns the final status. Template runs are longer than single modules (the
default wait is 180s; raise `timeout_s` for big reports).

- If it times out, the run is still going server-side. Use
  `get_template_run_status(run_id)` to check later.
- Treat only `completed` / `failed` as terminal.

### ⚠️ A successful run does not mean the data is current

This is the failure the user is most likely to hit, and it does not raise an
error. If a module fails to produce a new result — a missing data-source key, or
any other reason — the template **still runs successfully**, reusing that module's
**previous** result. The report is delivered on time, with some sections fresh and
others carrying old data, and every status you can read says `completed`.

So **never certify a report from the template's status alone.** Before presenting
a run, and especially before it goes to a client, look at each module's latest
result and *when it was produced*.

**Report the dates; don't judge them.** How old is too old is per-module and not
something you can infer from the report: a module tracking economic releases is
*supposed* to be weeks old, while a market-events module should be same-day. The
reference point is each module's **own `run_frequency`**, never the report's
cadence. So:

- Show the user which section's data is from when.
- Flag a module whose latest result is overdue **against its own schedule** —
  that's the real signal something broke.
- Leave the significance to the analyst. A three-week-old macro section may be
  perfectly correct.

If a module is overdue, the usual cause is a data-source credential, which is
fixed in the Wealthink app — a human action (see `build-qual-module`).

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
  module (`build-qual-module` / `build-quant-chart`). Because the template
  assembles published results, refreshing one section means **running that module**
  (`run-research`) and then the template; re-running the template alone will
  re-serve the same stale section.
- Everything is workspace-scoped. `plan_required` / 402 on a write → relay the
  upgrade message plainly.
