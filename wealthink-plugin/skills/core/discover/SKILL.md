---
name: discover
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - mcp__plugin_wealthink_mcp__lookup_*
description: >
  Find the user's Wealthink resources and their IDs — research modules
  (qualitative + quantitative), report templates, tags, data sources, available
  chart types, and futures expiry dates. Use this whenever you need a real ID
  before running, building, or referencing something, or when the user asks
  "what modules / templates / tags / data sources do I have?".
---

# Discover Wealthink Resources

Almost every action needs a real resource ID (a module, template, tag, or data
source). **Never guess an ID.** Use the connector's read tools to find it first,
then act. Fetch only what the current task needs.

## Discovery tools

```
Research modules
  list_module_options    ← cheapest: id + name across qual AND quant, unpaginated
  list_all_modules       all modules (qualitative + quantitative), full rows
  list_qual_modules      qualitative modules only
  list_quant_configs     quantitative chart modules only
  get_quant_config(id)   one quant module (add include_code=true for its ai_code)

Report templates
  list_templates         the user's report templates
  get_template_by_id(id) one template (add include_layout=true for custom_layout)
  list_template_reports(template_id=…)      generated runs for ONE template
  get_template_report_by_run_id(template_id, run_id)   one historical run

Market news (read-only — provisioned by Wealthink)
  list_events            the org's own tracked news items (supports filters)
  get_event(id)          one news item in full
  list_pool_tags         tags in the shared Common Event Pool
  get_pool_feed          the shared pool feed (no plan gate — see market-news)

Organising / building blocks
  list_tags              topics/instruments the workspace is organised around
  get_tag(id)            one tag
  list_qual_data_sources qualitative data sources (news/web/API)
  list_data_sources      external data-source integrations (see the note below)
  get_data_source_endpoints(name)   endpoints a data source exposes
  lookup_data_source_field(...)     fields available on an endpoint

Quant building inputs
  list_quant_chart_types available Plotly chart types for quant charts
  get_expiry_dates(...)  valid futures/derivatives expiry dates for an instrument
```

> **If a tool name doesn't resolve**, list the connector's tools and match on the
> suffix rather than giving up. A couple of endpoints currently surface under an
> auto-generated name (`list_tags_api_v1_tags_get`,
> `list_data_sources_api_v1_data_sources_get`) instead of the short one. They are
> the same tools; call whichever name the connector actually advertises.

## How to use it

1. **Match the user's words to a resource type.** "my gold analysis" → a
   qualitative module; "the silver chart" → a quant module; "weekly report" → a
   template; "RBI news" → events filtered by tag.
2. **Call the narrowest tool with the tightest filter.** For "what do I have?",
   `list_module_options` beats `list_all_modules` — it returns id + name only,
   across both module types, with no pagination to walk.
3. **Resolve to a single ID.** If several match, show the candidates and ask the
   user which one — don't pick silently.

## Filter, sort and page — don't fetch and filter client-side

Every list endpoint takes the same filter vocabulary. Use it; over-fetching and
then filtering in your own head is the main way these calls get expensive.

```
Paging      page, page_size          default 50, max 200 (replaces the old `limit`)
Sorting     sort_by, sort_order      an unknown sort_by silently falls back to the default
Search      q                        case-insensitive name search
Archived    is_archived              archived resources are excluded by default
Date ranges <field>_start / <field>_end     ISO-8601, e.g. created_at_start
```

Resource-specific filters are published in each tool's schema — among them
`module_type`, `fetch_type`, `commodity`, `created_via`, `run_frequency`,
`asset_class`, `frequency`, `is_active`, `status`, `is_published`, and
`next_run_at` ranges. **Read the tool schema rather than guessing**; it is
generated from the API, so it is authoritative.

## Payload-shape parameters (opt in, don't over-fetch)

Three heavy fields are stripped by default and returned only on request. The
defaults are the cheap path — pass the flag only when you will actually read the
field:

| Field | Ask for it with | Roughly |
|---|---|---|
| `custom_layout` (template layout TSX) | `include_layout=true` on `list_templates` / `get_template_by_id` | 13–14 KB per template |
| `ai_code` (quant module's generated code) | `include_code=true` on `list_quant_configs` / `get_quant_config` / `update_quant_config` | 6–9 KB per config |
| `result` rows on a run | `data="full"` (default is a compact form — see below) | can reach hundreds of KB |

For run results, prefer **`data="schema"`** — a Draft-7 JSON Schema of `result`
instead of the rows. It is the right input whenever you need to know the *shape*
(building a layout, checking which fields exist) rather than the numbers.
`data="both"` gives you schema plus values; `data="full"` only when the user is
actually reasoning over the data.

Never combine `include_layout=true` with an unfiltered `list_templates`.

## Presenting results

Summarise as a compact table; show only the columns that matter for the task.

```
## Qualitative modules
| ID       | Name                    | Last run    |
|----------|-------------------------|-------------|
| qm_abc…  | Gold Market SWOT        | 2 days ago  |
| qm_def…  | RBI Policy Watch        | yesterday   |

## Quantitative modules
| ID       | Name              | Instrument | Chart        |
|----------|-------------------|------------|--------------|
| cfg_123… | Silver MCX 7D     | SILVER     | candlestick  |
```

If the user only needs modules, don't dump tags and data sources too.

## Notes

- IDs are opaque strings — pass them through verbatim; never reformat them.
- Event *trackers* are configured by Wealthink, not discovered or created here.
  Two feeds are readable: `list_events` (the org's own) and `get_pool_feed` (the
  shared Common Event Pool) — see `market-news`.
- `list_data_sources` shows only sources the workspace can actually run. The
  connector pins agent callers to the enabled view, so a source you can't see is
  one that needs credentials added in the Wealthink app — a human action.
- Credential tools are deliberately not exposed to agents. If a data source needs
  a key, say so and point at the app; never try to read or set one.
- If a tool returns `plan_required` / 402, relay it plainly and continue with
  whatever the workspace *can* access.
