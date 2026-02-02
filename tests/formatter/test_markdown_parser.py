from formatter.markdown_parser import parse_markdown


def test_parse_markdown_headings_and_paragraphs():
    ast = parse_markdown("# Title\n\nHello")
    assert ast == [
        {
            "type": "heading",
            "level": 1,
            "text": "Title",
            "runs": [{"text": "Title", "bold": False}],
        },
        {
            "type": "paragraph",
            "text": "Hello",
            "runs": [{"text": "Hello", "bold": False}],
        },
    ]


def test_parse_markdown_strips_bold_and_softbreaks():
    ast = parse_markdown("先说**结论**\n下一句")
    paragraph = ast[0]
    assert paragraph["text"] == "先说结论 下一句"
    assert paragraph["runs"] == [
        {"text": "先说", "bold": False},
        {"text": "结论", "bold": True},
        {"text": " 下一句", "bold": False},
    ]


def test_parse_markdown_handles_nested_bold_markers():
    ast = parse_markdown("****加粗****")
    paragraph = ast[0]
    assert paragraph["text"] == "加粗"
    assert paragraph["runs"] == [{"text": "加粗", "bold": True}]


def test_parse_markdown_shifts_heading_levels():
    ast = parse_markdown("## 二级标题\n\n### 三级标题\n\n#### 四级标题\n\n##### 五级标题")
    assert ast[0]["type"] == "heading"
    assert ast[0]["level"] == 1
    assert ast[1]["type"] == "heading"
    assert ast[1]["level"] == 2
    assert ast[2]["type"] == "heading"
    assert ast[2]["level"] == 3
    assert ast[3]["type"] == "heading"
    assert ast[3]["level"] == 4
