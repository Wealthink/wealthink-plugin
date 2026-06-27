---
name: market-news
allowed-tools: mcp__plugin_wealthink_mcp__*
description: >
  Browse, filter, and summarise the market news and events Wealthink tracks for
  the user's workspace — across commodities, macro, policy, currencies, and
  equities. Use when the user asks what's happening in the market, wants recent
  news on a topic/instrument, asks for a news digest, or wants context before
  running deeper research. Read-first: news trackers are provisioned by Wealthink.
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

## Browse events

Use `list_events` with filters. Common patterns:

- **Recent across everything:** `list_events` with a sensible limit (e.g. 20),
  newest first.
- **By topic/instrument:** filter by a tag (e.g. `gold`, `rbi-policy`,
  `rupee`). If you don't know the exact tag, call `list_tags` first
  (see `discover`).
- **By date window:** filter from/to dates — e.g. "this week", "since the last
  RBI meeting".
- **By the news that's been vetted:** filter to approved items when the user
  wants only reviewed/curated news.
- **Drill into one item:** `get_event(event_id)` for the full title, content,
  source, published date, and relevance.

Combine filters (tag + date + approved) and paginate for large windows. Sort by
published date (desc) for a chronological digest.

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
- `list_events` returns only the user's workspace news — never cross-org data.
- If the user wants a *new* topic tracked that isn't in the stream, tell them to
  request it via the Wealthink app / account manager; you can't create trackers here.
