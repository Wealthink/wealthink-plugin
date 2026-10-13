# Plugin revamp — tool inventory

**Status:** draft for review · 2026-10-07

> **Update 2026-10-07:** nothing is pruned on the server. The plugin was rebuilt around the
> news tools and ignores the rest. See `wealthink-plugin/README.md`.

## What changes

Module building, module runs, templates, report layout and report sharing now live in the
desktop app. The plugin narrows to two jobs:

1. **Connection setup:** an MCP server config and a setup guide for connecting a Claude
   client to Wealthink (OAuth).
2. **Search skills:** using the Wealthink search engine (stories, the pulse, the live feed,
   companies, tags and thesis checks) from inside Claude.

## How this list was produced

- The dev MCP server is `https://dev-api.thewealthink.com/mcp`, not `dev.thewealthink.com/mcp`
  (that URL is the Next.js web app and returns 404). It requires OAuth.
- The MCP tools are generated from the API's OpenAPI spec, minus `mcp/wealthink_mcp/route_config.py`,
  plus the hand-written tools in `mcp/wealthink_mcp/tools/`. I built the server in-process from
  `wealthink-server@origin/develop` (207da7dd) against the live dev spec
  (`dev-api.thewealthink.com/openapi.json`). It exposes **88 tools**.
- I matched the tools against the web app: `dev.thewealthink.com/stories` calls the `/news/*` routes
  when signed in and `/public/*` when signed out. The `/news/*` tools are therefore the main search
  surface.
- Caveat: this list comes from the `develop` source, not from a `tools/list` call on the deployed
  server. If dev is ahead of or behind `develop`, a few tools may differ. To confirm, run an
  authenticated `tools/list` after connecting.

## Tools to REMOVE from the plugin (51 currently referenced)

The skills, agents, commands and hooks call these tools today. All of them belong to the
desktop-app workflows.

| Area | Tools |
|---|---|
| Qual modules | `list_qual_modules`, `create_qual_module`, `update_qual_module`, `archive_qual_module`, `run_module`, `run_qual_stream`, `test_run_qual`, `test_run_qual_stream`, `get_qual_run_status`, `list_qual_results` |
| Quant modules | `list_quant_configs`, `get_quant_config`, `create_quant_config`, `update_quant_config`, `archive_quant_config`, `run_quant_chart`, `test_run_quant`, `test_run_quant_stream`, `get_quant_result`, `list_quant_chart_types`, `get_expiry_dates` |
| Module discovery | `list_all_modules`, `list_module_options` |
| Data sources | `list_data_sources`, `list_qual_data_sources`, `create_qual_data_source`, `update_qual_data_source`, `delete_qual_data_source`, `get_data_source_endpoints`, `lookup_data_source_field` |
| Templates / reports | `list_templates`, `get_template_by_id`, `create_template`, `update_template`, `archive_template`, `run_template`, `get_template_run_status`, `list_template_reports`, `get_template_report_by_run_id`, `set_template_run_visibility`, `get_public_template_run` |
| Event configs (private tracking) | `list_events`, `get_event`, `update_event`, `archive_event`, `set_event_approval` |
| Org tags | `list_tags`, `get_tag`, `create_tag` |
| Old pool feed | `get_pool_feed` (superseded by the story tools below) |

`list_pool_tags` is the only currently referenced tool that stays.

## Tools to ADD to the plugin

### Core: the search engine (the `/stories` product)

| Tool | Route | Use |
|---|---|---|
| `get_news_pulse` | `GET /news/pulse` | Today's pulse, or the pre-market edition for a given date |
| `get_news_pulse_graph` | `GET /news/pulse/graph` | Drivers, sectors, industry parts and the most-covered companies |
| `list_news_stories` | `GET /news/stories` | Story table with filters: window ≤30d, category, event_type, sector, company, driver, state, surprise, from/to, cursor |
| `get_news_story` | `GET /news/stories/{id}` | One story. Counts against `story_opens`; returns **402** past the plan's history |
| `list_latest_news` | `GET /news/latest` | Live article feed (poll with `since`, page with `cursor`) |
| `search_news_companies` | `GET /news/companies` | Resolves a company name to the canonical name or ISIN before filtering |
| `list_pool_tags` | `GET /events/pool/tags` | Platform tag taxonomy (id + label) |

### Thesis check

| Tool | Use |
|---|---|
| `validate_my_thesis_statement` | Free pre-check: is the statement checkable? |
| `run_pool_thesis_check` | Runs a check. **Uses one weekly check from the plan** when it finds evidence; confirm before running |
| `list_pool_thesis_checks` / `get_pool_thesis_check` | Read back past checks |
| `get_my_thesis_config` | Which browse windows the user's plan unlocks |

### Plan / limits (to handle 402s and quota)

| Tool | Use |
|---|---|
| `get_my_usage` | Remaining story lists, story opens and checks; call before a large pull |
| `list_public_plans` | Explains which plan unlocks a locked window when a 402 names one |
| `get_billing_summary` | Optional: wallet balance and free checks |

### Decision needed: the `/events/pool/*` story tools

These tools return richer data than `/news/*`: company *directions*, knock-on links, first-order
effects and sector helped/hurt counts. The web app does not use them. Do we teach them?

- `list_pool_stories`, `get_pool_story`, `get_pool_article`, `list_pool_company_stories`, `get_pool_pulse`

## Leave out of the plugin (on the server, not taught)

- **Pipeline / debug:** `get_pool_article_trace`, `get_pool_thesis_check_trace`, `list_pool_dropped_headlines`, `get_health`
- **Admin / org:** `get_org_usage`, `list_connectors`, `get_connector`
- **Desktop-app internals:** `list_user_modules`, `get_user_module`, `create_user_module`, `push_user_module_result`, `publish_user_module_result`, `publish_qual_result`, `update_qual_result`, `cancel_qual_run`, `run_quant_module`, `fetch_raw_datasource_payload`, `update_tag`

The plugin can't hide these, because the MCP server still exposes all 88 tools. Removing them
from the agent surface would be a `route_config.py` change in `wealthink-server`. That is out
of scope here unless you want it.

## Plugin files: proposed fate

| Path | Fate |
|---|---|
| `skills/core/{build-qual-module,build-quant-chart,generate-layout,plan-research,research-reports,run-research,share-report,discover}` | Delete |
| `skills/core/market-news` | Rewrite → **search-stories** (pulse, stories, latest, companies, tags) |
| `skills/core/getting-started` | Rewrite → **connect** (OAuth via `/mcp`, dev vs prod URL, verify with `get_my_usage`) |
| `skills/core/understand-system` | Rewrite: the new mental model (story → articles → companies/sectors/drivers; plan limits) |
| New skill **thesis-check** | validate → confirm → run → read back |
| `skills/lenses/*` (4 personas) | Delete, or shrink to one paragraph each on how that persona reads the news |
| `agents/*` (8) | Delete all. Possibly keep `output-digest`, retargeted to large story/feed payloads |
| `commands/wealthink-status.md` | Delete (run polling no longer applies) |
| `commands/wealthink.md` | Rewrite as a natural-language router over the new skills |
| `hooks/publish_gate.py`, `archive_gate.py`, tests | Delete. Possibly replace with a confirm gate on `run_pool_thesis_check` (spends quota) |
| `hooks/session_start.py` | Rewrite the reminder (it still mentions modules, templates and publishing) |
| `.mcp.json` | Keep prod `api.thewealthink.com/mcp`; document dev in the setup guide |
| `plugin.json`, `marketplace.json`, READMEs, `ARCHITECTURE.md`, `docs/connect.md` | Rewrite descriptions and keywords; bump to 0.2.0 |
