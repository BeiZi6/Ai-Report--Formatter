from fastapi.testclient import TestClient

from apps.api.main import app


def test_preview_endpoint_returns_summary_and_refs():
    client = TestClient(app)
    response = client.post(
        "/api/preview",
        json={"markdown": "# Title\n\nHello [1]."},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["headings"] == 1
    assert payload["refs"] == ["[1]"]
    assert payload["lint_warnings"] == []
    assert payload["quality_report"]["stats"]["refs"] == 1


def test_preview_endpoint_includes_html_preview():
    client = TestClient(app)
    response = client.post(
        "/api/preview",
        json={
            "markdown": "Inline `code`\n\n| A | B |\n| --- | --- |\n| 1 | 2 |",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    html = payload.get("preview_html", "")
    assert "<code>" in html
    assert "<table" in html


def test_preview_endpoint_returns_structure_warnings():
    client = TestClient(app)
    response = client.post(
        "/api/preview",
        json={"markdown": "# 一级\n\n#### 四级"},
    )

    assert response.status_code == 200
    payload = response.json()
    codes = {item["code"] for item in payload["lint_warnings"]}
    assert "heading_level_jump" in codes


def test_preview_endpoint_supports_bibliography_source_manager():
    client = TestClient(app)
    response = client.post(
        "/api/preview",
        json={
            "markdown": "# Title\n\nSee [@smith2024].",
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
    payload = response.json()
    assert payload["refs"] == ["[1]"]
