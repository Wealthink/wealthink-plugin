#!/usr/bin/env python3
"""Wealthink thesis-check gate — PreToolUse backstop for `run_pool_thesis_check`.

A thesis check can spend one of the user's weekly checks, so it always asks
first, showing the statement that will be checked. This enforces what the
`thesis-check` skill already requires in prose; outside the plugin (Cursor, a
hand-configured server) this hook does not run and the skill is the guarantee.

Scoped by the hooks.json matcher to Wealthink's
`mcp__plugin_wealthink_mcp__run_pool_thesis_check` only.

Decision rule: always `ask`. An unreadable event stays silent rather than
blocking — the client's normal permission prompt still applies, because the
skill deliberately does not pre-approve this tool.
"""
import json
import sys

MAX_SHOWN = 200


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_input = data.get("tool_input") if isinstance(data, dict) else None
    if not isinstance(tool_input, dict):
        tool_input = {}

    statement = tool_input.get("statement")
    if isinstance(statement, str) and statement.strip():
        shown = statement.strip()
        if len(shown) > MAX_SHOWN:
            shown = shown[:MAX_SHOWN] + "…"
        subject = f'the statement "{shown}"'
    else:
        subject = "a statement this hook could not read"

    reason = (
        f"This runs a Wealthink Thesis Check on {subject}. It uses one of your "
        "weekly thesis checks if it finds evidence. Proceed?"
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
