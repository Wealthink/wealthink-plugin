# Wealthink for agents

Understand Indian markets with Wealthink from inside your agent. Wealthink is a
**coherence engine**, not a search engine: it reads recent
financial news and links it into one map. Each story is tied to its causes and
consequences, labelled with the sectors, macro drivers, categories and
companies it moves, and mapped to its **knock-on** effects on other sectors.
This plugin teaches the agent to set up the connection, to know what every tool
returns, and to turn any market question into a connected answer: what is
happening, why, how it reaches you, what supports and challenges your view,
and what to watch next. It uses the agent's own web search to fill the gaps.

> Building research modules and reports has moved to the **Wealthink desktop
> app**. This plugin is for understanding the news.

## Install

**Claude Code**

```bash
/plugin marketplace add Wealthink/wealthink-plugin
/plugin install wealthink@wealthink
```

Then connect: run `/mcp`, choose **`plugin:wealthink:mcp`**, then **Authenticate**.
OAuth opens in your browser; there is no token to copy and no password to type.

**Claude Desktop / claude.ai / Cowork**: go to **Customize → Plugins**, add the
`Wealthink/wealthink-plugin` marketplace, and install **Wealthink for agents**.

**Any other agent** (Codex, Cursor, Gemini CLI, OpenCode, Copilot…): the skills
are plain [Agent Skills](https://agentskills.io), so install them with
`npx skills add Wealthink/wealthink-plugin` and connect the MCP server; see
[`../docs/connect.md`](../docs/connect.md). For agents without skills support
(e.g. ChatGPT), use [`../docs/agent-instructions.md`](../docs/agent-instructions.md).

## What you can ask

| Ask | Skill |
|---|---|
| "What's moving the market today?" · "Pre-market brief" | `market-pulse` |
| "What's going on with HDFC Bank?" · "How is crude affecting paints?" · "Is my case for cement intact?" · "Brief me on my portfolio" | `market-context` |
| "Why did the RBI hold?" · "What came of the steel duty story?" | `trace-story` |
| "Run a thesis check on …" (paid plans) | `thesis-check` |
| "How do I connect?" | `connect` |
| Anything else about the markets | `/wealthink <your question>` |

`coherence-engine` underlies all of them. It explains what Wealthink is, the
data model (stories, links, knock-ons, labels, company directions), and every
tool's parameters and returns. Real payload samples are in
`skills/coherence-engine/references/data-model.md`.

## Tools used

The Wealthink MCP server also serves the desktop app, so it exposes many tools
(modules, templates, reports, data sources). This plugin uses only the news
tools and tells the agent to ignore the rest:

| | Core (on every server today) | Extended (newer servers; used when listed) |
|---|---|---|
| Pulse | `get_pool_pulse` | `get_news_pulse`, `get_news_pulse_graph` |
| Find stories | `list_pool_stories`, `list_pool_company_stories` | `list_news_stories`, `search_news_companies`, `list_latest_news` |
| Research | `list_pool_driver_moves`, `list_pool_knockons`, `get_pool_story_timeline` | |
| Read stories | `get_pool_story`, `get_pool_article` | `get_news_story` |
| Thesis Check (paid) | `run_pool_thesis_check`, `list_pool_thesis_checks`, `get_pool_thesis_check` | `validate_my_thesis_statement` |
| Plan and invites | `get_my_usage`, `get_my_referral` | `get_my_thesis_config`, `list_public_plans` |

Filters take exact values (listed in each tool's parameters); `list_pool_tags`
and `get_pool_feed` are desktop-app tools and are not listed to this plugin.

The skills use bare tool names, so they work with any client's prefix.

In Claude Code, tools load on demand (the connector isn't `alwaysLoad`).

## Quota and safety

- **Story opens are metered.** `get_pool_story` / `get_news_story` count once
  per story per day against the plan. The skills list first and open sparingly.
- **Thesis Check is a paid-plan feature with a weekly limit**; the tools are
  absent on free plans, where `market-context` reads supports and challenges
  without the scoring. The `thesis-check` skill confirms before every run. In Claude Code a `PreToolUse` hook
  also asks before every `run_pool_thesis_check`; see `hooks/README.md`.
- **No advice.** Company arrows are business impact, not price calls, and
  knock-ons are Wealthink's reasoning, not article claims. The skills label
  both.

## Layout

```
wealthink-plugin/
├── .claude-plugin/plugin.json
├── .mcp.json                 # https://api.thewealthink.com/mcp (OAuth)
├── commands/wealthink.md     # /wealthink router
├── hooks/                    # session reminder + thesis-check gate
└── skills/
    ├── connect/
    ├── coherence-engine/     # what Wealthink is, data model, tool reference (+ references/data-model.md)
    ├── market-context/       # the main workflow: any market question → a connected answer
    ├── market-pulse/
    ├── trace-story/
    └── thesis-check/
```
