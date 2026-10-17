# Connect Wealthink to your agent

Wealthink is a remote **MCP server**. Any MCP-capable agent can connect to it.
This page has the connection facts and the setup for each client. The
[`connect` skill](../wealthink-plugin/skills/connect/SKILL.md) has the same
steps written for an agent to follow.

## The fastest way: paste one prompt

Paste this into your agent (Claude Code, Codex, Cursor, Gemini CLI, Claude.ai,
ChatGPT…). It sets up what it can and tells you the rest:

```text
Set up Wealthink for me. Wealthink links Indian market news into connected stories and is used through MCP.

1. Read the setup guide and follow the steps for the agent you are:
   https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/connect/SKILL.md
2. Add the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth) and install the Wealthink skills if you support skills.
3. I sign in to Wealthink in my browser. Never ask me for an email, password or token.
4. When it's connected, call get_my_usage and get_pool_pulse and tell me in two lines what my plan includes and what's moving Indian markets today.

If you can't install things yourself (for example in a chat app), tell me exactly what to click instead.
```

## The connection

| | |
|---|---|
| **Endpoint** | `https://api.thewealthink.com/mcp` |
| **Transport** | `http` (streamable HTTP) |
| **Auth** | OAuth 2.0: browser sign-in and consent, no API key, no password |
| **Scope** | Your own account only |
| **Tools you see** | Your plan's: 10 on Free, 13 on Starter (adds Thesis Check). Pro and above see the desktop app's tools too |

There is **nothing to paste** for sign-in. Every client below opens a browser
for Wealthink sign-in on first use, then stores and refreshes the token itself.
If an agent asks you to type an email or password, something is wrong.

This plugin is for the **Free and Starter** plans. On Pro and above, use the
Wealthink desktop app, which ships its own plugin.

---

## Claude Code: install the plugin (recommended)

The only path that brings the skills, the `/wealthink` command and the
Thesis Check hook along with the tools.

```bash
claude plugin marketplace add Wealthink/wealthink-plugin
claude plugin install wealthink@wealthink
```

(or `/plugin marketplace add Wealthink/wealthink-plugin` and
`/plugin install wealthink@wealthink` inside Claude Code). Restart Claude Code
(`claude --continue` keeps your conversation), then:

```
/mcp  →  plugin:wealthink:mcp  →  Authenticate
```

> The server is listed as **`plugin:wealthink:mcp`**, not `wealthink`: plugin
> servers are named after their plugin. Its tools are
> `mcp__plugin_wealthink_mcp__<tool>`.

To update later: `claude plugin marketplace update wealthink`, then
`claude plugin update wealthink@wealthink`, then restart.

## Claude.ai / Claude Desktop / Cowork: install the plugin

**Customize** → **Plugins** → add the `Wealthink/wealthink-plugin` marketplace →
install **Wealthink for agents**. The connector and the skills arrive together;
authorise the connector when asked.

For the tools without the skills: **Settings → Connectors → Add custom
connector** with the endpoint.

---

## Other MCP clients

Use **`wealthink`** as the server name everywhere, so tool names are
predictable (`mcp__wealthink__get_pool_story`). Then add the skills with
[Skills for any agent](#skills-for-any-agent).

**Codex CLI**:

```bash
codex mcp add wealthink --url https://api.thewealthink.com/mcp
codex mcp login wealthink
```

**Cursor**: `~/.cursor/mcp.json` (or Settings → MCP), then **Connect**:

```json
{ "mcpServers": { "wealthink": { "url": "https://api.thewealthink.com/mcp" } } }
```

**Gemini CLI**: `~/.gemini/settings.json`, then `/mcp auth wealthink`:

```json
{ "mcpServers": { "wealthink": { "httpUrl": "https://api.thewealthink.com/mcp", "oauth": { "enabled": true } } } }
```

**VS Code (Copilot)**: `.vscode/mcp.json`:

```json
{ "servers": { "wealthink": { "type": "http", "url": "https://api.thewealthink.com/mcp" } } }
```

**OpenCode and other config-file clients**: add a remote HTTP MCP server
named `wealthink` at `https://api.thewealthink.com/mcp`. Your client's MCP docs
have the file.

**ChatGPT**: Settings → Apps & Connectors → Advanced → turn on **Developer
mode** (paid ChatGPT plans), then add a connector with the endpoint and OAuth.
ChatGPT can't load skills, so paste
[`agent-instructions.md`](./agent-instructions.md) into your project's
instructions or custom instructions.

**Claude Code without the plugin** (tools only):

```bash
claude mcp add --transport http wealthink https://api.thewealthink.com/mcp
```

## Skills for any agent

The skills in `wealthink-plugin/skills/` follow the open
[Agent Skills](https://agentskills.io) standard (`SKILL.md` folders), so Codex,
Cursor, Gemini CLI, OpenCode, GitHub Copilot, Goose, Amp and other
skills-compatible agents can load them:

```bash
npx skills add Wealthink/wealthink-plugin                       # choose agents interactively
npx skills add Wealthink/wealthink-plugin -a codex -g -y        # one agent, user-wide
```

Or copy the skill folders into your agent's skills directory. The skills use
bare tool names (`get_pool_story`), so they work with any prefix. Agents
without skills support can use [`agent-instructions.md`](./agent-instructions.md)
as a system prompt.

---

## What you give up outside the Claude Code plugin

1. **The skills**, unless you install them as above. They teach the agent to
   list before opening (story opens are metered on Free), follow story links,
   keep knock-ons (Wealthink's reasoning) apart from article claims, and cite
   every story. The server's own instructions cover the basics without them.
2. **The Thesis Check hook.** It matches the plugin's tool name,
   `mcp__plugin_wealthink_mcp__run_pool_thesis_check`. A hand-configured
   server produces `mcp__wealthink__…`, so nothing extra asks before a Thesis
   Check uses one of your weekly checks. The skill and the server instructions
   still tell the agent to confirm first.
3. **The skills' `allowed-tools` pre-approvals**, for the same reason. Calls
   fall back to your client's normal permission prompts.

## Tool names by path

| How you connected | Tool name |
|---|---|
| Plugin (Claude Code / Cowork) | `mcp__plugin_wealthink_mcp__get_pool_story` |
| Manual config, name `wealthink` | `mcp__wealthink__get_pool_story` |
| Manual config, name `<other>` | `mcp__<other>__get_pool_story` |

This matters whenever you write a permission rule, a hook matcher or a skill's
`allowed-tools`: name the form your setup produces.

## Troubleshooting

- **No Wealthink server listed.** The connector isn't registered. In Claude
  Code, check `claude plugin list` shows **wealthink@wealthink** enabled, restart,
  then retry `/mcp`. The plugin's server is called `plugin:wealthink:mcp`.
- **401 / "not authenticated".** Re-run your client's sign-in step. Claude
  Code flags the server in `/mcp`; its menu offers **Re-authenticate**.
- **402 `PLAN_REQUIRED`.** Not a connection error: your plan doesn't include
  that window or tool. The message names the plan that does.
- **429 `PLAN_LIMIT_REACHED`.** A daily or weekly limit is used up; it resets
  at `resets_at`.
- **403 `DESKTOP_APP_ONLY`.** That tool is for building research modules in the
  desktop app.
- **Module, template or report tools listed.** Your account is on Pro or
  above, where the server also serves the desktop app. Use the desktop app, or
  ignore them; the skills use only the news tools.
