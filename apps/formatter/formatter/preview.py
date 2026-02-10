from __future__ import annotations

import re
from typing import Any

AstNode = dict[str, Any]
QualityWarning = dict[str, str]
_REF_RE = re.compile(r"^\[(\d+)\]$")


def summarize_ast(ast: list[AstNode]) -> dict[str, int]:
    counts = {
        "headings": 0,
        "paragraphs": 0,
        "lists": 0,
        "tables": 0,
        "math_blocks": 0,
        "figures": 0,
    }

    def walk(nodes: list[AstNode]) -> None:
        for node in nodes:
            if node.get("auto_generated"):
                continue
            ntype = node.get("type")
            if ntype == "heading":
                counts["headings"] += 1
            elif ntype == "paragraph":
                counts["paragraphs"] += 1
            elif ntype == "list":
                counts["lists"] += 1
                for item in node.get("items", []):
                    walk(item)
            elif ntype == "table":
                counts["tables"] += 1
            elif ntype == "math_block":
                counts["math_blocks"] += 1
            elif ntype == "figure":
                counts["figures"] += 1

    walk(ast)
    return counts


def _walk_nodes(nodes: list[AstNode]):
    for node in nodes:
        yield node
        if node.get("type") == "list":
            for item in node.get("items", []):
                yield from _walk_nodes(item)
        if node.get("type") == "blockquote":
            yield from _walk_nodes(node.get("children", []))


def lint_structure(ast: list[AstNode], refs: list[str]) -> list[QualityWarning]:
    warnings: list[QualityWarning] = []
    last_heading_level: int | None = None

    for node in _walk_nodes(ast):
        if node.get("auto_generated"):
            continue
        if node.get("type") != "heading":
            continue

        level = int(node.get("level", 1))
        text = str(node.get("text", "")).strip()

        if not text:
            warnings.append(
                {
                    "code": "empty_heading",
                    "severity": "warning",
                    "message": f"发现空标题（H{level}）。",
                }
            )

        if last_heading_level is not None and level > last_heading_level + 1:
            warnings.append(
                {
                    "code": "heading_level_jump",
                    "severity": "warning",
                    "message": f"标题层级从 H{last_heading_level} 跳到了 H{level}。",
                }
            )

        last_heading_level = level

    numbers: list[int] = []
    for ref in refs:
        match = _REF_RE.match(ref)
        if match:
            numbers.append(int(match.group(1)))

    if numbers:
        missing = sorted(set(range(min(numbers), max(numbers) + 1)) - set(numbers))
        if missing:
            warnings.append(
                {
                    "code": "citation_number_gap",
                    "severity": "warning",
                    "message": f"引用编号存在断档：缺少 {', '.join(f'[{num}]' for num in missing)}。",
                }
            )

    return warnings


def build_export_quality_report(
    ast: list[AstNode], refs: list[str], lint_warnings: list[QualityWarning]
) -> dict[str, Any]:
    stats = summarize_ast(ast)
    stats["refs"] = len(refs)

    rules_applied = ["structure_lint_before_export"]
    if refs:
        rules_applied.extend(["citations_sorted_and_deduplicated", "bibliography_auto_append"])
    if stats.get("math_blocks", 0) > 0:
        rules_applied.append("math_blocks_auto_numbered")
    if stats.get("figures", 0) > 0:
        rules_applied.append("figure_caption_numbering")

    has_blockquote = any(node.get("type") == "blockquote" for node in _walk_nodes(ast))
    if has_blockquote:
        rules_applied.append("blockquote_rendering")

    has_task_items = any(node.get("task") is True for node in _walk_nodes(ast))
    if has_task_items:
        rules_applied.append("task_list_checkbox_rendering")

    has_links = any(
        run.get("link")
        for node in _walk_nodes(ast)
        for run in node.get("runs", [])
        if isinstance(run, dict)
    )
    if has_links:
        rules_applied.append("link_url_preserved")

    return {
        "rules_applied": rules_applied,
        "risks": [warning["message"] for warning in lint_warnings],
        "warnings": lint_warnings,
        "stats": stats,
    }
