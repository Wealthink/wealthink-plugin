# FE handoff: the "connect your AI agent" prompt

**From:** plugin team · **To:** web app (FE) · **Date:** 2026-10-17
**Status:** draft. Build it now; don't switch it on in prod until the
blockers below are cleared.

## What we're building

After sign-up (and on a "Use Wealthink in your AI agent" page), the user sees
one prompt with a **Copy** button. They paste it into their AI agent. The agent
connects the Wealthink MCP server, installs the Wealthink skills where it can,
has the user sign in once in the browser, and answers a first question.

Who sees it:

| Plan | Show |
|---|---|
| Free, Starter | This prompt (the public plugin is built for these plans) |
| Pro and above | The desktop app download instead. Pro uses the desktop app's own plugin |

## Blockers before going live

1. **Server release (Monday).** The MCP fixes and new tools are on
   `wealthink-server` branch `fix/mcp-plugin-bug-list` (commits `1381d0d5`,
   `c0ec980c`). Prod `wealthink-mcp` still runs the old build. The skills call
   tools that prod doesn't have yet (`list_pool_knockons`,
   `list_pool_driver_moves`, `get_pool_story_timeline`, `get_my_referral`).
2. **Plugin release (0.4.0).** Built on branch `feat/new-engine`, including
   the setup guide this prompt reads (`wealthink-plugin/skills/connect/SKILL.md`)
   and `docs/connect.md`. It goes live when merged to `main` of
   `github.com/Wealthink/wealthink-plugin`; until then every install gets the
   old plugin. Merge after the server release, not before.

The prompt below fetches the setup steps from `main`, so the page can ship as
soon as both are out, with no FE change.

## The prompt (the Copy button copies exactly this)

```text
Set up Wealthink for me. Wealthink links Indian market news into connected stories and is used through MCP.

1. Read the setup guide and follow the steps for the agent you are:
   https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/skills/connect/SKILL.md
2. Add the Wealthink MCP server (https://api.thewealthink.com/mcp, OAuth) and install the Wealthink skills if you support skills.
3. I sign in to Wealthink in my browser. Never ask me for an email, password or token.
4. When it's connected, call get_my_usage and get_pool_pulse and tell me in two lines what my plan includes and what's moving Indian markets today.

If you can't install things yourself (for example in a chat app), tell me exactly what to click instead.
```

Why one prompt for every agent: the steps per agent live in the repo, so we
can fix them without a web release. Coding agents (Claude Code, Codex, Cursor,
Gemini CLI) can fetch the page and run the install commands. Chat apps
(Claude.ai, ChatGPT) can't install anything, so they read the guide and tell
the user what to click.

## Per-agent tabs (under the prompt)

Show these as tabs, with the prompt above them. The user may skip the prompt
and follow a tab directly.

**Claude Code** (the agent can run these itself)

```bash
claude plugin marketplace add Wealthink/wealthink-plugin
claude plugin install wealthink@wealthink
```

Then restart Claude Code, run `/mcp`, choose `plugin:wealthink:mcp` and
**Authenticate**. Note that the server is listed as `plugin:wealthink:mcp`,
not `wealthink`.

**Claude.ai / Claude Desktop** (no prompt; click steps)

Customize → Plugins → add marketplace `Wealthink/wealthink-plugin` →
install **Wealthink for agents** → authorise the connector when asked.

**ChatGPT** (paid plans)

Settings → Apps & Connectors → Advanced → turn on Developer mode → add a
connector: URL `https://api.thewealthink.com/mcp`, auth OAuth. Then paste the
text of `docs/agent-instructions.md` into custom instructions or a project
(offer it behind a second Copy button). ChatGPT can't load skills.

**Codex, Cursor, Gemini CLI, VS Code, others**

```bash
npx skills add Wealthink/wealthink-plugin
```

Plus the MCP config per client from `docs/connect.md` (Codex:
`codex mcp add wealthink --url https://api.thewealthink.com/mcp` then
`codex mcp login wealthink`).

## Details for the page

- **Copy exactly.** Plain text, no smart quotes, keep the line breaks.
- **No personal data in the prompt.** No email, user id, token or referral
  code. The user signs in through OAuth; the agent never needs them.
- **Sign-in page.** The agent opens `/api/v1/oauth/authorize`, which sends the
  user to the web app's OAuth login (`WEB_OAUTH_LOGIN_PATH`, default
  `/login?oauth_state=…`). That page must work for a user who is already signed
  in (one click to approve) and for a new user (Google SSO or email, then
  back to approval).
- **After they paste.** Show a "Waiting for your agent to connect" state if you
  can detect the first MCP call for the user; otherwise a static "Done? Ask
  your agent: what's moving Indian markets today?"
- **Analytics.** Track `onboarding_prompt_copied` (with the selected tab) and
  the first MCP call per user, so we can measure copy → connected.

## Acceptance checks

1. A new Free user copies the prompt into Claude Code. The agent installs the
   plugin, the user signs in in the browser, and the agent reports the plan as
   "Free" and today's moves. No step asks for a password.
2. The same works in Codex or Cursor via `npx skills add` plus the MCP config.
3. In Claude.ai and ChatGPT the agent replies with the click steps, and they
   work.
4. A Starter user sees Thesis Check offered; a Free user doesn't.
5. A Pro user sees the desktop app download, not this prompt.
