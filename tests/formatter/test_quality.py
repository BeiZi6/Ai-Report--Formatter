from formatter.preview import build_export_quality_report, lint_structure


def test_lint_structure_detects_heading_issues_and_citation_gaps():
    ast = [
        {"type": "heading", "level": 1, "text": "标题"},
        {"type": "heading", "level": 3, "text": "跨级标题"},
        {"type": "heading", "level": 2, "text": "   "},
    ]

    warnings = lint_structure(ast, ["[1]", "[3]"])
    codes = {warning["code"] for warning in warnings}

    assert "heading_level_jump" in codes
    assert "empty_heading" in codes
    assert "citation_number_gap" in codes


def test_build_export_quality_report_collects_rules_and_risks():
    ast = [
        {"type": "paragraph", "text": "正文"},
        {"type": "math_block", "latex": "x"},
        {"type": "blockquote", "children": [{"type": "paragraph", "text": "引文"}]},
    ]

    report = build_export_quality_report(ast, ["[1]"], [{"code": "empty_heading", "message": "标题为空"}])

    assert "citations_sorted_and_deduplicated" in report["rules_applied"]
    assert "math_blocks_auto_numbered" in report["rules_applied"]
    assert "blockquote_rendering" in report["rules_applied"]
    assert report["risks"] == ["标题为空"]
    assert report["stats"]["refs"] == 1
