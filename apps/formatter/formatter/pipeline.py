from __future__ import annotations

from typing import Any

from formatter.citations import build_bibliography_nodes, has_bibliography_heading, normalize_citations
from formatter.markdown_parser import parse_markdown


def format_markdown(text: str) -> dict[str, Any]:
    normalized, refs = normalize_citations(text)
    ast = parse_markdown(normalized)

    if refs and not has_bibliography_heading(ast):
        ast.extend(build_bibliography_nodes(refs))

    return {"ast": ast, "refs": refs}
