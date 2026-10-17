---
name: connect
description: >
  Set up and verify the connection to Wealthink's market coherence engine from any
  AI agent: add the Wealthink MCP server, sign in with OAuth, install these
  skills, and confirm it works. Use when the user pastes the Wealthink setup
  prompt, at the start of a session, when the user is new, when a Wealthink
  tool reports "not connected" / "not authenticated" / 401, or when the user
  asks how to connect Wealthink to Claude, ChatGPT, Cursor, VS Code, Codex,
  Gemini CLI or another agent.
compatibility: Any MCP-capable agent with remote (streamable HTTP) MCP and OAuth support.
license: MIT
metadata:
  author: wealthink
  version: "0.4.0"
allowed-tools: mcp__plugin_wealthink_mcp__get_pool_pulse mcp__plugin_wealthink_mcp__get_my_usage
---

# Connect to Wealthink

| | |
|---|---|
| MCP endpoint | `https://api.thewealthink.com/mcp` |
| Transport | Streamable HTTP |
| Auth | OAuth 2.0 in the browser (dynamic client registration). No API key, no password |
| Skills | `https://github.com/Wealthink/wealthink-plugin` (open Agent Skills format) |
| Plans | Free and Starter. Pro and above use the Wealthink desktop app, which has its own plugin |

**Never ask the user for an email, password or token,** and never put one in a
config file. The client opens a browser for sign-in and consent, then stores
and refreshes the token itself.

## 0. Already connected?

If a Wealthink tool such as `get_my_usage` is in your tool list, call it. If it
answers, skip to [4. Verify](#4-verify). If it returns 401, go to the
authenticate step for your client.

## 1. Find your client

Work out which agent you are running in, then follow its section. Do the steps
you can run yourself (shell commands, config files); tell the user, in one
short numbered list, the steps only they can do (restarting, clicking
**Authenticate**, signing in in the browser).

### Claude Code

Install the plugin. It brings the MCP server, the skills and a hook that asks
before every Thesis Check. If you have a shell tool, run:

```bash
claude plugin marketplace add Wealthink/wealthink-plugin
claude plugin install wealthink@wealthink
```

If `claude plugin list` already shows `wealthink@wealthink`, run
`claude plugin marketplace update wealthink` and
`claude plugin update wealthink@wealthink` instead. Without a shell tool, the
user types `/plugin marketplace add Wealthink/wealthink-plugin`, then
`/plugin install wealthink@wealthink`.

The plugin loads when Claude Code starts. Tell the user:

1. Exit Claude Code and start it again with `claude --continue`, so this
   conversation carries on.
2. Run `/mcp`, choose **`plugin:wealthink:mcp`**, then **Authenticate**, and
   sign in in the browser.
3. Come back and say "done".

The server is listed as `plugin:wealthink:mcp`, not `wealthink`; its tools are
`mcp__plugin_wealthink_mcp__<tool>`. Don't also add a separate `wealthink`
server: the user would see every tool twice.

### Claude.ai, Claude Desktop, Cowork

You can't install anything from the chat. Tell the user:

1. Open **Customize → Plugins**, add the marketplace
   `Wealthink/wealthink-plugin`, and install **Wealthink for agents**.
2. Authorise the Wealthink connector when asked, and sign in in the browser.
3. Start a new chat and ask "What's moving Indian markets today?".

If they only want the tools: **Settings → Connectors → Add custom connector**,
URL `https://api.thewealthink.com/mcp`.

### ChatGPT

ChatGPT can't load skills or install connectors from the chat. Tell the user:

1. Settings → Apps & Connectors → Advanced → turn on **Developer mode** (paid
   ChatGPT plans).
2. Add a connector: URL `https://api.thewealthink.com/mcp`, authentication
   OAuth. Sign in in the browser.
3. Paste the text of
   `https://github.com/Wealthink/wealthink-plugin/blob/main/docs/agent-instructions.md`
   into the project's instructions or custom instructions.

### Codex CLI

```bash
codex mcp add wealthink --url https://api.thewealthink.com/mcp
npx skills add Wealthink/wealthink-plugin -a codex -g -y
```

Then the user runs `codex mcp login wealthink`, signs in in the browser, and
restarts Codex.

### Cursor

Add to `~/.cursor/mcp.json` (all projects), merging with any servers already
there:

```json
{ "mcpServers": { "wealthink": { "url": "https://api.thewealthink.com/mcp" } } }
```

```bash
npx skills add Wealthink/wealthink-plugin -a cursor -g -y
```

Then the user opens Cursor Settings → MCP, clicks **Connect** (or **Login**)
next to `wealthink`, and signs in in the browser.

### Gemini CLI

Add to `~/.gemini/settings.json`, merging with what is there:

```json
{ "mcpServers": { "wealthink": { "httpUrl": "https://api.thewealthink.com/mcp", "oauth": { "enabled": true } } } }
```

```bash
npx skills add Wealthink/wealthink-plugin -a gemini-cli -g -y
```

Then the user runs `/mcp auth wealthink` in Gemini CLI.

### VS Code (Copilot), OpenCode, others

Add a remote HTTP MCP server named **`wealthink`** at
`https://api.thewealthink.com/mcp` in the client's MCP config (VS Code:
`.vscode/mcp.json`, `{"servers": {"wealthink": {"type": "http", "url": "https://api.thewealthink.com/mcp"}}}`).
Install the skills with `npx skills add Wealthink/wealthink-plugin -a <agent> -g -y`
(`npx skills add --help` lists the agent names), or copy
`wealthink-plugin/skills/*` into the agent's skills folder. Then the user
signs in when the client asks.

Use the name `wealthink` for the server wherever you choose one, so tool
names stay predictable (`mcp__wealthink__get_pool_story`).

## 2. Sign in

The client opens a Wealthink page in the browser. A new user can sign up there
(Google or email); the plan starts on Free. Nothing is pasted back into the
chat.

## 3. Wait for the user

Don't loop or poll. Stop after giving the steps, and continue when the user
says they're done (in Claude Code, after the restart).

## 4. Verify

Call `get_my_usage`, then `get_pool_pulse`. Tell the user, in two lines, what
is live, calling the plan by `plan_name` (never `plan`):

```
Connected to Wealthink on the Free plan: the last 3 days of stories, 100 story opens a day.
Today: 220 stories in the last 24 h. Financial Services had the most one-sided news (5 stories hurt it), mostly from RBI rate news.
```

Take the sector line from the pulse's `sector_view`; if it is empty, say how
many stories landed and skip the sector. Then offer the starting points:

- "What's moving the market today?": `market-pulse`
- "What's going on with <company / sector / driver>?" or "Does the news back
  my view on …?": `market-context`
- "Why did <headline> happen, and what came of it?": `trace-story`
- On Starter: "Run a thesis check on …": `thesis-check`

## Troubleshooting

- **401 / "not authenticated" / token expired**: re-run the client's
  authenticate or login step. In Claude Code, `/mcp` → `plugin:wealthink:mcp`
  → **Re-authenticate**.
- **The server isn't listed**: the config wasn't loaded. Restart the client,
  and check the config file and server name. In Claude Code, `claude plugin list`
  should show `wealthink@wealthink` as enabled.
- **Tools missing from the session**: the client may load tools on demand;
  look them up by name (e.g. `get_pool_story`).
- **402 `PLAN_REQUIRED`**: not a connection problem. The plan doesn't include
  that window or tool; the message names the plan that does. Relay it once.
- **429 `PLAN_LIMIT_REACHED`**: a daily or weekly limit is used up until
  `resets_at`. Don't retry before then.
- **403 `DESKTOP_APP_ONLY`**: that tool builds research modules in the
  Wealthink desktop app. Use the news tools instead.
- **Many module, template or report tools listed**: the account is on Pro or
  above, where the same server also serves the desktop app. Ignore those tools
  here; the desktop app is the better home for that plan.
