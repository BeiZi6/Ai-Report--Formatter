from __future__ import annotations

import re
from typing import Any

_CITATION_RE = re.compile(r"\[(\d+)\]")
AstNode = dict[str, Any]


def _plain_run(text: str) -> AstNode:
    return {
        "text": text,
        "bold": False,
        "italic": False,
        "strike": False,
        "highlight": False,
        "superscript": False,
        "subscript": False,
        "code": False,
    }


def normalize_citations(text: str) -> tuple[str, list[str]]:
    numbers = sorted({int(match.group(1)) for match in _CITATION_RE.finditer(text)})
    refs = [f"[{number}]" for number in numbers]
    return text, refs


def has_bibliography_heading(ast: list[AstNode]) -> bool:
    return any(
        node.get("type") == "heading" and str(node.get("text", "")).strip() == "参考文献"
        for node in ast
    )


def build_bibliography_nodes(refs: list[str]) -> list[AstNode]:
    if not refs:
        return []

    heading = {
        "type": "heading",
        "level": 1,
        "text": "参考文献",
        "runs": [_plain_run("参考文献")],
        "auto_generated": True,
    }

    items = []
    for ref in refs:
        text = f"{ref} 待补充参考文献"
        items.append(
            [
                {
                    "type": "paragraph",
                    "text": text,
                    "runs": [_plain_run(text)],
                }
            ]
        )

    return [
        heading,
        {
            "type": "list",
            "ordered": True,
            "level": 1,
            "start": 1,
            "items": items,
            "auto_generated": True,
        },
    ]
