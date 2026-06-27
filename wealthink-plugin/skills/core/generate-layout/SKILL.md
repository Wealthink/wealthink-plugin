---
name: generate-layout
allowed-tools: mcp__plugin_wealthink_wealthink__*
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

- Fetch a real run of the template — `get_template_run_status(run_id)` (find a
  run via `list_template_reports`), or `run_template(template_id)` if none exists.
- Inspect the `result` payload: is it an array of section objects, a stringified
  array, or a single object? Note the field names you'll render.
- **These payloads are big.** `list_template_reports` and a completed run
  routinely run to **hundreds of KB** and will overflow context (in practice this
  has returned 500K+ chars and errored outright). **Always digest the run in a
  subagent** (`output-digest`) and have it return just the `result` schema + a
  couple of sample rows — never pull a full run into the main context.

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

### Reading a reference template's branding (mind the payload size)

`list_templates` returns the **full `custom_layout` blob for every row**, so an
unfiltered list is huge (~70KB per template — 20+ templates overflows context).
Two rules keep this cheap:

- **To browse/find a template:** call `list_templates` with a small page —
  `page_size: 5–10`, sorted `updated_at` desc — plus a name search (`q=…`) so the
  target lands on page 1. Don't page through everything.
- **To fetch one template you already know:** `list_templates(id=<template_id>)`
  returns just that single template (one blob, fits in context) — use this instead
  of listing all and filtering with `jq`. *(Yes, there is a single-template fetch:
  it's the `id` param on `list_templates`.)*
- **Decode** the `custom_layout` (gzip+base64) with the bundled script, then read
  the TSX:
  ```bash
  python3 "${CLAUDE_PLUGIN_ROOT}/skills/core/generate-layout/scripts/b64.py" decode <ref.b64>
  ```

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
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/core/generate-layout/scripts/b64.py" \
     encode Component.tsx > layout.b64
   ```
2. Save it by reading `layout.b64` and passing its contents straight into the tool
   call: `update_template(template_id, custom_layout=<contents of layout.b64>)`.
   **Do not `cat`/print the encoded blob into the chat first** — read it and put it
   directly in the `custom_layout` argument. Send only `custom_layout` — it's a
   partial update; the module list and other fields are untouched as long as you
   don't pass them.

## Step 6 — Verify and hand back

- Read the template back (decode its `custom_layout`) to confirm the encoded code
  round-trips and is the component you intended.
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
