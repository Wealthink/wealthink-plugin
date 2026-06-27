# Wealthink for agents

Do your financial research with Claude, powered by your Wealthink workspace.

This plugin teaches Claude how to use the **Wealthink MCP connector** the way a
research analyst actually works: browse the market news Wealthink tracks for you,
run qualitative and quantitative research, assemble multi-asset research reports,
and share them with clients — all in plain conversation.

It works in **Claude Code**, **Claude chat and Cowork (claude.ai)**, and **Claude
Desktop**. The plugin is the same for everyone; what each workspace is allowed to
do is decided by Wealthink on the backend (see [Plans & permissions](#plans--permissions)).

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
/mcp  →  select  wealthink  →  Authenticate
```

A browser window opens for Wealthink sign-in and consent. Approve it once; Claude
caches the token in your system keychain and refreshes it automatically, so you
won't be asked again on this machine. To confirm you're connected, just ask Claude
*"what's set up in my Wealthink workspace?"* — the `getting-started` skill verifies
the connection and orients you.

### claude.ai (chat / Cowork) and Claude Desktop

- **claude.ai** — open **Settings → Connectors**, add the **Wealthink** connector,
  and authorise it (the same OAuth browser consent). Install the Wealthink
  **Skills** from this repo's `skills/` folder via your workspace's Skills settings.
- **Claude Desktop** — add the server to `claude_desktop_config.json`, then
  approve the OAuth prompt on first use:
  ```json
  {
    "mcpServers": {
      "wealthink": { "type": "http", "url": "https://api.thewealthink.com/mcp" }
    }
  }
  ```

> Self-hosting or local dev? See the Wealthink server repo for stdio mode and
> pointing the connector at a local API.

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

- **`module-builder`** *(worker)* — builds one approved module spec, test-runs it, returns a summary. Fan out one per module.
- **`run-verify`** *(worker)* — runs one module, verifies the output, recommends a `run_id`. **Recommends, never publishes.**
- **`output-digest`** *(worker)* — absorbs a big run/report/`list_events` payload and returns a tight summary.

Orchestrators run an end-to-end flow by delegating to the core skills:

- **`wealthink-researcher`** — discover → run → synthesise → present.
- **`wealthink-report-builder`** — assemble modules → run → lay out → share.
- **`public-markets-research`** / **`pe-research`** *(lens orchestrators)* — the above in an equity-desk / PE voice.

### Hooks (Claude Code backstops)

Deterministic enforcement of guardrails that the skills already require in prose
(so they hold in Cowork too). They are scoped to Wealthink tools only:

- **Publish gate** — explicit confirmation before making a report run public (revoke passes through).
- **Archive gate** — explicit confirmation before soft-deleting a module/template/config/event.
- **Connection reminder** — a non-blocking reminder at session start to authenticate (OAuth) and never invent IDs.

See `hooks/README.md`. The matchers assume the bundled connector is named
`wealthink` (tool prefix `mcp__plugin_wealthink_mcp__`).

### Commands (Claude Code)

- **`/wealthink:wealthink <request>`** — universal natural-language entry point.
- **`/wealthink:wealthink-status <run_id>`** — quick status check on a running job.

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

Current release: **`0.0.1`** — initial pre-1.0 release. Bump `version` in
`.claude-plugin/plugin.json` (and the matching entry in the repo-root
`.claude-plugin/marketplace.json`) on each release:

- Patch (`0.0.x`): wording/doc tweaks.
- Minor (`0.x.0`): new skills/agents.
- Major (`x.0.0`): breaking structural changes (reserve `1.0.0` for the first
  production-stable release).

In Claude Code, run `/plugin` to update an installed plugin after a new version is
published.
