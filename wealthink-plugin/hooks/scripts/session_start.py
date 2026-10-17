#!/usr/bin/env python3
"""Wealthink session reminder — SessionStart backstop.

Injects a short, non-blocking reminder at session start: how to sign in, which
connector tools this plugin uses (the same server also serves the desktop app's
module/report tools, which should be ignored here), and the two quota rules.
It only injects context — it never blocks a tool call.
"""
import json


def main() -> None:
    context = (
        "Wealthink reminder: the Wealthink connector (plugin:wealthink:mcp) needs "
        'OAuth. If a Wealthink tool reports "not connected" / 401, use the connect '
        "skill (/mcp → plugin:wealthink:mcp → Authenticate); never ask for an email "
        "or password. Wealthink is a coherence engine for Indian markets: for any "
        "market question, use the market-context skill (coherence-engine has the "
        "data model and tool reference). If the connector also lists module / "
        "template / report / data-source tools (Pro and above), ignore them. "
        "Opening a story (get_pool_story) can use one of the user's daily story "
        "opens, so list first and open sparingly. run_pool_thesis_check is on "
        "Starter and above and can use one of the user's weekly checks: confirm "
        "before running it."
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
