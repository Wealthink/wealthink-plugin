# Connect Wealthink to your agent

The Wealthink platform is exposed as a remote **MCP server**. Any MCP-capable
agent can connect to it. This page is the canonical set of connection facts plus
a config snippet per client.

## The connection

| | |
|---|---|
| **Endpoint** | `https://api.thewealthink.com/mcp` |
| **Transport** | `http` (streamable HTTP) |
| **Auth** | OAuth 2.0 — browser consent, no API key, no password |
| **Scope** | Your own workspace only |

There is **nothing to paste**. Every client below opens a browser for Wealthink
sign-in and consent on first use, then caches and refreshes the token itself.
Wealthink never authenticates through the chat: if an agent asks you to type an
email or password, something is wrong.

---

## Claude Code — install the plugin (recommended)

This is the only path that ships the skills, agents and safety hooks, not just the
tools.

```bash
/plugin marketplace add Wealthink/wealthink-plugin
/plugin install wealthink@wealthink
```

Installing registers the MCP server automatically. Authorise it:

```
/mcp  →  plugin:wealthink:mcp  →  Authenticate
```

or from a shell, `claude mcp login plugin:wealthink:mcp`.

> The server is listed as **`plugin:wealthink:mcp`**, not `wealthink` — plugin
> servers are namespaced by their plugin. Its tools are named
> `mcp__plugin_wealthink_mcp__<tool>`.

## Cowork / claude.ai / Claude Desktop — install the plugin

Left sidebar → **Customize** → **Plugins** → add the `Wealthink/wealthink-plugin`
marketplace → install **Wealthink for agents**. The connector and the skills arrive
together; authorise the connector when prompted.

If you only want the connector, add **Wealthink** under **Settings → Connectors**
instead.

---

## Other MCP clients

These get the ~50 Wealthink tools. They do **not** get this repo's skills, agents
or hooks — read [What you give up](#what-you-give-up) before relying on them for
publishing or archiving.

Use `wealthink` as the server key everywhere, so tool names are consistent
(`mcp__wealthink__run_module`) and anything you write against them is portable.

**Cursor** — `.cursor/mcp.json` (or Settings → MCP):

```json
{
  "mcpServers": {
    "wealthink": { "type": "http", "url": "https://api.thewealthink.com/mcp" }
  }
}
```

**Claude Desktop** — `claude_desktop_config.json`, same shape:

```json
{
  "mcpServers": {
    "wealthink": { "type": "http", "url": "https://api.thewealthink.com/mcp" }
  }
}
```

**VS Code** — `.vscode/mcp.json`:

```json
{
  "servers": {
    "wealthink": { "type": "http", "url": "https://api.thewealthink.com/mcp" }
  }
}
```

**Codex / OpenCode and other config-file clients** — add an HTTP MCP server named
`wealthink` pointing at `https://api.thewealthink.com/mcp`. Consult your client's
MCP docs for the exact file; the endpoint and transport above are all it needs.

**ChatGPT** — add Wealthink as a custom connector with the same URL, and complete
the OAuth consent in the browser.

**Claude Code without the plugin** — if you want the tools but not the plugin:

```bash
claude mcp add --transport http wealthink https://api.thewealthink.com/mcp
```

---

## What you give up

Outside the bundled-plugin path, three things do not come with you:

1. **The skills.** They are the judgement layer — which tool to call for a real
   research task, in what order, and how to present the result. Without them the
   agent free-selects among ~50 tools.
2. **The hooks.** The publish gate and archive gate match the bundled tool prefix
   `mcp__plugin_wealthink_mcp__*`. A hand-configured server produces
   `mcp__wealthink__*`, which matches nothing — **so no confirmation fires before
   a report is made public or a module is archived.** Confirm those yourself.
3. **The `allowed-tools` pre-approvals** in each skill, for the same reason. Every
   call falls back to your client's normal permission behaviour.

The durable fix for (2) is server-side, so it protects every client rather than
only Claude Code. Until it lands, confirm publishes and deletions yourself.

## Tool names by path

| How you connected | Tool name |
|---|---|
| Plugin (Claude Code / Cowork) | `mcp__plugin_wealthink_mcp__run_module` |
| Manual config, key `wealthink` | `mcp__wealthink__run_module` |
| Manual config, key `<other>` | `mcp__<other>__run_module` |

This matters whenever you write a permission rule, a hook matcher, or a skill's
`allowed-tools`: they must name the form your setup actually produces.

## Troubleshooting

- **No Wealthink server in the list.** The connector isn't registered. On Claude
  Code, check `/plugin` shows **wealthink** installed and enabled, then retry
  `/mcp`. Don't diagnose from the label — the bundled server is called
  `plugin:wealthink:mcp`.
- **401 / "not authenticated".** Re-run the authorise step for your client. Claude
  Code flags the server in `/mcp`; its menu offers **Re-authenticate**.
- **`plan_required` / 402.** Not an error in the connector — your workspace's plan
  doesn't include that action. Contact your Wealthink account manager.
- **Responses too large to render.** Use an agentic harness that can isolate big
  payloads in a subagent. This is why plain chat is out of scope; see the plugin's
  `ARCHITECTURE.md` §2.
