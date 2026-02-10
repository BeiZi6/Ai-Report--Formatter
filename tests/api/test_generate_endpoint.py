import io

from fastapi.testclient import TestClient

from apps.api.main import app


def test_generate_endpoint_returns_docx():
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        json={
            "markdown": "# Title\n\nHello.",
            "config": {
                "cn_font": "SimSun",
                "en_font": "Times New Roman",
                "heading_cn_font": "SimHei",
                "heading_en_font": "Times New Roman",
                "heading1_size_pt": 16,
                "heading2_size_pt": 16,
                "heading3_size_pt": 16,
                "heading4_size_pt": 16,
                "heading_line_spacing": 1.5,
                "heading_para_before_lines": 0.0,
                "heading_para_after_lines": 0.0,
                "body_size_pt": 12,
                "line_spacing": 1.5,
                "para_before_lines": 0.0,
                "para_after_lines": 0.0,
                "indent_before_chars": 0,
                "indent_after_chars": 0,
                "first_line_indent_chars": 2,
                "justify": True,
                "clear_background": True,
                "page_num_position": "center",
                "figure_max_width_cm": 14.0,
                "figure_align": "center",
            },
            "bibliography": {"style": "ieee", "sources_text": ""},
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(response.content) > 0


def test_generate_endpoint_accepts_paragraph_units():
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        json={
            "markdown": "# Title\n\nHello.",
            "config": {
                "cn_font": "SimSun",
                "en_font": "Times New Roman",
                "heading_cn_font": "SimHei",
                "heading_en_font": "Times New Roman",
                "heading1_size_pt": 14,
                "heading2_size_pt": 14,
                "heading3_size_pt": 14,
                "heading4_size_pt": 14,
                "heading_line_spacing": 1.25,
                "heading_para_before_lines": 0.5,
                "heading_para_after_lines": 0.5,
                "body_size_pt": 12,
                "line_spacing": 1.25,
                "para_before_lines": 0.0,
                "para_after_lines": 0.0,
                "indent_before_chars": 0,
                "indent_after_chars": 0,
                "first_line_indent_chars": 2,
                "justify": True,
                "clear_background": True,
                "page_num_position": "center",
                "figure_max_width_cm": 14.0,
                "figure_align": "center",
            },
            "bibliography": {"style": "ieee", "sources_text": ""},
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(response.content) > 0


def test_generate_endpoint_builds_docx_in_memory_stream(monkeypatch):
    client = TestClient(app)
    captured = {"is_bytes_io": False}

    def fake_build_docx(ast, output_path, config=None):
        captured["is_bytes_io"] = isinstance(output_path, io.BytesIO)
        output_path.write(b"fake-docx-bytes")

    monkeypatch.setattr("apps.api.main.build_docx", fake_build_docx)

    response = client.post(
        "/api/generate",
        json={
            "markdown": "# Title\n\nHello.",
            "config": {
                "cn_font": "SimSun",
                "en_font": "Times New Roman",
                "heading_cn_font": "SimHei",
                "heading_en_font": "Times New Roman",
                "heading1_size_pt": 16,
                "heading2_size_pt": 16,
                "heading3_size_pt": 16,
                "heading4_size_pt": 16,
                "heading_line_spacing": 1.5,
                "heading_para_before_lines": 0.0,
                "heading_para_after_lines": 0.0,
                "body_size_pt": 12,
                "line_spacing": 1.5,
                "para_before_lines": 0.0,
                "para_after_lines": 0.0,
                "indent_before_chars": 0,
                "indent_after_chars": 0,
                "first_line_indent_chars": 2,
                "justify": True,
                "clear_background": True,
                "page_num_position": "center",
                "figure_max_width_cm": 14.0,
                "figure_align": "center",
            },
            "bibliography": {"style": "ieee", "sources_text": ""},
        },
    )

    assert response.status_code == 200
    assert captured["is_bytes_io"] is True
    assert response.content == b"fake-docx-bytes"


def test_generate_endpoint_accepts_bibliography_and_figure_settings():
    client = TestClient(app)
    response = client.post(
        "/api/generate",
        json={
            "markdown": "# Title\n\n![图](https://example.com/a.png)\n\nSee [@smith2024].",
            "config": {
                "cn_font": "SimSun",
                "en_font": "Times New Roman",
                "heading_cn_font": "SimHei",
                "heading_en_font": "Times New Roman",
                "heading1_size_pt": 14,
                "heading2_size_pt": 14,
                "heading3_size_pt": 14,
                "heading4_size_pt": 14,
                "heading_line_spacing": 1.25,
                "heading_para_before_lines": 0.5,
                "heading_para_after_lines": 0.5,
                "body_size_pt": 12,
                "line_spacing": 1.25,
                "para_before_lines": 0,
                "para_after_lines": 0,
                "indent_before_chars": 0,
                "indent_after_chars": 0,
                "first_line_indent_chars": 2,
                "justify": True,
                "clear_background": True,
                "page_num_position": "center",
                "figure_max_width_cm": 12.0,
                "figure_align": "right",
            },
            "bibliography": {
                "style": "ieee",
                "sources_text": """
@article{smith2024,
  author = {Smith, John},
  title = {A Practical Study},
  journal = {Journal of Testing},
  year = {2024}
}
""",
            },
        },
    )

    assert response.status_code == 200
