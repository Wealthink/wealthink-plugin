---
name: share-report
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Publish a finished Wealthink report run to a public, login-free link to share
  with a client, or revoke that access — and read a public run. Use when the user
  wants to share a report, generate a client link, make a report viewable without
  a Wealthink login, or retract a previously shared report.
---

# Share a Report with a Client

Sharing is **per run**, not per template: publishing one run exposes only that
run's report — the template configuration and every other run stay private. This
is how an analyst hands a finished briefing to a client.

## Step 1 — Get the run_id of a completed run

Only completed runs should be shared. Find the run_id via `research-reports`
(`list_template_reports` or `get_template_run_status`) and confirm
`status = completed` before publishing.

## Step 2 — Publish

`set_template_run_visibility(run_id, ...)` — mark the run public.

Then give the user the shareable link. The public report is served from
Wealthink's public report path for that run_id (e.g.
`https://app.thewealthink.com/shared/<run_id>` — use the workspace's actual
public base URL). The recipient needs **no Wealthink account** to view it.

## Step 3 — Revoke when done

`set_template_run_visibility(run_id, ...)` with visibility set back to private.
The link stops working immediately.

## Read a public run

`get_public_template_run(run_id)` returns a shared run with no auth — useful to
preview exactly what the client will see. The public view is **scrubbed**: it
never includes org/user identifiers or internal tracebacks. If the parent
template was later changed or removed, the run's report still serves correctly.

## Confirm before sharing

Publishing makes a report viewable by anyone with the link. **Always confirm with
the user before publishing**, and offer to revoke when they're done. Don't
publish runs that are still running or that failed.

> This confirmation is the rule, and it lives here so it holds everywhere. In
> Claude Code the **publish-gate hook** also enforces it — `set_*_visibility`
> calls that make a run public trigger an explicit confirmation prompt (revoking
> back to private passes through). Never let a public link depend on the hook
> alone; the confirmation above is the guarantee in Cowork.

This is also why publishing **stays on the main thread** — a run-and-verify agent
recommends a `run_id`, but the user, not an agent, decides to publish it.

## Errors

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| Permission denied / 403 | Caller can view but not share in this workspace | Have an authorised teammate share |
| `plan_required` / 402 | Sharing not on this plan | Relay the upgrade message plainly |
| Not found on share | Wrong run_id, or run belongs to another workspace | Re-confirm the run_id |
| Public link returns unauthorised | Run is private (never shared or revoked) | Re-publish if intended |
| Cannot share | Run isn't completed yet | Wait for the run to finish |
