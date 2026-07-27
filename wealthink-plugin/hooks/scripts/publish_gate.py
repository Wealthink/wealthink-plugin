#!/usr/bin/env python3
"""Wealthink publish gate — PreToolUse backstop for `set_*_visibility`.

Forces an explicit confirmation before a Wealthink report run is published to a
public, login-free link (an outward, hard-to-take-back action). Revoking access
(going back to private) only *removes* a link, so it is allowed through without
an extra prompt.

This is a Code-only backstop that enforces what the `share-report` skill already
requires in prose. In Cowork, and in any client where Wealthink was configured by
hand rather than installed as a plugin, this hook does not run at all — the skill
instruction is the guarantee there. Never let a public link depend on this hook
alone.

Scoped deliberately to Wealthink's `mcp__plugin_wealthink_mcp__set_*visibility`
tools (see hooks.json matcher) so it never fires on another connector's "publish".

Decision rule: **allow only a positively identified revoke; ask for everything
else.** An earlier version substring-scanned the serialised payload, so an
unrelated `false` anywhere in the input could mask a genuine publish. Anything
this script cannot read as an explicit "make it private" now prompts.
"""
import json
import sys

# Field names the connector might use to express visibility. Checked in order;
# the first one present decides. Keep in sync with the connector's schema.
VISIBILITY_KEYS = ("visibility", "is_public", "public", "state", "access")

PRIVATE_WORDS = {"private", "revoke", "revoked", "unlisted", "hidden", "none"}
PUBLIC_WORDS = {"public", "shared", "link", "publish", "published"}


def reads_as_private(value) -> bool:
    """True only when the value unambiguously means 'not public'."""
    if isinstance(value, bool):
        return value is False
    if isinstance(value, str):
        word = value.strip().lower()
        if word in PRIVATE_WORDS:
            return True
        # A recognised public word, or anything unfamiliar, is not a revoke we
        # can vouch for.
        return False
    return False


def is_revoke(tool_input: dict) -> bool:
    for key in VISIBILITY_KEYS:
        if key in tool_input:
            return reads_as_private(tool_input[key])
    # No recognisable visibility field at all — we cannot tell. Ask.
    return False


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        # Can't parse the event — do not block the user; the skill's own
        # confirmation step remains the guarantee.
        return

    tool_input = data.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        tool_input = {}

    if is_revoke(tool_input):
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
