# MCP handoff: a search-only tool surface for the Wealthink plugin

**From:** plugin team · **To:** server team (`wealthink-server/mcp`) · **Date:** 2026-10-07
**Inventory source:** `wealthink-server@origin/develop` (207da7dd) built in-process against `https://dev-api.thewealthink.com/openapi.json`. That build has **88 tools**.

> **Update 2026-10-07: pruning is on hold.** The desktop app reaches Wealthink only
> over MCP, so the old tools stay until a server-to-server API replaces that path. The
> plugin ignores the tools it doesn't need. The description, schema, error and annotation
> fixes in §5 still apply to the current tool names on `/mcp`.

## 0. Asks that apply now (no pruning needed)

0. **Stand up the `/mcp/search` profile (§2) next to `/mcp`.** This isn't pruning:
   `/mcp` keeps every tool for the desktop app. It is the only way to keep the ~70
   desktop tools out of an agent's context. A plugin or skill can't filter a
   server's tool list, and only Claude Code can hide tools on the user's side.
   Once it exists, the plugin and setup guide point at `/mcp/search`.
1. **Ship the `/news/*`, usage and thesis-config tools to prod.** Prod
   (`api.thewealthink.com/mcp`) lacks `get_news_pulse`, `get_news_pulse_graph`,
   `list_news_stories`, `get_news_story`, `list_latest_news`,
   `search_news_companies`, `get_my_usage`, `get_my_thesis_config`,
   `validate_my_thesis_statement` and `list_public_plans`; only dev has them. The
   plugin's skills work on prod's pool tools today and use these when present.
2. **Add a news paragraph to the server `instructions`.** Many agents won't install
   skills, so the MCP `instructions` field is the only guidance they ever see.
   Keep the module/report text for the desktop app and append the news section
   (the §6 text, using today's tool names).
3. **Per-tool `_meta["anthropic/alwaysLoad"]: true`** on the core news tools
   (`get_pool_pulse`, `list_pool_stories`, `list_pool_company_stories`,
   `get_pool_story`, `get_pool_article`, `list_pool_tags`), so Claude Code loads
   them upfront and leaves the other ~80 tools deferred.
4. **Optional: expose the skills as MCP prompts** (`prompts/list`), e.g.
   `market-context`, `market-pulse`, `trace-story`, so any MCP client can offer
   them as slash commands without installing anything.
5. **Make the pool list defaults agent-safe**: `limit` defaults to 200 on
   `list_pool_stories`, `list_pool_company_stories` and `list_pool_thesis_checks`.

## 0b. Findings from an agent test on prod (2026-10-13)

A fresh agent answered a real portfolio question using only the plugin's
skills and the prod tools. These are the fixes that belong on the server,
because tool descriptions reach every agent, with or without the plugin.

**Tool descriptions**

1. **`run_pool_thesis_check` says "Uses no check credit."** Thesis Check is
   paid-only with a weekly limit, so an agent reading this will treat it as
   free. Suggested: "Paid plans only; can use one of the user's weekly checks.
   Run only when the user asks for a thesis check, after confirming the
   statement."
2. **`list_pool_company_stories` says "Every story in the 72 h window".** It
   returns older stories: on 12 Oct, HDFC Bank rows went back to 05 Oct and
   Bajaj Finance rows to 02 Oct. Either fix the description ("about a week")
   or the window.
3. **`limit` (default 200, max 200) promises more than it delivers.** Asking for
   20, 25 or 30 rows returned 10–13, because the response budget trims first.
   Suggested description: "Up to about 12 rows fit per response; use
   `next_cursor` for more." Or lower the default to match.
4. **`get_pool_story`**: add that knock-ons end at an industry, not a company,
   and that each call uses a daily story open.
5. **`get_pool_article`**: add that `excerpt_is_publisher_summary: true` means
   the excerpt is a summary, not a quote.

**Behaviour**

6. **Linked stories come back with `headline: null`.** In the 7 Oct RBI hike
   story (`sf736fecf2040665`), most `follows_from`, `followed_by` and
   `related_stories` entries had no headline, including the strongest ones.
   Langfuse (production, `9b follow-up links (D5)`) shows the pipeline compares
   stories that all have headlines when it creates the links. So the nulls
   likely come from the layer that serves `get_pool_story`, probably when a
   linked story falls outside the 72 h pool. Without the headline, an agent
   must spend a story open to learn what a link is. Please serve the stored
   headline for every linked id.
7. **Opens can be skipped through articles (please confirm whether this
   matters).** A story's lead article id is the story id with `s` swapped for
   `a` (`sd7d0a67873285e2` → `ad7d0a67873285e2`). If `get_pool_article` isn't
   metered, an agent can read any story's lead article without using a story
   open. The test agent did this unprompted.
8. **Small data gaps.** The pulse lists Realty's `companies_helped` (Puravankara,
   Brigade) with no `direct_helped` bucket for Realty. The Signature Global
   bookings story has `companies: []`, so company search misses it.

## 1. Why

The Wealthink Claude plugin no longer builds modules or reports, because that moved to the desktop
app. The plugin now does two things only:

1. Connects a Claude client to Wealthink over OAuth.
2. Lets the user search the stories engine (the `/stories` product): the pulse, stories,
   the live feed, companies, tags and thesis checks.

The agent currently sees all 88 tools. About 70 of them are irrelevant to the plugin and are
loaded upfront (`alwaysLoad`). This costs context in every session and makes wrong-tool picks
likely: there are two "story" families and an old `get_pool_feed`.

## 2. Hard constraint: don't prune `/mcp`

The desktop app uses the **same endpoint**, `https://api.thewealthink.com/mcp`, and relies on the
module and template tools. See `wealthink-desktop/brand.config.json` (`mcpUrl`),
`resources/wealthink-plugin/.mcp.json` and `integrations/agent-plugins/wealthink-connect/mcp.json`.
Excluding those routes in `route_config.py` would break the desktop app.

### Ask 1: add a second, allow-listed endpoint

Expose a **search profile** at a new path, e.g. `https://api.thewealthink.com/mcp/search`
(dev: `https://dev-api.thewealthink.com/mcp/search`). Requirements:

- **Same process, same OAuth.** Keep the same JWT verifier and the same
  `.well-known/oauth-protected-resource` (with the path-qualified variant for `/mcp/search`).
  Users should not register a second OAuth client.
- **Allow-list, not deny-list.** `route_config.py` exposes new routes by default
  ("New API endpoints are exposed by default"). For this profile that rule would leak every
  future desktop tool to the plugin. Build the profile from an explicit `INCLUDED_TOOLS` set,
  e.g. by mapping everything else to `MCPType.EXCLUDE` or by filtering on a FastMCP tag such as
  `profile:search`.
- **Its own `instructions`.** The current `INSTRUCTIONS` text describes modules, templates,
  `run_module`, `set_template_run_visibility`, and so on. The search profile needs the text in §6.
- **Scope.** Optionally, restrict the profile to `mcp:read`, plus the thesis-check tools.

The plugin will then point `.mcp.json` at `/mcp/search`. `/mcp` stays exactly as it is for the
desktop app.

## 3. The allow-list (19 tools)

| # | Tool (current name) | Route | Proposed name on `/mcp/search` |
|---|---|---|---|
| 1 | `get_news_pulse` | `GET /news/pulse` | `get_pulse` |
| 2 | `get_news_pulse_graph` | `GET /news/pulse/graph` | `get_pulse_graph` |
| 3 | `list_news_stories` | `GET /news/stories` | `list_stories` |
| 4 | `get_news_story` | `GET /news/stories/{story_id}` | `get_story` |
| 5 | `list_latest_news` | `GET /news/latest` | `list_latest_articles` |
| 6 | `search_news_companies` | `GET /news/companies` | `search_companies` |
| 7 | `list_pool_company_stories` | `GET /events/pool/company-stories` | `list_company_stories` |
| 8 | `get_pool_article` | `GET /events/pool/articles/{id}` | `get_article` |
| 9 | `get_pool_pulse` | `GET /events/pool/pulse` | `get_sector_impact` (see §5.2) |
| 10 | `list_pool_stories` | `GET /events/pool/stories` | *drop if same data as #3* (see §5.2) |
| 11 | `get_pool_story` | `GET /events/pool/stories/{id}` | *drop if same data as #4* (see §5.2) |
| 12 | `list_pool_tags` | `GET /events/pool/tags` | `list_tags` |
| 13 | `get_my_thesis_config` | `GET /thesis/config` | `get_search_filters` |
| 14 | `validate_my_thesis_statement` | `POST /thesis/validate` | `validate_thesis` |
| 15 | `run_pool_thesis_check` | `POST /events/pool/thesis` | `run_thesis_check` |
| 16 | `list_pool_thesis_checks` | `GET /events/pool/checks` | `list_thesis_checks` |
| 17 | `get_pool_thesis_check` | `GET /events/pool/checks/{id}` | `get_thesis_check` |
| 18 | `get_my_usage` | `GET /usage` | `get_my_usage` |
| 19 | `list_public_plans` | `GET /public/plans` | `list_plans` |

The renames are optional. On a fresh endpoint they cost nothing, and the agent stops seeing
internal vocabulary ("pool", "my_thesis_config"). If you rename, keep the old names on `/mcp`.

## 4. Pruned from `/mcp/search` (69 tools; stays on `/mcp`)

| Area | Tools |
|---|---|
| Qual modules | `list_qual_modules`, `create_qual_module`, `update_qual_module`, `archive_qual_module`, `run_module`, `run_qual_stream`, `test_run_qual`, `test_run_qual_stream`, `get_qual_run_status`, `cancel_qual_run`, `list_qual_results`, `update_qual_result`, `publish_qual_result` |
| Quant modules | `list_quant_configs`, `get_quant_config`, `create_quant_config`, `update_quant_config`, `archive_quant_config`, `run_quant_chart`, `run_quant_module`, `test_run_quant`, `test_run_quant_stream`, `get_quant_result`, `list_quant_chart_types`, `get_expiry_dates` |
| User modules | `list_user_modules`, `get_user_module`, `create_user_module`, `push_user_module_result`, `publish_user_module_result` |
| Module discovery | `list_all_modules`, `list_module_options` |
| Data sources | `list_data_sources`, `list_qual_data_sources`, `create_qual_data_source`, `update_qual_data_source`, `delete_qual_data_source`, `get_data_source_endpoints`, `lookup_data_source_field`, `fetch_raw_datasource_payload` |
| Templates / reports | `list_templates`, `get_template_by_id`, `create_template`, `update_template`, `archive_template`, `run_template`, `get_template_run_status`, `list_template_reports`, `get_template_report_by_run_id`, `set_template_run_visibility`, `get_public_template_run` |
| Org event configs | `list_events`, `get_event`, `update_event`, `archive_event`, `set_event_approval` |
| Org tags | `list_tags` (org), `get_tag`, `create_tag`, `update_tag` |
| Superseded feed | `get_pool_feed` (replaced by stories) |
| Pipeline / debug | `get_pool_article_trace`, `get_pool_thesis_check_trace`, `list_pool_dropped_headlines`, `get_pool_pulse`* |
| Admin / ops | `get_org_usage`, `get_billing_summary`, `get_health`, `list_connectors`, `get_connector` |

\* Prune `get_pool_pulse` only if §5.2 finds it duplicates `get_news_pulse`; otherwise keep it as #9.

`get_billing_summary` and `get_health` are judgement calls. We'd drop them: the agent should send
quota questions to `get_my_usage`, and money questions to the web app.

## 5. Per-tool fixes so the agent performs well

Agents choose tools from the description and schema alone. These are the gaps we found.

### 5.1 Descriptions to rewrite

These are the proposed descriptions, written for a model reader. Where we are unsure of a
behaviour, the text marks it **[confirm]**.

**`get_pulse`** (was `get_news_pulse`). Current: "The latest pulse (or the pre-market edition of `date`)."
> Today's market pulse for Indian equities: the day's headline strip, the sector grid (which sectors news helped or hurt), story states (new/developing/settled), surprises, and the latest stories. Start here for "what's happening today?". `edition=premarket` with an IST `date` (YYYY-MM-DD) returns that morning's pre-market edition. Story ids in the response open with `get_story`.

**`get_pulse_graph`**. Current: "Drivers, sectors, industry parts and the most-covered companies."
> A graph of what today's news connects: macro drivers (e.g. "The rupee", "Crude oil"), the sectors and industry segments they move, and the most-covered companies (`companies`, 0–30, default 14). Use it for "how is crude affecting markets today?". It is not for listing stories.

**`list_stories`** (was `list_news_stories`)
> Search stories (clusters of articles about one event), newest first. Every filter is optional and they combine: `window` (24h/72h/7d/30d) or `from`/`to`, `category`, `event_type`, `source_type`, `sector`, `driver`, `company` (**an ISIN**; get it from `search_companies` first), `state`, `surprise`. Valid filter values come from `get_search_filters`. `limit=0` returns only totals and facets, which is cheap: use it to size a query before pulling. Page with `next_cursor`. Going further back than the plan's story history returns 402, naming the plan that allows it. Each listed story counts against the plan's `stories listed` meter **[confirm]**.

**`get_story`** (was `get_news_story`)
> Everything about one story: its articles and outlets, sectors, drivers, the companies tagged and the direction news moved each one, direct effects, knock-on effects, related stories, and what it follows from and what follows from it. **Each call uses one of the plan's daily story opens** (once per story per day). Open only the stories you will actually use; summarise from `list_stories` when the list fields are enough. A story older than the plan's history returns 402.

**`list_latest_articles`** (was `list_latest_news`)
> Individual articles as they arrive, newest first. These are raw articles, not clustered stories. It takes the same filters as `list_stories`. Use it for "what just came in?" or to watch a topic: save `poll_cursor` and pass it back as `since` to get only newer items (`more_new` says whether more arrived than fit). Use `cursor` for older pages. For "what happened", use `list_stories` instead.

**`search_companies`** (was `search_news_companies`). Current: "Search News Companies", which says nothing.
> Resolve a company name or ticker fragment to its ISIN, canonical name and sector (`q`, `limit` 1–20). Call it before filtering `list_stories` or `list_latest_articles` by `company`, because those take an ISIN, not a name. Never guess an ISIN.

**`list_company_stories`** (was `list_pool_company_stories`)
> Every story that tags one company, newest first, as far back as the plan's story history. Use it for "what's the news on <company>?". It takes a company **name fragment** in `name`. **[confirm: could it take an ISIN like the `/news` tools, for consistency?]**

**`get_article`** (was `get_pool_article`)
> One article as the pipeline tagged it: a verbatim excerpt, the companies it names with direction and channel, sectors, drivers and global moves. Use it to quote evidence behind a story. Article ids come from `get_story` or `list_latest_articles`.

**`list_tags`** (was `list_pool_tags`)
> The platform's tag taxonomy (id + label) used to label stories and articles. **[confirm: which `/news` filter, if any, accepts these tags? If none, say so here, or drop the tool from the profile.]**

**`get_search_filters`** (was `get_my_thesis_config`). The current name and description ("`/public/thesis/config` for a signed-in user…") hide what the tool returns: the full filter vocabulary for every search tool.
> The valid values for every search filter, and what this user's plan unlocks: `windows` (each with `available`, plus `required_plan` when locked), `history_hours`, `max_range_days`, `categories`, `event_types`, `source_types`, `sectors` (name + short_name), `outlets`, `drivers`, and `statement_max_chars` for thesis checks. Call it once per session, before filtering. It is cheap (about 2 KB) and uses no quota.

**`validate_thesis`** (was `validate_my_thesis_statement`)
> Check, for free, whether a statement can be thesis-checked (≤ `statement_max_chars`, one falsifiable claim about Indian markets). It returns `ok`, `kind` and, when the statement isn't checkable, a suggested `reword`. It uses no quota and stores nothing. Always call it before `run_thesis_check`.

**`run_thesis_check`** (was `run_pool_thesis_check`). Keep the current text, which is good, and **lead with the cost**:
> **Uses one of the plan's weekly thesis checks** when it finds evidence; confirm with the user first. …(current text)… Optional `company_isin` scopes the check to one company (get the ISIN from `search_companies`). Takes up to **[confirm: N s]**.

**`list_thesis_checks` / `get_thesis_check`**: fine as they are. Add "uses no quota" to both.

**`get_my_usage`**: good as it is. Add: "Call it before a large pull, and after any 402 or 429."

### 5.2 Remove the duplication between `/news/*` and `/events/pool/*`

There are two story families: `list_news_stories`/`get_news_story`/`get_news_pulse` and
`list_pool_stories`/`get_pool_story`/`get_pool_pulse`. Their descriptions overlap heavily. The
`/stories` web app uses only `/news/*`.

- If the two families read the same store, keep only the `/news/*` family on `/mcp/search` and
  make sure `get_story` returns everything `get_pool_story` does (directions, knock-ons,
  follows / followed_by). Its schema already lists those fields.
- If they differ, state the difference in both descriptions ("use X when…, use Y when…").
  At the moment an agent can't tell them apart.
- `get_pool_pulse` (sector helped/hurt, with the story ids behind each count) overlaps
  `get_news_pulse.sector_view`. Keep one.

### 5.3 Parameter consistency

| Issue | Fix |
|---|---|
| `company` is an **ISIN** on `/news/*` but a **name fragment** on `/events/pool/*` | Use one convention. We'd prefer to accept either, resolving server-side and reporting what matched under `meta.resolved`, as `fetch_raw_datasource_payload` already does |
| `category`, `event_type`, `source_type`, `sector` and `driver` are free strings | Put `enum`s in the schema (the values are fixed; see `get_search_filters`), or name `get_search_filters` in each parameter's description |
| `driver` accepts a label ("The rupee") or an id ("rupee"), but `get_search_filters.drivers` returns labels only | Return `{id, label}` |
| `list_pool_stories`, `list_pool_company_stories` and `list_pool_thesis_checks` default `limit` to **200** | Default to 20 for agents. 200 stories is a very large tool result |
| `list_pool_stories.all` duplicates `window=72h` | Drop it |

### 5.4 Output schemas

`run_pool_thesis_check`, `list_pool_tags`, `get_pool_story`, `get_pool_article`, `get_pool_pulse`,
`list_pool_stories`, `list_pool_company_stories`, `list_pool_thesis_checks` and
`get_pool_thesis_check` have **no output schema** (FastMCP shows `null`). Add response models so
clients get `structuredContent` and the agent knows the shape without calling the tool first.

### 5.5 Errors the agent must handle

These are **not in the OpenAPI responses**. Every story route lists only `200` and `422`, so
the agent can't tell from the spec that they exist:

- **402** (plan history or window exceeded; names `required_plan`)
- **429** or another code for a meter that has run out (**[confirm the code]**)
- **428 `PAGE_KEY_REQUIRED`** (seen on `/public/*` from an anonymous call). Confirm it can never
  reach an MCP caller.

Ask: declare these responses on the routes, and use one error body everywhere
(`error_code`, `message`, `required_plan`, `meter`, `resets_at`). The current error body repeats
the message in `message`, `error` and `detail`. Trim it to one field to save tokens.

Also: what does `preview: true` on `PulseResponse` / `StoryListResponse` / `StoryTeaser` mean
for a signed-in MCP caller? If it means truncated results, say so in the description, and add a
`preview_reason`.

### 5.6 Annotations (`tool_customization.py`)

| Tool | Current | Should be |
|---|---|---|
| `run_pool_thesis_check` | none (POST, not prefix-matched) | `readOnlyHint=False`, `destructiveHint=False`, **`anthropic/requiresUserInteraction: True`** (it spends weekly quota) |
| `validate_my_thesis_statement` | none (POST) | `readOnlyHint=True` |
| `get_news_story`, `get_pool_story` | `readOnlyHint=True` | Keep, but add to the description that each call uses a story open |
| All other allow-listed tools | `readOnlyHint=True` via `get_`/`list_` | OK. Add `openWorldHint=False` |

## 6. Proposed `instructions` for `/mcp/search` (under 250 words)

```
Wealthink is a coherence engine for Indian market news. Articles are clustered into
stories; each story is tagged with sectors, macro drivers (e.g. "The rupee"),
companies (with the direction the news moved them) and knock-on effects.

Start with get_pulse for "what's happening today". Use list_stories to search, and
get_story to open one. Use list_latest_articles for raw articles as they arrive.

Before filtering: call get_search_filters once for the valid categories, event
types, sectors, drivers and the windows this user's plan allows. Resolve a company
to its ISIN with search_companies; never guess one.

Plans meter usage. Each get_story call uses one daily story open, so summarise
from the list fields and open only stories you will cite. Use list_stories with
limit=0 to size a query cheaply. A 402 means the plan does not reach that far back
or that window: relay the named plan; do not retry. Check get_my_usage before a
large pull.

Thesis check: validate_thesis is free. run_thesis_check uses one of the user's
weekly checks, so confirm with the user before calling it. It returns the
stories that challenge or support a statement, with verbatim evidence. It is not
advice, and it does not decide whether the statement is right.

Never ask for a password; auth is OAuth.
```

## 7. What we need back

1. The `/mcp/search` URL on dev, so the plugin can test end to end.
2. Answers to the **[confirm]** items: meters per tool, the out-of-quota error code, `preview`
   semantics, whether `list_tags` maps to a filter, `/news` vs `/events/pool` equivalence, and
   thesis-check latency.
3. Typical response sizes for `get_pulse`, `list_stories?limit=20`, `get_story` and
   `run_thesis_check` on dev. We can't measure authenticated payloads from our side. We'd like
   each one under about 25 KB at the default limits.
4. An authenticated `tools/list` from `/mcp/search` on dev, so we can check the final names and
   schemas against this doc.

## 8. Plugin side (for reference, our work)

The plugin will remove all module, report, persona and agent content. It will ship these skills:
`connect` (OAuth setup guide), `search-stories`, `thesis-check` and `understand-wealthink`, plus
the `/wealthink` router command. A PreToolUse hook will confirm before `run_thesis_check`.
`.mcp.json` will point at `/mcp/search` once it exists.
