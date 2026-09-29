
"""
Sample evaluation dataset for EvidenceAI.

Update the questions and keywords to match
the actual PDFs uploaded into your project.
"""

EVALUATION_DATASET = [
    {
        "question": "What is artificial intelligence?",
        "expected_keywords": [
            "artificial intelligence",
            "machines",
            "human intelligence",
        ],
        "relevant_keywords": [
            "artificial intelligence",
            "intelligent systems",
        ],
    },
    {
        "question": "What is machine learning?",
        "expected_keywords": [
            "machine learning",
            "data",
            "learning",
        ],
        "relevant_keywords": [
            "machine learning",
            "training data",
        ],
    },
    {
        "question": "What is deep learning?",
        "expected_keywords": [
            "deep learning",
            "neural networks",
        ],
        "relevant_keywords": [
            "deep learning",
            "neural networks",
        ],
    },
]