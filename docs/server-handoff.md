# Server handoff: MCP changes for the Wealthink agent plugin

**From:** plugin team · **To:** server team (`wealthink-server/mcp`) · **Date:** 2026-10-13
**Prod endpoint:** `https://api.thewealthink.com/mcp` · **Dev:** `https://dev-api.thewealthink.com/mcp`

## Context

- **What this plugin is.** This repo's plugin is for **Free and Starter**
  users, who sign up on their own. It teaches their AI agent to use Wealthink
  as a **coherence engine**: recent Indian market news as connected stories,
  links, knock-ons and labels.
- **Pro and above** use the desktop app, which ships its own built-in plugin
  for the full toolset. That plugin lives in the desktop repo, not here.
- **How tools reach users.** Every plan uses the same `/mcp` endpoint. A
  reverse proxy reads the plan from the user's access token and exposes only
  that plan's tools. Nothing is removed from the server.
- **Launch waits for the proxy**, so Free and Starter users only ever see their
  own tools.

**Onboarding we're building toward:**

1. The user signs up on the website.
2. The website shows one prompt to paste into their agent.
3. The agent installs the plugin and connects the MCP server.
4. The user signs in with OAuth once.
5. The agent starts answering.

Launch clients are **Claude Code, Claude.ai / Claude Desktop and ChatGPT**.

**Why the server side matters:** an agent picks tools from three things only:
the server's `instructions`, each tool's description and each tool's schema.
ChatGPT can't load our skills, so for ChatGPT users those three are the whole
product.

## Plans

| | Free | Starter | Pro and above |
|---|---|---|---|
| Served by | This plugin | This plugin | Desktop app's built-in plugin |
| History windows | 24 h, 72 h | 24 h, 72 h, 7 d, 30 d | Desktop |
| Thesis Check | No | Yes, 40 per week | Desktop |
| Daily story opens | **[server: fill in]** | **[server: fill in]** | — |
| Tools | Table A | Table A + Table B | Everything |

Please fill in the blanks. The skills and tool descriptions will quote these
numbers, so they must match what the meters enforce.

## Summary

| # | Change | Priority | Launch blocker |
|---|---|---|---|
| 0 | Stop returning article text in any tool | P0 | No |
| 1 | Plan-aware proxy: tool lists, instructions and upgrades | P0 | **Yes** |
| 2 | News `instructions` for Free and Starter | P0 | **Yes** |
| 3 | Fix six tool descriptions | P0 | **Yes** |
| 4 | Serve headlines for every linked story | P0 | No |
| 5 | One error contract for 402 and 429 | P0 | **Yes** |
| 6 | A plan tool for the agent | P0 | **Yes** |
| 7 | Confirm OAuth works for the three launch clients | P0 | **Yes** |
| 8 | Log MCP tool calls to PostHog | P1 | No |
| 9 | Lower the `limit` default from 200 | P1 | No |
| 10 | Decide whether articles should bypass story-open metering | P1 | No |
| 11 | Output schemas and annotations | P1 | No |
| 12 | Fix two data gaps | P2 | No |
| 13 | Ship the `/news/*` tools to prod | P2 | No |
| D1–D9 | Fixes from the dev test on 2026-10-13 (D5, D6, D7, D8 block launch) | P0 | **D5, D6, D7, D8** |

## P0

### 0. Stop returning article text in any tool

Wealthink links to publishers' articles; it must not republish them. Keeping
article text out of every tool response keeps us legally safe and inside the
search-engine category. An agent that needs the exact wording opens the article
at its URL with its own browser or fetch tool.

**Allowed:** headline, publisher, URL, published time, a short description or
Exa summary (Exa's terms allow this), and everything Wealthink produces itself
(labels, directions, links, knock-on reasons, scores).

**Not allowed:** any span of the article body, including "excerpts" and
"evidence sentences" copied from the article.

| Where article text leaks today | Change |
|---|---|
| `get_pool_article` → `excerpt` (verbatim; `excerpt_is_publisher_summary: false` means it is the article's own sentence) | Replace with the description or Exa summary; drop `excerpt_is_publisher_summary` |
| `run_pool_thesis_check`, `get_pool_thesis_check` → each story's "verbatim evidence sentence" | Return a Wealthink-written reason ("why this challenges / supports the statement") plus the article URL |
| `/news/*` on dev: `list_news_stories`, `get_news_story`, `list_latest_news` rows carry a verbatim `excerpt` | Same as `get_pool_article`, before these ship to prod |
| `get_pool_article_trace`, `get_pool_thesis_check_trace`, `list_pool_dropped_headlines` | Pipeline debug views that may include fetched article content. Not in Table A or B. Audit them for Pro |

Update each tool's description to match: "a short description, not the
article's text; open `url` for the article".

### 1. Plan-aware proxy

**Tool lists by plan.** Build each plan's list from an **allow-list**, not the
deny-list in `route_config.py` ("New API endpoints are exposed by default").
With a deny-list, every new FastAPI route would appear on Free and Starter.

**Table A: Free and Starter**

| Tool | Route | Notes |
|---|---|---|
| `get_pool_pulse` | `GET /events/pool/pulse` | Always the last 24 h |
| `list_pool_stories` | `GET /events/pool/stories` | `from`/`to` up to the plan's window |
| `list_pool_company_stories` | `GET /events/pool/company-stories` | Up to the plan's window |
| `get_pool_story` | `GET /events/pool/stories/{id}` | Uses a story open |
| `get_pool_article` | `GET /events/pool/articles/{id}` | After #0 |
| `list_pool_tags` | `GET /events/pool/tags` | |
| `get_my_usage` | `GET /usage` | Meters, used, limits, reset times |
| The plan tool from #6 | | Plan, windows, features, upgrade option |

**Table B: Starter only**

| Tool | Route |
|---|---|
| `run_pool_thesis_check` | `POST /events/pool/thesis` |
| `list_pool_thesis_checks` | `GET /events/pool/checks` |
| `get_pool_thesis_check` | `GET /events/pool/checks/{id}` |

Pro and above get every tool, as the desktop app does today. Tool names stay
as they are; the desktop plugin and this plugin share them.

**Requirements:**

1. **Filter `tools/list` itself, not only the calls.** A tool the plan doesn't
   include must not appear in the list. If a client calls it anyway (cached
   list), return a 402 (see #5).
2. **Upgrades take effect without a new install.** If the proxy reads the plan
   only from the access token, an upgrade changes nothing until the token
   refreshes, and the client keeps the tool list it loaded. Please:
   - read the plan live (or cache it for at most a minute or so) rather than
     only from the token;
   - send `notifications/tools/list_changed` when the plan changes during a
     session.

   Tell us what the access token lifetime is, and whether the plan claim
   refreshes with it.
3. **`instructions` by plan.** Free and Starter get the news text in #2. Pro
   keeps the current desktop text. Today's text sends every agent to
   `list_module_options`, which Free and Starter won't have.
4. **Preload in Claude Code.** Set `_meta["anthropic/alwaysLoad"]: true` on
   every Table A and Table B tool, so Claude Code loads them upfront instead of
   searching for them. Other clients ignore the key.
5. **Same URL, OAuth and scopes as today.** Users connect once.

### 2. News `instructions` for Free and Starter

MCP servers send `instructions` to every agent on connect. For Free and
Starter, send this (Starter adds the last paragraph):

```
Wealthink is a coherence engine for Indian markets: it links recent financial
news into stories, each labelled with sectors, macro drivers, categories and
companies (with the direction the news moved them), and connected to its causes
(follows from), consequences (followed by), similar stories (related) and
knock-on effects on other industries.

Use get_pool_pulse for the last 24 h by sector; list_pool_stories to find
stories (filter by sector / driver / company fragment; all=true for 72 h;
from/to for longer ranges if the plan allows); list_pool_company_stories for one
company; get_pool_story to open one story with all its links (uses one of the
user's daily story opens, so open only what you will cite); get_pool_article
for an article's source, description and link (open the link for its text);
list_pool_tags for the exact labels. get_my_usage and <plan tool> show the
user's plan and what is left.

Knock-ons are Wealthink's reasoning, not article claims. A company direction is
business impact, not a price call. Give no buy/sell advice. A 402 means the plan
doesn't include that window or tool; a 429 means a limit is used up until
resets_at. Relay either once; don't retry.

[Starter only] run_pool_thesis_check can use one of the user's weekly checks:
run it only when the user asks for a thesis check, and confirm the statement
first.
```

### 3. Fix six tool descriptions

These came from a test on prod (12 Oct). A fresh agent answered a real
portfolio question using only the tools.

| Tool | Problem | Suggested text |
|---|---|---|
| `run_pool_thesis_check` | Says **"Uses no check credit."** Thesis Check is Starter-only with a weekly limit, so agents treat it as free and may run it unasked | Lead with: "Uses one of the user's weekly thesis checks. Run only when the user asks for a thesis check, after confirming the statement with them." Keep the rest |
| `list_pool_company_stories` | Says "Every story in the **72 h** window". On 12 Oct it returned stories from 7–10 days back, probably the account's 7-day window. Agents then label week-old news as "last 72 h" | "Every story that tags the company, newest first, as far back as the user's plan allows (72 h on Free; 30 days on Starter)." Also return `from` / `as_of`, as `list_pool_stories` does |
| `list_pool_stories` (`from`, `to`, `all`) | Says nothing about plan windows, so agents don't know 7 and 30 days exist, or why a range fails | On `from`: "Free reaches back 72 h; Starter 30 days. A longer range returns 402." |
| `list_pool_stories`, `list_pool_company_stories`, `list_pool_thesis_checks` (`limit`) | `limit` is 1–200 with a default of 200, but each response holds about 10–13 rows. Asking for 20, 25 or 30 returned 10, 13 and 13 | "About 12 rows fit per response; use `next_cursor` for more." See #9 |
| `get_pool_story` | Doesn't say a call uses a daily story open, or that knock-ons end at an industry, not a company | "Each call uses one of the user's daily story opens; open only stories you will cite. Knock-on links end at an industry part (e.g. 'NBFCs and lenders'), never a company." |
| `get_pool_article` | Describes the response as including "its verbatim excerpt" | After #0: "A short description of the article, not its text. Open `url` for the article." |

### 4. Serve headlines for every linked story

In `get_pool_story`, most entries in `follows_from`, `followed_by` and
`related_stories` came back as `{"story_id": "...", "headline": null}`,
including the strongest links. In the 7 Oct RBI hike story
(`sf736fecf2040665`), 11 of 12 *follows from*, 8 of 12 *followed by* and 9 of
10 *related* had no headline.

**What Langfuse shows:**

- The production stage that creates links, `9b follow-up links (D5)` in
  `wealthink-events-worker`, compares candidate stories that all have
  headlines and summaries.
- So the headline exists when the link is made, and is lost in the layer that
  serves `get_pool_story`.
- Our guess, not confirmed: the lookup only resolves stories inside the 72 h
  pool.

Without the headline, an agent must spend a story open to learn what a link is,
so it skips the "why did this happen" chain, which is the core of the product.
**Ask:** return the stored headline (and `first_seen`) for every linked id,
whatever its age.

### 5. One error contract for 402 and 429

The quota error is already well shaped:

```json
{
  "status": "error",
  "code": 429,
  "error_code": "PLAN_LIMIT_REACHED",
  "message": "You've used your Starter plan's checks for this week.",
  "details": {
    "limit": "thesis_checks_per_week", "limit_value": 40, "used": 40,
    "resets_at": "<ISO>", "upgrade_plan": "<next plan id or null>",
    "meter": "thesis_checks", "scope": "user", "period": "week"
  },
  "request_id": "…", "timestamp": "…"
}
```

Asks:

- **Use the same shape for 402**, i.e. a window, tool or feature the plan
  doesn't include. Suggested `error_code: "PLAN_REQUIRED"`, with `details`
  naming `feature` (or `window`) and `upgrade_plan`.
- **Return it through MCP as a tool error** (`isError: true`), with this JSON as
  the text, so every client shows it to the agent rather than failing the call.
- **Declare 402 and 429 on the routes.** Today they list only 200 and 422.
- Optional: drop `error` and `detail`, which repeat `message` and cost tokens.

### 6. A plan tool for the agent

The agent needs one cheap call that answers "what can this user do?". It's used
at connect time, after a 402/429, and to notice an upgrade. `get_my_usage`
covers the meters. Please add, or extend it with:

```
plan:        "free" | "starter" | …
windows:     ["24h", "72h"]            (Starter: + "7d", "30d")
features:    {"thesis_check": false}
upgrade:     {"plan": "starter", "url": "<pricing or checkout page>"}
```

It must be a user-level tool (`get_billing_summary` is org-level and Pro-only).

### 7. Confirm OAuth works for the three launch clients

Discovery is in place: dynamic client registration, PKCE (S256), and
`authorization_code` + `refresh_token` grants are all published in
`/.well-known/oauth-authorization-server`. We didn't register test clients on
prod. Please confirm that registration and sign-in succeed for each callback:

| Client | Redirect URI |
|---|---|
| Claude Code | `http://localhost:<random port>/callback` |
| Claude.ai / Claude Desktop | `https://claude.ai/api/mcp/auth_callback` |
| ChatGPT | `https://chatgpt.com/connector_platform_oauth_redirect` |

Verify the exact URIs against each client's current docs; they change. Also
confirm refresh tokens are issued and honoured, so users don't sign in again
every hour.

## P1

### 8. Log MCP tool calls to PostHog

Langfuse traces the news pipeline but not MCP tool calls, so we can't see how
agents use the plugin. From the proxy, send one PostHog event per call:

| Property | Example |
|---|---|
| `tool` | `get_pool_story` |
| `plan` | `free` |
| `client` | MCP `clientInfo.name` (e.g. `claude-code`, `claude-ai`, `chatgpt`) |
| `latency_ms`, `response_bytes` | |
| `status`, `error_code` | `ok`, `PLAN_LIMIT_REACHED` |
| `user_id` | The user's PostHog distinct id |

Also send a `mcp_connected` event at session start, to measure drop-off between
website sign-up and the first tool call.

### 9. Lower the `limit` default from 200

`list_pool_stories`, `list_pool_company_stories` and `list_pool_thesis_checks`
default `limit` to 200, but one response holds about 12 rows. Set the default
(and ideally the max) to what a response actually holds.

### 10. Decide: should articles bypass story-open metering?

`get_pool_story` uses a daily story open. A story's lead article id is the story
id with the `s` swapped for `a` (`sd7d0a67873285e2` → `ad7d0a67873285e2`). If
`get_pool_article` isn't metered, an agent can read the lead article of any
listed story without using an open. Our test agent did this unprompted. If
that's acceptable, nothing to do. If not, meter `get_pool_article` or make
article ids unguessable.

### 11. Output schemas and annotations

- **Output schemas:** the pool tools return no output schema. Response models
  give clients `structuredContent` and tell agents the shape before the first
  call.
- **Annotations:**
  - `run_pool_thesis_check`: `readOnlyHint=False`, `destructiveHint=False`,
    `anthropic/requiresUserInteraction: True` (it spends weekly quota).
  - Other Table A/B tools: `readOnlyHint=True`, `openWorldHint=False`.

## P2

### 12. Fix two data gaps

- `get_pool_pulse`: Realty listed `companies_helped` (Puravankara, Brigade) but
  had no `direct_helped` or `knockon_helped` bucket. The two should agree.
- The Signature Global Q2 bookings story (an exchange filing) had
  `companies: []`, so `list_pool_company_stories(name="Signature")` misses it.

### 13. Ship the `/news/*` tools to prod

These exist on dev only: `get_news_pulse`, `get_news_pulse_graph`,
`list_news_stories`, `get_news_story`, `list_latest_news`,
`search_news_companies`, `get_my_thesis_config`,
`validate_my_thesis_statement`, `list_public_plans`.

- **Before shipping:** say in both families' descriptions how `/news/*` differs
  from `/events/pool/*`. Today an agent can't tell `get_news_story` from
  `get_pool_story`.
- **For Free and Starter:** if both families serve the same stories, add only
  one to Table A.

## Dev test, 2026-10-13

We tested `https://dev-api.thewealthink.com/mcp` (server `Wealthink 3.4.2`) on
a **Starter** account, using our own OAuth client (dynamic registration, PKCE,
localhost callback). Newest dev news was `01 Oct 20:58 IST`.

**Working:**

- The proxy lists exactly Table A + Table B (10 tools, 7.4 KB of schema).
  `get_pool_feed` and every desktop tool are hidden. The thesis tools carry
  `needs:thesis_check`.
- The server declares `tools.listChanged: true`.
- `get_my_usage` returns `plan`, `upgrade_to` and the `thesis_checks` meter
  (40 / week). That covers most of #6.
- Every call took 0.08–0.42 s. Payloads: story 9 KB, list 11 KB, pulse 16 KB,
  article 2 KB.
- **#4 looks fixed on dev:** 39 linked headlines across 7 stories, none null.
- The `run_pool_thesis_check` description now says it uses a weekly check
  (#3, first row).
- Windows count back from the newest news, not from now. Default
  `list_pool_stories` is 24 h, `all=true` 72 h, `list_pool_company_stories`
  7 days, and a 7-day `from`/`to` returns stories on Starter.

### D1. Starter window is 7 days; 30 days is in the next release

A Starter range older than 7 days is refused with *"Your plan shows the last 7
days of stories. Older stories are on Pro."* The plan table above (Starter:
24 h, 72 h, 7 d, 30 d) is the target. **Ask:** ship the 30-day window for
Starter in the next release, and update the refusal text and the
`list_pool_stories` / `list_pool_company_stories` descriptions to match.

### D2. Thesis Check: Starter only, and its window must match Starter's

Thesis Check stays Starter-only (Table B). The `run_pool_thesis_check`
description says it searches *"every story of the last 30 days"*, while a
Starter user can only read 7 days of stories today. **Ask:** make the search
window the Starter window, and say that window in the description (`window_h`
already reports it).

### D3. Article excerpts are still verbatim (under review, see #0)

Status: the server team is checking. Evidence: `get_pool_article` describes
`excerpt` as *"its verbatim excerpt"*. All 14 excerpts we sampled were 71–309
characters, with `excerpt_is_publisher_summary: false`, i.e. sentences taken
from the article. The thesis description also promises *"a verbatim evidence
sentence"*. Both need the #0 rule: headline, description or Exa summary, and
the link.

### D4. Internal pipeline fields in `get_pool_article` (under review)

Status: the server team is checking whether they help the agent. The response
includes `ko_log`, `co_rejected` (rejected companies with probabilities),
`is_results`, `company_specific`, `sector_source`, `flagged` and `copy_of`.
None of the skills use them. If they don't help, drop them: they cost tokens
and expose how stories are scored.

### D5. Return errors as JSON, not as a printed Python dict

**Today** every non-plan error reaches the agent like this
(`isError: true`, one text block):

```
Error calling tool 'list_pool_stories': HTTP error 400: Bad Request - {'status': 'error', 'code': 400, 'error_code': 'HISTORY_OUT_OF_RANGE', 'message': 'Stories go back 30 days at most.', 'details': {'max_days': 30}, 'request_id': 'req_ac7b06b4f626', 'timestamp': '…', 'error': '…', 'detail': '…'}
```

The body is a Python `repr` (single quotes, `None`), so it isn't valid JSON and
an agent can't read `error_code` reliably. Plan refusals go the other way: one
sentence with no code at all, and the upgrade clause repeats itself:

```
Your plan shows the last 7 days of stories. Older stories are on Pro. The Pro plan has more. Tell the user; retrying will not help.
```

**Ask:** in the layer that turns an HTTP error from FastAPI into an MCP tool
error (FastMCP's OpenAPI tool runner, or a middleware around it), return:

- `isError: true`;
- **one text block holding the FastAPI body re-serialised with `json.dumps`**
  (not `str()` of the dict and not prefixed with "Error calling tool…");
- the same object as `structuredContent`, for clients that read it;
- for plan refusals (402 and 429), the same JSON shape as #5, with the friendly
  sentence as `message` and `"retry": false`. Keep the sentence, and say the
  upgrade plan once.

Target, for the refusal above:

```json
{"status":"error","code":402,"error_code":"PLAN_REQUIRED","message":"Your plan shows the last 7 days of stories. Older stories are on Pro.","details":{"window":"30d","plan_window":"7d","upgrade_plan":"pro"},"retry":false,"request_id":"req_…"}
```

And for a non-plan error:

```json
{"status":"error","code":400,"error_code":"HISTORY_OUT_OF_RANGE","message":"Stories go back 30 days at most.","details":{"max_days":30},"request_id":"req_ac7b06b4f626"}
```

Drop `error` and `detail` (they repeat `message`) and `timestamp`. Add a test
that parses the text block of an error result with `json.loads` and reads
`error_code`, for a 400, a 402, a 404, a 422 and a 429.

### D6. `instructions` are still the desktop text for every plan

Dev sends Starter the full desktop `instructions` (modules, templates,
`fetch-raw-datasource-payload`, `list_module_options`), with one added sentence
telling limited plans to ignore it. About 80 % of the text is about tools the
user doesn't have, and ChatGPT users see nothing else. Prompt for whoever picks
this up:

```
In wealthink-server/mcp, the server `instructions` (INSTRUCTIONS in
mcp/wealthink_mcp/server.py) are one string sent to every plan. Make them
plan-aware, the same way PlanToolFilter makes tools/list plan-aware:

1. Keep the current text as the Pro+ (research workspace) instructions.
2. Add a NEWS_INSTRUCTIONS string for plans without the research workspace,
   using the text in docs/server-handoff.md section 2 of the plugin repo
   (Wealthink/wealthink-plugin). Append the "[Starter only]" paragraph only
   when the plan has the thesis_check feature.
3. Choose the string in the initialize response from the caller's plan
   features (same entitlements read and cache as PlanToolFilter; same fallback
   order: stale cache, desktop client_kind → Pro text, else news text without
   the thesis paragraph). No token (stdio/local dev) → Pro text.
4. The news text must not name any tool the plan doesn't list. Add a test that
   every backtick- or snake_case tool name in NEWS_INSTRUCTIONS is in
   LIMITED_TOOLS, and that the Starter paragraph appears only with thesis_check.
5. Tests: Free, Starter, Pro and unreadable-entitlements initialize responses
   each get the expected text.

Don't change tool names or the Pro text. Report the instruction size in bytes
for each plan.
```

### D7. `alwaysLoad` is not set yet (#1, requirement 4)

No tool carries `_meta["anthropic/alwaysLoad"]`. Claude Code therefore defers
all 10 tools behind its tool search, so the agent has to look them up before
the first call and may not find them. With only 7.4 KB of schema for the whole
Free/Starter list, preloading costs little. **Ask:** set it on every Table A
and Table B tool for Free and Starter. Pro can stay deferred (135 KB).

### D8. The OAuth login page has no Google sign-in (launch blocker)

`/api/v1/oauth/authorize` redirects to
`https://dev.thewealthink.com/login?oauth_state=…`. With `oauth_state` set, the
web app renders `OauthLogin`, which is an email and password form only: no
"Continue with Google", no sign-up link. A Google user who types a password
gets *"If you signed up with Google, use Continue with Google"*, pointing to a
button that isn't there. They can only connect if they already have a web
session (the page then skips the form). Prod (`app.thewealthink.com`) ships the
same bundle.

**Ask (web team):** when `oauth_state` is present, show the full login page,
Google included, and sign-up for new users. Carry `oauth_state` through the
Google round trip. After any sign-in, call the OAuth callback with
`oauth_state_id` and redirect to its `redirect_url` instead of `/org`.

### D9. Small fixes

1. **Refusal text repeats itself:** "Older stories are on Pro. The Pro plan has
   more." Say the upgrade once (D5).
2. **`list_pool_company_stories` returns `from` but not `as_of`.**
   `list_pool_stories` returns both. Add `as_of`, so the agent can say how
   fresh the list is.
3. **Say the window anchor.** Windows count back from the newest news
   (`as_of`), not from now. A `from` after the newest story returns 400
   *"a range cannot start after the latest news"*. Say this in the
   `from`/`to` descriptions.
4. **Empty or malformed ids:** `get_pool_article` with `article_id: ""` returns
   a generic 404 `HTTP_ERROR` "Not Found" instead of `ARTICLE_NOT_FOUND`.
   Validate ids (`s…` / `a…`) and return a 422 naming the field.
5. **`get_pool_article` description** still says "verbatim excerpt"
   (follows D3).
6. **Plan tool gaps (#6):** `get_my_usage` has `plan` and `upgrade_to`, but not
   the windows, the features or an upgrade URL. Add `windows`,
   `features.thesis_check` and `upgrade.url`.
7. **Dev data is 12 days old** (`as_of` 01 Oct on 13 Oct). Please keep the dev
   pipeline running, so window and freshness tests mean something.
8. **`story_opens` limit is `null`** in `get_my_usage` for Starter. If story
   opens are unmetered on Starter, say so; otherwise fill in the plan table.

## Decided (no action)

- **Tool names stay as they are.**
- **Knock-ons can contradict across stories.** Different events push an
  industry different ways; the skills tell agents this is expected.
- **SEBI review:** not applicable.
- **Exa summaries** may be passed to users and agents.
- **No connector-directory listings** (Claude, ChatGPT) for now.
- **Testing:** the plugin team tests on its own accounts, switching plans.

## What we need back

1. The blanks in the plan table (daily story opens per plan).
2. The access token lifetime, whether the plan claim refreshes, and how the
   proxy handles a mid-session upgrade (#1).
3. The 402 `error_code` and `details` shape (#5).
4. The name and shape of the plan tool (#6).
5. OAuth confirmed for the three launch clients (#7).
6. Confirmation that no tool returns article text (#0).
7. The cause of the null headlines, and an ETA (#4).
8. The decision on article metering (#10).
9. ~~A date when the proxy is live on dev~~ Live on dev; tested 2026-10-13.
10. The release that gives Starter 30 days, and the thesis window to match
    (D1, D2).
11. Decisions on verbatim excerpts and internal article fields (D3, D4).
12. The error format change and its test (D5).
13. When the OAuth login page gets Google sign-in (D8).
