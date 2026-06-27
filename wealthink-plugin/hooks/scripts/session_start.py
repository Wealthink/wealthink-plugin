#!/usr/bin/env python3
"""Wealthink sign-in reminder — SessionStart backstop.

Injects a short, non-blocking reminder at session start so the agent checks for
a signed-in Wealthink session before making Wealthink calls, and never invents
resource IDs. This is the safe form of the "sign-in check" guardrail: it cannot
false-positive against hosted connectors (which may authenticate at connect
time), because it only injects context — it never blocks a tool call.

The hard guarantee lives in the `getting-started` skill; this hook just keeps it
top-of-mind in Claude Code.
"""
import json


def main() -> None:
    context = (
        "Wealthink reminder: Wealthink MCP tools require an authenticated (OAuth) "
        'connection. If any Wealthink tool reports "not connected" / "not '
        'authenticated" / 401, use the getting-started skill: run /mcp and '
        "Authenticate the wealthink server (browser consent) before retrying — "
        "never ask the user for an email or password. Never invent module / "
        "template / tag / config IDs — resolve them with the `list_*` discovery "
        "tools first. Publishing a report (making a run public) and archiving a "
        "resource are confirm-before-acting actions."
    )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
