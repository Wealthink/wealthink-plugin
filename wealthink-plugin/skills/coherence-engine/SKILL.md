---
name: coherence-engine
description: >
  Wealthink is a coherence engine for Indian markets: it links the last 24–72
  hours of financial news into one map of stories, their causes and
  consequences, knock-on effects across sectors, and the companies, sectors,
  macro drivers and categories they touch. This skill explains the Wealthink
  MCP tools, what each returns, and what problems they solve. Use for any
  question about what is happening in Indian markets, why, and what it means
  for a company, sector, portfolio or view.
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth). Works with any MCP-capable agent.
license: MIT
metadata:
  author: wealthink
  version: "0.3.0"
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_pulse mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_company_stories mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article mcp__plugin_wealthink_mcp__list_pool_tags
---

# Wealthink: the market's news, connected

Wealthink is not a search engine. It reads Indian financial news as it lands
and works out how events fit together: what caused what, which stories are
the same event, which macro force sits behind them, and how news in one place
reaches other sectors. Use it to show the user connections they wouldn't see
from headlines.

Tool names below are bare; your client may prefix them
(`mcp__plugin_wealthink_mcp__get_pool_story`). The server also lists desktop-app
tools (modules, templates, reports); ignore them.

## The map

- **Story**: articles about one event. `state` is `new` → `developing` →
  `settled`.
- **Labels**: sectors, macro drivers (rates, rupee, crude, monsoon…),
  categories, and companies with a direction (`helps` / `hurts` / `mixed` /
  `neutral`). A direction is business impact, not a price call.
- **Links** between stories, each with a `strength` 0–1 (above ~0.65 is solid):
  *follows from* (the cause), *followed by* (what came next), *related*
  (similar, not causal). Two stories that list each other both ways are one
  event. New stories have no links yet; that says nothing about importance.
- **Knock-ons**: how a driver or industry reaches other industries (2nd / 3rd
  order), with `link_strength`, `size` and a `reason`. They are Wealthink's
  reasoning, not article claims, and they end at an industry, not a company.
  Different stories can push the same industry in opposite directions; that is
  the market, not an error.

## Tools

| Tool | Params | Returns |
|---|---|---|
| `get_pool_pulse` | none | Last 24 h only. Per sector: stories reporting it helped / hurt, direct and via knock-ons, with story ids, companies and the drivers behind them. A summary of the news, not a forecast |
| `list_pool_stories` | `sector`, `driver`, `company` (name fragments), `all` (72 h instead of 24 h), `from` / `to` (ISO range), `limit`, `cursor` | Story rows, newest first, unranked: headline, state, article count, companies with direction, sectors, drivers, effects, link count |
| `list_pool_company_stories` | `name` (fragment), `limit`, `cursor` | The same rows for one company. Can reach back about a week, further than the other lists; check `first_seen` |
| `get_pool_story` | `story_id` | One story: articles (`article_id`, publisher, URL), company directions, first-order effects, knock-ons, related / follows-from / followed-by. **Counts against the user's daily story opens** |
| `get_pool_article` | `article_id` | Publisher, headline, URL, a short description, `source_type` (Official, Filing, Company, Analysis, Sources say), `event_type`, `category`, `surprise`, and the companies, sectors and drivers it was tagged with |
| `list_pool_tags` | none | The exact sector, driver and category labels to filter with |
| `run_pool_thesis_check` and past checks | see the `thesis-check` skill | Paid plans only |

List calls return about 10–13 rows per page whatever `limit` says (`count` is
the total, `next_cursor` the next page). Narrow with a driver or company filter
rather than paging through a whole sector. Payload samples:
[references/data-model.md](references/data-model.md).

## What it solves for the user

- **"What's moving the market?"**: `get_pool_pulse` names the sectors with the
  most one-sided news and the drivers behind them (`market-pulse`).
- **"What's going on with X?"** (company, sector, driver, portfolio): X's own
  stories, its sector's, and the drivers reaching its sector, joined into a few
  threads (`market-context`).
- **"Why did this happen / what came of it?"**: walk *follows from* and
  *followed by* from one story (`trace-story`).
- **"Does the news back my view?"**: sort the threads into challenges (first)
  and supports, quoting the evidence (`market-context`). Run a Thesis Check only
  when the user asks for one by name.

Wealthink covers 24–72 h. If you have web search, use it after the map for its
gaps (newer news, primary sources, numbers, older history), and say which
claims came from where.

## Rules

- Open about 3 stories per subject (8–10 at most); rows usually suffice.
- Wealthink gives you the map, not the articles. Don't present tool text as
  quotes from the article; cite `[publisher](url)`, and for exact wording open
  the link with your web fetch or browser tool. Name the window you read.
- Label knock-ons and the pulse as Wealthink's reasoning. No buy/sell advice.
- Keep answers to about 300–400 words unless the user asks for more.
- 401: follow `connect`; never ask for a password. 402: the plan doesn't cover
  it; say so once, don't retry. Empty: widen the window before saying there's
  no news.
