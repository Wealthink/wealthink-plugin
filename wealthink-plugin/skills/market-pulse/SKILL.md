---
name: market-pulse
description: >
  What's moving Indian markets right now: which sectors the last 24 hours of
  news helped or hurt, which macro drivers are behind it, and which stories
  are still developing, from Wealthink's news map. Use for "what's happening
  in the market today", "morning brief", "anything big today?".
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth). Works with any MCP-capable agent.
license: MIT
metadata:
  author: wealthink
  version: "0.5.0"
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_pulse mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_driver_moves mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article
---

# Market pulse

Tools and the data model are in `coherence-engine`.

`get_pool_pulse` counts, per sector, the stories from the last 24 h that
report it helped or hurt, directly or through knock-ons. Lead with the most
one-sided sectors, and group them by the driver behind them
(`breakdown.driver_knockons`, or `list_pool_driver_moves(window="24h")` for
each driver's up and down count): one driver often explains several sectors.
Open two to four of the stories behind the biggest counts (the ids are in the
pulse) for the headlines and evidence.

Present counts as counts of stories, not market moves, and cite the story ids
you lean on. If the pulse comes back with `stale: true` elsewhere in the
session, say the news may be out of date. If the user wants index
or price moves and you have web search, look them up and label them as from the
web. Close with what's still developing.
