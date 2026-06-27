# Wealthink hooks — Code-enforced backstops

These hooks **enforce in Claude Code** the guardrails that the skills already
state in prose. They are a backstop, never the only line of defence: every rule
here also lives in a skill instruction so it holds in Cowork (where hooks may not
run). See `ARCHITECTURE.md` §3 and §8.

| Hook | Event | Matcher | Effect |
|------|-------|---------|--------|
| Connection reminder | `SessionStart` | — | Injects a non-blocking reminder to authenticate Wealthink (OAuth) and never invent IDs. Cannot false-positive on already-connected sessions. |
| Publish gate | `PreToolUse` | `mcp__plugin_wealthink_mcp__set_.*visibility` | Forces an explicit confirmation before making a report run **public**; allows **revoke** (back to private) through. |
| Archive gate | `PreToolUse` | `mcp__plugin_wealthink_mcp__archive_.*` | Forces an explicit confirmation before soft-deleting a module / template / config / event. |

## Scope discipline

Matchers are deliberately scoped to `mcp__plugin_wealthink_mcp__*` tool
names so the gates fire **only** on Wealthink calls — never on a CRM's "publish
campaign" or a mail connector's "delete". The prefix follows the plugin-bundled
MCP naming format `mcp__plugin_<plugin-name>_<server-name>__<tool>`, where this
plugin is named `wealthink` and the server key in `.mcp.json` is also
`wealthink`. If either is renamed, update the matchers in `hooks.json` to match —
the skill instructions remain the guarantee in the meantime.

## Scripts

Dependency-free Python 3 (stdlib only). Each reads the hook event JSON on stdin
and prints a `hookSpecificOutput` decision:

- `scripts/publish_gate.py` — `ask` on publish, `allow` on revoke.
- `scripts/archive_gate.py` — `ask` on any archive.
- `scripts/session_start.py` — injects `additionalContext`.

If a script can't parse its input it exits quietly without blocking — the skill's
own confirmation step then stands.
