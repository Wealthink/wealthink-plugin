---
name: trace-story
description: >
  Follow one Indian market story through Wealthink's news map: what caused it,
  what happened next, and which sectors it reaches through knock-on effects.
  Use for "why is this happening", "how did we get here", "what came of it",
  "how does this affect X".
compatibility: Requires the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth). Uses the agent's own web search when available.
license: MIT
metadata:
  author: wealthink
  version: "0.3.0"
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_story_timeline mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_company_stories mcp__plugin_wealthink_mcp__list_pool_knockons
---

# Trace a story

Tools and the data model are in `coherence-engine`.

Find the story with `list_pool_stories`, then call
`get_pool_story_timeline(story_id)`: it walks *follows from* back (the cause)
and *followed by* forward (what came next), oldest first, with each step's
companies and driver moves, and lists similar stories apart. It doesn't count
as a story open. Open a step with `get_pool_story` only when you need its
articles or evidence, and use its knock-ons (or `list_pool_knockons`) to show
which industries the story reaches, and why.

Present it as a short timeline, each step with its `story_id` and how it
joins (`follows` / `followed_by` / `related`), then the reach, then what's
still open. A `note` saying linked stories were left out means they are older
than the plan shows. When the chain runs past the window the user's plan allows and
you have web search, fill the missing step from the web and mark it as such.
