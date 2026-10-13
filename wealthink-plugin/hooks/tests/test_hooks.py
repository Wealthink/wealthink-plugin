#!/usr/bin/env python3
"""Tests for the Wealthink plugin hooks.

Run:  python3 hooks/tests/test_hooks.py

Stdlib only, no test framework — these run anywhere python3 does, including the
CI job in .github/workflows/validate.yml.

The thesis gate must `ask` for every readable call — a thesis check can spend a
weekly check, so no input shape may slip through as an allow — and stay silent
(never block) on input it cannot parse.
"""
import json
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
TOOL = "mcp__plugin_wealthink_mcp__run_pool_thesis_check"


def run(script: str, event) -> dict:
    """Feed an event to a hook and return its hookSpecificOutput ({} if silent)."""
    payload = event if isinstance(event, str) else json.dumps(event)
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"{script} exited {result.returncode}: {result.stderr}")
    if not result.stdout.strip():
        return {}
    return json.loads(result.stdout)["hookSpecificOutput"]


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn

    return register


@case("thesis_asks_and_shows_statement")
def _():
    out = run("thesis_gate.py", {
        "tool_name": TOOL,
        "tool_input": {"statement": "Cement demand improves on infra spending"},
    })
    assert out["permissionDecision"] == "ask", out
    assert "Cement demand improves" in out["permissionDecisionReason"], out
    assert "weekly" in out["permissionDecisionReason"], out


@case("thesis_with_isin_still_asks")
def _():
    out = run("thesis_gate.py", {
        "tool_name": TOOL,
        "tool_input": {"statement": "Margins recover", "company_isin": "INE002A01018"},
    })
    assert out["permissionDecision"] == "ask", out


@case("thesis_long_statement_is_truncated")
def _():
    out = run("thesis_gate.py", {"tool_name": TOOL, "tool_input": {"statement": "x" * 500}})
    assert out["permissionDecision"] == "ask", out
    assert "x" * 201 not in out["permissionDecisionReason"], out
    assert "…" in out["permissionDecisionReason"], out


@case("thesis_missing_statement_asks")
def _():
    out = run("thesis_gate.py", {"tool_name": TOOL, "tool_input": {}})
    assert out["permissionDecision"] == "ask", out
    assert "could not read" in out["permissionDecisionReason"], out


@case("thesis_non_dict_input_asks")
def _():
    out = run("thesis_gate.py", {"tool_name": TOOL, "tool_input": ["not", "a", "dict"]})
    assert out["permissionDecision"] == "ask", out


@case("thesis_malformed_event_is_silent")
def _():
    assert run("thesis_gate.py", "{not json") == {}


@case("session_start_injects_context")
def _():
    out = run("session_start.py", {})
    assert out["hookEventName"] == "SessionStart", out
    ctx = out["additionalContext"]
    for needle in ("plugin:wealthink:mcp", "market-context", "story opens", "run_pool_thesis_check"):
        assert needle in ctx, (needle, ctx)


def main() -> int:
    failed = 0
    for name, fn in CASES:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL  {name}: {exc}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
