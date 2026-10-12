"""
Evaluation dataset for EvidenceAI.

Questions and keywords are based on the PDF documents
currently loaded in the project.
"""

EVALUATION_DATASET = [

    # 1. Artificial Intelligence
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

    # 2. Machine Learning
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

    # 3. Deep Learning
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

    # 4. Retrieval Augmented Generation
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

    # 5. Urban Gardening
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

    # 6. Gardening Containers
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

    # 7. Machine Learning Training Data
    {
        "question": "What role does training data play in machine learning?",
        "expected_keywords": [
            "training data",
            "machine learning",
            "patterns",
        ],
        "relevant_keywords": [
            "training data",
            "examples",
            "learn patterns",
        ],
    },

    # 8. Neural Network Structure
    {
        "question": "How do multiple layers help a deep learning model?",
        "expected_keywords": [
            "multiple layers",
            "neural networks",
            "features",
        ],
        "relevant_keywords": [
            "deep learning",
            "multiple layers",
            "features",
        ],
    },

    # 9. RAG and External Information
    {
        "question": "How does retrieval help a language model answer questions?",
        "expected_keywords": [
            "retrieval",
            "relevant information",
            "language model",
        ],
        "relevant_keywords": [
            "retrieval",
            "documents",
            "language model",
        ],
    },

    # 10. Gardening Sunlight
    {
        "question": "Why is sunlight important for edible plants?",
        "expected_keywords": [
            "sunlight",
            "edible plants",
            "growth",
        ],
        "relevant_keywords": [
            "direct sunlight",
            "plant growth",
            "edible plants",
        ],
    },

    # 11. Gardening Drainage
    {
        "question": "What can happen if excess water cannot drain from a plant container?",
        "expected_keywords": [
            "excess water",
            "drainage",
            "waterlogging",
        ],
        "relevant_keywords": [
            "drainage holes",
            "excess water",
            "roots",
        ],
    },

    # 12. AI and Pattern Recognition
    {
        "question": "How can artificial intelligence recognize patterns in information?",
        "expected_keywords": [
            "artificial intelligence",
            "recognizing patterns",
            "information",
        ],
        "relevant_keywords": [
            "AI",
            "patterns",
            "intelligent systems",
        ],
    },

]
