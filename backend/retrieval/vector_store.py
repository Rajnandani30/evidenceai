import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)

    def add_embeddings(self, embeddings):
        embeddings = np.array(embeddings).astype("float32")
        self.index.add(embeddings)

    def search(self, query_embedding, top_k: int = 3):
        query_embedding = np.array(query_embedding).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        return distances, indices


if __name__ == "__main__":
    embeddings = np.array(
        [
            [0.1, 0.2, 0.3],
            [0.2, 0.3, 0.4],
            [0.9, 0.8, 0.7],
        ],
        dtype="float32",
    )

    store = VectorStore(dimension=3)

    store.add_embeddings(embeddings)

    query = np.array([[0.15, 0.25, 0.35]], dtype="float32")

    distances, indices = store.search(query, top_k=2)

    print("Distances:", distances)
    print("Indices:", indices)