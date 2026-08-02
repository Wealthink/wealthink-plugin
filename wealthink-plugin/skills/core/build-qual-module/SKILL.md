---
name: build-qual-module
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__create_qual_data_source
  - mcp__plugin_wealthink_mcp__create_qual_module
  - mcp__plugin_wealthink_mcp__create_tag
  - mcp__plugin_wealthink_mcp__run_module
  - mcp__plugin_wealthink_mcp__test_run_qual
  - mcp__plugin_wealthink_mcp__test_run_qual_stream
  - mcp__plugin_wealthink_mcp__update_qual_data_source
  - mcp__plugin_wealthink_mcp__update_qual_module
  - Agent(module-builder)
  - Agent(output-digest)
description: >
  Create, refine, or archive a qualitative research module on Wealthink — an
  LLM-driven analysis (SWOT, market summary, news digest, policy-impact read,
  thesis check) that runs over tracked news/events or manual search queries and
  produces structured research. Use when the user says "set up a module that
  tracks X", "create an analysis for Y", "change what my gold SWOT looks at",
  "add a tag to that module", or "retire this analysis".
---

# Build a Qualitative Research Module

A qualitative module is a reusable, schedulable analysis: a research question +
the news/sources it reads + the shape of its output. Examples for a multi-asset
firm: "SWOT on gold this week", "RBI policy → rate-path read", "rupee drivers
digest", "earnings-season sentiment for my equity watchlist".

## Step 0 — Gather the building blocks (via `discover`)

Modules reference real IDs — fetch them first, never guess:

- `list_tags` — the workspace's own tag IDs/labels. A module with **fetch type =
  events** reads the tracked news under one or more of these.
- `list_pool_tags` — tags in the **Common Event Pool**, the platform-curated shared
  news feed. A separate namespace from `list_tags`.
- `list_qual_data_sources` / `list_data_sources` — the data sources the analysis
  may draw on.

If the user needs a tag or data source that doesn't exist yet, you can create one
(`create_tag`; `create_qual_data_source`) — confirm with the user first.

### Two tag fields, two different failure modes

A qual module takes **`user_tags`** (the org's own events) and **`pool_tags`** (the
shared Common Event Pool). They behave differently when a name doesn't match, and
this is the single easiest way to build a module that looks fine and analyses
nothing:

| | Unknown name is… | Consequence |
|---|---|---|
| `user_tags` | **auto-created** | A typo silently becomes a new, empty tag. The module reads nothing from it — no error. |
| `pool_tags` | **silently dropped** | The pool contribution vanishes. The module still runs, on less data than intended — no error. |

So: **resolve both against their own list tool before creating anything.** Never
hand-type a pool tag; it must come from `list_pool_tags`. Create a user tag
deliberately — via `create_tag`, or by passing a new name you and the user have
agreed on — never by accident.

Pool tags are worth reaching for when the analysis needs macro or geopolitical
context the org doesn't track itself. The pool has no plan gate, so this is free
breadth.

## Step 1 — Decide how the module gets its inputs

Two fetch modes:

- **`events`** — the module analyses the news Wealthink already tracks under the
  given **tag(s)**. This is the common case for a managed workspace. Requires at
  least one tag.
- **`manual`** — the module runs its own **search queries** against the chosen
  data sources at run time. Requires at least one query. Use when the topic isn't
  in the tracked news stream.

## Step 2 — Try the spec before you save it

`test_run_qual` runs a spec **without creating anything**. Use it whenever the
module's shape is uncertain — a new `context`, an unfamiliar tag set, a first
attempt at a structured output format. It is the difference between iterating on a
draft and leaving a trail of half-right modules in the user's workspace.

(`test_run_qual_stream` is the streaming variant; prefer the blocking form unless
the user wants to watch it arrive.)

Show the user the test output, refine the spec, and only then create it. If the
spec is already settled — the user dictated it, or you're copying a known-good
module — skip straight to Step 3.

## Step 3 — Create the module

Call `create_qual_module`. Provide:

- **name** — clear display name ("RBI Policy Watch").
- **context** — the actual research instruction / question the LLM follows. This
  is the heart of the module; make it specific ("Assess this week's RBI
  communications for rate-cut signals and summarise the likely impact on bond
  yields and the rupee.").
- **fetch type** — `events` or `manual` (per Step 1).
- **`user_tags`** — required for `events`. IDs/names resolved from `list_tags`; an
  unrecognised name is auto-created as a new empty tag (see Step 0).
- **`pool_tags`** — *(optional)* Common Event Pool tags, resolved from
  `list_pool_tags`. Unrecognised names are silently dropped (see Step 0).
- **search queries** — required for `manual`.
- **data sources** — the source(s) to read.
- *(optional)* output format (structured JSON schema vs markdown), result count,
  location, a commodity/instrument hint, and **`run_frequency`** (cron) — read the
  schedule rules below before setting one.

Prefer a **structured output format** (named sections) when the module will feed
a report — it makes report layout and stitching predictable.

### Scheduling: `run_frequency` now actually fires

This used to be inert metadata. It isn't any more — a worker executes it, so
setting it commits the user to recurring runs (and recurring cost).

- **Confirm the schedule with the user before setting it.** "Weekly" in
  conversation is not consent to a cron entry.
- An **invalid cron expression is rejected at save** with a 400. Don't retry the
  same string; fix it or drop it.
- `run_frequency` **cannot** combine with an absolute `time_window`
  (`mode="absolute"`) — that combination 422s. A fixed date range and a repeating
  schedule are contradictory; use a relative window for scheduled modules.
- **Repeated credential failures auto-pause a schedule.** A paused schedule looks
  identical to a live one except for `schedule_status`, `schedule_paused_reason`
  and `schedule_paused_at`. **Read those back** before telling the user their
  schedule is running — and if it's paused for credentials, the fix is adding the
  key in the Wealthink app, which is a human action.

## Step 4 — Confirm

Read the created module back (`list_qual_modules` / the create response) and show
the user a summary — including the resolved tags and, if you set one, the schedule
and its `schedule_status`. Offer to run it once via `run-research` (`run_module`)
so they can see real output before relying on it.

## Building several modules at once

What you need to know to sequence this well:

- **A module takes 2–4 minutes to build and run**, so building N of them one after
  another is slow. `module-builder` agents run concurrently — spawn one per
  approved spec. Hand each a complete spec with IDs and tags already resolved; it
  cannot come back with questions.
- **Modules sharing a data source share its rules** — field names, precision, how
  a value is classified. They succeed or fail together. Modules on different
  sources fail independently.
- **`test_run_qual` runs a spec without saving anything** (Step 2), so a rule can
  be checked before it is committed to N modules. Test-runs are concurrent too.
- **A qual module's output is the least predictable part.** A payload shows you
  endpoints and precision, but not what a `context` will make the LLM write.

Sequencing across a whole plan — several modules, several reports, which can
overlap — is worked out in `plan-research`.

## Fixing a module that already exists

Use the **`module-fixer`** agent. It has no `create_*` tools and is bounded to
five edit→run cycles, so a repair terminates. Give it the assertions the output
must satisfy — without them it returns `blocked` rather than guessing, since
"fix this" has no definition of done.

## Refine an existing module

`update_qual_module(module_id, ...)` — partial update; send only what changes.

> **Replace-not-append:** the data-source list is *replaced* by what you send.
> To keep existing sources and add one, include the full intended list.

## Retire a module

`archive_qual_module(module_id)` — soft-delete (recoverable). Archive is the
removal path for modules; there is no hard-delete for them. **Always confirm with
the user before archiving** — and in Claude Code the removal-gate hook enforces
this by requiring an explicit confirmation on `archive_*` calls. The confirmation
is the rule; the hook is the backstop.

## Data sources (optional management)

- `create_qual_data_source(...)` — add a news/web/API source.
- `update_qual_data_source(...)` — edit one.
- `delete_qual_data_source(...)` — **hard delete, not recoverable.** This is the
  one destructive tool in the plugin that isn't an archive. Any module reading
  from that source loses it. Confirm explicitly with the user, name the source
  and what still depends on it, and prefer editing over deleting. In Claude Code
  the removal-gate hook also prompts on `delete_*`.

## Notes

- A good `context` is the difference between a vague and a sharp module — invest
  in it, and reflect the user's actual question.
- Everything is scoped to the user's workspace; you only ever see their modules.
- If a write returns `plan_required` / 402, relay the upgrade message plainly.
