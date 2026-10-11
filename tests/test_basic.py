def test_basic_math():
    assert 2 + 3 == 5


def test_text_normalization():
    text = "EvidenceAI"
    assert text.lower() == "evidenceai"