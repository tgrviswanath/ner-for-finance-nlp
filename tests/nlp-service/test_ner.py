import pytest
from app.core.entities import ENTITY_META, FINANCE_PATTERNS


def test_entity_meta_has_required_keys():
    for label, meta in ENTITY_META.items():
        assert "label" in meta
        assert "color" in meta
        assert "icon" in meta


def test_finance_patterns_have_label_and_pattern():
    for p in FINANCE_PATTERNS:
        assert "label" in p
        assert "pattern" in p


def test_extract_entities():
    # Only run if spaCy model is installed
    pytest.importorskip("spacy")
    try:
        from app.core.service import extract_entities
        result = extract_entities(
            "Apple Inc. reported revenue of $119.6 billion in Q1 2024. "
            "CEO Tim Cook said EPS reached $2.18. Ticker AAPL rose 3.5%."
        )
        assert "entities" in result
        assert "by_label" in result
        assert "label_counts" in result
        assert result["total"] >= 0
    except OSError:
        pytest.skip("spaCy model not installed")
