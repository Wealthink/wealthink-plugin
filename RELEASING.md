# Releasing the Wealthink plugin

For maintainers and coding agents changing this repo. One source tree ships
to every client:

| Client | What it installs | Where it reads it from |
|---|---|---|
| Claude Code, Claude.ai, Desktop, Cowork | `wealthink-plugin/` via `.claude-plugin/` | the `main` branch, through `.claude-plugin/marketplace.json` |
| Codex | `wealthink-plugin/` via `.codex-plugin/` | the `main` branch, through `.agents/plugins/marketplace.json` |
| ChatGPT | `wealthink-plugin.zip` | the latest GitHub release |

Merging to `main` ships to Claude and Codex users straight away. ChatGPT users
get a change only once a release is published.

## Rules

- **Never build or upload `wealthink-plugin.zip` by hand.** The `release`
  workflow builds it from the file list in `AGENTS.md` and attaches it when a
  release is published. A hand-made zip can include the Claude-only files
  (`.claude-plugin/`, `hooks/`, `commands/`), which ChatGPT's plugin creator
  rejects.
- **Bump every version copy together.** The version lives in
  `wealthink-plugin/.claude-plugin/plugin.json`,
  `wealthink-plugin/.codex-plugin/plugin.json`,
  `.claude-plugin/marketplace.json` and each skill's `metadata.version`. CI
  fails if any one differs.
- **A new plugin file goes in the `AGENTS.md` file list,** with its raw URL.
  CI fails if a file under `skills/` is missing from the list, and the zip is
  built from that list only.
- **Claude-only features stay out of the ChatGPT package.** Hooks, commands
  and anything that relies on `${CLAUDE_PLUGIN_ROOT}` or
  `mcp__plugin_wealthink_mcp__` tool names work only in Claude Code.
- **Release only from `main`.** The `release` workflow refuses a tag whose
  commit isn't on `main`, and a ruleset lets only admins create, move or
  delete `v*` tags.
- **Don't rename the MCP server key `mcp` or the plugin name `wealthink`.**
  Claude's tool names are built from both, and the hooks match on them.

## Steps

1. On a branch, make the change and bump the version (semver) in every copy.
2. Run the checks:
   ```bash
   python3 .github/scripts/check_manifests.py
   python3 wealthink-plugin/hooks/tests/test_hooks.py
   python3 .github/scripts/package_plugin.py dist/wealthink-plugin.zip
   claude plugin validate . --strict
   claude plugin validate ./wealthink-plugin --strict
   ```
3. Open a PR. The `validate` workflow runs the same checks; merge when green.
4. On GitHub, publish a release from `main` tagged `v<version>`, for example
   `v0.5.0`. The `release` workflow fails if the tag doesn't match the
   version, and otherwise attaches `wealthink-plugin.zip`.
5. Check that
   https://github.com/Wealthink/wealthink-plugin/releases/latest/download/wealthink-plugin.zip
   downloads and lists the files in `AGENTS.md`, and that it was built by CI:
   ```bash
   gh attestation verify wealthink-plugin.zip -R Wealthink/wealthink-plugin
   ```
