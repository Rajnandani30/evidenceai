
import pytest

from backend.evaluation.evaluator import (
    calculate_retrieval_precision,
)


def test_default_threshold_preserves_one_keyword_behavior():
    chunks = [
        {"text": "Machine learning uses training data."},
        {"text": "Urban gardening needs sunlight."},
    ]

    keywords = ["machine learning", "training data"]

    score = calculate_retrieval_precision(chunks, keywords)

    assert score == 0.5


def test_two_keyword_threshold_is_stricter():
    chunks = [
        {"text": "Machine learning uses training data."},
        {"text": "Machine learning is useful."},
        {"text": "Urban gardening needs sunlight."},
    ]

    keywords = ["machine learning", "training data"]

    score = calculate_retrieval_precision(
        chunks,
        keywords,
        min_keyword_matches=2,
    )

    assert score == pytest.approx(1 / 3)


def test_empty_chunks_return_zero():
    score = calculate_retrieval_precision(
        [],
        ["machine learning"],
    )

    assert score == 0.0


def test_invalid_threshold_is_rejected():
    with pytest.raises(ValueError):
        calculate_retrieval_precision(
            [{"text": "Machine learning"}],
            ["machine learning"],
            min_keyword_matches=0,
        )
