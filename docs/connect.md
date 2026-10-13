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

This is the only path that ships the skills and the thesis-check hook, not just
the tools.

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

These get every Wealthink tool, including the desktop app's module and report
tools. Add the skills with [Skills for any agent](#skills-for-any-agent). The
Claude Code hook doesn't come with them; see [What you give up](#what-you-give-up).

Use `wealthink` as the server key everywhere, so tool names are consistent
(`mcp__wealthink__get_pool_story`) and anything you write against them is portable.

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

**Codex CLI**:

```bash
codex mcp add wealthink --url https://api.thewealthink.com/mcp
codex mcp login wealthink
```

**Gemini CLI**: `~/.gemini/settings.json`, then run `/mcp auth wealthink`:

```json
{
  "mcpServers": {
    "wealthink": { "httpUrl": "https://api.thewealthink.com/mcp", "oauth": { "enabled": true } }
  }
}
```

**OpenCode and other config-file clients**: add a remote HTTP MCP server named
`wealthink` that points at `https://api.thewealthink.com/mcp`. Check your
client's MCP docs for the exact file.

**ChatGPT**: go to Settings → Apps & Connectors → Advanced and turn on **Developer
mode** (paid ChatGPT plans). Then add a connector with the endpoint URL and OAuth
authentication. ChatGPT can't load skills, so paste
[`agent-instructions.md`](./agent-instructions.md) into your custom
instructions or project.

**Claude Code without the plugin** — if you want the tools but not the plugin:

```bash
claude mcp add --transport http wealthink https://api.thewealthink.com/mcp
```

## Skills for any agent

The skills in `wealthink-plugin/skills/` follow the open
[Agent Skills](https://agentskills.io) standard (`SKILL.md` folders). Codex,
Cursor, Gemini CLI, OpenCode, GitHub Copilot / VS Code, Goose, Amp, Roo Code
and other skills-compatible agents can load them:

```bash
npx skills add Wealthink/wealthink-plugin                 # choose agents interactively
npx skills add Wealthink/wealthink-plugin -a codex -g     # one agent, user-wide
```

You can also copy the skill folders into your agent's skills directory. The
skills use bare tool names (`get_pool_story`), so they work whatever prefix your
client adds. Agents without skills support can use
[`agent-instructions.md`](./agent-instructions.md) as a system prompt.

---

## What you give up

Outside the bundled-plugin path, three things don't come with you:

1. **The skills**, unless you install them as above. They teach the agent how to read the news engine: list
   before opening (story opens are metered), follow `follows` / `followed_by`
   links, separate knock-ons (Wealthink's reasoning) from article claims, and
   cite every source. Without them the agent picks freely among every tool on
   the server, including the desktop app's module and report tools.
2. **The thesis-check hook.** It matches the bundled prefix
   `mcp__plugin_wealthink_mcp__run_pool_thesis_check`. A hand-configured server
   produces `mcp__wealthink__…`, which matches nothing, so **nothing asks
   before a Thesis Check uses one of your weekly checks.** Confirm it yourself.
3. **The `allowed-tools` pre-approvals** in each skill, for the same reason.
   Every call falls back to your client's normal permission behaviour.

## Optional: hide the tools this plugin doesn't use (Claude Code)

The Wealthink server also serves the desktop app, so it lists about 88 tools; the
plugin uses 19. A plugin can't ship permission rules, but you can hide the rest
yourself. In Claude Code, a bare-name **deny** rule removes a tool from the
model's context and from tool search entirely. Add this to
`~/.claude/settings.json` (all projects) or `.claude/settings.json` (one project):

```json
{
  "permissions": {
    "deny": [
      "mcp__plugin_wealthink_mcp__archive_event",
      "mcp__plugin_wealthink_mcp__archive_qual_module",
      "mcp__plugin_wealthink_mcp__archive_quant_config",
      "mcp__plugin_wealthink_mcp__archive_template",
      "mcp__plugin_wealthink_mcp__cancel_qual_run",
      "mcp__plugin_wealthink_mcp__create_qual_data_source",
      "mcp__plugin_wealthink_mcp__create_qual_module",
      "mcp__plugin_wealthink_mcp__create_quant_config",
      "mcp__plugin_wealthink_mcp__create_tag",
      "mcp__plugin_wealthink_mcp__create_template",
      "mcp__plugin_wealthink_mcp__create_user_module",
      "mcp__plugin_wealthink_mcp__delete_qual_data_source",
      "mcp__plugin_wealthink_mcp__fetch_raw_datasource_payload",
      "mcp__plugin_wealthink_mcp__get_billing_summary",
      "mcp__plugin_wealthink_mcp__get_connector",
      "mcp__plugin_wealthink_mcp__get_data_source_endpoints",
      "mcp__plugin_wealthink_mcp__get_event",
      "mcp__plugin_wealthink_mcp__get_expiry_dates",
      "mcp__plugin_wealthink_mcp__get_health",
      "mcp__plugin_wealthink_mcp__get_org_usage",
      "mcp__plugin_wealthink_mcp__get_pool_article_trace",
      "mcp__plugin_wealthink_mcp__get_pool_feed",
      "mcp__plugin_wealthink_mcp__get_pool_thesis_check_trace",
      "mcp__plugin_wealthink_mcp__get_public_template_run",
      "mcp__plugin_wealthink_mcp__get_qual_run_status",
      "mcp__plugin_wealthink_mcp__get_quant_config",
      "mcp__plugin_wealthink_mcp__get_quant_result",
      "mcp__plugin_wealthink_mcp__get_tag",
      "mcp__plugin_wealthink_mcp__get_template_by_id",
      "mcp__plugin_wealthink_mcp__get_template_report_by_run_id",
      "mcp__plugin_wealthink_mcp__get_template_run_status",
      "mcp__plugin_wealthink_mcp__get_user_module",
      "mcp__plugin_wealthink_mcp__list_all_modules",
      "mcp__plugin_wealthink_mcp__list_connectors",
      "mcp__plugin_wealthink_mcp__list_data_sources",
      "mcp__plugin_wealthink_mcp__list_events",
      "mcp__plugin_wealthink_mcp__list_module_options",
      "mcp__plugin_wealthink_mcp__list_pool_dropped_headlines",
      "mcp__plugin_wealthink_mcp__list_qual_data_sources",
      "mcp__plugin_wealthink_mcp__list_qual_modules",
      "mcp__plugin_wealthink_mcp__list_qual_results",
      "mcp__plugin_wealthink_mcp__list_quant_chart_types",
      "mcp__plugin_wealthink_mcp__list_quant_configs",
      "mcp__plugin_wealthink_mcp__list_tags",
      "mcp__plugin_wealthink_mcp__list_template_reports",
      "mcp__plugin_wealthink_mcp__list_templates",
      "mcp__plugin_wealthink_mcp__list_user_modules",
      "mcp__plugin_wealthink_mcp__lookup_data_source_field",
      "mcp__plugin_wealthink_mcp__publish_qual_result",
      "mcp__plugin_wealthink_mcp__publish_user_module_result",
      "mcp__plugin_wealthink_mcp__push_user_module_result",
      "mcp__plugin_wealthink_mcp__run_module",
      "mcp__plugin_wealthink_mcp__run_qual_stream",
      "mcp__plugin_wealthink_mcp__run_quant_chart",
      "mcp__plugin_wealthink_mcp__run_quant_module",
      "mcp__plugin_wealthink_mcp__run_template",
      "mcp__plugin_wealthink_mcp__set_event_approval",
      "mcp__plugin_wealthink_mcp__set_template_run_visibility",
      "mcp__plugin_wealthink_mcp__test_run_qual",
      "mcp__plugin_wealthink_mcp__test_run_qual_stream",
      "mcp__plugin_wealthink_mcp__test_run_quant",
      "mcp__plugin_wealthink_mcp__test_run_quant_stream",
      "mcp__plugin_wealthink_mcp__update_event",
      "mcp__plugin_wealthink_mcp__update_qual_data_source",
      "mcp__plugin_wealthink_mcp__update_qual_module",
      "mcp__plugin_wealthink_mcp__update_qual_result",
      "mcp__plugin_wealthink_mcp__update_quant_config",
      "mcp__plugin_wealthink_mcp__update_tag",
      "mcp__plugin_wealthink_mcp__update_template"
    ]
  }
}
```

Skip this if you also use Wealthink modules, templates or reports from Claude
Code: it hides them too. The list matches the server as of 2026-10-07. A tool
added to the server later isn't hidden until you add it here.

## Tool names by path

| How you connected | Tool name |
|---|---|
| Plugin (Claude Code / Cowork) | `mcp__plugin_wealthink_mcp__get_pool_story` |
| Manual config, key `wealthink` | `mcp__wealthink__get_pool_story` |
| Manual config, key `<other>` | `mcp__<other>__get_pool_story` |

This matters whenever you write a permission rule, a hook matcher, or a skill's
`allowed-tools`: they must name the form your setup actually produces.

## Troubleshooting

- **No Wealthink server in the list.** The connector isn't registered. On Claude
  Code, check `/plugin` shows **wealthink** installed and enabled, then retry
  `/mcp`. Don't diagnose from the label — the bundled server is called
  `plugin:wealthink:mcp`.
- **401 / "not authenticated".** Re-run the authorise step for your client. Claude
  Code flags the server in `/mcp`; its menu offers **Re-authenticate**.
- **402.** Not a connector error: your plan doesn't cover that time window or
  feature. The error names the plan that does.
- **Many unrelated tools listed** (modules, templates, reports). The same server
  serves the Wealthink desktop app. Ignore them; the plugin's skills use only
  the news tools.
