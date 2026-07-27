#!/usr/bin/env python3
"""Wealthink removal gate — PreToolUse backstop for `archive_*` and `delete_*`.

Forces an explicit confirmation before removing a Wealthink module, template,
config, event, or data source.

Two different removals reach this gate, and the prompt says which one it is:

- `archive_*` is a **soft delete** — recoverable, but the resource disappears
  from active lists, so it should never happen silently on the wrong ID.
- `delete_*` (currently `delete_qual_data_source`) is a **hard delete**. Modules
  that read from that source lose it.

This is a Code-only backstop that enforces what the build/manage skills already
require in prose. In Cowork, and in any client where Wealthink was configured by
hand rather than installed as a plugin, this hook does not run — the skill
instruction is the guarantee there.

Scoped to Wealthink's own tools (see the hooks.json matchers) so it never fires
on another connector's "delete"/"archive" action.
"""
import json
import sys

FALLBACK = "a Wealthink removal tool"


def describe(tool: str) -> str:
    """Word the prompt for the kind of removal actually being attempted."""
    if "__delete_" in tool or tool.startswith("delete_"):
        return (
            f"This will permanently delete a Wealthink resource via `{tool}`. This "
            "is a hard delete — it is not recoverable, and anything referencing the "
            "resource will lose it. Confirm the correct ID with the user before "
            "proceeding."
        )
    return (
        f"This will archive (soft-delete) a Wealthink resource via `{tool}`. It is "
        "recoverable but will disappear from active lists. Confirm the correct ID "
        "with the user before proceeding."
    )


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool = data.get("tool_name") or FALLBACK

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": describe(tool),
                }
            }
        )
    )


if __name__ == "__main__":
    main()
