# Wealthink for agents

Do your financial research with Claude, powered by your Wealthink workspace.

This plugin teaches Claude how to use the **Wealthink MCP connector** the way a
research analyst actually works: browse the market news Wealthink tracks for you,
run qualitative and quantitative research, assemble multi-asset research reports,
and share them with clients — all in plain conversation.

It targets **agentic harnesses**: **Claude Code** and **Cowork (claude.ai)**,
where Claude can spawn subagents and isolate large tool output. Plain chat is
**not** a supported surface — Wealthink responses (a full `list_events`, a whole
run output, a stitched report) routinely exceed what a chat UI will render.

Other MCP clients (Cursor, VS Code, Codex, OpenCode, ChatGPT custom connectors)
can connect to the Wealthink MCP server directly — see
[`docs/connect.md`](../docs/connect.md) — and get the tools, but not the plugin's
skills, agents or hooks.

The plugin is the same for everyone; what each workspace is allowed to do is
decided by Wealthink on the backend (see [Plans & permissions](#plans--permissions)).

---

## Install & connect

### Claude Code (two commands)

```bash
# 1. Add the Wealthink marketplace
/plugin marketplace add Wealthink/wealthink-plugin

# 2. Install the plugin (this also registers the Wealthink MCP server)
/plugin install wealthink@wealthink
```

### Connect (OAuth — no token to copy)

The Wealthink connector authenticates with **OAuth**. There's no API key to paste
and no password to type into the chat.

```
/mcp  →  plugin:wealthink:mcp  →  Authenticate
```

Installing the plugin registers the server for you; it appears in `/mcp` under the
plugin's name, as **`plugin:wealthink:mcp`** — not as `wealthink`. (`claude mcp
login plugin:wealthink:mcp` runs the same flow from a shell.)

A browser window opens for Wealthink sign-in and consent. Approve it once; Claude
caches the token in your system keychain and refreshes it automatically, so you
won't be asked again on this machine. To confirm you're connected, just ask Claude
*"what's set up in my Wealthink workspace?"* — the `getting-started` skill verifies
the connection and orients you.

### Cowork / claude.ai and Claude Desktop

Open **Customize → Plugins** in the left sidebar, add this marketplace
(`Wealthink/wealthink-plugin`), and install **Wealthink for agents**. That brings
the connector *and* the skills across in one step — you do not need to copy
anything by hand. Authorise the connector when prompted.

### Any other MCP client

Cursor, VS Code, Codex, OpenCode and ChatGPT custom connectors can talk to the
Wealthink MCP server directly. Configuration snippets and the one caveat that
matters (tool names differ from the bundled path) are in
[`docs/connect.md`](../docs/connect.md).

---

## What you can do

Once Wealthink is connected, just ask Claude in natural language:

- *"What's moved in gold and the rupee this week?"* — Claude browses the news
  Wealthink has tracked for your workspace and summarises it.
- *"Run my gold market SWOT and show me the result."*
- *"Generate a silver MCX futures chart for the near-month expiry."*
- *"Build my weekly multi-asset research report and share it with my client."*
- *"Set up a new module that analyses RBI policy news for rate-cut signals."*
- *"Lay out last week's report as a two-column dashboard."*

You don't need to know module IDs, expiry codes, or API details — Claude
discovers them for you with the connector's tools.

---

## How it fits together

```
You (Code / chat / Cowork / Desktop)
   │  "run my weekly gold report"
   ▼
Claude  ── uses these skills to plan the work ──┐
   │                                            │
   │  calls Wealthink MCP tools                 │  skills = the playbooks
   ▼                                            ▼  in this plugin
Wealthink MCP connector ──────────────► Wealthink platform (your workspace)
   run_module · run_template ·                  modules · templates · charts ·
   run_quant_chart · list_events · …            the news Wealthink tracks for you
```

- **The MCP connector** exposes Wealthink as ~50 tools Claude can call
  (`list_qual_modules`, `run_module`, `run_quant_chart`, `run_template`,
  `list_events`, …). It is delivered and maintained by Wealthink, and this plugin
  bundles it (`.mcp.json`) so installing the plugin registers it automatically.
- **This plugin** is the *knowledge layer* on top: skills that tell Claude which
  tools to use for which real research task, in what order, and how to present
  the result. The connector provides the tools; the plugin provides the judgement.

---

## What's inside

The plugin is split into two layers: **core** (persona-agnostic mechanics — how to
build a module, run a report, share a link) and **lenses** (thin persona adapters
that map a desk's vocabulary onto core and hand off). Lenses depend on core; core
never references a lens. Adding a persona is additive — drop a folder under
`skills/lenses/` and never touch core. See `ARCHITECTURE.md` for the full design.

### Core skills — mechanics (Claude picks the right one automatically)

| Skill | Use it to… |
|-------|------------|
| `getting-started` | Connect, authenticate, and see what's already set up in your workspace |
| `discover` | Find your modules, templates, tags, data sources, and their IDs |
| `market-news` | Browse and filter the market news/events Wealthink tracks for you |
| `plan-research` | Plan a new report: capture intent → gap-analyse your sources → propose a build plan |
| `understand-system` | Map an existing report/process (PDF, deck, code) onto Wealthink artifacts |
| `run-research` | Run a qualitative module or generate a quantitative chart, and present the result |
| `build-qual-module` | Create or refine a qualitative research module (an analysis question over news/sources) |
| `build-quant-chart` | Create or refine a quantitative chart module (e.g. an MCX futures chart) |
| `research-reports` | Build, run, and fetch multi-module research report templates |
| `share-report` | Publish a finished report run to a client link, or revoke it |
| `generate-layout` | Generate a report's visual layout as a branded, frontend-rendered design (matches your existing templates) |

### Lens skills — persona adapters

| Lens | For… |
|------|------|
| `public-markets` | Equity desks: coverage, morning notes, earnings, sector rotation |
| `private-equity` *(scaffold)* | PE: portfolio monitoring, deal screens, LP packs |
| `venture` *(scaffold)* | VC: pipeline, thesis monitoring, portfolio updates |
| `fund-manager` *(scaffold)* | Funds: allocation, risk, mandate/board reporting |

### Agents (autonomous workers + orchestrators — Claude Code & Cowork)

Workers run autonomously (they can't ask questions) and either fan out in parallel
or digest a large payload so it never floods the conversation:

- **`module-builder`** *(worker)* — builds one approved module spec, test-runs it, returns a summary. **Creates only; never repairs.** Fan out one per module, concurrently — building them in sequence costs minutes each.
- **`module-fixer`** *(worker)* — repairs one existing module against a **written acceptance spec**, within five edit→run cycles, then returns `fixed` or `blocked` with the exact unmet assertion. **Repairs only; never creates.**
- **`run-verify`** *(worker)* — runs one module, verifies the output, recommends a `run_id`. **Recommends, never publishes.**
- **`output-digest`** *(worker)* — absorbs a big run/report/`list_events` payload and returns a tight summary.

Every worker carries a `maxTurns` cap and a `tools:` allowlist, so its scope is
enforced rather than merely described. A builder cannot edit; a fixer cannot
create; none of them can publish or archive.

Orchestrators run an end-to-end flow by delegating to the core skills:

- **`wealthink-researcher`** — discover → run → synthesise → present.
- **`wealthink-report-builder`** — assemble modules → run → lay out → share.
- **`public-markets-research`** / **`pe-research`** *(lens orchestrators)* — the above in an equity-desk / PE voice.

### Hooks (Claude Code backstops)

Deterministic enforcement of guardrails that the skills already require in prose
(so they hold in Cowork too). They are scoped to Wealthink tools only:

- **Publish gate** — explicit confirmation before making a report run public. Only a
  positively identified revoke passes through; an unrecognised payload asks.
- **Removal gate** — explicit confirmation before archiving (soft-delete) or deleting
  (hard) a module/template/config/event/data source. The prompt says which it is.
- **Connection reminder** — a non-blocking reminder at session start to authenticate (OAuth) and never invent IDs.

See `hooks/README.md`. The matchers target the **bundled** connector's tool prefix,
`mcp__plugin_wealthink_mcp__` (plugin name `wealthink` + server key `mcp`). If you
configure Wealthink by hand in another client the tool names differ and these hooks
do not fire — the skills' own confirmation rules are the guarantee there. See
[`docs/connect.md`](../docs/connect.md).

### Commands (Claude Code)

- **`/wealthink:wealthink <request>`** — universal natural-language entry point.
- **`/wealthink:wealthink-status <run_id>`** — quick status check on a running job.

---

## Tool loading

The connector is registered with **`alwaysLoad: true`**, so all its tool schemas
load at session start instead of being discovered on demand.

This is a trade-off, and it is deliberate. By default Claude Code defers MCP tool
definitions and searches for them when needed — which is cheaper per session, but
means every subagent re-discovers the same tools. Measured on a real session:
**136 tool-search calls, with `run_quant_chart` re-selected 32 times.** Because
those are turns and turn cost compounds, loading upfront wins for this connector.

The cost: the schemas occupy context for the whole session, and startup blocks
until the server connects (capped at 5s). If your sessions are short, or you run
Wealthink alongside several other connectors, **remove the line** from
`.mcp.json` — nothing else depends on it:

```json
{ "mcpServers": { "mcp": { "type": "http", "url": "https://api.thewealthink.com/mcp" } } }
```

Requires Claude Code v2.1.121 or later; earlier versions ignore the field.

## Fewer permission prompts

Each skill pre-approves the tools it needs via `allowed-tools`, but **that grant
covers only the turn that invoked the skill** — it clears when you send your next
message. In a long research session that means the reads start prompting again
from your second message onward.

For a smoother session, allow the read tools once at the session or project level.
In Claude Code, run `/permissions` and add:

```
mcp__plugin_wealthink_mcp__list_*
mcp__plugin_wealthink_mcp__get_*
```

Or in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "mcp__plugin_wealthink_mcp__list_*",
      "mcp__plugin_wealthink_mcp__get_*"
    ]
  }
}
```

**Allow reads, not writes.** Nothing in the plugin pre-approves
`set_template_run_visibility`, `archive_*` or `delete_*` — those should always
stop and ask, and the hooks below add a second confirmation on top. Adding them
to an allow rule removes the only protection a non-Claude-Code client has.

If you configured Wealthink manually rather than through the plugin, substitute
your own server key — see [`docs/connect.md`](../docs/connect.md#tool-names-by-path).

---

## Plans & permissions

The plugin offers the full capability set to everyone. **What your workspace is
actually allowed to do is enforced by Wealthink on the backend**, not by this
plugin — so you may occasionally hit an action your plan doesn't include.

- **Market news is provisioned for you.** Wealthink configures and runs the
  news/event tracking for your workspace. Through the connector you *read* that
  news and build research on top of it. Setting up new event trackers happens in
  the Wealthink app / with your account manager, not through Claude.
- **Graceful limits.** If an action isn't available on your plan, the connector
  returns a clear `plan_required` message. Claude will relay it ("this action
  needs a Pro plan — contact your account manager") rather than failing cryptically.

Everything else — building and running modules, generating charts, producing and
sharing reports — is available to every workspace by default.

---

## Versioning

Current release: **`0.1.0`** — pre-1.0. Bump `version` in
`.claude-plugin/plugin.json` (and the matching entry in the repo-root
`.claude-plugin/marketplace.json` — CI fails if they drift) on each release:

- Patch (`0.0.x`): wording/doc tweaks.
- Minor (`0.x.0`): new skills/agents.
- Major (`x.0.0`): breaking structural changes (reserve `1.0.0` for the first
  production-stable release).

In Claude Code, run `/plugin` to update an installed plugin after a new version is
published.

## Contributing

`ARCHITECTURE.md` is the design contract — read it before adding or changing a
skill, agent, hook or command. The short version: skills own every workflow and
all user interaction, agents do autonomous/parallel/large-payload work, hooks are
deterministic backstops for rules that are *also* written into the skills, and
lenses depend on core while core never references a lens.

Before opening a PR:

```bash
python3 wealthink-plugin/hooks/tests/test_gates.py
python3 .github/scripts/check_manifests.py
claude plugin validate . --strict
claude plugin validate ./wealthink-plugin --strict
```

CI runs the same four.
