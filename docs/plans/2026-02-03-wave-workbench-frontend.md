# Wave Workbench UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Re-skin the Next.js front page into a developer-themed "Wave Workbench" with monochrome palette, framer-motion wave ribbon, and refined cards without adding new flows.

**Architecture:** Keep existing two-panel layout; inject a top wave ribbon component for CTA/status; use framer-motion for staged entrances and ribbon motion; update global CSS tokens to grayscale + glass. No API changes.

**Tech Stack:** Next.js 16, React 19, framer-motion, CSS (global), TypeScript.

---

### Task 1: Add animation dependency
**Files:**
- Modify: `apps/web/package.json`
- Modify: `apps/web/package-lock.json`

**Steps:**
1. Install `framer-motion` in `apps/web` using npm to update lockfile: `cd apps/web && npm install framer-motion`.
2. Verify lockfile updated and no peer warnings block install.

### Task 2: Update page layout & interactions
**Files:**
- Modify: `apps/web/src/app/page.tsx`

**Steps:**
1. Import framer-motion primitives; add helper components: `WaveRibbon`, `StatCard`, `PreviewCard` with terminal cursor, `StatusPill` with dots.
2. Adjust main JSX: place `WaveRibbon` above page; keep hero copy but align with new palette; add staggered motion wrappers for hero, panels, stats.
3. Keep existing logic (state, api calls) intact; wire status text into ribbon CTA/status.

### Task 3: Refresh styling for monochrome dev theme
**Files:**
- Modify: `apps/web/src/app/globals.css`

**Steps:**
1. Replace color tokens with black/graphite/silver, accent via subtle white glows; add variables for wave gradient.
2. Add styles for wave ribbon, terminal cursor, shimmer skeleton, breathing pill, CTA pulse, and responsive tweaks for <1024px.
3. Ensure `prefers-reduced-motion` keeps existing block and covers new animations.

### Task 4: Quick QA
**Files:**
- Commands only.

**Steps:**
1. Run `cd apps/web && npm run lint` to ensure no type/lint errors.
2. Manual smoke: `npm run dev` (if time) verify layout loads, ribbon animates, textarea editable, buttons clickable.

### Task 5: Hand-off
**Files:**
- None.

**Steps:**
1. Summarize changes and remaining risks; propose next steps (optional tests, perf tuning).
