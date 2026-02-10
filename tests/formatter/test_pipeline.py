from formatter.pipeline import format_markdown


def test_pipeline_returns_ast_and_refs():
    result = format_markdown("# Title\n\nHello [1].")
    assert result["refs"] == ["[1]"]
    assert result["ast"][0]["type"] == "heading"


def test_pipeline_appends_bibliography_with_sorted_refs():
    result = format_markdown("# Title\n\nHello [3] [1] [3].")

    assert result["refs"] == ["[1]", "[3]"]
    bibliography_heading = dict(result["ast"][-2])
    bibliography_heading.pop("auto_generated", None)
    assert bibliography_heading == {
        "type": "heading",
        "level": 1,
        "text": "参考文献",
        "runs": [
            {
                "text": "参考文献",
                "bold": False,
                "italic": False,
                "strike": False,
                "highlight": False,
                "superscript": False,
                "subscript": False,
                "code": False,
            }
        ],
    }
    bibliography = result["ast"][-1]
    assert bibliography["type"] == "list"
    assert bibliography["ordered"] is True
    assert [item[0]["text"] for item in bibliography["items"]] == [
        "[1] 待补充参考文献",
        "[3] 待补充参考文献",
    ]
