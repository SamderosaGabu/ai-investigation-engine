import pytest

from engine.core import chunk_text


def test_character_chunks():
    text = "abcde" * 200
    result = chunk_text(text, size=100, overlap=20)

    assert len(result) > 1
    assert all(len(x) <= 100 for x in result)

    for first, second in zip(result, result[1:]):
        assert first[-20:] == second[:20]


def test_paragraph_chunks():
    text = (
        "First paragraph contains project information.\n\n"
        "Second paragraph describes the investigation.\n\n"
        "Third paragraph explains the findings."
    )

    result = chunk_text(
        text,
        size=85,
        overlap=10,
        strategy="paragraphs"
    )

    assert len(result) >= 2

    combined = " ".join(result)

    assert "First paragraph" in combined
    assert "Second paragraph" in combined
    assert "Third paragraph" in combined


def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text(
            "Some text",
            size=100,
            overlap=100,
            strategy="characters"
        )


def test_empty_text():
    assert chunk_text("", strategy="characters") == []
    assert chunk_text("", strategy="paragraphs") == []