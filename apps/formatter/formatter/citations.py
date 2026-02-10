from __future__ import annotations

import re
from typing import Any

_CITATION_RE = re.compile(r"\[(\d+)\]")
_KEY_CITATION_RE = re.compile(r"\[@([A-Za-z0-9:_-]+)\]")
_MANUAL_SOURCE_RE = re.compile(r"^\[(?P<id>[^\]]+)\]\s*(?P<text>.+)$")
_BIB_ENTRY_RE = re.compile(
    r"@(?P<entry_type>[A-Za-z]+)\s*\{\s*(?P<key>[^,\s]+)\s*,(?P<body>.*?)\}\s*(?=@|$)",
    re.S,
)
_BIB_FIELD_RE = re.compile(r"(?P<name>[A-Za-z]+)\s*=\s*(?P<value>\{.*?\}|\".*?\")\s*,?", re.S)
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


def _normalize_source_key(raw_key: str) -> str:
    return raw_key.strip().lower()


def _clean_bib_value(raw_value: str) -> str:
    value = raw_value.strip()
    if (value.startswith("{") and value.endswith("}")) or (
        value.startswith('"') and value.endswith('"')
    ):
        value = value[1:-1]
    return re.sub(r"\s+", " ", value).strip()


def _parse_bib_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field_match in _BIB_FIELD_RE.finditer(body):
        name = field_match.group("name").strip().lower()
        value = _clean_bib_value(field_match.group("value"))
        if value:
            fields[name] = value
    return fields


def _format_bib_entry(fields: dict[str, str]) -> str | None:
    author = fields.get("author", "").replace(" and ", ", ").strip()
    title = fields.get("title", "").strip()
    container = (fields.get("journal") or fields.get("booktitle") or fields.get("publisher") or "").strip()
    year = fields.get("year", "").strip()

    parts = [part for part in [author, title, container, year] if part]
    if not parts:
        return None

    text = ". ".join(parts)
    if not text.endswith("."):
        text = f"{text}."
    return text


def parse_bibliography_sources(text: str) -> dict[str, str]:
    sources: dict[str, str] = {}

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        manual_match = _MANUAL_SOURCE_RE.match(stripped)
        if manual_match:
            source_id = _normalize_source_key(manual_match.group("id"))
            source_text = manual_match.group("text").strip()
            if source_id and source_text:
                sources[source_id] = source_text

    for entry_match in _BIB_ENTRY_RE.finditer(text):
        source_id = _normalize_source_key(entry_match.group("key"))
        fields = _parse_bib_fields(entry_match.group("body"))
        formatted = _format_bib_entry(fields)
        if source_id and formatted and source_id not in sources:
            sources[source_id] = formatted

    return sources


def normalize_citations(text: str) -> tuple[str, list[str], dict[int, str]]:
    numbers = sorted({int(match.group(1)) for match in _CITATION_RE.finditer(text)})
    next_number = (max(numbers) + 1) if numbers else 1
    key_to_number: dict[str, int] = {}

    def replace_key_citation(match: re.Match[str]) -> str:
        nonlocal next_number
        source_key = _normalize_source_key(match.group(1))
        if source_key not in key_to_number:
            key_to_number[source_key] = next_number
            next_number += 1
        return f"[{key_to_number[source_key]}]"

    normalized_text = _KEY_CITATION_RE.sub(replace_key_citation, text)
    all_numbers = sorted({int(match.group(1)) for match in _CITATION_RE.finditer(normalized_text)})
    refs = [f"[{number}]" for number in all_numbers]
    number_key_map = {number: key for key, number in key_to_number.items()}
    return normalized_text, refs, number_key_map


def _format_reference_item(ref: str, source_text: str | None, style: str) -> str:
    if not source_text:
        return f"{ref} 待补充参考文献"

    normalized_style = style.strip().lower()
    if normalized_style == "apa":
        return source_text
    return f"{ref} {source_text}"


def _parse_ref_number(ref: str) -> int | None:
    match = _CITATION_RE.fullmatch(ref)
    if not match:
        return None
    return int(match.group(1))


def has_bibliography_heading(ast: list[AstNode]) -> bool:
    return any(
        node.get("type") == "heading" and str(node.get("text", "")).strip() == "参考文献"
        for node in ast
    )


def build_bibliography_nodes(
    refs: list[str],
    *,
    style: str = "ieee",
    sources: dict[str, str] | None = None,
    key_number_map: dict[int, str] | None = None,
) -> list[AstNode]:
    if not refs:
        return []

    sources = sources or {}
    key_number_map = key_number_map or {}

    heading = {
        "type": "heading",
        "level": 1,
        "text": "参考文献",
        "runs": [_plain_run("参考文献")],
        "auto_generated": True,
    }

    items = []
    for ref in refs:
        ref_number = _parse_ref_number(ref)
        source_text = None
        if ref_number is not None:
            source_text = sources.get(str(ref_number).lower())
            if source_text is None:
                source_key = key_number_map.get(ref_number)
                if source_key:
                    source_text = sources.get(_normalize_source_key(source_key))

        text = _format_reference_item(ref, source_text, style)
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
