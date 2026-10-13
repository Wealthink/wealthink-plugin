---
name: connect
description: >
  Set up and verify the connection to Wealthink's market coherence engine from any
  AI agent: add the Wealthink MCP server, sign in with OAuth, install these
  skills, and confirm it works. Use at the start of a session, when the user
  is new, when a Wealthink tool reports "not connected" / "not authenticated"
  / 401, or when the user asks how to connect Wealthink to Claude, ChatGPT,
  Cursor, VS Code, Codex, Gemini CLI or another agent.
compatibility: Any MCP-capable agent with remote (streamable HTTP) MCP and OAuth support.
license: MIT
metadata:
  author: wealthink
  version: "0.3.0"
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_pulse mcp__plugin_wealthink_mcp__list_pool_tags
---

# Connect to Wealthink

| | |
|---|---|
| MCP endpoint | `https://api.thewealthink.com/mcp` |
| Transport | Streamable HTTP |
| Auth | OAuth 2.0 in the browser (dynamic client registration). No API key, no password |
| Skills | `https://github.com/Wealthink/wealthink-plugin` (open Agent Skills format) |

**Never ask the user for an email, password or token.** Wealthink never
authenticates through the chat. The client opens a browser for sign-in and
consent, then stores and refreshes the token itself.

## 1. Add the MCP server

Use the server name **`wealthink`** wherever the client asks for one, so tool
names stay predictable (`mcp__wealthink__get_pool_story` and similar).

| Client | How |
|---|---|
| Claude Code | Install the plugin: `/plugin marketplace add Wealthink/wealthink-plugin`, then `/plugin install wealthink@wealthink`. Run `/mcp`, pick `plugin:wealthink:mcp`, and choose **Authenticate** |
| Claude Desktop / claude.ai | **Customize → Plugins**, add the `Wealthink/wealthink-plugin` marketplace, install **Wealthink**. Or add a custom connector with the endpoint |
| ChatGPT | Settings → Apps & Connectors → Advanced → turn on Developer mode (paid plans), then add a connector with the endpoint and OAuth authentication |
| Cursor | `.cursor/mcp.json`: `{"mcpServers": {"wealthink": {"url": "https://api.thewealthink.com/mcp"}}}` |
| VS Code (Copilot) | `.vscode/mcp.json`: `{"servers": {"wealthink": {"type": "http", "url": "https://api.thewealthink.com/mcp"}}}` |
| Codex CLI | `codex mcp add wealthink --url https://api.thewealthink.com/mcp`, then `codex mcp login wealthink` |
| Gemini CLI | `~/.gemini/settings.json`: `{"mcpServers": {"wealthink": {"httpUrl": "https://api.thewealthink.com/mcp", "oauth": {"enabled": true}}}}`, then `/mcp auth wealthink` |
| Others | Add a remote HTTP MCP server at the endpoint. Any client that supports MCP OAuth works |

The repo's `docs/connect.md` has full snippets and troubleshooting per client.

## 2. Install the skills (agents other than the Claude plugin)

The skills follow the open Agent Skills standard (`SKILL.md` folders), so any
skills-compatible agent can use them: Codex, Cursor, Gemini CLI, OpenCode,
GitHub Copilot, Goose, Amp and more.

```bash
npx skills add Wealthink/wealthink-plugin          # pick agents interactively
npx skills add Wealthink/wealthink-plugin -a codex -a cursor -g   # specific agents, user-wide
```

Or copy `wealthink-plugin/skills/*` into your agent's skills directory.
Agents without skills support can use `docs/agent-instructions.md` as a
system prompt instead.

## 3. Verify

Call `get_pool_pulse`. A response with `as_of` and `stories_24h` means the
connection works. Then tell the user what's live, in one line:

```
Connected to Wealthink. 253 stories in the last 24 h (to 07 Oct 17:57 IST).
```

Then give the user a first taste of what Wealthink does: name the one or two
sectors with the most one-sided news today, and the driver behind them, from
the same pulse response.

Then offer the starting points:

- "What's moving the market today?": `market-pulse`
- "What's going on with <company / sector / driver>?" or "Is my view on … still
  right?": `market-context`
- "Why did <headline> happen, and what came of it?": `trace-story`

## Troubleshooting

- **401 / "not authenticated" / token expired**: re-run the client's
  authenticate or login step. In Claude Code, `/mcp` → the server →
  **Re-authenticate**.
- **The server isn't listed**: the config wasn't loaded. Restart the client,
  or check that the config file and server name are right. In the Claude Code
  plugin the server is labelled `plugin:wealthink:mcp`.
- **Tools missing from the session**: the client may load tools on demand;
  look them up by name (e.g. `get_pool_story`).
- **402 / plan_required**: this isn't a connection problem. The plan doesn't
  cover that window or feature.
- **Many unrelated tools listed** (modules, templates, reports): the same server
  serves the Wealthink desktop app. Ignore them for news work.
