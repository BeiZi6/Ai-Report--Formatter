# Frontend Redesign + FastAPI Backend Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the Streamlit UI with a minimal, professional Next.js frontend backed by a FastAPI API, while keeping the formatter core unchanged.

**Architecture:** Add `apps/api` (FastAPI) exposing `/api/preview` and `/api/generate` using existing formatter logic. Add `apps/web` (Next.js App Router) for the redesigned UI, with a clean two-column layout and restrained styling. Keep existing `apps/formatter` core.

**Tech Stack:** FastAPI, Uvicorn, pytest, Next.js (App Router), React, TypeScript, Playwright (optional), CSS (custom, no Tailwind defaults).

---

### Task 1: Backend preview endpoint (TDD)

**Files:**
- Create: `apps/api/main.py`
- Create: `apps/api/requirements.txt`
- Create: `apps/api/__init__.py`
- Create: `tests/api/test_preview_endpoint.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from apps.api.main import app


def test_preview_endpoint_returns_summary_and_refs():
    client = TestClient(app)
    response = client.post(
        "/api/preview",
        json={"markdown": "# Title\n\nHello [1]."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["headings"] == 1
    assert payload["refs"] == ["[1]"]
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/api/test_preview_endpoint.py::test_preview_endpoint_returns_summary_and_refs -v`
Expected: FAIL (module/app not found)

**Step 3: Write minimal implementation**

```python
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from formatter.app_logic import build_preview_payload


# Ensure formatter package is importable when running via apps/api
FORMATTER_PATH = Path(__file__).resolve().parents[1] / "formatter"
if str(FORMATTER_PATH) not in sys.path:
    sys.path.append(str(FORMATTER_PATH))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.post("/api/preview")
async def preview(payload: dict) -> dict:
    markdown = payload.get("markdown", "")
    return build_preview_payload(markdown)
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/api/test_preview_endpoint.py::test_preview_endpoint_returns_summary_and_refs -v`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/api/main.py apps/api/requirements.txt apps/api/__init__.py tests/api/test_preview_endpoint.py
git commit -m "feat: add preview endpoint"
```

---

### Task 2: Backend generate endpoint (TDD)

**Files:**
- Modify: `apps/api/main.py`
- Create: `tests/api/test_generate_endpoint.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient

from apps.api.main import app


def test_generate_endpoint_returns_docx():
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        json={
            "markdown": "# Title\n\nHello.",
            "config": {
                "cn_font": "SimSun",
                "en_font": "Times New Roman",
                "heading_font": "SimHei",
                "heading_size_pt": 16,
                "body_size_pt": 12,
                "line_spacing": 1.5,
                "para_before_pt": 0,
                "para_after_pt": 0,
                "first_line_indent": True,
                "justify": True,
                "clear_background": True,
                "page_num_position": "center",
            },
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(response.content) > 0
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/api/test_generate_endpoint.py::test_generate_endpoint_returns_docx -v`
Expected: FAIL (endpoint missing)

**Step 3: Write minimal implementation**

```python
import tempfile

from fastapi.responses import Response

from formatter.docx_builder import build_docx
from formatter.ui_config import build_format_config


@app.post("/api/generate")
async def generate(payload: dict) -> Response:
    config = payload.get("config", {})
    markdown = payload.get("markdown", "")
    preview = build_preview_payload(markdown)

    format_config = build_format_config(**config)
    with tempfile.NamedTemporaryFile(suffix=".docx") as tmp:
        build_docx(preview["ast"], tmp.name, config=format_config)
        tmp.seek(0)
        data = tmp.read()

    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=ai-report.docx"},
    )
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/api/test_generate_endpoint.py::test_generate_endpoint_returns_docx -v`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/api/main.py tests/api/test_generate_endpoint.py
git commit -m "feat: add generate endpoint"
```

---

### Task 3: Frontend scaffold + baseline styles

**Files:**
- Create: `apps/web/` (Next.js App Router)
- Modify: `.gitignore`

**Step 1: Scaffold Next.js app**

Run: `npx create-next-app@latest apps/web --ts --eslint --app --src-dir`
Expected: `apps/web` with `src/app` structure

**Step 2: Update `.gitignore`**

Add:
```
node_modules/
.next/
out/
.env
.env.local
```

**Step 3: Commit**

```bash
git add apps/web .gitignore
git commit -m "chore: scaffold nextjs app"
```

---

### Task 4: Frontend layout + UI (TDD via Playwright)

**Files:**
- Create: `apps/web/playwright.config.ts`
- Create: `apps/web/tests/app.spec.ts`
- Modify: `apps/web/src/app/page.tsx`
- Modify: `apps/web/src/app/globals.css`

**Step 1: Write the failing Playwright test**

```ts
import { test, expect } from '@playwright/test';

test('landing renders core sections', async ({ page }) => {
  await page.goto('http://localhost:3000/');
  await expect(page.getByRole('heading', { name: 'AI 报告排版助手' })).toBeVisible();
  await expect(page.getByLabel('Markdown 输入')).toBeVisible();
  await expect(page.getByRole('button', { name: '生成 Word' })).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `cd apps/web && npx playwright test`
Expected: FAIL (page content not implemented)

**Step 3: Implement minimal UI + styles**

- `page.tsx`: build two-column layout (input/config on left, preview/export on right)
- `globals.css`: define CSS variables, minimal-professional palette, custom fonts
  - Use `next/font/google` with **Alegreya** (display) + **IBM Plex Sans** (UI)
  - Avoid Inter/Roboto/system fonts
  - Palette: warm paper (#F7F4EF), ink (#1B2428), muted accent (#2D5E5B)
  - Use subtle borders, generous spacing, thin separators

**Step 4: Run test to verify it passes**

Run: `cd apps/web && npx playwright test`
Expected: PASS

**Step 5: Commit**

```bash
git add apps/web/src/app/page.tsx apps/web/src/app/globals.css apps/web/tests/app.spec.ts apps/web/playwright.config.ts
git commit -m "feat: add minimal professional ui"
```

---

### Task 5: Frontend → API wiring

**Files:**
- Create: `apps/web/src/lib/api.ts`
- Modify: `apps/web/src/app/page.tsx`

**Step 1: Write failing test (doc-only)**

```ts
// Manual verification checklist:
// - typing markdown triggers preview summary update
// - generate button downloads docx
// - empty input disables primary button
```

**Step 2: Implement API client + wiring**

```ts
export async function fetchPreview(markdown: string) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown }),
  });
  return res.json();
}

export async function generateDocx(markdown: string, config: Record<string, unknown>) {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ markdown, config }),
  });
  return res.blob();
}
```

**Step 3: Manual verification**

Run:
- `cd apps/api && uvicorn main:app --reload --port 8000`
- `cd apps/web && NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev`

Expected:
- preview updates on input
- download works

**Step 4: Commit**

```bash
git add apps/web/src/lib/api.ts apps/web/src/app/page.tsx
git commit -m "feat: wire frontend to api"
```

---

### Task 6: Docs + local run instructions

**Files:**
- Create: `apps/api/README.md`
- Create: `apps/web/README.md`

**Step 1: Write docs**

Include:
- API run command
- Frontend dev command
- Required env vars (`NEXT_PUBLIC_API_BASE`)

**Step 2: Commit**

```bash
git add apps/api/README.md apps/web/README.md
git commit -m "docs: add api and web run instructions"
```

---

### Task 7: Full test run

**Step 1: Run backend tests**

Run: `python3 -m pytest -v`
Expected: PASS

**Step 2: Commit (if needed)**

```bash
git add -A
git commit -m "test: green test suite"
```

---

## Execution Handoff

Plan complete and saved to `docs/plans/2026-02-01-frontend-redesign-implementation-plan.md`. Two execution options:

1. **Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration
2. **Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
