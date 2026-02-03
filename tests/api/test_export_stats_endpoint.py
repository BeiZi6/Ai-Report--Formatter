from fastapi.testclient import TestClient

from apps.api.main import app


def _base_generate_payload():
    return {
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
        },
    }


def test_export_stats_starts_at_zero(tmp_path, monkeypatch):
    db_path = tmp_path / "export_counts.db"
    monkeypatch.setenv("EXPORT_DB_PATH", str(db_path))
    client = TestClient(app)

    response = client.get("/api/exports/stats")

    assert response.status_code == 200
    payload = response.json()
    assert payload["today"] == 0
    assert payload["total"] == 0


def test_generate_increments_export_stats(tmp_path, monkeypatch):
    db_path = tmp_path / "export_counts.db"
    monkeypatch.setenv("EXPORT_DB_PATH", str(db_path))
    client = TestClient(app)

    before = client.get("/api/exports/stats").json()
    response = client.post("/api/generate", json=_base_generate_payload())
    after = client.get("/api/exports/stats").json()

    assert response.status_code == 200
    assert after["today"] == before["today"] + 1
    assert after["total"] == before["total"] + 1
