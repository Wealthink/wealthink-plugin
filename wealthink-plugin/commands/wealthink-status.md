---
description: Check the status of a Wealthink run via the MCP connector. Pass a run_id, or leave empty to be prompted.
---

# Check a Wealthink Run Status

> $ARGUMENTS

Check the status of the run with the given `run_id`. Wealthink has separate
status tools per run type — pick by what you know, or try in this order:

- Qualitative module run → `get_qual_run_status(run_id)`
- Report (template) run → `get_template_run_status(run_id)`
- Latest chart result for a quant module → `get_quant_result(config_id)`

A status check rarely needs the run's data. Pass **`data="schema"`** unless the
user asked to see the numbers — it returns the result's shape instead of its rows
and keeps a large run from flooding the response.

## Interpret and present

| Status | Meaning | Action |
|--------|---------|--------|
| `pending` / `running` | Still working | In progress — offer to check again |
| `completed` | Finished | Show the result |
| `failed` | Errored | Show the `error` field, plainly |

**Completed** — present the key fields and the output: for a qualitative run,
render the analysis (`module_output`) as a clean report; for a report run, the
stitched `result` per section; describe any chart rather than dumping Plotly JSON.

**Running / pending** — tell the user it's still in progress. Offer to wait and
check again shortly; treat only `completed` / `failed` as terminal.

**Failed** — surface the `error` field clearly. Don't auto-retry.

**No run_id provided (empty `$ARGUMENTS`)** — ask for one: "Share the run_id —
you'll have gotten it when you started the run, or I can list recent runs." To
list them you need to know the resource: `list_qual_results` for a qualitative
module, or `list_template_reports(template_id=<id>)` for a report (the template_id
is required — find it with `discover` first).

**A run the user didn't start** — scheduled runs happen on their own now. If a
result looks unfamiliar, check the module's `run_frequency` and `schedule_status`
before treating it as a mystery.

**`plan_required` / 402** — relay the upgrade message plainly.
