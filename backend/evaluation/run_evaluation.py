
import json
import time
from pathlib import Path

from backend.app import chunks, search_engine
from backend.generation.llm import generate_answer
from backend.evaluation.evaluator import evaluate_response
from backend.evaluation.test_dataset import EVALUATION_DATASET


def run_evaluation():
    """Run the EvidenceAI evaluation dataset."""

    if not chunks:
        print("No PDF documents are loaded.")
        print("Upload at least one PDF before evaluating.")
        return

    results_summary = []

    print("\n===================================")
    print("       EvidenceAI Evaluation")
    print("===================================\n")

    for index, test_case in enumerate(
        EVALUATION_DATASET, start=1
    ):
        question = test_case["question"]

        print(f"\nTest {index}/{len(EVALUATION_DATASET)}")
        print("Question:", question)

        # Step 1: Retrieve relevant chunks
        start_time = time.time()

        retrieved_chunks = search_engine.search(
            question,
            top_k=5,
        )

        if not retrieved_chunks:
            print("No relevant chunks retrieved.")
            continue

        # Step 2: Generate answer and verified sources
        answer, verified_sources = generate_answer(
            question,
            retrieved_chunks,
        )

        response_time = time.time() - start_time

        # Step 3: Debug citation verification
        print("\n========== DEBUG VERIFIED SOURCES ==========")
        print("Sources type:", type(verified_sources))
        print("Sources value:")
        print(repr(verified_sources))

        print("\nAnswer citation matches:")
        import re

        citation_pattern = (
            r"\[Source\s+\d+\s*:\s*.+?,\s*Page\s*\d+\]"
        )

        citations = re.findall(
            citation_pattern,
            answer,
            flags=re.IGNORECASE,
        )

        print("Detected citations:", citations)
        print("Number of citations:", len(citations))
        print("============================================")

        # Step 4: Evaluate the response
        metrics = evaluate_response(
            question=question,
            answer=answer,
            retrieved_chunks=retrieved_chunks,
            verified_sources=verified_sources,
            expected_keywords=test_case[
                "expected_keywords"
            ],
            relevant_keywords=test_case[
                "relevant_keywords"
            ],
            response_time=response_time,
        )

        results_summary.append(metrics)

        # Step 5: Display the generated answer
        print("\nAnswer:")
        print(answer)

        print("\nEvaluation Metrics:")
        print(
            json.dumps(
                metrics,
                indent=4,
                ensure_ascii=False,
            )
        )

    # Step 6: Calculate average metrics
    if not results_summary:
        print("\nNo evaluation results were generated.")
        return

    metric_names = [
        "retrieval_precision",
        "answer_coverage",
        "citation_accuracy",
        "response_time_seconds",
    ]

    averages = {}

    for metric in metric_names:
        averages[metric] = round(
            sum(
                item[metric]
                for item in results_summary
            )
            / len(results_summary),
            3,
        )

    print("\n===================================")
    print("       FINAL EVALUATION")
    print("===================================")

    print(json.dumps(averages, indent=4))

    # Step 7: Save results to a JSON file
    output_path = (
        Path(__file__).parent
        / "evaluation_results.json"
    )

    output_data = {
        "total_tests": len(results_summary),
        "average_metrics": averages,
        "individual_results": results_summary,
    }

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            output_data,
            output_file,
            indent=4,
            ensure_ascii=False,
        )

    print("\nResults saved to:")
    print(output_path)


if __name__ == "__main__":
    run_evaluation()