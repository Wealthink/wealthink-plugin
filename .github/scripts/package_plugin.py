#!/usr/bin/env python3
"""Build the ChatGPT / Codex plugin package.

Run:  python3 .github/scripts/package_plugin.py dist/wealthink-plugin.zip

The zip holds exactly the files AGENTS.md lists (plugin.json, mcp.json, the
logos in assets/ and the skills), at their paths relative to the plugin root.
The Claude-only parts (.claude-plugin/, .mcp.json, hooks/, commands/) and the
legacy .codex-plugin/ manifest are left out: ChatGPT's plugin creator rejects
what it can't use.
"""
import pathlib
import re
import sys
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "wealthink-plugin"

block = re.search(
    r"<!-- plugin-files:start -->(.*?)<!-- plugin-files:end -->",
    (ROOT / "AGENTS.md").read_text(),
    re.S,
)
files = re.findall(r"^\| `([^`]+)` \|", block.group(1), re.M)

out = pathlib.Path(sys.argv[1])
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for rel in files:
        zf.write(PLUGIN_ROOT / rel, rel)

print(f"ok    {out} ({len(files)} files)")
