# Docx Styles + Page Layout Implementation Design

## Overview
Implement Word style writing and page layout so exported .docx matches configured typography and spacing. The formatter should set `Normal` and `Heading 1–4` styles, apply page margins, add a footer page number, and remain resilient via paragraph-level fallbacks when style writes fail.

## Goals
- Apply body and heading styles consistently using `python-docx` styles.
- Enforce margins (top/bottom 2.54cm, left/right 3.18cm) on the document section.
- Insert a footer page number field (PAGE), centered by default.
- Provide fallbacks: if style or footer insertion fails, export still succeeds with paragraph-level formatting.

## Non-Goals
- Advanced bibliography formatting or template-based styling.
- Full visual preview of the Word document.

## Architecture
Enhance `formatter/docx_builder.py` with a small set of helper functions:
- `apply_page_margins(document, config)`
- `apply_style_defaults(document, config)`
- `add_page_number_footer(document, position)`
- `render_ast(document, ast, config)`

`build_docx(ast, output_path, config)` will orchestrate those steps and keep errors non-fatal.

## Data Flow
1. `FormatConfig` supplies `BodyStyle` and `HeadingStyle` values.
2. `build_docx` applies margins and styles to the document.
3. Footer page number is inserted (best effort).
4. AST is rendered into headings and paragraphs using styles; paragraph-level overrides are applied when needed.
5. Document is saved to the output path.

## Style Mapping
- **Normal** style: body font (CN/EN), size, line spacing, paragraph spacing, justification.
- **Heading 1–4** styles: heading font, size, line spacing, paragraph spacing, alignment.
- **First-line indent**: `2 * body_size_pt` (converted to Pt) for body paragraphs.

For CN/EN font support, set `style.font.name` and update the East Asia font (`w:eastAsia`) to keep Chinese fonts intact. If any style update fails, use paragraph-level formatting during rendering.

## Error Handling
- Margin, style, and footer operations are wrapped in `try/except` with graceful degradation.
- If style writing fails, continue rendering with paragraph-level settings.
- Footer insertion failure does not stop export.

## Testing Strategy
1. **Style existence**: confirm `Normal` and `Heading 1–4` styles exist after export.
2. **Style values**: verify size, line spacing, and paragraph spacing align with config.
3. **Paragraph formatting**: ensure first-line indent equals `2 * body_size_pt` and alignment is justified.
4. **Margins**: verify section margins match 2.54cm/3.18cm.
5. **Footer PAGE field**: assert footer XML includes `PAGE` field code.
6. **Fallback behavior**: force `apply_style_defaults` to raise and ensure export still succeeds.

## Future Extensions
- Template presets for different report types.
- Advanced heading numbering and table/list styling.
- Full preview rendering in the UI.
