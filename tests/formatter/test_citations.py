from formatter.citations import build_bibliography_nodes, normalize_citations, parse_bibliography_sources


def test_normalize_citations_extracts_sorted_unique_refs():
    text = "This is a claim [2], duplicate [2], and another [1]."
    normalized, refs, key_number_map = normalize_citations(text)
    assert normalized == "This is a claim [2], duplicate [2], and another [1]."
    assert refs == ["[1]", "[2]"]
    assert key_number_map == {}


def test_normalize_citations_rewrites_key_refs_to_numeric_refs():
    text = "See [@smith2024] then [@doe2025]."
    normalized, refs, key_number_map = normalize_citations(text)

    assert normalized == "See [1] then [2]."
    assert refs == ["[1]", "[2]"]
    assert key_number_map == {1: "smith2024", 2: "doe2025"}


def test_parse_bibliography_sources_supports_manual_and_bibtex_entries():
    raw = """
[1] Manual source entry.
@article{smith2024,
  author = {Smith, John and Doe, Jane},
  title = {A Practical Study},
  journal = {Journal of Testing},
  year = {2024}
}
"""

    sources = parse_bibliography_sources(raw)
    assert sources["1"] == "Manual source entry."
    assert "smith, john" in sources["smith2024"].lower()
    assert "a practical study" in sources["smith2024"].lower()


def test_build_bibliography_nodes_uses_source_text_and_style():
    nodes = build_bibliography_nodes(
        refs=["[1]"],
        style="apa",
        sources={"1": "Wang, L. (2024). Report Writing."},
        key_number_map={},
    )

    bibliography = nodes[-1]
    assert bibliography["type"] == "list"
    assert bibliography["items"][0][0]["text"] == "Wang, L. (2024). Report Writing."
