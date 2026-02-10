from __future__ import annotations

from typing import Any

from .markdown_parser import render_preview_html
from .pipeline import format_markdown
from .preview import build_export_quality_report, lint_structure, summarize_ast


def build_preview_payload(text: str) -> dict[str, Any]:
    result = format_markdown(text)
    summary = summarize_ast(result["ast"])
    preview_html = render_preview_html(text)
    lint_warnings = lint_structure(result["ast"], result["refs"])
    quality_report = build_export_quality_report(result["ast"], result["refs"], lint_warnings)
    return {
        "summary": summary,
        "refs": result["refs"],
        "ast": result["ast"],
        "preview_html": preview_html,
        "lint_warnings": lint_warnings,
        "quality_report": quality_report,
    }
