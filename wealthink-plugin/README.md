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

> This plugin is for the **Free and Starter** plans. Building research modules
> and reports, and the Pro plans, live in the **Wealthink desktop app**, which
> ships its own plugin.

## Install

**Claude Code**

```bash
claude plugin marketplace add Wealthink/wealthink-plugin
claude plugin install wealthink@wealthink
```

(or `/plugin marketplace add …` and `/plugin install …` inside Claude Code).
Restart Claude Code, then connect: run `/mcp`, choose
**`plugin:wealthink:mcp`**, then **Authenticate**.
OAuth opens in your browser; there is no token to copy and no password to type.

**Claude Desktop / claude.ai / Cowork**: go to **Customize → Plugins**, add the
`Wealthink/wealthink-plugin` marketplace, and install **Wealthink for agents**.

**Any other agent** (Codex, Cursor, Gemini CLI, OpenCode, Copilot…): the skills
are plain [Agent Skills](https://agentskills.io), so install them with
`npx skills add Wealthink/wealthink-plugin` and connect the MCP server; the
[setup guide](./skills/connect/SKILL.md) has the config for each client. For
agents without skills support (e.g. ChatGPT), use
[`agent-instructions.md`](./agent-instructions.md).

## What you can ask

| Ask | Skill |
|---|---|
| "What's moving the market today?" · "Pre-market brief" | `market-pulse` |
| "What's going on with HDFC Bank?" · "How is crude affecting paints?" · "Is my case for cement intact?" · "Brief me on my portfolio" | `market-context` |
| "Why did the RBI hold?" · "What came of the steel duty story?" | `trace-story` |
| "Run a thesis check on …" (Starter) | `thesis-check` |
| "How do I connect?" | `connect` |
| Anything else about the markets | `/wealthink <your question>` |

`coherence-engine` underlies all of them. It explains what Wealthink is, the
data model (stories, links, knock-ons, labels, company directions), and every
tool's parameters and returns. Real payload samples are in
`skills/coherence-engine/references/data-model.md`.

## Tools used

The server lists each plan's own tools, and this plugin uses all of them:

| | Free | Starter |
|---|---|---|
| Pulse | `get_pool_pulse` | same |
| Find stories | `list_pool_stories`, `list_pool_company_stories` | same |
| Research | `list_pool_driver_moves`, `list_pool_knockons`, `get_pool_story_timeline` | same |
| Read stories | `get_pool_story`, `get_pool_article` | same |
| Plan and invites | `get_my_usage`, `get_my_referral` | same |
| Thesis Check | — | `run_pool_thesis_check`, `list_pool_thesis_checks`, `get_pool_thesis_check` |

Filters take exact values (listed in each tool's parameters). On Pro and above
the server also lists the desktop app's module, template and report tools; the
skills ignore them, and those plans are better served by the desktop app.

The skills use bare tool names, so they work with any client's prefix. The
server marks the Free and Starter tools `alwaysLoad`, so Claude Code loads
them at the start of a session instead of on demand.

## Quota and safety

- **Story opens are metered on Free** (100 a day). `get_pool_story` counts once
  per story per day; lists, articles and timelines don't. The skills list first
  and open sparingly.
- **Thesis Check is on Starter, with a weekly limit** (40); the tools are
  absent on Free, where `market-context` reads supports and challenges
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
├── agent-instructions.md     # system prompt for agents without skills (e.g. ChatGPT)
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
