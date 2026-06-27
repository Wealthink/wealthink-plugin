---
name: discover
allowed-tools: mcp__plugin_wealthink_wealthink__*
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
  list_all_modules       all modules (qualitative + quantitative) in one list
  list_qual_modules      qualitative modules only
  list_quant_configs     quantitative chart modules only
  get_quant_config(id)   full detail of one quant module

Report templates
  list_templates         the user's report templates
  list_template_reports  generated report runs/reports

Market news (read-only — provisioned by Wealthink)
  list_events            recent tracked news items (supports filters)
  get_event(id)          one news item in full

Organising / building blocks
  list_tags              topics/instruments the workspace is organised around
  get_tag(id)            one tag
  list_qual_data_sources qualitative data sources (news/web/API)
  list_data_sources      all external data-source integrations available
  get_data_source_endpoints(name)   endpoints a data source exposes
  lookup_data_source_field(...)     fields available on an endpoint

Quant building inputs
  list_quant_chart_types available Plotly chart types for quant charts
  get_expiry_dates(...)  valid futures/derivatives expiry dates for an instrument
```

## How to use it

1. **Match the user's words to a resource type.** "my gold analysis" → a
   qualitative module; "the silver chart" → a quant module; "weekly report" → a
   template; "RBI news" → events filtered by tag.
2. **Call the narrowest list tool**, optionally with a name/search filter.
3. **Resolve to a single ID.** If several match, show the candidates and ask the
   user which one — don't pick silently.

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
- `list_events` is the only events surface most users have; event *trackers* are
  configured by Wealthink, not discovered/created here.
- If a tool returns `plan_required` / 402, relay it plainly and continue with
  whatever the workspace *can* access.
