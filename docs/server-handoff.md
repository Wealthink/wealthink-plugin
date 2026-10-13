# Server handoff: MCP changes for the Wealthink agent plugin

**From:** plugin team · **To:** server team (`wealthink-server/mcp`) · **Date:** 2026-10-13
**Prod endpoint:** `https://api.thewealthink.com/mcp` · **Dev:** `https://dev-api.thewealthink.com/mcp`

## Context

The Wealthink agent plugin no longer builds modules or reports; that moved to
the desktop app. The plugin now teaches any AI agent (Claude, ChatGPT, Cursor,
Codex, Gemini CLI…) to use Wealthink as a **coherence engine**: the last 24–72
hours of Indian market news as connected stories, links, knock-ons and labels.
It uses these prod tools:

`get_pool_pulse`, `list_pool_stories`, `list_pool_company_stories`,
`get_pool_story`, `get_pool_article`, `list_pool_tags`, and, on paid plans,
`run_pool_thesis_check`, `list_pool_thesis_checks`, `get_pool_thesis_check`.

**Nothing on `/mcp` should be removed.** The desktop app connects through the
same endpoint and needs the module and template tools. Pruning waits for a
server-to-server API.

Why this matters: an agent picks tools from three things only, which are the
server's `instructions`, each tool's description and each tool's schema. Many
agents won't install our skills, so for them these three are the whole
product. The fixes below are the ones the skills can't make.

## Summary

| # | Change | Priority | Effort |
|---|---|---|---|
| 0 | Stop returning article text in any tool | P0 | Small–medium |
| 1 | Fix five tool descriptions | P0 | Small |
| 2 | Add a news section to the server `instructions` | P0 | Small |
| 3 | Serve headlines for every linked story | P0 | Small–medium |
| 4 | Add a news-only endpoint, `/mcp/search` | P0 | Medium |
| 5 | Lower the `limit` default from 200 | P1 | Small |
| 6 | Decide whether articles should bypass story-open metering | P1 | Decision |
| 7 | Preload the core news tools in Claude Code (`alwaysLoad`) | P1 | Small |
| 8 | Declare errors, output schemas and annotations | P1 | Medium |
| 9 | Fix two data gaps | P2 | Small |
| 10 | Ship the `/news/*` and usage tools to prod | P2 | Depends on release |

## P0

### 0. Stop returning article text in any tool

Wealthink links to publishers' articles; it must not republish them. Keeping
article text out of every tool response keeps us legally safe and inside the
search-engine category. An agent that needs the exact wording opens the
article at its URL with its own browser or fetch tool.

**Allowed in responses:** headline, publisher, URL, published time, a short
description or Exa summary, and everything Wealthink produces itself (labels,
directions, links, knock-on reasons, scores).

**Not allowed:** any span of the article body, including "excerpts" and
"evidence sentences" copied from the article.

| Where article text leaks today | Change |
|---|---|
| `get_pool_article` → `excerpt` (verbatim; `excerpt_is_publisher_summary: false` means it is the article's own sentence) | Replace with the description / Exa summary, and drop `excerpt_is_publisher_summary` |
| `run_pool_thesis_check` and `get_pool_thesis_check` → each story's "verbatim evidence sentence" | Return a Wealthink-written reason ("why this challenges / supports the statement") plus the article URL |
| `/news/*` on dev: `list_news_stories`, `get_news_story`, `list_latest_news` rows carry a verbatim `excerpt` | Same as `get_pool_article`, before these ship to prod |
| `get_pool_article_trace`, `get_pool_thesis_check_trace`, `list_pool_dropped_headlines` (also on `/mcp`) | We haven't inspected these payloads. They are pipeline debug views and may include fetched article content. Audit them, and keep them off `/mcp/search` |

Update each tool's description to match ("a short description, not the
article's text; open `url` for the article"). Please also check the desktop
tools that return news (`list_events`, `get_event`, `get_pool_feed`) against
the same rule.

The plugin already tells agents not to present tool text as quotes, and to open
the link for exact wording.

### 1. Fix five tool descriptions

These came from a test on prod (12 Oct). A fresh agent answered a real
portfolio question using only the tools.

| Tool | Problem | Suggested description text |
|---|---|---|
| `run_pool_thesis_check` | Says **"Uses no check credit."** Thesis Check is paid-only with a weekly limit, so agents treat it as free and may run it unasked | Lead with: "Paid plans only. Can use one of the user's weekly checks. Run only when the user asks for a thesis check, after confirming the statement with them." Keep the rest |
| `list_pool_company_stories` | Says "Every story in the **72 h** window". On 12 Oct it returned HDFC Bank stories back to 05 Oct and Bajaj Finance back to 02 Oct, about a week. Agents then label week-old news as "last 72 h" | Either state the real window ("about the last 7 days, newest first") or make the tool honour 72 h. Also return `from` / `as_of` like `list_pool_stories` does |
| `list_pool_stories`, `list_pool_company_stories`, `list_pool_thesis_checks` (`limit`) | `limit` is 1–200 with a default of 200, but the response budget cuts every page to about 10–13 rows. Asking for 20, 25 or 30 returned 10, 13 and 13 | Parameter description: "About 12 rows fit per response; use `next_cursor` for more." See also #5 |
| `get_pool_story` | Doesn't say a call uses one of the user's daily story opens, or that knock-on links end at an industry, not a company | Add: "Each call uses one of the user's daily story opens; open only stories you will cite. Knock-on links end at an industry part (e.g. 'NBFCs and lenders'), never a company." |
| `get_pool_article` | Describes the response as including "its verbatim excerpt" | After #0: "A short description of the article, not its text. Open `url` for the article." |

### 2. Add a news section to the server `instructions`

MCP servers send an `instructions` text to every agent on connect. Wealthink's
current text covers only modules, reports and charts, and tells agents to start
with `list_module_options`. An agent without our plugin is pointed at
desktop-app tools and never learns the news tools exist.

Keep the current text for the desktop app and **append** this:

```
News and market context. Wealthink is also a coherence engine for Indian
markets: it links the last 24–72 hours of financial news into stories, each
labelled with sectors, macro drivers, categories and companies (with the
direction the news moved them), and connected to its causes (follows from),
consequences (followed by), similar stories (related) and knock-on effects on
other industries.

For questions about what is happening in the market, use the pool tools, not
the module tools: get_pool_pulse (last 24 h by sector), list_pool_stories
(filter by sector / driver / company fragment; all=true for 72 h),
list_pool_company_stories, get_pool_story (one story with all its links; uses
one of the user's daily story opens), get_pool_article (an article's source,
description and link; open the link for its text) and list_pool_tags (the exact
labels). Knock-ons are Wealthink's reasoning, not
article claims. A company direction is business impact, not a price call.

run_pool_thesis_check is for paid plans and can use one of the user's weekly
checks: run it only when the user asks for a thesis check, and confirm the
statement first.
```

### 3. Serve headlines for every linked story

In `get_pool_story`, most entries in `follows_from`, `followed_by` and
`related_stories` came back as `{"story_id": "...", "headline": null}`. This
included the strongest links. In the 7 Oct RBI hike story
(`sf736fecf2040665`): 11 of 12 *follows from*, 8 of 12 *followed by* and 9 of
10 *related* had no headline.

**What Langfuse shows:**

- The production stage that creates links, `9b follow-up links (D5)` in
  `wealthink-events-worker`, compares candidate stories that all have headlines
  and summaries.
- So the headline exists when the link is made, and is lost in the layer that
  serves `get_pool_story`.
- Our guess, not confirmed: the lookup only resolves linked stories inside the
  72 h pool, so older causes come back empty.

**Why it matters:** the "why did this happen" chain is the core of the
product. Without the headline, an agent has to spend a story open just to learn
what a link is, so in practice it skips the link.

**Ask:** return the stored headline (and ideally `first_seen`) for every
linked id, whatever its age.

### 4. Add a news-only endpoint, `/mcp/search`

A plugin or skill can't filter a server's tool list. Today every agent that
connects loads about 70 desktop tools it should ignore, which costs context
and confuses tool choice. Only Claude Code users can hide tools, and only by
hand.

Add a second path served by the same process, leaving `/mcp` unchanged:

- **URL:** `https://api.thewealthink.com/mcp/search` (and the same on dev).
- **OAuth:** the same OAuth and JWT verifier, plus the path-qualified
  `.well-known/oauth-protected-resource`. Users shouldn't register a second
  client.
- **Tools:** built from an **allow-list** (the nine tools in Context, plus the
  `/news/*` and usage tools once they're on prod), not the deny-list in
  `route_config.py`. With a deny-list, every future desktop tool would leak
  into it.
- **Instructions:** its own `instructions`, i.e. the news text from #2 alone.

Once it's live on dev, the plugin's `.mcp.json` and setup guide move to it.

## P1

### 5. Lower the `limit` default from 200

`list_pool_stories`, `list_pool_company_stories` and `list_pool_thesis_checks`
default `limit` to 200, while the response budget returns about 12 rows. Set
the default (and ideally the max) to what one response actually holds, so the
schema tells the truth.

### 6. Decide: should articles bypass story-open metering?

`get_pool_story` uses a daily story open. A story's lead article id is the
story id with the `s` swapped for `a` (`sd7d0a67873285e2` →
`ad7d0a67873285e2`). If `get_pool_article` isn't metered, any agent can read
the lead article of any story it has listed without using an open. Our test
agent found and used this without being told.

If that's acceptable, nothing to do. If not, either meter `get_pool_article`
or make article ids unguessable.

### 7. Preload the core news tools in Claude Code (`alwaysLoad`)

Set `_meta["anthropic/alwaysLoad"]: true` on `get_pool_pulse`,
`list_pool_stories`, `list_pool_company_stories`, `get_pool_story`,
`get_pool_article` and `list_pool_tags`. Claude Code then loads these upfront
and leaves the others deferred. Other clients ignore the key.

### 8. Declare errors, output schemas and annotations

- **Errors:** story routes declare only `200` and `422`. Declare `402` (plan
  window or feature, with `required_plan`) and the out-of-quota code (which is
  it, 429?). Use one error body (`error_code`, `message`, `required_plan`,
  `meter`, `resets_at`).
- **Output schemas:** the nine pool tools return no output schema. Adding
  response models gives clients `structuredContent` and tells agents the shape
  before the first call.
- **Annotations:**
  - `run_pool_thesis_check`: `readOnlyHint=False`, `destructiveHint=False`,
    `anthropic/requiresUserInteraction: True` (it spends weekly quota).
  - The other pool tools: `readOnlyHint=True`, `openWorldHint=False`.

## P2

### 9. Fix two data gaps

- `get_pool_pulse`: Realty listed `companies_helped` (Puravankara, Brigade) but
  had no `direct_helped` or `knockon_helped` bucket. Either the bucket is
  missing or the companies come from elsewhere; the two should agree.
- The Signature Global Q2 bookings story (an exchange filing) had
  `companies: []`, so `list_pool_company_stories(name="Signature")` misses it.

### 10. Ship the `/news/*` and usage tools to prod

These exist on dev only: `get_news_pulse`, `get_news_pulse_graph`,
`list_news_stories`, `get_news_story`, `list_latest_news`,
`search_news_companies`, `get_my_usage`, `get_my_thesis_config`,
`validate_my_thesis_statement`, `list_public_plans`. The skills use them when
present.

Before shipping, say in both families' descriptions how `/news/*` differs from
`/events/pool/*`. At the moment an agent can't tell `get_news_story` from
`get_pool_story`.

## Not a bug

Knock-on links can point in opposite directions across stories (e.g. Banks →
NBFCs "helps" in one story and "hurts" in another). Different events push an
industry different ways; the skills now tell agents this is expected.

## What we need back

1. Confirmation that no tool returns article text (#0), including the trace tools.
2. Confirmation of the real window for `list_pool_company_stories` (#1).
3. The cause of the null headlines, and an ETA for the fix (#3).
4. The `/mcp/search` URL on dev (#4).
5. The decision on article metering (#6), and the out-of-quota error code (#8).
