def chunk_text(text: str, chunk_size: int = 100):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


if __name__ == "__main__":
    sample_text = (
        "Artificial Intelligence is a field of computer science. "
        "Machine Learning is a branch of Artificial Intelligence. "
        "Deep Learning uses neural networks to learn from data."
    )

    chunks = chunk_text(sample_text, chunk_size=10)

    print(f"Created {len(chunks)} chunks.")

    for i, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {i}:")
        print(chunk)