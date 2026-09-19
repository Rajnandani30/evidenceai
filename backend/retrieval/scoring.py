def normalize_scores(scores, reverse=False):
    if not scores:
        return []

    minimum = min(scores)
    maximum = max(scores)

    if maximum == minimum:
        return [1.0 for _ in scores]

    normalized = []

    for score in scores:
        value = (score - minimum) / (maximum - minimum)

        if reverse:
            value = 1 - value

        normalized.append(value)

    return normalized


if __name__ == "__main__":
    bm25_scores = [2.0, 5.0, 8.0]

    normalized_bm25 = normalize_scores(bm25_scores)

    print("Original BM25 scores:")
    print(bm25_scores)

    print("\nNormalized BM25 scores:")
    print(normalized_bm25)

    distances = [0.2, 0.5, 0.9]

    normalized_distances = normalize_scores(
        distances,
        reverse=True
    )

    print("\nOriginal distances:")
    print(distances)

    print("\nNormalized distances:")
    print(normalized_distances)