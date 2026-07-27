# Wealthink hooks — Code-enforced backstops

These hooks **enforce in Claude Code** the guardrails that the skills already
state in prose. They are a backstop, never the only line of defence: every rule
here also lives in a skill instruction so it holds in Cowork (where hooks may not
run). See `ARCHITECTURE.md` §3 and §8.

| Hook | Event | Matcher | Effect |
|------|-------|---------|--------|
| Connection reminder | `SessionStart` | `startup\|resume` | Injects a non-blocking reminder to authenticate Wealthink (OAuth) and never invent IDs. Cannot false-positive on already-connected sessions. Scoped to `startup\|resume` so it doesn't re-inject on every clear/compact. |
| Publish gate | `PreToolUse` | `mcp__plugin_wealthink_mcp__set_.*visibility` | Forces an explicit confirmation before making a report run **public**; allows **revoke** (back to private) through. |
| Removal gate | `PreToolUse` | `mcp__plugin_wealthink_mcp__(archive\|delete)_.*` | Forces an explicit confirmation before archiving (soft-delete) or deleting (hard, e.g. `delete_qual_data_source`) a resource. The prompt states which kind it is. |

### How the publish gate decides

It **allows only a positively identified revoke, and asks for everything else.**
It reads the visibility field out of `tool_input` (`visibility`, `is_public`,
`public`, `state`, `access` — first one present wins) and treats the call as a
revoke only when that field unambiguously means private. An unrecognised value,
a missing field, or an unfamiliar payload shape all produce `ask`.

That default matters: the earlier version substring-scanned the serialised
payload, so a genuine publish carrying any unrelated `false` — say
`{"is_public": true, "include_charts": false}` — read as a revoke and skipped the
confirmation entirely. `tests/test_gates.py` pins that case.

If the connector's visibility field is ever renamed, add it to `VISIBILITY_KEYS`
in `scripts/publish_gate.py`. Until then an unknown shape simply prompts, which
is the safe direction to fail.

## Scope discipline

Matchers are deliberately scoped to `mcp__plugin_wealthink_mcp__*` tool
names so the gates fire **only** on Wealthink calls — never on a CRM's "publish
campaign" or a mail connector's "delete". The prefix follows the plugin-bundled
MCP naming format `mcp__plugin_<plugin-name>_<server-name>__<tool>`, where this
plugin is named `wealthink` (`plugin.json`) and the server key is `mcp`
(`.mcp.json`). If either is renamed, update the matchers in `hooks.json` to
match — the skill instructions remain the guarantee in the meantime.

> **These matchers only fire for the bundled server.** A user who configures
> Wealthink by hand in another client gets tools named `mcp__<their key>__*`,
> which match nothing here — so no gate fires. That is why every rule below is
> also written into the skills, and why the durable cross-client fix is
> server-side, where tool annotations and per-tool approval metadata reach every
> client rather than just this one.

## Scripts

Dependency-free Python 3 (stdlib only). Each reads the hook event JSON on stdin
and prints a `hookSpecificOutput` decision:

- `scripts/publish_gate.py` — `ask` on publish, `allow` only on a recognised revoke.
- `scripts/archive_gate.py` — `ask` on any archive or delete.
- `scripts/session_start.py` — injects `additionalContext`.

If a script can't parse its input it exits quietly without blocking — the skill's
own confirmation step then stands. The same is true if `python3` isn't on PATH:
the gates stop gating silently, which is exactly why every rule they enforce is
also written into the skills.

## Tests

```bash
python3 hooks/tests/test_gates.py
```

Stdlib only, no framework. Covers publish, revoke, unknown payload shapes,
malformed input, and the masked-publish regression above.
