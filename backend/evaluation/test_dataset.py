
"""
Evaluation dataset for EvidenceAI.

Questions and keywords are based on the actual PDF
documents currently loaded in the project.
"""

EVALUATION_DATASET = [

    # ---------------------------------
    # 1. Solar System
    # ---------------------------------
    {
        "question": "How many planets are in the Solar System?",
        "expected_keywords": [
            "eight planets",
            "Solar System",
        ],
        "relevant_keywords": [
            "eight planets",
            "Solar System",
        ],
    },

    # ---------------------------------
    # 2. Earth
    # ---------------------------------
    {
        "question": "What percentage of Earth's surface is covered by water?",
        "expected_keywords": [
            "71 percent",
            "water",
        ],
        "relevant_keywords": [
            "Earth",
            "71 percent",
            "water",
        ],
    },

    # ---------------------------------
    # 3. Mars
    # ---------------------------------
    {
        "question": "Why is Mars called the Red Planet?",
        "expected_keywords": [
            "Red Planet",
            "iron minerals",
            "reddish color",
        ],
        "relevant_keywords": [
            "Mars",
            "iron minerals",
            "reddish color",
        ],
    },

    # ---------------------------------
    # 4. Artificial Intelligence
    # ---------------------------------
    {
        "question": "What is artificial intelligence?",
        "expected_keywords": [
            "artificial intelligence",
            "human intelligence",
            "recognizing patterns",
        ],
        "relevant_keywords": [
            "artificial intelligence",
            "intelligent systems",
            "human intelligence",
        ],
    },

    # ---------------------------------
    # 5. Machine Learning
    # ---------------------------------
    {
        "question": "How do machine learning systems learn?",
        "expected_keywords": [
            "machine learning",
            "learn patterns",
            "examples",
        ],
        "relevant_keywords": [
            "machine learning",
            "training data",
            "learn patterns",
        ],
    },

    # ---------------------------------
    # 6. Deep Learning
    # ---------------------------------
    {
        "question": "What type of neural networks does deep learning use?",
        "expected_keywords": [
            "deep learning",
            "neural networks",
            "multiple layers",
        ],
        "relevant_keywords": [
            "deep learning",
            "neural networks",
            "multiple layers",
        ],
    },

    # ---------------------------------
    # 7. RAG
    # ---------------------------------
    {
        "question": "What is the purpose of Retrieval Augmented Generation?",
        "expected_keywords": [
            "Retrieval Augmented Generation",
            "information retrieval",
            "Large Language Models",
        ],
        "relevant_keywords": [
            "RAG",
            "retrieval",
            "LLM",
            "PDF",
        ],
    },

    # ---------------------------------
    # 8. Urban Gardening
    # ---------------------------------
    {
        "question": "How much direct sunlight do most edible plants need?",
        "expected_keywords": [
            "six to eight hours",
            "direct sunlight",
        ],
        "relevant_keywords": [
            "edible plants",
            "direct sunlight",
            "six to eight hours",
        ],
    },

    # ---------------------------------
    # 9. Gardening Containers
    # ---------------------------------
    {
        "question": "Why should gardening containers have drainage holes?",
        "expected_keywords": [
            "drainage holes",
            "waterlogging",
        ],
        "relevant_keywords": [
            "containers",
            "drainage holes",
            "waterlogging",
        ],
    },

    # ---------------------------------
    # 10. Python Programming
    # ---------------------------------
    {
        "question": "Why is Python useful for programming and IoT?",
        "expected_keywords": [
            "Python",
            "easy to read",
            "hardware platforms",
        ],
        "relevant_keywords": [
            "Python",
            "hardware platforms",
            "open-source",
            "programming",
        ],
    },

]