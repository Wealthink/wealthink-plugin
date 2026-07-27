# Wealthink Plugin — Architecture

> Design reference for the Wealthink Claude plugin. Defines the primitives, the
> rules for choosing between them, the repository layout (core + persona lenses),
> the full skill/agent/hook inventory, per-flow specs, and how the plugin behaves
> alongside other connectors/plugins. Review this before writing or changing any
> `SKILL.md`, agent, hook, or command.

---

## 1. What the plugin is

The **MCP connector** exposes Wealthink as ~50 tools (auto-generated CRUD from
the OpenAPI spec, plus 4 hand-written run/stream wrappers). **This plugin is the
knowledge layer**: it tells Claude *which* tools to use for a real research task,
*in what order*, with what guardrails, and how to present the result. The
connector provides tools; the plugin provides judgement.

---

## 2. Target harnesses

**This plugin targets Claude Cowork and Claude Code — both agentic harnesses.**
Plain Claude chat is explicitly **out of scope**: Wealthink MCP responses
(`list_events`, full run outputs, stitched reports) are routinely too large for
the chat UI, which errors out. We assume a harness that can spawn subagents and
isolate large tool output.

This raises agents from "Code-only accelerator" to **first-class on both
targets**, and adds a second reason to use them beyond parallelism (see
constraint 4).

**Third-party MCP clients are a third tier.** Cursor, VS Code, Codex, OpenCode
and ChatGPT can all connect to the Wealthink MCP server and use its ~50 tools,
but they get **none of this plugin** — no skills, no agents, no hooks. The
customer-facing docs must say so plainly (`docs/connect.md`), and anything we
want to hold for *every* client has to live on the server, not here. That is the
single most important boundary in this document: **the plugin is Claude-surface
leverage; the server is the universal contract.**

## 3. Primitives and their hard constraints

| Primitive | Runs on | Can talk to user? | Parallel? | Use for |
|---|---|---|---|---|
| **Skill** | Cowork · Code | ✅ yes (main thread) | no | The playbook for a coherent workflow, **including all user interaction** |
| **Agent** (subagent) | Cowork · Code | ❌ **no** — runs autonomously, returns one result | ✅ yes | Self-contained no-questions work fanned out in parallel; **and digesting large/noisy MCP output** |
| **Hook** | **Code** (Cowork: limited/unconfirmed) | ❌ no — deterministic shell on a lifecycle event | n/a | **Deterministic backstop** for guardrails that also live in a skill |
| **Command** | **Code** (Cowork: limited) | ✅ (it's a prompt) | no | Natural-language entry points |

Four consequences drive every decision below:

1. **Subagents cannot ask the user anything mid-flow.** Any step like "ask if
   this is what you intended" must live on the **main thread** (a skill), never
   inside an agent. Give an agent a *complete, approved* task; it returns a
   result.
2. **Hooks are not a way to ask questions.** A hook can *block/gate* a tool call
   or inject context — it can't run a conversation. The valuable hooks here are
   **confirmation gates on irreversible/outward actions** and **sign-in checks**.
3. **Hooks/commands are Code-primary, so a hook is a backstop — never the only
   line of defense.** Every guardrail (confirm-before-publish, confirm-before-
   archive, sign-in check) must be written as an instruction **in the skill** so
   it holds in Cowork too; the Code hook then *enforces* it deterministically.
   If the only thing stopping an accidental public link is a hook, it fails the
   moment the hook doesn't run.
4. **Large MCP payloads belong in a subagent, not the main context.** A run
   output, a full `list_events`, or a stitched report can blow past what's
   useful to hold (and what the UI can render). Spawn an agent to *consume* the
   big payload and return a tight digest. This is context isolation, independent
   of parallelism, and it directly addresses the size problem that rules out
   plain chat. Applies on **both** Cowork and Code.

### The governing rule (skill-first, agents for scale + isolation)

> **Skills own every workflow and all user interaction. Agents do the autonomous,
> parallel, or large-output work the main thread shouldn't hold. Hooks
> deterministically enforce guardrails that are also written into the skills.**
>
> A safety behavior must never live *only* in a hook (Code-only) — its rule lives
> in the skill; the hook enforces it. A single MCP tool call (e.g. "list modules")
> is **not** a skill — it's a step inside one.

### The verify-one-then-fan-out pattern (the core orchestration shape)

For any "do N of these in parallel" flow (build N modules, run+verify N modules).

> **Approval is not verification.** An earlier revision of this document called
> this *approve-then-fan-out* and fanned out as soon as the user approved the
> specs. That is wrong, and it was expensive: approval proves the user wants the
> module, only a passing run proves the spec is *correct*. Sibling modules share
> their classification and precision rules, so fanning out on unverified specs
> pushes one wrong assumption into all N — and every later correction costs N
> edits, N re-runs and N verifications. **Build one, verify it with the user, then
> clone.** The extra round-trip is one run; the alternative is paying every
> mistake N times.

```
Main thread (skill)              Agents                        Main thread (skill)
─────────────────────            ──────────────────            ───────────────────
gather intent / discover
inspect ONE real payload
  → derive field/precision/
    classification rules
match + propose specs
ASK USER → approve specs
BUILD ONE + RUN IT
ASK USER → is this right?   ◄─── the checkpoint the flow exists for
                                 (fix the spec here, once, not N times)
                           ──►   spawn 1 agent per REMAINING item
                                 (autonomous: do work,
                                  return result, NO questions)
                           ◄──   results returned
review results WITH user
  → anything wrong goes to module-fixer WITH an acceptance spec,
    never back into module-builder
ASK USER → approve outward action (publish / make public)
execute outward action (gated by a hook in Code)
```

Both Cowork and Code can fan out, so this is the default. If a harness can't
spawn subagents, the same skill walks the remaining items **sequentially** inline
after the checkpoint — identical tools, identical approvals, just no parallelism.
The skill is authoritative; the agent is the scale path.

**Build and repair are different jobs.** `module-builder` creates one module and
stops; `module-fixer` repairs one existing module against a **written acceptance
spec**, within a five-cycle budget, and returns the specific unmet assertion when
it can't. Reusing the builder as a repair loop is a real failure mode with a
measured cost — it produced 66–80-turn agents and 8.25 edits per module against a
contract that allowed one. Two things prevent it: the builder has no `update_*`
tools and the fixer has no `create_*` tools, so neither can drift into the other's
job, and every worker carries a `maxTurns` cap so a runaway dies regardless of what
its prose says. **A budget written only in prose is not a budget** — the builder's
prose already said "test-run it once".

---

## 4. Repository layout & layering (core + lenses)

The platform serves many financial personas — private equity, VC, public markets,
fund managers, research analysts. Their **mechanics are identical** ("run a
module", "build a template", "stitch a report", "share a link"); only their
**framing** differs (vocabulary, default modules/cadence, output shape). So this
is **one plugin split into two layers**, not a plugin per persona.

**Discovery constraint (confirmed against the plugin spec).** Claude Code scans
`skills/` and `agents/` **only one level deep by default** —
`skills/<name>/SKILL.md` and `agents/<name>.md`. It is **not recursive**, so
`skills/core/discover/SKILL.md` is *not* found automatically. To group into
`core/` and `lenses/` subfolders you **register the roots in `plugin.json`**. The
invocation name comes from each file's frontmatter `name:` (the folder path is
ignored), so the namespace stays **flat** and grouping is purely organizational —
moving today's flat skills into `core/` changes **no invocation names**
(`wealthink:discover` stays `wealthink:discover`).

```
wealthink-plugin/
  .claude-plugin/plugin.json     # registers the skill roots
  .mcp.json                      # the bundled connector (server key: mcp)
  skills/
    core/                        # infra / mechanics — persona-agnostic
      getting-started/  discover/  market-news/
      build-qual-module/  build-quant-chart/  run-research/
      research-reports/  share-report/  generate-layout/
      plan-research/  understand-system/
    lenses/                      # persona adapters — additive, thin
      private-equity/  public-markets/  venture/  fund-manager/
  agents/                        # flat — default discovery, no manifest key
    module-builder.md  module-fixer.md  run-verify.md            # workers
    output-digest.md                                            # digest
    wealthink-researcher.md  wealthink-report-builder.md        # orchestrators
    pe-research.md  public-markets-research.md                  # lens orchestrators
  hooks/                         # root — single, universal set (+ tests/)
  commands/                      # root — single, universal set
  ARCHITECTURE.md  README.md
```

```json
// .claude-plugin/plugin.json
{
  "name": "wealthink",
  "version": "0.1.0",
  "mcpServers": "./.mcp.json",
  "skills": ["./skills/core/", "./skills/lenses/"]
}
```

Three manifest behaviours to respect:
- **`skills` *adds* to the default** — the top-level `skills/` is always scanned,
  so keep **nothing directly in `skills/`** (only `core/` and `lenses/`), or you
  get phantom scans.
- **`agents` *replaces* the default**, so we deliberately **don't declare it**.
  The agents live flat in `agents/` and are found by default discovery. The
  core/lens split for agents is conceptual (see the inventory below), not a
  directory split — nesting them would require the manifest key and buy nothing,
  since agent invocation names come from frontmatter either way.
- **`hooks` and `commands` are likewise undeclared** — `hooks/hooks.json` and
  `commands/*.md` are picked up by convention.

**Bundled-connector naming.** The plugin is named `wealthink` and the server key
in `.mcp.json` is `mcp`, so tools are callable as
`mcp__plugin_wealthink_mcp__<tool>` and the server registers as
`plugin:wealthink:mcp`. Every hook matcher, every skill `allowed-tools` entry,
and every "how do I connect?" instruction has to agree with those two strings —
renaming either without sweeping the prose is how the connect flow silently
starts pointing at a menu entry that doesn't exist.

### The layering contract (the rule that keeps it from rotting)

> **Lenses depend on core. Core never references a lens.**

- **Core** = self-contained, persona-agnostic mechanics. A core skill/agent never
  names PE/VC/equities. Core is the **only** place that owns how to build a
  module, run a template, share a link. The worker agents (`module-builder`, `module-fixer`,
  `run-verify`, `output-digest`) are core and **never forked per persona**.
- **A lens is a thin adapter**, not a re-implementation. It may contain *only*:
  vocabulary mapping (persona terms → Wealthink artifacts), default parameters
  (tags, cadence, output shape), starter templates, and example phrasings — and
  it **ends by handing off to a core skill**. The moment a lens invents its own
  MCP call sequence, that logic belongs in core instead.
- **Lens agents** (optional) are persona-flavoured *orchestrators*: they set voice
  and priorities and call core skills/agents. They never hold mechanics.

**Routing follows the layers.** Write **core descriptions in mechanical language**
("build a qualitative module") and **lens descriptions in persona language** ("set
up portfolio-company monitoring", "build my LP quarterly pack"). The model loads
core on mechanical intent and a lens on persona intent; `getting-started` can
capture the user's role once to bias selection.

**Adding a persona is additive and isolated:** drop a folder under
`skills/lenses/` (+ optional `agents/lenses/` orchestrator), bump the minor
version — and **never touch core.** That isolation is the entire point of the
split; the dependency rule guarantees it.

---

## 5. Inventory

### Core skills (mechanics — the `skills/core/` layer, persona-agnostic)

| Skill | Status | Purpose |
|---|---|---|
| `getting-started` | exists | Connect (OAuth), confirm the connection, see what's set up |
| `discover` | exists | **Shared sub-step** — find resources & IDs (`list_*`). Used by nearly every flow |
| `market-news` | exists | Browse/filter tracked events |
| `plan-research` | **new (UC3)** | Plan a research report: intent → data-source gap analysis → proposed build plan → handoff |
| `understand-system` | **new (UC4)** | Parse a customer's existing research system → map to Wealthink artifacts → handoff to plan |
| `build-qual-module` | exists | Create/refine/retire a qualitative module (UC1 orchestration) |
| `build-quant-chart` | exists | Create/refine a quant chart module (UC1 orchestration) |
| `run-research` | exists | Run a single module/chart and present it (UC2 single-run) |
| `research-reports` | exists | Build/run/fetch report templates |
| `share-report` | exists | Publish/revoke a report run to a client link (UC5) |
| `generate-layout` | exists | Generate the report's visual layout as a base64-encoded TSX `custom_layout`, matching branding (UC6) |

### Lens skills (persona adapters — the `skills/lenses/` layer, additive)

Thin adapters: vocabulary map + default params (tags, cadence, output shape) +
starter templates, each **ending in a handoff to a core skill**. **Never
re-implement mechanics.** Scaffold one per persona as demand appears:

| Lens skill | Status | Maps persona language → core |
|---|---|---|
| `public-markets` | **built out** — the reference lens | coverage, earnings, sector rotation → `build-*` / `run-research` |
| `private-equity` | scaffold | portfolio monitoring, deal screens, LP packs → `build-*` / `research-reports` |
| `venture` | scaffold | pipeline, thesis tracking, portfolio updates → `build-*` / `research-reports` |
| `fund-manager` | scaffold | allocation, risk, mandate reporting → `research-reports` / `share-report` |

`public-markets` is the worked example — copy its shape when filling out the
others. The three scaffolds are currently ~85% the same document with the nouns
swapped; that is fine while they're scaffolds, but each one earns its keep only
when it carries defaults a real desk of that kind would recognise.

### Agents (first-class on both targets — autonomous, ask nothing, return a result)

Two jobs: **fan-out** (parallel autonomous work) and **digest** (consume a large
MCP payload so it never hits the main context / UI). The worker + digest agents
are **core (`agents/core/`) and never forked per persona**; persona-flavoured
*orchestrators* live in `agents/lenses/` and only set voice/priorities while
calling core skills and agents.

| Agent | Layer | Job | Input → Output |
|---|---|---|---|
| `module-builder` | core worker | fan-out | One **approved** module spec → creates it + test-runs once → returns summary. Creates only; never repairs. `maxTurns: 15` |
| `module-fixer` | core worker | repair | One **existing** module + a **written acceptance spec** → up to 5 edit→run cycles → `fixed` or `blocked` with the exact unmet assertion. Repairs only; never creates. `maxTurns: 20` |
| `run-verify` | core worker | fan-out | One module ID → runs (MCP poll wrapper) → verifies output → returns verdict + best `run_id`. **Recommends, never publishes.** |
| `output-digest` | core worker | digest | A large run output / `list_events` / stitched report → returns a tight, structured summary. Used by any flow whose tool response is too big to hold. Runs on a cheap fast model — it exists to absorb bulk |
| `wealthink-researcher` | orchestrator | orchestrator | End-to-end ad-hoc research |
| `wealthink-report-builder` | orchestrator | orchestrator | End-to-end report build/run/layout/share |
| `public-markets-research` | lens orchestrator | orchestrator | The above in an equity-desk voice; sets priorities only, holds no mechanics |
| `pe-research` | lens orchestrator | orchestrator | The above in a PE voice; sets priorities only, holds no mechanics |

**Every agent declares a `tools:` allowlist.** No agent has
`set_*_visibility`, `archive_*` or `delete_*` — so "recommends, never publishes"
is mechanical, not just prose. Outward and destructive actions stay on the main
thread with the user. When you add an agent, give it the narrowest tool list that
lets it finish its job.

### Hooks (Code-enforced backstops — every rule here is *also* a skill instruction)

| Hook | Event | Purpose |
|---|---|---|
| connection check | SessionStart (`startup\|resume`) | If not authenticated, remind the user to connect Wealthink via OAuth before any Wealthink call |
| publish gate | PreToolUse on `set_*_visibility` | Force explicit confirmation before minting a public link. **Allows only a positively identified revoke; asks for everything else** — an unreadable payload must never read as "safe" |
| removal gate | PreToolUse on `archive_*` and `delete_*` | Confirm before archiving (soft) or deleting (hard, `delete_qual_data_source`) a resource |

> These enforce in Code what the skills already require. In Cowork, and in any
> client where Wealthink was configured by hand rather than installed as a plugin,
> the hook does not run — the skill instruction is the guarantee. Never make a
> guardrail depend on the hook alone.
>
> **The matchers only fire for the bundled connector.** They are written against
> `mcp__plugin_wealthink_mcp__*`; a hand-configured server yields
> `mcp__<their key>__*` and matches nothing. That is a structural ceiling on what
> hooks can protect, and it is why the durable cross-client guardrail belongs on
> the MCP server itself: tool annotations and per-tool approval metadata reach
> every client, a hook matcher reaches one.
>
> `hooks/tests/test_gates.py` pins the gate decisions, including the
> masked-publish case that an earlier substring-matching implementation got wrong.

### Commands (Code entry points; Cowork uses the skills directly)

`/wealthink:wealthink <request>` (universal router) and
`/wealthink:wealthink-status <run_id>` (status check) — exist; keep.

---

## 6. Per-flow specs

Legend: **[skill]** main-thread playbook · **[step]** single MCP call inside a
skill · **[ask]** main-thread user question · **[agent]** autonomous fan-out or
digest · **[hook]** Code-enforced backstop (rule also in the skill).

### UC1 — Create / update section modules  *(originally "Agent, parallel")*

Reclassified: **interactive orchestration skill + parallel `module-builder`
fan-out** (verify-one-then-fan-out). Not a single agent — it is full of approvals.

1. Search/filter similar modules — **[step]** `discover` (`list_*_modules`)
2. Check for a match — inline reasoning (no agent)
3. If match: reuse vs update? — **[ask]**
4. Test-run the candidate — **[step]** `run-research`
5. Is this what you intended? — **[ask]**
6. Assemble the approved spec(s) for all requested modules — **[skill]** `build-qual-module` / `build-quant-chart`
7. **Build one + verify with the user** — **[ask]**. Fix the spec here, once.
8. **Fan out:** one **[agent]** `module-builder` per *remaining* module → create + test-run + return summary. Anything wrong goes to **[agent]** `module-fixer` with an acceptance spec. Sequential fallback if the harness can't fan out.
8. Run & publish now? — **[ask]** → hand off to UC2

### UC2 — Run & publish module outputs  *(originally "Agent, parallel")*

Reclassified: **parallel `run-verify` agent** for the autonomous run+verify core;
**publish stays on the main thread, gated.** "Keep polling" is **not** a skill —
it's the MCP `run_module` blocking wrapper.

1. Search/filter target modules — **[step]** `discover`
2. **Fan out:** one **[agent]** `run-verify` per module → `run_module`/`run_quant_chart` (poll wrapper) → verify output → return verdict + best `run_id`
3. Review verdicts WITH user; pick run_ids to publish — **[ask]**
4. Publish chosen run_id — **[skill]** `share-report`, **[hook]** publish gate

> The agent **recommends**; it never publishes. Publishing is outward + irreversible.
> `run-verify` is also a **digest** agent: the large run output dies inside it and
> only the compact verdict + `run_id` reaches the main context. If a user later
> wants the full output rendered, use `output-digest` on demand.

### UC3 — Plan a research report  *(originally "Skill")* ✅

Stays a **skill** (`plan-research`). Advisory, interactive, ends in a handoff.

1. Capture intent — internal vs distribution? audience? update frequency? — **[ask]**
2. Explore current data sources — **[step]** `list_data_sources` / `discover`
3. Gap analysis: which sources solve it, which data points are missing — **[skill]** reasoning
4. Present the build plan: modules to create vs reuse, sources, templates, event tags — **[skill]**
5. Start building? — **[ask]** → handoff to UC1

### UC4 — Understand a customer's research system  *(originally "Skill")* ✅

Stays a **skill** (`understand-system`); optional parser agent for heavy docs.

1. Gather context: report kind, agenda, audience, mobile vs web — **[ask]**
2. Fetch code-writing instructions + payload schema — **[step]**
3. Identify the system (PDF / PPT / code / chat blob) — **[skill]**
4. Parse it — **[skill]**; *optional* **[agent]** parser for a large PDF/PPT/code dump (one isolated task, returns structured extract)
5. Dissect into Wealthink artifacts: data sources, modules, events, research — **[skill]**
6. Present the understanding — **[skill]**
7. Hand off to `plan-research`? — **[ask]**

### UC5 — Send public reports  *(originally "Agent")*  ❌→ **Skill + hook**

Reclassified: short, fully interactive, irreversible — an agent can't ask "is
this the run_id?". This is `share-report` (exists) **+ a publish-gate hook**.

1. Find the template — **[step]** `discover` / `list_templates`
2. Check the output run_id — **[step]** `list_template_reports` / `get_template_run_status`
3. Publish this run_id? — **[ask]**
4. Mark public + return the link — **[skill]** `share-report`, **[hook]** publish gate
5. Offer to revoke afterwards — **[skill]**

### UC6 — Layout generator  *(originally "Skill")* ✅

Stays a **skill** (`generate-layout`). Mechanism: a base64-encoded TSX component
stored in the template's `custom_layout` — **not** a grid config.

1. Inherit context (template, audience, design intent) from the handoff; ask only
   if essential and missing — **[ask]**
2. Learn the data shape from a real run; learn branding from another template's
   decoded `custom_layout` — **[step]** (digest the large `list_templates` payload)
3. Design source: implement a handed-in design (UXPilot / Claude-designed), else
   match existing branding, else a sensible default; get approval — **[ask]**
4. Write the TSX component → base64-encode → `update_template(custom_layout=…)` — **[step]**
5. Return the link to open in Wealthink — **[skill]**

---

## 7. Cross-cutting concerns (missing from the original six flows)

- **Payload shape is a first-class decision, and it comes before digestion.** The
  connector strips its three heavy fields by default and returns them only on
  request — `include_layout=true` for a template's `custom_layout`,
  `include_code=true` for a quant module's `ai_code`, and `data="full"` for a run's
  rows (`data="schema"` returns a JSON Schema of `result` instead). The rule for
  every skill: **ask for the shape when you need the shape, and the data only when
  the user is reasoning over the data.** A digest agent is the fallback for when
  you genuinely need the values and they're still too big — not the first move.
  Note this inverts the pre-July guidance, which assumed heavy fields came back by
  default and told skills to page defensively around them.
- **Try before you save.** `test_run_qual` / `test_run_quant` execute a spec
  without persisting it. Validating a draft belongs on the main thread, where the
  user can react to the output; by the time a `module-builder` agent is spawned the
  spec is already approved and its job is to create.
- **Two event feeds.** The org's own (`list_events`) and the platform-curated
  Common Event Pool (`get_pool_feed`), which every member reads with no plan gate.
  They are separate tag namespaces, and a qual module can draw on both. The pool is
  a data source for existing workflows, not a workflow of its own — which is why it
  is folded into `market-news` and `build-qual-module` rather than given a skill.
- **Schedules have side effects now.** `run_frequency` executes. Setting one
  commits the user to recurring runs, so it needs the same confirm-first treatment
  as any other outward action, and `schedule_status` must be read back before
  telling a user their schedule is live.
- **Large-output digestion** — any flow whose tool response is too big to hold
  (run outputs, full `list_events`, stitched reports) routes through a digest
  agent (`output-digest`, or `run-verify` for the run case). This is the
  architectural answer to "the chat UI errors on big responses" and applies on
  both Cowork and Code.
- **Sign-in / session** — every flow needs it. Skill instruction in
  `getting-started`; Code hook enforces it. Never assumed.
- **Confirmation guardrails** on `set_*_visibility` and `archive_*` — written
  into the skills *and* enforced by Code hooks; the questions live on the main
  thread.
- **`market-news`** — an existing capability none of the six flows referenced.
- **`discover` is one reused sub-step**, not re-implemented per flow.
- **Partial-failure & `plan_required` / 402** — surface plainly, continue with
  what the workspace can do. Already in the existing skills; keep.
- **Polling is not a skill** — it's the MCP `run_module`/`run_template` poll
  wrapper (or an SSE stream tool).
- **Tenant scope** — everything is the user's workspace; never imply cross-org.

---

## 8. Coexistence with other connectors & plugins

A client workspace runs Wealthink's connector **alongside others** — email
(Gmail), a marketing/CRM tool, a portfolio/custody connection, and the plugins
those ship. Multiple MCP connectors and plugins coexisting is the **normal case**,
and the layered design is built for it. Nothing breaks by default: tools are
namespaced per connector, skills per plugin, and Wealthink's session
(`~/.wealthink/mcp_config.json`) is isolated from every other connector's auth.
The discipline is four rules:

1. **Namespace discipline.** The real risk is *ambiguous selection*, not
   collision. Wealthink tools/skills must be unmistakably Wealthink-flavoured
   (`run_module`, `set_template_run_visibility`) — never a bare `login` / `search`
   / `share` a mail or CRM connector could also expose. Skills name the exact
   tool they mean.
2. **Connector-aware, never connector-dependent.** **Core skills depend on *only*
   the Wealthink connector** — their one hard dependency; they never assume Gmail
   or a portfolio tool exists. **Cross-connector composition lives in the lens /
   orchestrator layer and is always *defensive*:** detect whether the other
   connector's tools are present, use them if so, degrade gracefully if not
   ("…then, *if a mail connector is available*, offer to email it; otherwise
   return the link"). Never hard-fail because a connector the client didn't
   install is missing.
3. **Scoped guardrails.** Hook matchers target Wealthink tool-name patterns
   *specifically* (`set_*_visibility`, `archive_*`) so they fire only on
   Wealthink calls — never on the marketing tool's "publish campaign" or the
   CRM's "delete contact". Don't rely on any other plugin's hooks; each plugin
   guards its own edges.
4. **Tight descriptions = correct routing.** With many plugins installed the
   model routes by description. Wealthink skills/agents describe themselves around
   *Wealthink* intent (the "stay in lane" sections) so they activate on "run my
   gold SWOT", not on "share this Google Doc" or "email the team". The
   `/wealthink` router classifies-and-delegates within Wealthink, not everything.

**Composition is the upside, and the lens layer is its seam.** The reason a client
wants all these connectors together is the cross-tool flow — *"run my weekly LP
report, pull current AUM from our portfolio connector, and email it to my LPs."*
That spans Wealthink → portfolio → mail → CRM. Core stays pure (it only knows
Wealthink); the **lens/orchestrator layer choreographs across whatever connectors
are present.** Multi-connector environments are where the persona lenses earn
their value.

**Scaling caveat.** More connectors = more tool schemas in the shared context =
more tokens and more chance of mis-selection. Two design choices already absorb
this: **progressive disclosure** (a skill hands the model a short explicit tool
list instead of free-selecting among hundreds) and **digest agents**
(`output-digest` / `run-verify` keep big Wealthink payloads out of a context that
now also holds other vendors' schemas). If tool counts ever climb high enough to
hurt selection, the lever is **tool-filtering/grouping on the MCP side** — a
future knob, not a blocker today.

---

## 9. Build order (proposed)

1. **Restructure into `core/` + `lenses/` and register the roots in
   `plugin.json`** (§4) — `git mv` the existing skills into `skills/core/`, create
   the empty `skills/lenses/` + `agents/lenses/` scaffold, list the roots. No
   invocation-name changes; verify with `claude plugin validate`.
2. **Guardrails as skill instructions first, then Code hooks** — confirm-before-
   publish, confirm-before-archive, sign-in check. The skill text is the
   guarantee; the hooks (publish gate, archive gate, session check) enforce it
   in Code. **Hook matchers must be Wealthink-scoped** (§8).
3. **`output-digest` agent** — the cross-cutting large-payload digester; unblocks
   every other flow that returns big output.
4. **`plan-research` (UC3)** and **`understand-system` (UC4)** core skills — the
   front of the funnel.
5. **`module-builder` + `module-fixer` agents (UC1)** + wire verify-one-then-fan-out into
   `build-qual-module` / `build-quant-chart`.
6. **`run-verify` agent (UC2)** + wire into `run-research` / `share-report`.
7. **Confirm `share-report` (UC5)** and **`generate-layout` (UC6)** match the gated
   flows above.
8. **First lens, end-to-end** — scaffold one persona (e.g. `public-markets`) as
   the template for the rest; confirm it only maps vocabulary/defaults and
   delegates to core, per the §4 layering contract.
9. Update `README.md` (two-layer skills/agents tables) and bump `plugin.json`
   (minor).

Each core skill follows the existing `SKILL.md` shape (frontmatter `name` +
`description`, then the playbook). Each **lens** skill is a thin adapter that ends
in a handoff to a core skill — if you find yourself writing MCP call sequences in
a lens, move them to core. Each agent's system prompt must state explicitly:
*"You run autonomously and cannot ask the user questions — you receive a complete
task and return a result"*, and digest agents must add *"return a compact summary,
never the raw payload."*
