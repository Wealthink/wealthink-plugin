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
5. The portable manifest (plugin.json, OpenAI's Agent Plugins format) and its
   marketplace
   (.agents/plugins/marketplace.json) agree with the Claude manifest on name
   and version, and point at the plugin directory.
6. The file list in AGENTS.md is exactly the files ChatGPT's plugin creator
   should copy. It fetches by that list, so a new skill file missing from it
   silently ships a plugin without it.
7. Every skill's `metadata.version` matches the plugin version, so a release
   can't ship with half the version copies bumped.
8. The legacy Codex manifest (.codex-plugin/plugin.json, kept for Codex
   builds that don't read the portable format) agrees with plugin.json on
   name, version and interface.
9. The portable mcp.json and Claude's .mcp.json point at the same server URL.
   They are two hand-kept copies, so an endpoint change in one would ship a
   package pointing somewhere else.
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
codex_marketplace = load(ROOT / ".agents" / "plugins" / "marketplace.json")
codex_plugin = load(ROOT / "wealthink-plugin" / "plugin.json")
portable_mcp = load(ROOT / "wealthink-plugin" / "mcp.json")
legacy_codex_plugin = load(ROOT / "wealthink-plugin" / ".codex-plugin" / "plugin.json")

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

if plugin and codex_plugin:
    for field in ("name", "version"):
        if codex_plugin.get(field) != plugin.get(field):
            errors.append(
                f"wealthink-plugin/plugin.json {field} is {codex_plugin.get(field)!r} "
                f"but .claude-plugin/plugin.json has {plugin.get(field)!r}"
            )

if mcp and portable_mcp:
    claude_urls = {s.get("url") for s in (mcp.get("mcpServers") or {}).values() if isinstance(s, dict)}
    portable_urls = {s.get("url") for s in (portable_mcp.get("mcpServers") or {}).values() if isinstance(s, dict)}
    if claude_urls != portable_urls:
        errors.append(
            f"server URL mismatch: .mcp.json has {sorted(map(str, claude_urls))} "
            f"but mcp.json has {sorted(map(str, portable_urls))}"
        )

if codex_marketplace and codex_plugin:
    entries = codex_marketplace.get("plugins") or []
    entry = next((e for e in entries if e.get("name") == codex_plugin.get("name")), None)
    if entry is None:
        errors.append(
            f".agents/plugins/marketplace.json has no entry named {codex_plugin.get('name')!r}"
        )
    else:
        path = (entry.get("source") or {}).get("path", "")
        if not (ROOT / path / "plugin.json").exists():
            errors.append(
                f".agents/plugins/marketplace.json source path {path!r} does not "
                "contain a plugin.json"
            )

PLUGIN_ROOT = ROOT / "wealthink-plugin"

if plugin:
    for skill in sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md")):
        match = re.search(r'^  version: "([^"]+)"$', skill.read_text(), re.M)
        found_version = match.group(1) if match else None
        if found_version != plugin.get("version"):
            errors.append(
                f"{skill.relative_to(ROOT)}: metadata.version is {found_version!r} "
                f"but the plugin is {plugin.get('version')!r}"
            )
RAW = "https://raw.githubusercontent.com/Wealthink/wealthink-plugin/main/wealthink-plugin/"
agents_md = (ROOT / "AGENTS.md").read_text()
block = re.search(r"<!-- plugin-files:start -->(.*?)<!-- plugin-files:end -->", agents_md, re.S)
if block is None:
    errors.append("AGENTS.md is missing its plugin-files block")
else:
    rows = re.findall(r"^\| `([^`]+)` \| (\S+) \|$", block.group(1), re.M)
    for rel, url in rows:
        if url != RAW + rel:
            errors.append(f"AGENTS.md: raw URL for {rel!r} should be {RAW + rel!r}")
    listed = {rel for rel, _ in rows}
    expected = {"plugin.json", "mcp.json"} | {
        p.relative_to(PLUGIN_ROOT).as_posix()
        for folder in ("skills", "assets")
        for p in (PLUGIN_ROOT / folder).rglob("*")
        if p.is_file() and p.name != ".DS_Store"
    }
    for rel in sorted(expected - listed):
        errors.append(f"AGENTS.md doesn't list plugin file {rel!r}")
    for rel in sorted(listed - expected):
        errors.append(f"AGENTS.md lists {rel!r}, which isn't a plugin file")

packaged = {rel for rel, _ in rows} if block else set()

if codex_plugin:
    openai = (codex_plugin.get("extensions") or {}).get("com.openai")
    interface = openai.get("interface") if isinstance(openai, dict) else None
    if not isinstance(interface, dict) or not interface:
        errors.append("plugin.json has no extensions.com.openai.interface object")
        interface = {}
    for field in ("logo", "logoDark", "composerIcon", "composerIconDark"):
        if field not in interface:
            continue
        value = interface[field]
        target = (PLUGIN_ROOT / value).resolve() if isinstance(value, str) else None
        # The zip is built from the AGENTS.md list, so an icon outside the
        # plugin root or missing from the list never reaches the package.
        if (
            target is None
            or not target.is_file()
            or not target.is_relative_to(PLUGIN_ROOT)
            or target.relative_to(PLUGIN_ROOT).as_posix() not in packaged
        ):
            errors.append(
                f"plugin.json interface.{field} is {value!r}; it must be a "
                "file inside wealthink-plugin/ listed in AGENTS.md"
            )

    if legacy_codex_plugin:
        for field in ("name", "version", "interface"):
            if legacy_codex_plugin.get(field) != (interface if field == "interface" else codex_plugin.get(field)):
                errors.append(
                    f"wealthink-plugin/.codex-plugin/plugin.json {field} doesn't match "
                    "plugin.json (interface: extensions.com.openai.interface)"
                )

    # ChatGPT's installer rejects any interface link that isn't https://
    # (a mailto: supportURL blocked the 0.5.0 install).
    for field, value in interface.items():
        if field.endswith("URL") and not str(value).startswith("https://"):
            errors.append(
                f"plugin.json interface.{field} is {value!r}; "
                "ChatGPT only accepts https:// links"
            )

# OpenAI's Agent Plugins schemas, vendored in .github/schemas/ so CI doesn't
# depend on agent-plugins.org being up. Skipped where jsonschema isn't installed;
# CI installs it.
try:
    import jsonschema
except ImportError:
    jsonschema = None
    print("skip  schema validation of plugin.json and mcp.json (pip install jsonschema)")
if jsonschema:
    for doc, name in ((codex_plugin, "plugin"), (portable_mcp, "mcp")):
        if doc is None:
            continue
        schema = json.loads((ROOT / ".github" / "schemas" / f"{name}.schema.json").read_text())
        for err in jsonschema.Draft202012Validator(schema).iter_errors(doc):
            path = "/".join(str(p) for p in err.absolute_path) or "(root)"
            errors.append(f"wealthink-plugin/{name}.json {path}: {err.message}")

if errors:
    for err in errors:
        print(f"FAIL  {err}")
    sys.exit(1)

schemas = "portable manifests match their schemas" if jsonschema else "schemas NOT checked"
print(f"ok    manifests parse, versions agree, tool prefix is consistent, server URLs agree, AGENTS.md file list is complete, skill versions agree; {schemas}")
