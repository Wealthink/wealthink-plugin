# Building the Wealthink plugin for ChatGPT or Codex

For an agent asked to make a ChatGPT or Codex plugin from this repo (for
example ChatGPT's `@plugin create` with this repo's link). Everything you need
is listed here, so you don't have to browse GitHub's file pages.

## The package

The plugin root is `wealthink-plugin/`. Copy exactly these files, keeping
their paths relative to that root. If you were given a link to a branch or
tag (`.../tree/<ref>`), put that ref in place of `main` in every URL below.

<!-- plugin-files:start -->
| Path in the plugin | Raw URL |
|---|---|
| `.codex-plugin/plugin.json` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/.codex-plugin/plugin.json |
| `.mcp.json` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/.mcp.json |
| `skills/coherence-engine/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/coherence-engine/SKILL.md |
| `skills/coherence-engine/references/data-model.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/coherence-engine/references/data-model.md |
| `skills/connect/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/connect/SKILL.md |
| `skills/market-context/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/market-context/SKILL.md |
| `skills/market-pulse/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/market-pulse/SKILL.md |
| `skills/thesis-check/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/thesis-check/SKILL.md |
| `skills/trace-story/SKILL.md` | https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/trace-story/SKILL.md |
<!-- plugin-files:end -->

If you can download an archive instead, the whole repo is at
https://github.com/Wealthink/wealthink-plugin/archive/refs/heads/main.zip;
take the `wealthink-plugin/` folder from it and drop the files listed under
"Leave out".

Copy the files byte for byte. Don't rewrite, summarise or merge the skills:
each `SKILL.md` is loaded by its frontmatter `name` and `description`.

## The connection

Wealthink is a remote MCP server: `https://api.thewealthink.com/mcp`,
streamable HTTP, OAuth 2.0 in the browser with dynamic client registration.
There is no API key. Never ask the user for an email, password or token.

- **The user already has a Wealthink app or connector in ChatGPT:** keep it.
  If the plugin being updated has an `.app.json`, keep that file unchanged
  and keep `"apps": "./.app.json"` in `.codex-plugin/plugin.json`. Replacing
  it breaks the user's sign-in.
- **They don't:** use `.mcp.json` as shipped. The user signs in in the browser
  when the plugin is installed or first used.

## Leave out

These are for Claude Code only and don't work in ChatGPT or Codex:

- `.claude-plugin/`
- `hooks/`
- `commands/`
- `agent-instructions.md` (a system prompt for agents without skills; a
  plugin has the skills)

## Check it worked

Once installed and signed in, call `get_my_usage`, then `get_pool_pulse`, and
tell the user in two lines what their plan includes and what's moving Indian
markets today.

## Updating

To update an installed plugin, fetch the files again and replace them. The
version is `version` in `.codex-plugin/plugin.json`.
