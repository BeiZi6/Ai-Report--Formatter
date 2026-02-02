from docx import Document

from formatter.config import FormatConfig
from formatter.docx_builder import build_docx


def test_build_docx_creates_docx(tmp_path):
    ast = [
        {"type": "heading", "level": 1, "text": "Title"},
        {"type": "paragraph", "text": "Hello"},
    ]
    output = tmp_path / "out.docx"
    build_docx(ast, output, FormatConfig())
    assert output.exists()


def test_build_docx_renders_bold_runs(tmp_path):
    ast = [
        {
            "type": "paragraph",
            "text": "Hello Bold",
            "runs": [
                {"text": "Hello ", "bold": False},
                {"text": "Bold", "bold": True},
            ],
        }
    ]
    output = tmp_path / "out.docx"
    build_docx(ast, output, FormatConfig())
    assert output.exists()

    doc = Document(output)
    runs = doc.paragraphs[0].runs
    assert runs[0].text == "Hello "
    assert runs[1].text == "Bold"
    assert runs[1].bold is True
