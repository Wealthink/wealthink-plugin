#!/usr/bin/env python3
"""Wealthink publish gate — PreToolUse backstop for `set_*_visibility`.

Forces an explicit confirmation before a Wealthink report run is published to a
public, login-free link (an outward, hard-to-take-back action). Revoking access
(going back to private) only *removes* a link, so it is allowed through without
an extra prompt.

This is a Code-only backstop that enforces what the `share-report` skill already
requires in prose. In Cowork (where this hook may not run) the skill instruction
is the guarantee — never let a public link depend on this hook alone.

Scoped deliberately to Wealthink's `mcp__plugin_wealthink_mcp__set_*visibility` tools (see
hooks.json matcher) so it never fires on another connector's "publish" action.
"""
import json
import sys


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        # Can't parse the event — do not block the user; the skill's own
        # confirmation step remains the guarantee.
        return

    tool_input = data.get("tool_input", {}) or {}
    blob = json.dumps(tool_input).lower()

    # Treat it as a *revoke* only when the payload clearly sets private / false
    # and does not contain the string value "public".
    going_private = '"public"' not in blob and (
        "private" in blob or "false" in blob or "revoke" in blob
    )

    if going_private:
        decision = "allow"
        reason = "Revoking public access to a Wealthink report run — safe to proceed."
    else:
        decision = "ask"
        reason = (
            "This publishes a Wealthink report run to a public, login-free link that "
            "anyone with the URL can view. Confirm the run_id is the run you intend to "
            "share and that it has completed before proceeding."
        )

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )


if __name__ == "__main__":
    main()
