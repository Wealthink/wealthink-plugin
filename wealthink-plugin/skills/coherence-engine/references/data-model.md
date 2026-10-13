# Wealthink news: payloads and fields

The samples are real responses from the core tools, trimmed (marked `…`).
Timestamps are IST strings like `"07 Oct 17:57 IST"`.

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
  "from": "06 Oct 17:57 IST", "as_of": "07 Oct 17:57 IST",
  "count": 10, "showing": 5,
  "stories": [{
    "story_id": "sf736fecf2040665",
    "headline": "RBI Monetary Policy: Rates raised by 25 bps, stance changed to 'calibrated tightening'",
    "first_seen": "07 Oct 10:02 IST", "last_update": "07 Oct 13:30 IST",
    "state": "developing", "articles": 15,
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
| `count` / `showing` / `next_cursor` | Total matches, rows returned, and the cursor for the next page. Rows are trimmed to a response budget, usually 10–13 rows whatever `limit` says |
| `state` | `new` (first seen), `developing` (still gaining articles), `settled` (coverage stopped) |
| `articles` | Number of articles clustered into the story. More articles means better established |
| `companies` | `"<name> (<direction>)"`, with `", close call"` appended when the evidence is nearly balanced. The direction is business impact, not a price call |
| `effects` | First-order effects: drivers `up` / `down`; industry parts `helps` / `hurts` / `mixed` |
| `knock_ons_shown` | Displayed knock-on links (the full list is in the story) |
| `related_stories` | Count of related + follows-from + followed-by links. 0 means the story is a dead end for threading |

The company list also includes `settled` stories from earlier days, so it gives
a short history.

## `get_pool_story`: one story with every link

```json
{
  "story_id": "sd7d0a67873285e2",
  "headline": "RBI liquidity management: Central bank to use ‘appropriate mix’ of tools to align WACR with repo rate",
  "state": "new", "articles": 1,
  "sectors": ["Financial Services"], "drivers": ["Interest rates and RBI policy"],
  "first_order_effects": {"Interest rates and RBI policy": "up"},
  "articles_list": [{"article_id": "ad7d0a67873285e2", "publisher": "CNBC-TV18",
                     "headline": "…", "published": "07 Oct 13:16 IST", "url": "https://www.cnbctv18.com/…"}],
  "citations (copies, not processed)": [],
  "company_directions": [],
  "knock_on_links": [
    {"from": "Interest rates and RBI policy", "to": "NBFCs and lenders", "to_sector": "Financial Services",
     "direction": "hurts", "order": 2, "shown": true, "link_strength": "likely", "confidence": 0.7,
     "size": "noticeable", "reason": "Higher rates raise NBFCs' cost of funds faster than they can reprice loans",
     "articles_supporting": 1},
    {"from": "Real estate", "to": "Cement", "to_sector": "Construction Materials",
     "direction": "hurts", "order": 3, "shown": false, "link_strength": "possible", "confidence": 0.58,
     "size": "noticeable", "reason": "Housing is the largest source of cement demand", "articles_supporting": 1}
  ],
  "related_stories": [{"story_id": "sf736fecf2040665",
                       "headline": "RBI Monetary Policy: Rates raised by 25 bps, stance changed to 'calibrated tightening'",
                       "strength": 0.67}],
  "follows_from (this story is a consequence or follow-up of)": [
    {"story_id": "s6caf0edb48a8172", "headline": "RBI Shifts Stance, Hikes Repo Rate For First Time Since February 2023 …", "strength": 0.84}],
  "followed_by (later stories that follow from this one)": [
    {"story_id": "s0ecd0274b89a6c8", "headline": "Why Rate cuts off the table? Repo rate raised after 4 yrs …", "strength": 0.68}]
}
```

| Field | Meaning |
|---|---|
| `articles_list` | Processed articles. `article_id` opens with `get_pool_article` |
| `citations (copies, not processed)` | Other outlets' copies. List and link them; never quote them |
| `company_directions` | Net direction per company over the story's articles. It can be empty even for a macro story |
| `first_order_effects` | The drivers or industry parts the news itself moves |
| `knock_on_links` | Chains outward. `order` 2 = one hop and 3 = two hops; follow `from` → `to` to see the chain (rates → real estate → cement). `shown: false` or `confidence` < 0.5 means a weak lead |
| `related_stories` | The closest similar stories. Not causal |
| `follows_from (…)` | Earlier stories this one is a consequence of: the **why**. A linked story's `headline` can be `null`; open it only if the link matters |
| `followed_by (…)` | Later stories that follow from it: the **what next** |

The link keys contain spaces and parentheses. Read them by their prefix:
`follows_from`, `followed_by`.

## `get_pool_article`: evidence

```json
{
  "article_id": "ad7d0a67873285e2", "publisher": "CNBC-TV18",
  "headline": "RBI liquidity management: …", "url": "https://www.cnbctv18.com/…",
  "excerpt": "<a short description of the article>",
  "pills": {"category": ["Regulation", "Macro"], "sector": ["Financial Services"],
            "event_type": ["Policy decision"], "source_type": "Official"},
  "surprise": true,
  "sectors": ["Financial Services"], "drivers": ["rates"],
  "companies": [], "published": "07 Oct 13:16 IST", "story_id": "sd7d0a67873285e2"
}
```

`excerpt` is a short description, not the article's text, and must not be
presented as a quote. Link `url`, and open it with your own web fetch or browser
tool when you need the exact wording. Use `pills.source_type` and `surprise` to
weigh the story. Fields not shown here (`ko_log`, `co_rejected`,
`is_results`, `flagged`) are pipeline internals. Don't present them to users.

## `list_pool_tags`: the vocabulary

It returns `{"result": [{"id": "wt-platform:crude_oil", "label": "Crude oil"}, …], "total": 36}`.
The labels cover three groups:

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
- **Categories**: Company · Macro · Policy · Commodity · Market · Regulation

Pass a distinctive fragment of a label as a `sector=` / `driver=` filter
(e.g. `"Auto"`, `"rupee"`, `"rates"`). Always fetch the live list; it can grow.

## Extended tools (newer servers)

`list_news_stories` / `get_news_story` / `get_news_pulse` return the same
stories in the website's shape. Story rows add `categories`, `event_types`,
`source_type`, `outlet_count`, `surprise` and a short `excerpt` (a description, not article text). Companies
are objects (`isin`, `name`, `arrow`, `p_better`, `p_worse`, `channels`:
demand / costs / pricing / regulation / financing / one_off). Story links are
`related`, `follows` and `followed_by`. Knock-ons are `knockons[]`, which
carry no `confidence` / `shown`. `get_news_pulse_graph` returns `nodes`
(driver / sector / part / company) and `edges` (member / company / knockon,
with direction and strength).
