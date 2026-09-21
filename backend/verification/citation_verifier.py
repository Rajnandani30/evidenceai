def verify_citations(answer, documents):
    verified_sources = []

    answer_lower = answer.lower()

    for document in documents:
        file_name = document["file_name"]

        if file_name.lower() in answer_lower:
            verified_sources.append(file_name)

    return verified_sources


if __name__ == "__main__":
    sample_answer = (
        "Machine Learning allows computers to learn patterns from data "
        "[Source 1: machine_learning.txt]."
    )

    sample_documents = [
        {
            "file_name": "machine_learning.txt",
            "text": "Machine Learning allows computers to learn patterns from data."
        },
        {
            "file_name": "ai_basics.txt",
            "text": "Artificial Intelligence is a field of computer science."
        },
    ]

    sources = verify_citations(
        sample_answer,
        sample_documents
    )

    print("Verified Sources:")

    for source in sources:
        print("-", source)