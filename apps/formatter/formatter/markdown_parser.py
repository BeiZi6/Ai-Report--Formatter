from __future__ import annotations

from markdown_it import MarkdownIt


def _append_run(runs: list[dict], text: str, bold: bool) -> None:
    if not text:
        return
    if runs and runs[-1]["bold"] == bold:
        runs[-1]["text"] += text
    else:
        runs.append({"text": text, "bold": bold})


def _build_inline_runs(token) -> tuple[str, list[dict]]:
    runs: list[dict] = []
    bold_level = 0

    for child in token.children or []:
        if child.type == "strong_open":
            bold_level += 1
            continue
        if child.type == "strong_close":
            bold_level = max(0, bold_level - 1)
            continue
        if child.type in {"softbreak", "hardbreak"}:
            _append_run(runs, " ", bold_level > 0)
            continue
        if child.type in {"text", "code_inline"}:
            _append_run(runs, child.content, bold_level > 0)
            continue
        if child.content:
            _append_run(runs, child.content, bold_level > 0)

    text = "".join(run["text"] for run in runs).strip()
    return text, runs


def parse_markdown(text: str) -> list[dict]:
    md = MarkdownIt()
    tokens = md.parse(text)
    ast: list[dict] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.type == "heading_open":
            level = max(1, min(4, int(token.tag[1]) - 1))
            text_token = tokens[i + 1]
            text, runs = _build_inline_runs(text_token)
            ast.append(
                {
                    "type": "heading",
                    "level": level,
                    "text": text,
                    "runs": runs or [{"text": text, "bold": False}],
                }
            )
            i += 3
            continue
        if token.type == "paragraph_open":
            text_token = tokens[i + 1]
            text, runs = _build_inline_runs(text_token)
            ast.append(
                {
                    "type": "paragraph",
                    "text": text,
                    "runs": runs or [{"text": text, "bold": False}],
                }
            )
            i += 3
            continue
        i += 1
    return ast
