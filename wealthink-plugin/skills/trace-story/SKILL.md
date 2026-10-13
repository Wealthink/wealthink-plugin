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
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_story mcp__plugin_wealthink_mcp__get_pool_article mcp__plugin_wealthink_mcp__list_pool_stories mcp__plugin_wealthink_mcp__list_pool_company_stories
---

# Trace a story

Tools and the data model are in `coherence-engine`.

Find the story with `list_pool_stories`, open it, then walk *follows from*
back for the cause and *followed by* forward for what came next. Each link
carries the neighbour's headline and strength, so open a neighbour only when
you need its own links or evidence. Keep a visited set, because links can
loop. Use the knock-ons to show which industries the story reaches, and why.

Present it as a short timeline with each join's type and strength, then the
reach, then what's still open. When the chain runs past Wealthink's 72 h and
you have web search, fill the missing step from the web and mark it as such.
