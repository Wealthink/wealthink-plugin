# Wealthink news: payloads and fields

The samples are real responses from the core tools, trimmed (marked `…`).
Range bounds and research timestamps are ISO 8601 in IST
(`"2026-10-16T22:04:50+05:30"`, sendable back as `from` / `to`); story rows
also keep short display times like `"07 Oct 17:57 IST"`.

## Fields on every story and research answer

| Field | Meaning |
|---|---|
| `as_of` | The newest moment the answer covers. Windows count back from here, not from now |
| `data_from` | The oldest story Wealthink holds. A `data_note` says when a window reaches back before it |
| `stale` / `stale_warning` | `true` when the pipeline hasn't updated for 2 hours: tell the user the news may be out of date |
| `pipeline_versions` | The pipeline versions that judged these stories; rules differ between versions |
| `about` | What the numbers are: counts of news and Wealthink's judgments, not a forecast |
| `hint` | Only on an empty answer: why, and what to try (a longer window, a broader filter) |
| `count` / `showing` / `next_cursor` / `note` | Total, rows on this page, the next page, and a note when more exist |

## `get_pool_pulse`: the last 24 hours

```json
{
  "as_of": "07 Oct 17:57 IST", "stories_24h": 253, "articles_24h": 455,
  "states": {"new": 78, "developing": 34, "settled": 141},
  "sector_view": {
    "Automobile and Auto Components": {
      "direct_helped": {"stories": 1, "story_ids": ["s23adb5a96fadd52"]},
      "direct_hurt":   {"stories": 1, "story_ids": ["sf736fecf2040665"]},
      "knockon_hurt":  {"stories": 14, "story_ids": ["sd7d0a67873285e2", "…"]},
      "breakdown": {
        "companies_helped": ["Tata Motors Passenger Vehicles Ltd.", "Gabriel India Ltd."],
        "companies_hurt": ["Bajaj Auto Ltd.", "Maruti Suzuki India Ltd.", "…"],
        "sector_wide_stories": {},
        "driver_knockons": ["Interest rates and RBI policy (hurts)", "Crude oil (hurts)"]
      }
    },
    "…": {}
  },
  "note": "… one vote per story, no weighting. Not a market forecast.",
  "pipeline_version": "baseline-5"
}
```

| Field | Meaning |
|---|---|
| `sector_view.<sector>` | Up to four buckets, `direct_helped`, `direct_hurt`, `knockon_helped` and `knockon_hurt`, each with a story count and the `story_ids`. A bucket is missing when it's 0 |
| `breakdown.companies_helped/_hurt` | Companies whose stories drove the counts |
| `breakdown.sector_wide_stories` | Stories about the whole sector rather than one company, keyed `helped` / `hurt` |
| `breakdown.driver_knockons` | The drivers reaching the sector, with their direction |

How to read it: a sector that is mostly `knockon_*` is being moved by
something elsewhere. Name the driver behind it. Counts are story votes, **not
a forecast or an index move**.

## `list_pool_stories` / `list_pool_company_stories`: story rows

```json
{
  "from": "2026-10-06T17:57:00+05:30", "as_of": "2026-10-07T17:57:00+05:30",
  "data_from": "2026-09-01T22:04:50+05:30", "stale": false,
  "count": 10, "showing": 5,
  "stories": [{
    "story_id": "sf736fecf2040665",
    "headline": "RBI Monetary Policy: Rates raised by 25 bps, stance changed to 'calibrated tightening'",
    "first_seen": "07 Oct 10:02 IST", "last_update": "07 Oct 13:30 IST",
    "last_seen": "2026-10-07T13:30:00+05:30",
    "state": "developing", "articles": 15,
    "categories": ["Policy", "Macro"], "event_types": ["Policy decision"], "surprise": true,
    "companies": ["Ashok Leyland Ltd. (hurts)", "Canara Bank (helps)", "HDFC Bank Ltd. (neutral)",
                  "Maruti Suzuki India Ltd. (hurts)", "…"],
    "sectors": ["Automobile and Auto Components", "Capital Goods", "Financial Services", "Realty"],
    "drivers": ["Interest rates and RBI policy", "The rupee"],
    "effects": {"Interest rates and RBI policy": "up", "Banks": "helps", "The rupee": "down"},
    "knock_ons_shown": 4, "related_stories": 23
  }],
  "next_cursor": "NQ",
  "note": "5 more stories not shown (response budget). Pass next_cursor …"
}
```

| Field | Meaning |
|---|---|
| `count` / `showing` / `next_cursor` | Total matches, rows returned, and the cursor for the next page. Rows are trimmed to a response budget (about 6,000 characters), so a page holds about 9 rows whatever `limit` says; `limit` only lowers it |
| `state` | `new` (first seen), `developing` (still gaining articles), `settled` (coverage stopped) |
| `articles` | Number of articles clustered into the story. More articles means better established |
| `companies` | `"<name> (<direction>)"`, with `", close call"` appended when the evidence is nearly balanced. The direction is business impact, not a price call |
| `effects` | First-order effects: drivers `up` / `down`; industry parts `helps` / `hurts` / `mixed` |
| `knock_ons_shown` | Displayed knock-on links (the full list is in the story) |
| `related_stories` | Count of related + follows-from + followed-by links. 0 means the story is a dead end for threading |
| `categories` / `event_types` / `surprise` | Why the row matched an `event_type`, `category` or `surprise` filter |

Filters: `sector`, `driver`, `event_type` and `category` take exact values (see
"Fixed filter values" below). `sector` also matches a story whose named
company is in that sector.

### `list_pool_company_stories`: one company over time

Pass `company` as an ISIN (`"INE646L01027"`) or a name. The answer adds:

```json
{
  "company": {"name": "InterGlobe Aviation Ltd.", "isin": "INE646L01027", "sector": "Services"},
  "tally": {"helps": 0, "hurts": 3, "mixed": 0, "neutral": 0},
  "by_channel": {"demand": 3}, "close_calls": 0,
  "stories": [{"story_id": "s1681ff92f26afe3", "headline": "Domestic air passenger traffic falls 6.34% …",
               "arrow": "hurts", "strength": "weak", "close_call": false, "channels": ["demand"], "…": "…"}]
}
```

A name that matches several companies (`"Bank"`) returns `candidates`
(`name`, `isin`, `sector`, `stories`) and no stories: ask the user which one,
or pass its ISIN. `strength` is `strong` / `moderate` / `weak` for a helps or
hurts arrow, from the story's average; null when neutral or mixed.

The company list also includes `settled` stories from earlier days, so it gives
a short history.

## `get_pool_story`: one story with every link

```json
{
  "story_id": "sd7d0a67873285e2",
  "headline": "RBI liquidity management: Central bank to use ‘appropriate mix’ of tools to align WACR with repo rate",
  "first_seen": "2026-10-07T13:16:00+05:30", "last_seen": "2026-10-07T13:16:00+05:30",
  "state": "new", "article_count": 1,
  "categories": ["Policy"], "event_types": ["Policy decision"], "surprise": false,
  "sectors": ["Financial Services"], "drivers": ["Interest rates and RBI policy"],
  "articles": [{"article_id": "ad7d0a67873285e2", "publisher": "CNBC-TV18",
                "headline": "…", "published": "2026-10-07T13:16:00+05:30", "url": "https://www.cnbctv18.com/…"}],
  "citations": [],
  "companies": [{"name": "PB Fintech Ltd.", "isin": "INE417T01026", "sector": "Financial Services",
                 "arrow": "hurts", "strength": "strong", "close_call": false, "articles": 1,
                 "p_better": 0.08, "p_worse": 0.92}],
  "first_order_effects": {"Interest rates and RBI policy": "up"},
  "knock_ons": [
    {"from": "Interest rates and RBI policy", "to": "NBFCs and lenders", "to_sector": "Financial Services",
     "direction": "hurts", "order": 2, "shown": true, "link_strength": "likely",
     "size": "noticeable", "reason": "Higher rates raise NBFCs' cost of funds faster than they can reprice loans",
     "articles_supporting": 1},
    {"from": "Real estate", "to": "Cement", "to_sector": "Construction Materials",
     "direction": "hurts", "order": 3, "shown": false, "link_strength": "possible",
     "size": "noticeable", "reason": "Housing is the largest source of cement demand", "articles_supporting": 1}
  ],
  "follows_from": [{"story_id": "s6caf0edb48a8172",
                    "headline": "RBI Shifts Stance, Hikes Repo Rate For First Time Since February 2023 …",
                    "link_strength": "strong"}],
  "followed_by": [{"story_id": "s0ecd0274b89a6c8",
                   "headline": "Why Rate cuts off the table? Repo rate raised after 4 yrs …",
                   "link_strength": "likely"}],
  "related": [{"story_id": "sf736fecf2040665",
               "headline": "RBI Monetary Policy: Rates raised by 25 bps, stance changed to 'calibrated tightening'",
               "link_strength": "possible"}]
}
```

| Field | Meaning |
|---|---|
| `articles` | Processed articles, oldest first. `article_id` opens with `get_pool_article` |
| `citations` | Other outlets' copies, not processed. List and link them; never quote them |
| `companies` | Each company, rolled up over the story's articles: `arrow` and `strength` as on a row; `close_call: true` means read before relying on it; `p_better` / `p_worse` are for ranking only. It can be empty even for a macro story |
| `first_order_effects` | The drivers or industry parts the news itself moves |
| `knock_ons` | Chains outward, shown ones first. `order` 2 = one hop and 3 = two hops; follow `from` → `to` to see the chain (rates → real estate → cement). `shown: false` (below the bar the website shows) or `link_strength: "possible"` means a weak lead |
| `follows_from` | Earlier stories this one is a consequence of: the **why** |
| `followed_by` | Later stories that follow from it: the **what next** |
| `related` | The closest similar stories. Not causal |

Story links carry `link_strength` (`strong`, `likely` or `possible`), strongest
first. A linked story's `headline` can be `null`; open it only if the link
matters.

## `get_pool_article`: evidence

```json
{
  "article_id": "a4c882d2966bcdee", "publisher": "CNBC-TV18",
  "headline": "Stock Crash: PB Fintech shares fall 28%; …", "url": "https://www.cnbctv18.com/…",
  "published": "2026-10-16T19:56:35+05:30", "story_id": "s55ea6a5c8c05ec1",
  "excerpt": "<one sentence>", "excerpt_source": "article",
  "categories": ["Company", "Regulation"], "event_types": ["Policy decision"], "source_type": "Analysis",
  "sectors": ["Financial Services"], "drivers": [], "surprise": true,
  "global": false, "global_moves": {}, "india_moves": {},
  "companies": [{"name": "PB Fintech Ltd.", "isin": "INE417T01026", "sector": "Financial Services",
                 "arrow": "hurts", "strength": "strong", "channels": ["regulation"],
                 "p": 0.9, "p_better": 0.08, "p_worse": 0.92}]
}
```

| Field | Meaning |
|---|---|
| `excerpt` / `excerpt_source` | One sentence of the article (`"article"`) or the publisher's own blurb (`"publisher_summary"`). Publisher text, not the article: link `url`, and open it for exact wording |
| `categories` | Contains `"Company"` when the article is mainly about one or a few named companies' own business |
| `event_types` | Contains `"Results"` when the article is mainly about a company's reported results |
| `global_moves` / `india_moves` | World prices or demand the article reports moving (`{"Global crude oil prices": "up"}`), and what that moves in India, keyed by an Indian driver (usable as `driver=`) or a business part such as `"Appliances and electronics"` (filter by its sector, which is in `sectors`) |
| `companies[].arrow` / `strength` | Direction for the business, not the share price, and how strongly. `p`, `p_better`, `p_worse` are for ranking only, never price odds |

Use `source_type` and `surprise` to weigh the story.

## `list_pool_driver_moves`: what the news is doing to macro drivers

Without `driver`: per driver, `up`, `down` and `unconfirmed` story counts and
what "up" means. With `driver`:

```json
{
  "driver": "The rupee", "up_means": "the rupee strengthens against the dollar",
  "moves": [
    {"story_id": "sf231d5e1a494e10", "title": "Rupee has a fair case to appreciate: RBI DG …",
     "last_seen": "2026-10-15T23:19:20+05:30", "direction": "up",
     "means": "the rupee strengthens against the dollar", "day_check": "not_confirmed"},
    {"story_id": "sf88e7b52f687150", "title": "INR slides as oil prices resurge …",
     "direction": "down", "means": "the rupee weakens against the dollar", "day_check": "confirmed"}
  ]
}
```

`day_check`: `confirmed` (other reports that day back the move),
`not_confirmed` (they don't; the website hides it and its knock-ons appear
nowhere else, so treat it as a lead), `pending` (not checked yet), or `null`
(the move is older than the day check; it is not "not confirmed").

## `list_pool_knockons`: what a move reached next

Needs a `sector` (the industry affected) or a `driver` (what moved), or both:

```json
{
  "stories": 4,
  "knockons": [{"from": "Crude oil", "to": "Airlines", "to_sector": "Services", "direction": "hurts",
                "link_strength": "likely", "size": "large",
                "reason": "Jet fuel is an airline's largest cost and tracks crude",
                "stories": 3, "story_ids": ["sf88e7b52f687150", "scba95f8ac8ce3cd", "…"]}]
}
```

One row per effect, merged across the window's stories, most stories first.
They are Wealthink's reasoning, not article claims.

## `get_pool_story_timeline`: how a development unfolded

```json
{
  "story_id": "s55ea6a5c8c05ec1",
  "timeline": [
    {"story_id": "s5d42639f5c79656", "title": "IRDAI moves to curb commissions on insurance policies",
     "first_seen": "2026-10-07T15:23:20+05:30", "state": "developing", "link": "follows",
     "companies": {"HDFC Bank Ltd.": "hurts", "…": "…"}, "driver_moves": {}, "link_strength": "likely"},
    {"story_id": "s55ea6a5c8c05ec1", "link": "this", "…": "…"}
  ],
  "related": [{"story_id": "s6f9821c12953301", "link": "related", "…": "…"}]
}
```

Oldest first, up to 10 steps each way, each story once. `link` says how a step
joins: `follows` (an earlier cause), `followed_by` (a later consequence),
`related` (similar, not causal); `link_strength` says how closely it links to
the step before it. A `note` says when linked stories older than
the plan's history were left out. It doesn't count as a story open.

## Fixed filter values

`sector`, `driver`, `event_type` and `category` take these exact values (each
tool's parameters list them too). Anything else is refused with the allowed
list, so never pass a fragment.

- **Sectors**: Automobile and Auto Components · Capital Goods · Chemicals ·
  Construction · Construction Materials · Consumer Durables · Consumer
  Services · Fast Moving Consumer Goods · Financial Services · Healthcare ·
  Information Technology · Media Entertainment & Publication · Metals &
  Mining · Oil Gas & Consumable Fuels · Power · Realty · Services ·
  Telecommunication · Textiles
- **Drivers**: Interest rates and RBI policy · The rupee · Crude oil ·
  Natural gas and LNG · Coal · Global metal prices · Gold and silver · Farm
  output and the monsoon · Trade barriers and tariffs · Government capital
  spending
- **Event types**: Results · Order win · Capex · Deal · Fund raising ·
  Brokerage rating · Credit rating · Management change · Legal / penalty ·
  Policy decision · Pricing · Data release
- **Categories**: Company · Policy · Regulation · Macro · Commodity · Market
- **Windows**: 24h · 72h · 7d · 30d · 90d · 1y, as far as the plan reaches
  (`get_my_usage` → `windows`)
