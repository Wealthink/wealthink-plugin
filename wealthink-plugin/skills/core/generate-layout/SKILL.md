---
name: generate-layout
allowed-tools:
  - mcp__plugin_wealthink_mcp__get_*
  - mcp__plugin_wealthink_mcp__list_*
  - Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/b64.py *)
  - Read
  - Write
  - mcp__plugin_wealthink_mcp__run_template
  - mcp__plugin_wealthink_mcp__update_template
  - Agent(output-digest)
description: >
  Generate the visual layout of a Wealthink report/template as a frontend-rendered
  design — write a self-contained TypeScript/React component, gzip+base64-encode it,
  and save it to the template's custom_layout. Use when the user wants to lay out,
  design, generate a layout for, restyle, or implement a (possibly third-party,
  e.g. UXPilot / Claude-designed) layout for a report. Matches existing branding by
  default. This is the single home for all Wealthink report layout work.
---

# Generate a Report Layout (custom_layout)

A Wealthink report's visual layout is a **self-contained TypeScript/React
component** that the frontend renders against the report's data. You write the
component, **gzip+base64-encode it**, and store it in the template's
**`custom_layout`** field. That is the *only* layout mechanism this skill uses —
there is no grid config here.

```
write Component.tsx ──► gzip+base64-encode ──► update_template(custom_layout=<gz+b64>) ──► frontend renders it
```

- The backend stores **gzip-compressed, then base64-encoded code** in
  `custom_layout` (compressed + encoded to keep the API payload small) — the
  stored value decodes to the gzip magic `H4sI…`. **Always use the bundled
  `b64.py` to encode before saving and decode when reading** — it does the
  gzip+base64 round-trip for you. Do not hand-roll plain base64: the field never
  holds raw or plain-base64 TSX, and a plain-base64 payload won't render.
- The component receives the report payload as a prop and renders **everything
  dynamically from its `result` key** (array | stringified-array | object).
- The exact code contract, mobile rules, and a ready skeleton live in
  **`reference/frontend-layout-format.md`** in this skill folder. Read it before
  writing any component — it is the spec the frontend recognises.

## Step 1 — Inherit the context (don't re-interrogate)

This skill is usually reached **mid-flow** — handed off from `research-reports` or
an orchestrator after a report exists. **Pick up what's already known** from the
conversation: which template, its purpose/audience, the modules and their order,
and any design intent the user already stated. Only ask if something essential is
genuinely missing (e.g. you don't know which template). Confirm the target
`template_id` via `discover` if it wasn't passed.

## Step 2 — Learn the data you're rendering

The component must read real fields, so know the data shape first:

- Find a run: `list_template_reports(template_id=<id>)` — **`template_id` is
  required**, and the response is metadata only (`id, run_id, date, status,
  is_public, public_link`). That's exactly what you need here; don't ask for more.
- **Fetch the shape, not the data.** `get_template_run_status(run_id, data="schema")`
  returns a Draft-7 JSON Schema of `result` instead of the rows themselves. You are
  writing a component against *field names and types* — the schema is the right
  input, and it turns a payload of thousands of OHLCV rows into a short structural
  description.
  - Use `data="both"` if you also want a look at real values (e.g. to size a
    column or check a date format).
  - Only reach for `data="full"` if you genuinely need to reason over the numbers,
    and route it through the `output-digest` agent when you do.
- If no run exists yet, `run_template(template_id)` first.

> `data="schema"` is the single biggest token lever available here. A full stitched
> report has overflowed context outright in the past (500K+ chars); the schema of
> the same payload is a few hundred lines.

## Step 3 — Decide the design source

In priority order:

1. **A design the user handed in** (UXPilot, Claude-designed mockup, an image,
   HTML, or a written spec) → **implement that design** as the component. Match it
   faithfully; don't invent a different one.
2. **No design given → match existing branding.** Pick a reference template that
   already has a `custom_layout`, **decode it**, and read its design language
   (palette, fonts, spacing, header/section structure). Produce a new component in
   that same visual language so the firm's reports look consistent.
3. **No design and no reference with a layout** → generate a clean, sensible
   default that follows the format spec and mobile rules.

### Reading a reference template's branding

> **`custom_layout` is not returned by default.** `list_templates` and
> `get_template_by_id` both omit it unless you pass **`include_layout=true`**.
> Without that flag the decode step below silently gets nothing — you'll conclude
> the template has no layout when it does. This is the one parameter this skill
> cannot work without.

The defaults are lean, so the sequence is cheap:

- **To browse/find a reference template:** `list_templates(q=<name>, page_size=5,
  sort_by="updated_at", sort_order="desc")` — **without** `include_layout`. You are
  only picking a target here; don't pull layouts you won't read.
- **To fetch the one you picked:** `get_template_by_id(id, include_layout=true)`.
  One template, one blob (~13–14 KB), which fits comfortably.
- **Never** combine `include_layout=true` with an unfiltered list — that is the one
  call that still blows context, and it is now entirely avoidable.
- **Decode** the `custom_layout` (gzip+base64) with the bundled script, then read
  the TSX:
  ```bash
  python3 ${CLAUDE_SKILL_DIR}/scripts/b64.py decode <ref.b64>
  ```
  Run it exactly in that form — unquoted, via `${CLAUDE_SKILL_DIR}`. This skill's
  `allowed-tools` pre-approves that precise command shape, so it runs without a
  permission prompt; any other spelling of the same path will prompt.

## Step 4 — Write the component

Follow **`reference/frontend-layout-format.md`** exactly. The non-negotiables:

- `export default function CustomTemplate({ ... }) { … }` — single props object;
  render **only** from its `result` key, handling array / stringified-array /
  object. Mirror the prop name used by existing decoded templates.
- **All styles inline** (`style={{}}`), no external CSS classes.
- **Mobile-first + a scoped reset + the robust viewport hook** — copy the skeleton
  from the reference and adapt it; don't re-derive the hook (the mobile rules are
  strict and easy to get wrong).
- Self-contained: no imports the host won't have; inline any logic.

Write the component to a local `.tsx` file so you can encode it cleanly. **Do not
paste the full component into the chat** — summarise the design (structure,
palette, key sections) for the user instead.

## Step 5 — Encode and save

1. Gzip+base64-encode the component **into a file** (so the blob never has to land
   in chat):
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/b64.py encode Component.tsx > layout.b64
   ```
2. Save it by reading `layout.b64` and passing its contents straight into the tool
   call: `update_template(template_id, custom_layout=<contents of layout.b64>)`.
   **Do not `cat`/print the encoded blob into the chat first** — read it and put it
   directly in the `custom_layout` argument. Send only `custom_layout` — it's a
   partial update; the module list and other fields are untouched as long as you
   don't pass them.

## Step 6 — Verify and hand back

- Read the template back with **`get_template_by_id(template_id,
  include_layout=true)`** and decode its `custom_layout` to confirm the encoded
  code round-trips and is the component you intended. Without `include_layout=true`
  the field comes back absent and the verification is vacuous.
- Return the Wealthink link so the user can open the report and see it rendered.
- If they want changes, edit the `.tsx`, re-encode, re-save.

## Notes

- **Encode (gzip+base64) before saving, decode when reading** — always via
  `b64.py`; the field never holds raw or plain-base64 TSX, and plain base64 won't
  render.
- Don't dump the component or the raw run payload into chat; describe them.
- A layout can't fix a weak report — if a section reads poorly, fix the module
  (`build-qual-module` / `build-quant-chart`) and re-run.
- `plan_required` / 402 → relay plainly. Everything is workspace-scoped — never
  imply cross-org data.
