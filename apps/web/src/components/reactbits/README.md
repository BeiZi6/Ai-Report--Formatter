# React Bits Integration Notes

This folder keeps manually adapted React Bits components for the Next.js app.

- Prefer `TS + CSS` variants from React Bits docs for compatibility with this codebase.
- Export components via `index.ts` to keep import paths stable.
- Keep each component client-safe (`"use client"`) and add reduced-motion fallback.
- Add app-specific wrappers here before using components directly in pages.
