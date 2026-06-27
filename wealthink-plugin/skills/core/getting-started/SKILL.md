---
name: getting-started
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Connect to Wealthink, sign in, and orient a new user in their workspace. Use
  this at the start of a session, when the user is new to Wealthink, when a tool
  reports "not logged in", or when the user asks "what can I do here?",
  "what's set up in my workspace?", or "how do I get started?".
---

# Getting Started with Wealthink

Wealthink is a research platform for wealth and investment research teams. You
reach it through the **Wealthink MCP connector**, which gives you tools to browse
the market news Wealthink tracks for the user, run qualitative and quantitative
research, and assemble and share research reports.

Your job in this skill: make sure the user is signed in, then show them what
their workspace already contains so they know what to do next.

## Step 1 — Make sure you're connected to Wealthink

The Wealthink connector authenticates with **OAuth** — there is no token to copy
and no password to type into the chat. Authentication happens once in the browser
and is cached.

**First-time connect:**
- **Claude Code** — run `/mcp`, select **wealthink**, and choose **Authenticate**.
  A browser window opens for Wealthink sign-in/consent; approve it. Claude Code
  caches the token in your system keychain and refreshes it automatically, so you
  won't be asked again on this machine.
- **claude.ai (chat / Cowork)** — authorise the **Wealthink** connector under
  **Settings → Connectors**; the OAuth consent opens in a browser tab.

**Confirm you're connected** before doing real work: call a lightweight read tool
such as `list_all_modules`. If it returns data (even an empty list), you're
connected and can continue to Step 2.

**If a tool reports "not connected" / "not authenticated" / 401:**
1. Re-run the connect step above (`/mcp` → **wealthink** → **Authenticate**, or
   **Settings → Connectors** on claude.ai).
2. If **wealthink** isn't listed in `/mcp` at all, the plugin's MCP server may not
   be enabled — check `/plugin` shows **wealthink** installed and enabled, then
   retry `/mcp`.
3. Retry the read tool. Never ask the user for an email or password — Wealthink
   never authenticates through the chat.

## Step 2 — Orient: show what's already in the workspace

Run a few read-only discovery tools in parallel and summarise the result:

- `list_all_modules` — qualitative + quantitative research modules they already have
- `list_templates` — research report templates
- `list_events` (with a small limit, e.g. 10) — recent market news Wealthink is tracking for them
- `list_tags` — the topics/instruments their workspace is organised around

Present a short, friendly orientation — for example:

```
Your Wealthink workspace
  • 6 research modules (4 qualitative, 2 quantitative)
  • 2 report templates ("Weekly Macro+Commodity", "Daily Bullion Brief")
  • Tracking 38 recent news items across tags: gold, silver, rupee, RBI policy
  • Latest report run: Weekly Macro+Commodity — 2 days ago

What would you like to do?
  – Get a market briefing on a topic           → market-news + run-research
  – Run a module or report and see the result  → run-research / research-reports
  – Build a new module or report               → build-qual-module / build-quant-chart / research-reports
```

Only list sections that have content. Keep it scannable.

## What this platform can do for the user

| You want to… | Skill to use |
|--------------|--------------|
| See what's happening in the market | `market-news`, then `run-research` |
| Run an analysis and read the result | `run-research` |
| Create/tune an analysis question | `build-qual-module` |
| Create/tune a chart (e.g. MCX futures) | `build-quant-chart` |
| Produce a full multi-section report | `research-reports` |
| Share a report with a client | `share-report` |
| Lay out a report visually | `generate-layout` |

## Good to know

- **Market news is provisioned by Wealthink.** The user reads and analyses the
  news Wealthink tracks for them; they don't set up new trackers through Claude
  (that's done in the Wealthink app / with their account manager).
- **Some actions depend on the plan.** Everything in this plugin is offered to
  everyone, but the Wealthink backend decides what each workspace may do. If a
  tool returns `plan_required` / a 402, relay it plainly: *"That action needs a
  Pro plan — contact your Wealthink account manager."* Never present it as a bug.
- **Never invent IDs.** Use `discover` (or the `list_*` tools) to find real
  module/template/tag IDs before acting on them.
