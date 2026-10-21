# Building the Wealthink plugin for ChatGPT or Codex

For an agent asked to make a ChatGPT or Codex plugin from this repo (for
example ChatGPT's `@plugin create` with this repo's link). Everything you need
is listed here, so you don't have to browse GitHub's file pages.

## The package

The package is `wealthink-plugin.zip`, built from the files below and nothing
else. Normally the user attaches it: use it as it is. If they didn't and you
can reach GitHub, it's at
https://github.com/Wealthink/wealthink-plugin/releases/latest/download/wealthink-plugin.zip

The plugin root is `wealthink-plugin/`. Copy exactly these files, keeping
their paths relative to that root. If you were given a link to a branch or
tag (`.../tree/<ref>`), put that ref in place of `main` in every URL below.

<!-- plugin-files:start -->
| Path in the plugin | Raw URL |
|---|---|
| `plugin.json` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/plugin.json |
| `mcp.json` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/mcp.json |
| `assets/logo.svg` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/assets/logo.svg |
| `skills/coherence-engine/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/coherence-engine/SKILL.md |
| `skills/coherence-engine/references/data-model.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/coherence-engine/references/data-model.md |
| `skills/connect/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/connect/SKILL.md |
| `skills/market-context/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/market-context/SKILL.md |
| `skills/market-pulse/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/market-pulse/SKILL.md |
| `skills/thesis-check/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/thesis-check/SKILL.md |
| `skills/trace-story/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/trace-story/SKILL.md |
<!-- plugin-files:end -->

Copy the files byte for byte. Don't rewrite, summarise or merge the skills:
each `SKILL.md` is loaded by its frontmatter `name` and `description`. `assets/logo.svg` is the Wealthink logo, which `interface.logo` and
`interface.composerIcon` in `plugin.json` both point at.

## The connection

Wealthink is a remote MCP server: `https://api.thewealthink.com/mcp`,
streamable HTTP, OAuth 2.0 in the browser with dynamic client registration.
There is no API key. Never ask the user for an email, password or token.

The package uses OpenAI's portable Agent Plugins format: `plugin.json` at the
root (presentation under `extensions.com.openai.interface`) and `mcp.json` for
the server. There is no `.codex-plugin/plugin.json`.

- **The user already has a Wealthink app or connector in ChatGPT:** keep it.
  If the plugin being updated has an `.app.json`, keep that file unchanged
  and set `extensions.com.openai.apps` to `"./.app.json"` in `plugin.json`.
  Replacing it breaks the user's sign-in. The app already is the connection,
  so leave `mcp.json` out rather than add a second server alongside it.
- **They don't:** use `mcp.json` as shipped. The server supports OAuth
  discovery and dynamic client registration, so the user signs in in the
  browser when the plugin is installed or first used.

## Leave out

These are for Claude Code only and don't work in ChatGPT or Codex:

- `.claude-plugin/`
- `.mcp.json` (Claude's copy of the server config; `mcp.json` is the portable one)
- `hooks/`
- `commands/`
- `agent-instructions.md` (a system prompt for agents without skills; a
  plugin has the skills)

## Check it worked

Once installed and signed in, call `get_my_usage`, then `get_pool_pulse`, and
tell the user in two lines what their plan includes and what's moving Indian
markets today.

## Updating

To update an installed plugin, fetch the latest release zip and update the
existing plugin in place rather than creating a second one, keeping its
`.app.json`. The version is `version` in `plugin.json`.

## Changing this repo

Maintainers and coding agents: read [RELEASING.md](./RELEASING.md) before
changing or releasing the plugin.
