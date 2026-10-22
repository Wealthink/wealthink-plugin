---
name: thesis-check
description: >
  Run Wealthink's Thesis Check (Starter and above) when the user explicitly
  asks for a thesis check: it scores one statement against the stories the
  plan shows (the last 30 days on Starter) and returns those that challenge or
  support it, with the evidence and match strength. Also reads the user's past checks. For "does the
  news back my view?" without that request, use market-context instead.
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth) and the Starter plan or above; the tools are absent on Free.
license: MIT
metadata:
  author: wealthink
  version: "0.5.1"
allowed-tools: mcp__plugin_wealthink_mcp__list_pool_thesis_checks mcp__plugin_wealthink_mcp__get_pool_thesis_check
---

# Thesis Check

Starter and above, with a weekly limit (40 on Starter; `get_my_usage` →
`meters.thesis_checks`). If `run_pool_thesis_check` isn't in your tool list,
or returns 402, the user's plan doesn't include it: say once that Thesis Check
is on Starter, and test the view with `market-context` instead. A 429 means
this week's checks are used up until `resets_at`.

| Tool | Params | Returns |
|---|---|---|
| `run_pool_thesis_check` | `statement` (one falsifiable claim, ≤ ~200 chars), `company_isin` (optional; only if you know it) | Stories that challenge or support it, challenges first, each with its evidence, the article link and a match strength 0–1, plus close calls |
| `list_pool_thesis_checks` | `limit`, `cursor` | The user's past checks, newest first, with verdicts |
| `get_pool_thesis_check` | `check_id` | One past check in full |

Run it only when the user asks for a thesis check, and **confirm the exact
statement with them first**: it can use one of their weekly checks. Split a
compound view into separate statements. Present challenges first, link each
story's article, and never call the thesis right or wrong.
