# AI Report Formatter (AI-to-Word) - Design

## Overview
Build a Streamlit web app that converts AI-generated Markdown into a Word report (.docx) with academic formatting. The UI provides a simple input area, a style configuration sidebar, and a structural summary preview. Output uses python-docx and injects Word-native formulas (OMML).

## Goals
- Accept Markdown input and export a .docx with consistent academic formatting.
- Provide configurable typography and spacing (CN/EN fonts, sizes, line/paragraph spacing, indent, alignment).
- Map Markdown headings to Word heading levels.
- Normalize inline citations like [1] into a reference list.
- Convert LaTeX ($...$, $$...$$) into Word formulas (OMML).
- Keep the UI minimal and Notion-like with light blue accents.

## Non-Goals (MVP)
- Full fidelity visual preview of Word output.
- File upload for templates or images.
- Advanced bibliography styles (e.g., GB/T 7714) beyond a simple numbered list.

## User Experience
- Left: multi-line Markdown input.
- Sidebar: style controls.
- Right: structural preview showing block types, heading levels, table size, list depth, citation count, and formula conversion stats.
- Primary CTA: "Generate and Download Word".

## Style Controls (MVP)
- Chinese font (default SimSun)
- English font (default Times New Roman)
- Heading size (default "Sanhao" equivalent)
- Body size (default "Xiaosi" equivalent)
- Line spacing (default 1.5x)
- Paragraph spacing (before/after)
- First-line indent (toggle; 2-character indent)
- Justification (always both-side)
- Page margins (top/bottom 2.54cm, left/right 3.18cm)
- Clear background color (toggle)
- Page number position (center or right)

## Architecture
- Streamlit app in `apps/formatter`.
- Pure-Python pipeline:
  - `MarkdownParser`: parse Markdown into an AST.
  - `CitationNormalizer`: detect [n] patterns and build a references block.
  - `LatexConverter`: transform LaTeX to OMML via MathML conversion.
  - `DocxBuilder`: map AST + config to python-docx and output .docx.

## Markdown Support (MVP)
- Headings (#, ##)
- Paragraphs
- Emphasis (bold/italic)
- Lists (ordered/unordered)
- Code blocks
- Tables
- Block quotes

## Data Flow
1. User input + config -> `FormatConfig`.
2. Markdown -> AST.
3. Normalize citations -> append references block.
4. Convert LaTeX -> OMML (fallback to monospace text on failure).
5. Build docx with styles and layout.
6. Export file for download.

## LaTeX to Word Formula
- Recognize `$...$` and `$$...$$`.
- Convert LaTeX -> MathML -> OMML.
- Inject OMML XML into docx runs.
- If conversion fails, render as monospace text and mark in preview.

## Citation Normalization
- Detect inline `[1]`, `[2]` tokens.
- Generate a "References" section at the end.
- Preserve numbering and order of appearance.

## Error Handling
- If Markdown parsing fails: export as plain text with a warning in preview.
- If LaTeX conversion fails: fallback per formula and record failures.
- Always allow export unless critical exceptions occur.

## Testing
- Unit tests for:
  - Heading mapping
  - Paragraph styles (indent/spacing/alignment)
  - Table generation (rows/cols)
  - Citation normalization
  - LaTeX conversion success/failure

## Future Extensions (Post-MVP)
- Template presets (exam report, lab report, official doc).
- Advanced citation formatting (GB/T 7714).
- Better table styling and auto column width.
- Full HTML preview (optional).
