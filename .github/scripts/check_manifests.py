#!/usr/bin/env python3
"""Repo consistency checks that `claude plugin validate` doesn't cover.

Run:  python3 .github/scripts/check_manifests.py

1. Both manifests are valid JSON.
2. The version in plugin.json matches the marketplace entry. They are two
   hand-maintained copies of one number, and `plugin.json` wins at install time —
   so a mismatch silently ships a version the marketplace doesn't advertise.
3. The marketplace entry's `source` actually points at the plugin directory.
4. Every hook matcher and every skill/agent tool grant uses the tool prefix the
   bundled connector actually produces, derived from plugin name + server key.
   Rename either one without sweeping the repo and the gates stop firing.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
errors = []


def load(path: pathlib.Path):
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001 - report, don't raise
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON — {exc}")
        return None


marketplace = load(ROOT / ".claude-plugin" / "marketplace.json")
plugin = load(ROOT / "wealthink-plugin" / ".claude-plugin" / "plugin.json")
mcp = load(ROOT / "wealthink-plugin" / ".mcp.json")

if marketplace and plugin:
    entries = marketplace.get("plugins") or []
    entry = next((e for e in entries if e.get("name") == plugin.get("name")), None)
    if entry is None:
        errors.append(
            f"marketplace.json has no entry named {plugin.get('name')!r}"
        )
    else:
        if entry.get("version") != plugin.get("version"):
            errors.append(
                "version mismatch: plugin.json is "
                f"{plugin.get('version')!r} but the marketplace entry is "
                f"{entry.get('version')!r}"
            )
        # Plugin `source` paths are relative to the marketplace root (the repo
        # root), not to the .claude-plugin/ directory the manifest sits in.
        source = (ROOT / entry.get("source", "")).resolve()
        if not (source / ".claude-plugin" / "plugin.json").exists():
            errors.append(
                f"marketplace entry source {entry.get('source')!r} does not "
                "contain a plugin manifest"
            )

if plugin and mcp:
    servers = list((mcp.get("mcpServers") or {}).keys())
    if len(servers) != 1:
        errors.append(f".mcp.json should declare exactly one server, found {servers}")
    else:
        expected = f"mcp__plugin_{plugin['name']}_{servers[0]}__"
        found = set()
        for path in ROOT.rglob("*"):
            if path.is_dir() or ".git" in path.parts:
                continue
            if path.suffix not in {".md", ".json", ".py"}:
                continue
            for match in re.findall(r"mcp__plugin_[A-Za-z0-9_-]+__", path.read_text()):
                found.add(match)
        wrong = found - {expected}
        if wrong:
            errors.append(
                f"stale tool prefix(es) {sorted(wrong)} — the bundled connector "
                f"produces {expected!r} (plugin name {plugin['name']!r} + server "
                f"key {servers[0]!r})"
            )

if errors:
    for err in errors:
        print(f"FAIL  {err}")
    sys.exit(1)

print("ok    manifests parse, versions agree, tool prefix is consistent")
