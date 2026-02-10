from __future__ import annotations

from typing import Any

from formatter.citations import (
    build_bibliography_nodes,
    has_bibliography_heading,
    normalize_citations,
    parse_bibliography_sources,
)
from formatter.markdown_parser import parse_markdown


def format_markdown(
    text: str,
    *,
    bibliography_style: str = "ieee",
    bibliography_sources: str = "",
) -> dict[str, Any]:
    normalized, refs, key_number_map = normalize_citations(text)
    ast = parse_markdown(normalized)
    sources = parse_bibliography_sources(bibliography_sources)

    if refs and not has_bibliography_heading(ast):
        ast.extend(
            build_bibliography_nodes(
                refs,
                style=bibliography_style,
                sources=sources,
                key_number_map=key_number_map,
            )
        )

    return {"ast": ast, "refs": refs, "normalized_markdown": normalized}
