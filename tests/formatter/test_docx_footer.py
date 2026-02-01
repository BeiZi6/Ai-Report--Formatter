from docx import Document

from formatter.config import FormatConfig
from formatter.docx_builder import build_docx


def test_footer_contains_page_field(tmp_path):
    output = tmp_path / "out.docx"
    build_docx([{"type": "paragraph", "text": "Hello"}], output, FormatConfig())
    doc = Document(output)
    footer_xml = doc.sections[0].footer._element.xml
    assert "PAGE" in footer_xml
