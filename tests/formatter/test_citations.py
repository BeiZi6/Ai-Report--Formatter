from formatter.citations import normalize_citations


def test_normalize_citations_extracts_sorted_unique_refs():
    text = "This is a claim [2], duplicate [2], and another [1]."
    normalized, refs = normalize_citations(text)
    assert normalized == "This is a claim [2], duplicate [2], and another [1]."
    assert refs == ["[1]", "[2]"]
