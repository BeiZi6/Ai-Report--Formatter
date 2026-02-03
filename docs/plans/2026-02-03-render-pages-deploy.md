# Render API + Cloudflare Pages Deployment Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy the existing FastAPI backend to Render Free Web Service and ship the Next.js frontend as a static export on Cloudflare Pages, wired via `NEXT_PUBLIC_API_BASE`.

**Architecture:** Backend runs as a single Render free web service (auto-sleep, wake-on-request). Frontend is a static export served by Cloudflare Pages; all dynamic calls hit the Render API over HTTPS with permissive CORS.

**Tech Stack:** FastAPI + Uvicorn, Next.js 16 (static export), Cloudflare Pages, Render Free Web Service.

### Task 1: Make API CORS safe for hosted frontend

**Files:**
- Modify: `apps/api/main.py`

**Step 1: Allow hosted origins**
- Update `allow_origins` to `['*']` or include Render and Cloudflare Pages domains (simplest: `['*']`).

**Step 2: Quick lint check (optional)**
- Run: `python -m compileall apps/api/main.py`
- Expected: completes without error.

### Task 2: Prepare Next.js for static export

**Files:**
- Modify: `apps/web/next.config.ts`
- Modify: `apps/web/package.json`

**Step 1: Enable static output**
- Set `output: 'export'` in Next config.

**Step 2: Add export script**
- Add script `"export": "next build && next export"`.

**Step 3: Local dry run**
- Run: `cd apps/web && npm install && npm run export`
- Expected: `out/` folder generated.

### Task 3: Deploy backend to Render Free

**Files:**
- Modify: `render.yaml`

**Step 1: Define FastAPI service**
- Set service `env: python`, `buildCommand: pip install -r apps/api/requirements.txt`, `startCommand: uvicorn apps.api.main:app --host 0.0.0.0 --port $PORT`.

**Step 2: Push to repo & render deploy**
- Commit changes; connect repo to Render; choose Free plan; region closest to users.

**Step 3: Note API URL**
- After deploy, note `https://<service>.onrender.com` for NEXT_PUBLIC_API_BASE.

### Task 4: Deploy frontend to Cloudflare Pages

**Files:**
- Create (optional): `apps/web/.env.production` (local only)

**Step 1: Create project**
- In Cloudflare Pages, “Connect to Git” pointing to repo; set root to `apps/web`.

**Step 2: Build settings**
- Build command: `npm run export`
- Build output: `out`
- Node version: 20 (Pages default ok) or set `NODE_VERSION=20`.

**Step 3: Env var**
- Add `NEXT_PUBLIC_API_BASE=https://<service>.onrender.com`.

**Step 4: Trigger deploy**
- Start first deploy; verify site loads and API calls succeed (no CORS error).

### Task 5: Verification

**Step 1: Frontend smoke**
- Open Pages URL; input sample Markdown; ensure preview and export work.

**Step 2: Backend health**
- `curl https://<service>.onrender.com/api/exports/stats` -> JSON stats.

**Step 3: Monitor quota**
- In Render dashboard, confirm free instance hours remaining and auto-sleep enabled.

