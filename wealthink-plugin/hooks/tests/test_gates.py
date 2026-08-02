#!/usr/bin/env python3
"""Tests for the Wealthink PreToolUse gates.

Run:  python3 hooks/tests/test_gates.py

Stdlib only, no test framework — these run anywhere python3 does, including the
CI job in .github/workflows/validate.yml.

The case that matters most is `publish_masked_by_unrelated_false`: the original
gate substring-scanned the serialised payload, so an unrelated `false` anywhere
in the input made a genuine publish look like a revoke and skipped the
confirmation. That input must produce `ask`.
"""
import json
import pathlib
import subprocess
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def run(script: str, event) -> dict:
    """Feed an event to a gate and return its decision ({} if it stayed silent)."""
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


def decision(out: dict):
    return out.get("permissionDecision")


CASES = []


def case(name):
    def register(fn):
        CASES.append((name, fn))
        return fn

    return register


# --- publish gate --------------------------------------------------------


@case("publish_visibility_public")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "visibility": "public"},
    })
    assert decision(out) == "ask", out


@case("revoke_visibility_private")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "visibility": "private"},
    })
    assert decision(out) == "allow", out


@case("publish_is_public_true")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "is_public": True},
    })
    assert decision(out) == "ask", out


@case("revoke_is_public_false")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "is_public": False},
    })
    assert decision(out) == "allow", out


@case("publish_masked_by_unrelated_false")
def _():
    # The regression: a real publish carrying an unrelated false-valued flag.
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "is_public": True, "include_charts": False},
    })
    assert decision(out) == "ask", out


@case("publish_unknown_shape_asks")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1", "mode": "somethingNew"},
    })
    assert decision(out) == "ask", out


@case("publish_no_visibility_field_asks")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": {"run_id": "r_1"},
    })
    assert decision(out) == "ask", out


@case("publish_malformed_input_is_silent")
def _():
    # Fail open: unparseable event must not block the user. The skill's own
    # confirmation step stands.
    assert run("publish_gate.py", "not json at all") == {}


@case("publish_non_dict_tool_input_asks")
def _():
    out = run("publish_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__set_template_run_visibility",
        "tool_input": "public",
    })
    assert decision(out) == "ask", out


# --- archive / delete gate ----------------------------------------------


@case("archive_asks_and_says_recoverable")
def _():
    out = run("archive_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__archive_qual_module",
        "tool_input": {"module_id": "qm_1"},
    })
    assert decision(out) == "ask", out
    assert "recoverable" in out["permissionDecisionReason"], out


@case("delete_asks_and_says_not_recoverable")
def _():
    out = run("archive_gate.py", {
        "tool_name": "mcp__plugin_wealthink_mcp__delete_qual_data_source",
        "tool_input": {"data_source_id": "ds_1"},
    })
    assert decision(out) == "ask", out
    assert "not recoverable" in out["permissionDecisionReason"], out


@case("archive_malformed_input_is_silent")
def _():
    assert run("archive_gate.py", "{{{") == {}


def main() -> None:
    failures = 0
    for name, fn in CASES:
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {name}\n      {exc}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
