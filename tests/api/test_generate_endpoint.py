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
                "heading_font": "SimHei",
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
            },
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
                "heading_font": "SimHei",
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
            },
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(response.content) > 0
