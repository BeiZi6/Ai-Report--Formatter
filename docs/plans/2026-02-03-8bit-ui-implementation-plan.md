# 8-bit UI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restyle the AI 报告排版助手 web UI into a light-gray, black/white 8-bit (NES-like) theme with pixel typography, dot-matrix background, and pixelated controls while keeping current functionality.

**Architecture:** Re-skin existing React/Next.js layout by swapping the global design tokens, backgrounds, and component styles in `globals.css`, plus light structural tweaks in `page.tsx` to support pixel borders and decorative bands. No business logic changes; animations remain via framer-motion but adjusted to fit 8-bit feel.

**Tech Stack:** Next.js App Router, React, TypeScript, CSS (global), Framer Motion.

### Task 1: Palette & Typography Tokens

**Files:**
- Modify: `apps/web/src/app/globals.css`

**Step 1:** Add @import for pixel fonts (Press Start 2P for display, Space Mono for body) near top of CSS.
**Step 2:** Replace color tokens with light-gray base (`--bg-1: #f4f4f4`, accents in #0f0f0f and #ffffff) and add pixel shadow/border tokens (e.g., `--pixel-border: #0f0f0f`).
**Step 3:** Update font variables: display uses Press Start 2P, UI uses Space Mono; ensure fallbacks are monospace.

### Task 2: Background, Grid, and Page Frame

**Files:**
- Modify: `apps/web/src/app/globals.css`

**Step 1:** Change body background to layered light gray with black 2px dot grid (background-size ~18px) and subtle scanline noise; set `image-rendering: pixelated`.
**Step 2:** Give `.page` a thick pixel frame using multi-shadow (outer/inner) and set padding adjusted for new frame.
**Step 3:** Update skip-link focus colors to match new palette.

### Task 3: Panels, Cards, and Inputs 8-bit Styling

**Files:**
- Modify: `apps/web/src/app/globals.css`

**Step 1:** Replace glassmorphism panels with flat light blocks, pixel borders (box-shadow steps), and harsher radii (4px/0 where suitable).
**Step 2:** Restyle buttons to 8-bit pill/rectangle with step shadows and hover “press” effect; ensure disabled state contrasts on light theme.
**Step 3:** Update fields (textarea/input/select) to square corners, high-contrast outlines, focus using dashed border.
**Step 4:** Retheme status pills, chips, stats, preview cards to monochrome pixel borders; adjust spacing to fit pixel font metrics.

### Task 4: Hero & Ribbon Accents

**Files:**
- Modify: `apps/web/src/app/page.tsx`
- Modify: `apps/web/src/app/globals.css`

**Step 1:** Swap ribbon copy badge to 8-bit label style; keep motion but adjust colors to monochrome.
**Step 2:** Add optional top “scanline band” div (or class on existing elements) if needed for depth; ensure semantic structure unchanged.
**Step 3:** Tighten hero/panel typography sizes to suit pixel font legibility.

### Task 5: QA / Verification

**Files:** n/a

**Step 1:** Run `npm run lint` (or `pnpm run lint` if lockfile indicates) to ensure style changes keep code clean.
**Step 2:** Manually open the page (`npm run dev` locally) to verify readability, focus states, and button states on light gray background.
