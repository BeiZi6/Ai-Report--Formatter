# Frontend Redesign (Minimal Professional) + FastAPI API Design

**Goal:** Replace the current Streamlit UI with a modern, minimal, professional frontend and a lightweight FastAPI backend, keeping the existing formatter core unchanged.

## 1) Architecture & Page Structure

- **Stack:** Next.js (App Router) for frontend, FastAPI for backend.
- **API surface:**
  - `POST /api/preview` → returns structure summary (blocks, citations, hierarchy)
  - `POST /api/generate` → returns a `.docx` file stream
- **Layout:** Single-screen workspace with two columns.
  - Left: Markdown input + style controls (font/size/line spacing/paragraph spacing/alignment/page number position)
  - Right: lightweight structured preview + export action
- **Aesthetic:** minimal, editorial-professional, typographic hierarchy, generous whitespace, understated borders, restrained color usage.

## 2) Interaction & Data Flow

- Markdown input changes trigger **debounced** `/api/preview` calls (400–600ms).
- Preview is structural only (no heavy rendering) for speed and clarity.
- Style controls do **not** trigger preview; they only affect export.
- “Generate Word” calls `/api/generate` and downloads the returned file.
- Input empty → disabled primary action; warning text shown in subtle tone.

## 3) Error Handling / Testing / Deployment

- **Backend errors:** standardized JSON `{code, message, detail?}`.
- **Frontend errors:** show `message` with optional “details” disclosure.
- **Timeouts:** 15–20s client timeout; prompt user to retry or shorten input.
- **Tests:**
  - Backend pytest for preview/generate happy path + empty input + invalid markdown
  - Frontend Playwright e2e for “input → preview → generate”
- **Deployment:** Frontend static host (Vercel/Render). Backend on Render/Fly. CORS locked to frontend domain.

## Scope Constraints

- No multi-page routing in v1
- No template library/history in v1
- Formatter core stays unchanged
