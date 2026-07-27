---
name: getting-started
allowed-tools:
  - mcp__plugin_wealthink_mcp__list_*
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

**First-time connect** — the user authorises the Wealthink connector in whatever
client they are using. Point them at their client's connector/MCP settings; the
exact path differs per client, and
<https://github.com/Wealthink/wealthink-plugin/blob/main/docs/connect.md> covers
each one:

- **Claude Code** — run `/mcp`, pick the Wealthink server (the bundled one is
  listed as **`plugin:wealthink:mcp`**), and choose **Authenticate**. A browser
  window opens for Wealthink sign-in/consent; approve it. The token is cached in
  the system keychain and refreshed automatically, so this is a one-time step per
  machine. `claude mcp login plugin:wealthink:mcp` does the same from a shell.
- **Cowork / claude.ai / Claude Desktop** — install the Wealthink plugin from
  **Customize → Plugins**, or authorise the **Wealthink** connector under
  **Settings → Connectors**. The same OAuth consent opens in a browser tab.
- **Any other MCP client** — authorise the Wealthink server in that client's MCP
  settings. Note that outside the plugin they get the tools but none of these
  skills or the safety hooks, so confirm outward actions extra carefully.

**Confirm you're connected** before doing real work: call a lightweight read tool
such as `list_all_modules`. If it returns data (even an empty list), you're
connected and can continue to Step 2.

**If a tool reports "not connected" / "not authenticated" / 401:**
1. Re-run the connect step above for the user's client.
2. If no Wealthink server appears in the client's MCP list at all, the connector
   isn't registered. On Claude Code, check `/plugin` shows **wealthink** installed
   and enabled, then retry `/mcp`. Do not diagnose this from the server's label —
   the bundled server is named after the plugin (`plugin:wealthink:mcp`), not
   `wealthink`.
3. Retry the read tool. Never ask the user for an email or password — Wealthink
   never authenticates through the chat.

## Step 2 — Orient: show what's already in the workspace

Run a few read-only discovery tools in parallel and summarise the result:

- `list_module_options` — the cheapest inventory: id + name for every qualitative
  and quantitative module in one unpaginated call
- `list_templates` — research report templates. Pass `page_size: 5` and don't pass
  `include_layout` — layouts are excluded by default and you don't need them here.
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
| Find what you have, and its ID | `discover` |
| See what's happening in the market | `market-news`, then `run-research` |
| Work out what to build in the first place | `plan-research` |
| Replicate a report/process you already produce | `understand-system` |
| Run an analysis and read the result | `run-research` |
| Create/tune an analysis question | `build-qual-module` |
| Create/tune a chart (e.g. a futures candlestick) | `build-quant-chart` |
| Produce a full multi-section report | `research-reports` |
| Share a report with a client | `share-report` |
| Lay out a report visually | `generate-layout` |

If the user's role is clear from the conversation (equity desk, PE, VC, fund
manager), the matching **lens** skill — `public-markets`, `private-equity`,
`venture`, `fund-manager` — maps their vocabulary onto these and hands off.

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
