#!/usr/bin/env python3
"""Wealthink archive gate — PreToolUse backstop for `archive_*`.

Forces an explicit confirmation before soft-deleting a Wealthink module,
template, config, or event. Archiving is recoverable, but it removes the
resource from active lists, so it should never happen silently on the wrong ID.

This is a Code-only backstop that enforces what the build/manage skills already
require in prose. In Cowork (where this hook may not run) the skill instruction
is the guarantee.

Scoped to Wealthink's `mcp__plugin_wealthink_wealthink__archive_*` tools (see hooks.json matcher)
so it never fires on another connector's "delete"/"archive" action.
"""
import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool = data.get("tool_name", "a Wealthink archive tool")
    reason = (
        f"This will archive (soft-delete) a Wealthink resource via `{tool}`. It is "
        "recoverable but will disappear from active lists. Confirm the correct ID "
        "with the user before proceeding."
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
