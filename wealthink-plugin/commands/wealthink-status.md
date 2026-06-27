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
you'll have gotten it when you started the run, or I can list recent runs with
`list_qual_results` / `list_template_reports`."

**`plan_required` / 402** — relay the upgrade message plainly.
