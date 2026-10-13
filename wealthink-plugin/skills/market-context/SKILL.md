---
name: market-context
description: >
  Explain what is happening to a company, sector, macro driver, theme or
  portfolio in Indian markets over the last 24–72 hours, how the stories
  connect, and whether the news supports or challenges the user's view, using
  Wealthink's connected news map. Use for "what's going on with HDFC Bank",
  "how are rates hitting autos", "does the news back my view on cement",
  "brief me on my portfolio".
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth). Uses the agent's own web search when available.
license: MIT
metadata:
  author: wealthink
  version: "0.3.0"
allowed-tools: mcp__plugin_wealthink_mcp__list_pool_tags mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_company_stories mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article mcp__plugin_wealthink_mcp__get_pool_pulse
---

# Market context

Tools and the data model are in `coherence-engine`.

A subject is moved by three rings of news: its own stories, its sector's, and
the macro drivers reaching its sector (`get_pool_pulse` →
`sector_view[<sector>].breakdown.driver_knockons`). Pull rows for each ring,
open the few stories that carry the answer, and join them into threads through
their links and knock-ons. The value is in the joins: a cause the user didn't
know, two headlines that are one event, a driver behind several stories, or a
knock-on that reaches their company through its industry (say that last step
is your inference).

If the user has a view, show the challenges first, then the supports, each
with the article it rests on, linked, then the swing factor. Don't call the view right or
wrong.

Lead with the bottom line, name each thread's labels and the window, and end
with two or three things to watch. For a portfolio, group holdings by sector
and pull the sector and driver rings once per sector.
