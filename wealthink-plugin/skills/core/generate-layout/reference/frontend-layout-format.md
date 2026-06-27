# Frontend Layout Format — Wealthink `custom_layout`

This is the exact contract the Wealthink frontend recognises and renders. The
`generate-layout` skill writes a component to this spec, base64-encodes it, and
stores it in the template's `custom_layout`. **Follow it precisely.**

## Goal

Generate clean, structured TypeScript/React code that defines all the components
and layout for a report or dashboard, to be rendered for visual consumption by
humans.

## Code-writing instructions

- Design a **single default-exported component** that receives the report payload
  as one props object:
  ```tsx
  export default function CustomTemplate({ testResult }) {
    // read testResult.result dynamically and render the design
  }
  ```
- **All styles must be inline** — React `style={{}}` props. No external CSS
  classes or stylesheets (the one allowed `<style>` block is the scoped reset /
  font `@import` described below).
- **All rendered values must be read dynamically from the props.** Never hard-code
  the sample values — the component must render correctly when the data changes.
- The data of interest is the **`result`** key. It may be:
  - an **array** of section/row objects,
  - a **stringified array** (JSON string), or
  - a single **object**.
  Handle all three cases when reading from it (normalise to an array, see skeleton).
- Keep the component **self-contained**: no imports the host app won't provide
  beyond React; inline any helper logic.

> **Data contract / prop name:** current templates pass the payload as
> `testResult` with a `.result` key. The first instruction example also shows
> `{ data }` — these are historically inconsistent. **Mirror the prop name used by
> the firm's existing decoded `custom_layout` templates** (decode one and check);
> default to `{ testResult }` + `testResult.result` if there's no reference. Either
> way, read everything from `result` dynamically.

## Mobile responsiveness requirements (inline-style components)

Since all styles are inline, media queries aren't available — implement
responsiveness in JS and follow these rules:

1. **Never assume a global CSS reset exists.** The host may not set
   `box-sizing: border-box`. Give the root `className="x-scope"` and inject a
   scoped reset:
   ```
   .x-scope, .x-scope *, .x-scope *::before, .x-scope *::after { box-sizing: border-box; }
   .x-scope { max-width: 100%; overflow-wrap: break-word; }
   .x-scope img, .x-scope svg { max-width: 100%; }
   ```
   If you `@import` fonts, it must be the **first line** of the `<style>` block.
2. **Robust viewport hook.** A hook that only listens to `resize` breaks on
   Android webviews (stale `innerWidth` on first paint). Inside the mount effect:
   (a) measure once immediately, (b) re-measure on `requestAnimationFrame`,
   (c) re-measure on a ~300 ms `setTimeout`, and (d) listen to `resize`,
   `orientationchange`, and `window.visualViewport`'s `resize`. Measure with
   `window.innerWidth || document.documentElement.clientWidth`.
3. **Be mobile-first.** Default the width state to a phone width (~360) when
   `window` is undefined, so SSR/first paint renders the mobile layout and
   enhances upward — never desktop-first.
4. **Grid tracks must never have a fixed min wider than a phone.** Avoid
   `minmax(280px, 1fr)` in auto-fill/auto-fit grids (a ~320 px screen overflows).
   Use `minmax(min(100%, 260px), 1fr)`, or collapse to a single column on mobile.
   Prefer container-driven `auto-fit` over JS breakpoints for tile/card grids.
5. **Don't put `overflow-x: hidden` on an ancestor of a `position: sticky`
   element** — it silently disables the sticky. Fix overflow at its source
   (rules 1 & 4) instead.
6. **Collapse multi-column layouts on mobile.** Two-column "sidebar + content"
   must become a single stacked column below the breakpoint (e.g. ≤ 760 px). Use
   `clamp()` for large display/hero text.
7. **No fixed pixel widths on containers.** Use `width: 100%` / `max-width` with
   `margin: 0 auto`; reduce horizontal padding on mobile.
8. **Charts / SVGs must be fluid:** render with `width="100%"` + a fixed `viewBox`
   (never a fixed pixel width), capped with `max-width: 100%`.

## Starting skeleton (copy and adapt — don't re-derive the hook)

```tsx
import React, { useState, useEffect } from "react";

// Mobile-first viewport hook — robust on Android webviews (rules 2 & 3).
function useViewportWidth() {
  const [width, setWidth] = useState(
    typeof window === "undefined"
      ? 360
      : window.innerWidth || document.documentElement.clientWidth
  );
  useEffect(() => {
    const measure = () =>
      setWidth(window.innerWidth || document.documentElement.clientWidth);
    measure();                                    // (a) immediately
    const raf = requestAnimationFrame(measure);   // (b) next frame
    const t = setTimeout(measure, 300);           // (c) after layout settles
    window.addEventListener("resize", measure);
    window.addEventListener("orientationchange", measure);
    window.visualViewport?.addEventListener("resize", measure);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(t);
      window.removeEventListener("resize", measure);
      window.removeEventListener("orientationchange", measure);
      window.visualViewport?.removeEventListener("resize", measure);
    };
  }, []);
  return width;
}

function asRows(result) {
  // result: array | stringified-array | object
  if (Array.isArray(result)) return result;
  if (typeof result === "string") {
    try {
      const v = JSON.parse(result);
      return Array.isArray(v) ? v : [v];
    } catch {
      return [];
    }
  }
  if (result && typeof result === "object") return [result];
  return [];
}

export default function CustomTemplate({ testResult }) {
  const width = useViewportWidth();
  const isMobile = width <= 760;
  const rows = asRows(testResult?.result);

  return (
    <div
      className="x-scope"
      style={{ width: "100%", maxWidth: 1100, margin: "0 auto", padding: isMobile ? 16 : 32 }}
    >
      <style>{`
        .x-scope, .x-scope *, .x-scope *::before, .x-scope *::after { box-sizing: border-box; }
        .x-scope { max-width: 100%; overflow-wrap: break-word; }
        .x-scope img, .x-scope svg { max-width: 100%; }
      `}</style>

      {/* Header — use clamp() for hero text (rule 6) */}
      <h1 style={{ fontSize: "clamp(20px, 4vw, 34px)", margin: "0 0 16px" }}>
        {testResult?.title ?? "Report"}
      </h1>

      {/* Card grid — collapses to one column on mobile (rules 4 & 6) */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: isMobile
            ? "1fr"
            : "repeat(auto-fit, minmax(min(100%, 260px), 1fr))",
          gap: isMobile ? 12 : 20,
        }}
      >
        {rows.map((row, i) => (
          <section
            key={i}
            style={{ width: "100%", background: "#fff", borderRadius: 12, padding: isMobile ? 14 : 20 }}
          >
            {/* TODO: read fields from `row` dynamically — never hard-code values */}
          </section>
        ))}
      </div>
    </div>
  );
}
```

## Pre-save checklist

- [ ] Single `export default function …({ <prop> })`; renders only from `result`.
- [ ] Handles `result` as array, stringified-array, and object.
- [ ] All styles inline; only the scoped-reset/`@import` `<style>` block is used.
- [ ] Root has `className="x-scope"` + the reset; `@import` (if any) is line 1.
- [ ] Viewport hook does immediate + rAF + 300 ms + resize/orientationchange/visualViewport.
- [ ] Mobile-first default width (~360 when `window` is undefined).
- [ ] No grid `minmax` min wider than a phone; multi-column collapses ≤ 760 px.
- [ ] No fixed container px widths; `width:100%`/`max-width` + `margin:0 auto`.
- [ ] Charts/SVGs use `width="100%"` + `viewBox`, capped `max-width:100%`.
- [ ] No `overflow-x:hidden` ancestor over a sticky element.
