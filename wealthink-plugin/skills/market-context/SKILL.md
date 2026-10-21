---
name: market-context
description: >
  Explain what is happening to a company, sector, macro driver, theme or
  portfolio in Indian markets over recent days (3 days on Free, 30 on Starter, 90 on Pro, a year on Advanced), how the stories
  connect, and whether the news supports or challenges the user's view, using
  Wealthink's connected news map. Use for "what's going on with HDFC Bank",
  "how are rates hitting autos", "does the news back my view on cement",
  "brief me on my portfolio".
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth). Uses the agent's own web search when available.
license: MIT
metadata:
  author: wealthink
  version: "0.5.1"
allowed-tools: mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_company_stories mcp__plugin_wealthink_mcp__list_pool_driver_moves mcp__plugin_wealthink_mcp__list_pool_knockons mcp__plugin_wealthink_mcp__get_pool_story_timeline mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article mcp__plugin_wealthink_mcp__get_pool_pulse mcp__plugin_wealthink_mcp__get_my_usage
---

# Market context

Tools and the data model are in `coherence-engine`.

A subject is moved by three rings of news, each with its own tool:

1. **Its own stories**: `list_pool_company_stories(company=<ISIN or name>)`
   gives the tally and the stories; for a sector, `list_pool_stories(sector=…)`.
2. **Its sector's**: `list_pool_stories(sector=<exact sector>, window=…)`.
3. **The drivers reaching it**: `list_pool_driver_moves` (which drivers moved,
   and whether other reports backed it: `day_check`), then
   `list_pool_knockons(sector=<its sector>)` for the effects that reached its
   industry and why.

Use the longest window the plan opens that fits the question
(`get_my_usage` → `windows`). Open the few stories that carry the answer, and
join them into threads through their links (`get_pool_story_timeline`) and
knock-ons. The value is in the joins: a cause the user didn't
know, two headlines that are one event, a driver behind several stories, or a
knock-on that reaches their company through its industry (say that last step
is your inference).

If the user has a view, show the challenges first, then the supports, each
with the article it rests on, linked, then the swing factor. Don't call the view right or
wrong.

Lead with the bottom line, name each thread's labels and the window, cite the
`story_id` behind each claim, and end with two or three things to watch. A
`not_confirmed` driver move is a lead, not a fact: say so. For a portfolio, group holdings by sector
and pull the sector and driver rings once per sector.
