---
name: share-report
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
description: >
  Publish a finished Wealthink report run to a public, login-free link to share
  with a client, or revoke that access — and read a public run. Sharing is per
  *run*, not per template. Use when the user says "send this to my client", "give
  me a shareable link", "make this report public", "can they view it without an
  account?", or "revoke that link".
---

# Share a Report with a Client

Sharing is **per run**, not per template: publishing one run exposes only that
run's report — the template configuration and every other run stay private. This
is how an analyst hands a finished briefing to a client.

## Step 1 — Get the run_id of a completed run

Only completed runs should be shared. Find the run_id via `research-reports` —
**`list_template_reports(template_id=<id>)`**, which requires the template_id and
returns metadata only (`id`, `run_id`, `date`, `status`, `is_public`,
`public_link`). That listing is ideal here: it already tells you the status and
whether the run is public, without pulling any report content.

Confirm `status = completed` before publishing. If `is_public` is already true,
the run has a live link — say so and show `public_link` rather than re-publishing.

> **`completed` does not mean every section is current.** A template assembles its
> modules' latest published results, so if one module failed to produce a new
> result the run still completes — reusing that module's older output, with no
> error (see `research-reports`). Before a link goes to a client, check when each
> module's data was produced and tell the user which sections are from when. Judge
> a module against **its own** `run_frequency`, not the report's cadence: a monthly
> economic section is *supposed* to be weeks old. Surface the dates and let the
> analyst decide — but never hand over a client link while silently assuming a
> `completed` status means fresh.

## Step 2 — Publish

`set_template_run_visibility(run_id, <visibility → public>)` — mark the run public.

**Read the tool's own schema for the visibility argument's name and values** and
set it explicitly. Do not send a bare `run_id` and rely on a default: publishing
is the outward action, and it must be unambiguous in the call itself. The same
explicitness is what lets the Claude Code publish gate tell a publish from a
revoke — an unrecognisable payload makes it prompt (correctly, but noisily).

Then give the user the shareable link. **Use the `public_link` the platform
returns** — either from the publish response or by re-reading
`list_template_reports(template_id=<id>)`, whose rows carry `is_public` and
`public_link`. Never construct the URL from a remembered base path; it differs per
deployment, and a hand-built link is how a client gets sent a dead page. If no
`public_link` comes back, say so and point the user at the run in the Wealthink
app. The recipient needs **no Wealthink account** to view it.

## Step 3 — Revoke when done

`set_template_run_visibility(run_id, <visibility → private>)` — same tool, the
visibility argument set explicitly back to private. The link stops working
immediately.

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
> alone: it only fires for the bundled connector in Claude Code. Everywhere else
> — Cowork, and any client where Wealthink was configured by hand — the
> confirmation above is the only thing standing between the user and a public
> link.

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
