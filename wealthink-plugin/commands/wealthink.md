---
name: wealthink
description: >
  Do anything on Wealthink in natural language — browse tracked market news, run
  research modules and charts, build and share reports — using the Wealthink MCP
  connector. Describe what you want; the right tools and skills are chosen for you.
---

# Wealthink

Handle this Wealthink request using the Wealthink MCP connector:

> $ARGUMENTS

## How to handle it

1. **Connection check.** If a tool reports the connector isn't authenticated
   ("not connected" / 401), use `getting-started` to have the user connect
   Wealthink via OAuth (`/mcp` → **wealthink** → **Authenticate**) before
   retrying. Never ask for an email or password.
2. **Classify the intent** and route to the matching skill:
   - *What's happening / news on X* → `market-news` (`list_events`)
   - *Plan / set up new research, "what should I build?"* → `plan-research`
   - *"Here's our current report/process — replicate it"* → `understand-system`
   - *Run / show me the result of an analysis or chart* → `run-research`
     (`run_module` / `run_quant_chart`)
   - *Create / change an analysis* → `build-qual-module`
   - *Create / change a chart* → `build-quant-chart`
   - *Build / run / fetch a report* → `research-reports` (`run_template`)
   - *Share a report with a client* → `share-report`
   - *Lay out / redesign a report* → `generate-layout`
   - *What do I have / find an ID* → `discover`
3. **Resolve names to IDs** with the `list_*` tools — never guess an ID.
4. **For runs**, prefer the blocking wrappers (`run_module`, `run_quant_chart`,
   `run_template`) so you return a finished result. If one times out, use the
   returned `run_id` with `get_qual_run_status` / `get_template_run_status`.
5. **Scale & isolate when needed.** For "do N of these" (build/run several
   modules), approve the specs with the user, then fan out one worker agent per
   item (`module-builder` to build, `run-verify` to run+verify) — agents recommend,
   the user approves outward actions. For any single response that's too big to
   hold/render (a full run, a wide `list_events`, a stitched report), route it
   through an `output-digest` agent.
6. **Present clearly** — an analyst-style summary, charts described in prose, no
   raw JSON dumps.

If the request is ambiguous, ask ONE clarifying question before acting.

## Notes

- Market-news *trackers* are provisioned by Wealthink and aren't created here.
- If a tool returns `plan_required` / 402, relay it plainly ("that needs a Pro
  plan — contact your account manager") instead of failing cryptically.
- Everything is scoped to the user's workspace.
