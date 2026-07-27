---
name: market-news
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
description: >
  Browse, filter, and summarise the market news and events Wealthink tracks for
  the user's workspace — across commodities, macro, policy, currencies, and
  equities. Use when the user asks "what's happening in gold this week?", "any
  news on the RBI?", "give me a market digest", or wants context before running
  deeper research. Note: news trackers are provisioned by Wealthink — this skill
  reads and curates the stream, it does not create trackers.
---

# Market News & Events

Wealthink continuously tracks market news for the user's workspace and stores it
as **events** — dated news/data items tagged by topic and instrument. This skill
is how you read and summarise that stream. For a multi-asset research firm this
spans commodities (gold, silver, crude), macro/policy (RBI, inflation, rates),
currencies (rupee), and equities.

> **Trackers are provisioned by Wealthink.** Setting up *what* gets tracked
> (event configs) happens in the Wealthink app / with the account manager — it is
> not available through this connector. Through Claude you read the resulting
> news and build research on top of it.

## Two feeds

There are **two** news streams, and a good answer often draws on both:

| Feed | Tool | What it is |
|---|---|---|
| The workspace's own | `list_events` | News Wealthink tracks specifically for this org |
| **Common Event Pool** | `get_pool_feed` | A platform-curated shared feed — macro, geopolitics, cross-market items — readable by **every** member with no plan gate |

The pool exists so each org doesn't have to configure and pay for the same
macro/geopolitical fetches. Its tags are a separate namespace: list them with
`list_pool_tags`, not `list_tags`.

When the user asks a broad macro question ("what's driving markets this week?"),
check the pool as well as their own feed. When they ask about something specific
to their coverage, their own feed is usually enough.

## Browse events

Use `list_events` (own feed) or `get_pool_feed` (shared pool) with filters. Both
take the same filter vocabulary:

- **Keyword search:** `q=<text>` — case-insensitive substring across **title OR
  summary**. This is the fastest way to answer "any news on X?" when you don't
  have a tag for X. Note it is broader than the per-field `title=` / `summary=`
  filters, which match one field only.
- **Recent across everything:** a sensible `page_size` (e.g. 20), newest first.
- **By topic/instrument:** filter by tag. If you don't know the exact tag, call
  `list_tags` (own feed) or **`list_pool_tags`** (pool) first — they are different
  namespaces and a tag from one will not match the other.
- **By date window:** ISO-8601 `<field>_start` / `<field>_end` — e.g. "this week",
  "since the last RBI meeting".
- **By the news that's been vetted:** filter to approved items when the user wants
  only reviewed/curated news.
- **Drill into one item:** `get_event(event_id)` for the full title, content,
  source, published date, and relevance.

Combine filters (tag + date + `q` + approved) and page with `page` / `page_size`
(default 50, max 200) for large windows. Sort with `sort_by` / `sort_order` —
published date descending for a chronological digest. Filter server-side rather
than pulling broadly and narrowing afterwards.

## Summarise like an analyst

Don't dump raw event JSON. Produce a tight, decision-useful digest:

> **Big windows are a digest job.** A wide `list_events` pull (a long date range,
> or many tags) can return far more than is useful to hold or render. When the
> result is large, spawn an `output-digest` agent on the same `list_events` query
> — it absorbs the full list and returns the themed summary below, keeping the raw
> events out of the main context. For a small, focused pull, summarise inline.

```
## Gold & rupee — this week (12 tracked items)

**Gold**
- RBI gold reserves up ~X tonnes (3 items) — supportive backdrop.
- MCX gold near-month firm on safe-haven flows (4 items).

**Rupee / macro**
- USDINR pressure from higher US yields (2 items).
- Inflation print due Thu — watch for rate-path repricing (1 item).

Top sources: <names>.   Window: 06–12 Jun.
```

Group by theme/instrument, lead with what matters, cite how many items support
each point, and keep it skimmable. Offer an obvious next step:
> "Want me to run your Gold Market SWOT on this, or build a briefing report?"

## Handing off to deeper research

Market news is usually the *context* step. After summarising, the natural next
moves are:
- `run-research` — run a qualitative module that analyses these events.
- `research-reports` — produce a full report that includes this news.
- `build-qual-module` — turn a recurring question about this stream into a saved
  module. A qual module can read the pool alongside the org's own events: it takes
  **`pool_tags`** as well as user tags. Resolve pool tags with `list_pool_tags`
  first — unlike user tags, an unrecognised pool tag is **silently dropped**, and
  the module then fetches nothing from the pool.

## Curating news (may be plan-gated)

Some workspaces can lightly curate the stream:
- `update_event(...)` — correct/enrich an item's metadata.
- `set_event_approval(...)` — mark an item approved/rejected for use in modules.
- `archive_event(...)` — hide an item.

These are write actions. If the backend returns `plan_required` / 402, relay it
plainly ("curating news needs a Pro plan — contact your account manager") and
continue in read-only mode. **Confirm with the user before approving/archiving**,
since approval affects what downstream modules consume.

## Notes

- Default to **read-only** unless the user explicitly asks to approve/edit/hide.
- `list_events` returns only the user's workspace news — never another org's. The
  Common Event Pool is the one shared surface, and it is platform-curated: it
  contains no org's private events. Pool curation is platform-operator only; the
  agent can read the pool but never edit it.
- If the user wants a *new* topic tracked that isn't in either stream, tell them to
  request it via the Wealthink app / account manager; you can't create trackers here.
