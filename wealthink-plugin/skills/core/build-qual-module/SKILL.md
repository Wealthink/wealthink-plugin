---
name: build-qual-module
allowed-tools: mcp__plugin_wealthink_wealthink__*
description: >
  Create, refine, or archive a qualitative research module on Wealthink — an
  LLM-driven analysis (SWOT, market summary, news digest, policy-impact read,
  thesis check) that runs over tracked news/events or manual search queries and
  produces structured research. Use when the user wants to set up a new analysis,
  change what an existing analysis does, or retire one.
---

# Build a Qualitative Research Module

A qualitative module is a reusable, schedulable analysis: a research question +
the news/sources it reads + the shape of its output. Examples for a multi-asset
firm: "SWOT on gold this week", "RBI policy → rate-path read", "rupee drivers
digest", "earnings-season sentiment for my equity watchlist".

## Step 0 — Gather the building blocks (via `discover`)

Modules reference real IDs — fetch them first, never guess:

- `list_tags` — tag IDs/labels. A module with **fetch type = events** reads the
  tracked news under one or more tags.
- `list_qual_data_sources` / `list_data_sources` — the data sources the analysis
  may draw on.

If the user needs a tag or data source that doesn't exist yet, you can create
one (`create_tag`; `create_qual_data_source`) — confirm with the user first.

## Step 1 — Decide how the module gets its inputs

Two fetch modes:

- **`events`** — the module analyses the news Wealthink already tracks under the
  given **tag(s)**. This is the common case for a managed workspace. Requires at
  least one tag.
- **`manual`** — the module runs its own **search queries** against the chosen
  data sources at run time. Requires at least one query. Use when the topic isn't
  in the tracked news stream.

## Step 2 — Create the module

Call `create_qual_module`. Provide:

- **name** — clear display name ("RBI Policy Watch").
- **context** — the actual research instruction / question the LLM follows. This
  is the heart of the module; make it specific ("Assess this week's RBI
  communications for rate-cut signals and summarise the likely impact on bond
  yields and the rupee.").
- **fetch type** — `events` or `manual` (per Step 1).
- **tags** — required for `events`. Any new tag names are auto-created.
- **search queries** — required for `manual`.
- **data sources** — the source(s) to read.
- *(optional)* output format (structured JSON schema vs markdown), result count,
  location, a commodity/instrument hint, and a run schedule (cron) for
  auto-runs.

Prefer a **structured output format** (named sections) when the module will feed
a report — it makes report layout and stitching predictable.

## Step 3 — Confirm, then optionally test

Read the created module back (`list_qual_modules` / the create response) and show
the user a summary. Offer to run it once via `run-research` (`run_module`) so they
can see real output before relying on it.

## Building several modules at once (approve-then-fan-out)

When the user wants **several** modules built in one go (the UC1 flow, often
arriving from `plan-research`), the shape is **approve on the main thread, then
fan out**:

1. **On the main thread (this skill):** discover building blocks, draft each
   module's spec, and **get the user's approval of every spec** — including a
   test-run of any uncertain candidate (Step 3). All questions happen here; an
   agent can't ask anything.
2. **Fan out:** spawn one **`module-builder`** agent per *approved* spec. Each
   agent autonomously creates its module, test-runs it once, and returns a compact
   summary. Hand each agent a complete spec with IDs/expiries already resolved —
   it cannot come back with questions.
3. **Review the summaries with the user.** Re-run or refine any module that came
   back `weak` / `blocked`.

If the harness can't spawn subagents, walk the approved specs **sequentially**
inline with the same `create_*` + test-run steps — identical tools and approvals,
just no parallelism.

## Refine an existing module

`update_qual_module(module_id, ...)` — partial update; send only what changes.

> **Replace-not-append:** the data-source list is *replaced* by what you send.
> To keep existing sources and add one, include the full intended list.

## Retire a module

`archive_qual_module(module_id)` — soft-delete (recoverable). There is no
hard-delete through the connector; archive is the removal path. **Always confirm
with the user before archiving** — and in Claude Code the archive-gate hook
enforces this by requiring an explicit confirmation on `archive_*` calls. The
confirmation is the rule; the hook is the backstop.

## Data sources (optional management)

- `create_qual_data_source(...)` — add a news/web/API source.
- `update_qual_data_source(...)`, `delete_qual_data_source(...)`.

## Notes

- A good `context` is the difference between a vague and a sharp module — invest
  in it, and reflect the user's actual question.
- Everything is scoped to the user's workspace; you only ever see their modules.
- If a write returns `plan_required` / 402, relay the upgrade message plainly.
