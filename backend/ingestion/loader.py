from pathlib import Path


def load_documents(data_folder: str):
    documents = []

    data_path = Path(data_folder)

    for file_path in data_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "file_name": file_path.name,
                "text": text,
            }
        )

    return documents


if __name__ == "__main__":
    documents = load_documents("data/sample_documents")

    print(f"Loaded {len(documents)} documents.")

    for document in documents:
        print(f"- {document['file_name']}")