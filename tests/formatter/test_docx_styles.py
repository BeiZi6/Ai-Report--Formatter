from docx import Document
from docx.shared import Cm, Pt

from formatter.config import FormatConfig
from formatter.docx_builder import build_docx


def test_docx_styles_and_margins_applied(tmp_path):
    config = FormatConfig()
    output = tmp_path / "out.docx"
    ast = [
        {"type": "heading", "level": 1, "text": "Title"},
        {"type": "paragraph", "text": "Hello"},
    ]
    build_docx(ast, output, config)

    doc = Document(output)
    section = doc.sections[0]
    assert round(section.top_margin.cm, 2) == 2.54
    assert round(section.left_margin.cm, 2) == 3.18

    normal = doc.styles["Normal"]
    assert normal.font.size == Pt(config.body_style.size_pt)

    h1 = doc.styles["Heading 1"]
    assert h1.font.size == Pt(config.heading_styles[1].size_pt)
