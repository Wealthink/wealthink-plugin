# Wealthink hooks

These hooks enforce in Claude Code what the skills already say in prose. They
are a backstop: every rule here is also in a skill, so it still holds where
hooks don't run (Cowork, or a hand-configured server).

| Hook | Event | Matcher | Effect |
|------|-------|---------|--------|
| Session reminder | `SessionStart` | `startup\|resume` | Injects a non-blocking reminder: sign in via `/mcp` (never by password), use `market-context` for market questions and ignore any module/report tools (listed only on Pro and above), story opens are metered, and thesis checks need confirmation. |
| Thesis-check gate | `PreToolUse` | `mcp__plugin_wealthink_mcp__run_pool_thesis_check` | Always asks before running a Thesis Check, quoting the statement (truncated at 200 characters), because a check can use one of the user's weekly checks. Unparseable input stays silent rather than blocking; the client's own permission prompt still applies, because no skill pre-approves this tool. |

The matcher uses the bundled connector's prefix, `mcp__plugin_wealthink_mcp__`.
A hand-configured server (`mcp__wealthink__…`) doesn't match it, so the gate
doesn't fire there. `.github/scripts/check_manifests.py` fails CI if the prefix
drifts from the plugin name and server key.

Tests: `python3 hooks/tests/test_hooks.py` (stdlib only; also run in CI).
