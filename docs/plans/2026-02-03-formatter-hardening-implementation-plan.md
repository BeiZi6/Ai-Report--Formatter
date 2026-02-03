# Formatter Reliability & UI Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the formatter API robust (imports + validation + correct counters), fix DOCX table borders, align E2E selectors with the new UI wording, and add the requested verse overlay with glowing/scrolling treatment.

**Architecture:** Package `apps/formatter` as an editable install so both FastAPI and Streamlit import it without sys.path hacks; use Pydantic models for request validation and move side effects after successful DOCX generation; adjust DOCX table creation to remove inside vertical borders; stabilize Playwright selectors with data-testid; enhance the wave ribbon component with an overlaid animated verse using CSS-only effects.

**Tech Stack:** FastAPI + Pydantic v2, python-docx, Next.js 16/React 19, Playwright 1.58, CSS/Framer Motion.

### Task 1: Make formatter importable without runtime sys.path hacks

**Files:**
- Create: `apps/formatter/pyproject.toml`
- Modify: `apps/api/requirements.txt`, `apps/api/README.md`, `apps/api/main.py`

**Steps:**
1. Create a minimal setuptools-based `pyproject.toml` for `formatter` (name `formatter`, version 0.1.0, include package data if needed).
2. Add editable dependency line `-e ../formatter` to `apps/api/requirements.txt` (relative to that file).
3. Update `apps/api/README.md` install instructions to include editable install (single pip command).
4. Remove or simplify `sys.path` hack in `apps/api/main.py` once editable install is relied upon; keep fallback if necessary.

### Task 2: Validate API payloads and move export counter after success

**Files:**
- Modify/Create: `apps/api/schemas.py` (new), `apps/api/main.py`
- Tests: `apps/api/tests/test_api.py` (new)

**Steps:**
1. Define Pydantic models for preview and generate requests with defaults mirroring `DEFAULT_CONFIG`; forbid unknown fields and type-coerce safely.
2. Update `/api/preview` and `/api/generate` to accept models, build config from validated data, and return 422 on missing/invalid fields.
3. Move `increment_export_count()` to execute only after DOCX is built and streamed successfully; ensure exceptions don’t increment.
4. Add pytest-based tests using FastAPI TestClient to cover: (a) missing config -> 422, (b) invalid type -> 422, (c) successful generate increments counter and returns docx bytes.

### Task 3: Produce true three-line tables (no insideV)

**Files:**
- Modify: `apps/formatter/formatter/docx_builder.py`

**Steps:**
1. Set `insideV` border to `nil` within `_apply_three_line_table`.
2. Remove `Table Grid` style or replace with a minimal custom style so default vertical borders are not reintroduced.
3. Smoke-test DOCX output locally to confirm only top/bottom/header lines render.

### Task 4: Stabilize indent controls and Playwright selectors

**Files:**
- Modify: `apps/web/src/app/page.tsx`, `apps/web/tests/app.spec.ts`

**Steps:**
1. Add `data-testid` attributes to indent inputs (`left-indent`, `right-indent`, `first-line-indent`) and, if needed, related fields to avoid text-fragile selectors.
2. Update Playwright test to query by data-testid or updated labels (`左缩进/右缩进/首行缩进`).
3. Run Playwright: `cd apps/web && npx playwright test tests/app.spec.ts`.

### Task 5: Add glowing verse overlay on the wave ribbon

**Files:**
- Modify: `apps/web/src/app/page.tsx`, `apps/web/src/app/globals.css`

**Steps:**
1. Insert a new centered overlay element inside `WaveRibbon` showing the verse `秦琼卖马颜面抛，杨志也曾卖宝刀` with a flamboyant display font stack.
2. Style with constrained max-width, responsive sizing, animated glow, and scrolling marquee when text overflows.
3. Ensure accessibility (aria-hidden if decorative, or readable text with sufficient contrast) and that the button/status remain legible and clickable.

### Task 6: Verification

**Steps:**
1. Backend: `cd apps/api && python -m pytest` (new tests).
2. Frontend: `cd apps/web && npx playwright test tests/app.spec.ts`.
3. Manual: hit `/api/preview` and `/api/generate` via curl to confirm 422 on bad payload and count increments only on success.
