
import csv
import json
from pathlib import Path

from engine.core import search

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "data" / "evaluation_questions.json"
OUTPUT_FILE = ROOT / "data" / "evaluation_results.csv"


def expected_groups(item):
    """
    Each group contains acceptable document filenames
    for one required supporting source.
    """
    if "expected_docs" in item:
        return [[name] for name in item["expected_docs"]]

    if "expected_doc_candidates" in item:
        return item["expected_doc_candidates"]

    if "expected_doc" in item:
        return [[item["expected_doc"]]]

    raise ValueError("Question has no expected documents")


def evaluate_question(item, k=10):
    results = search(item["question"], k=k)

    retrieved = [result["name"] for result in results]
    groups = expected_groups(item)

    matched = 0
    first_rank = None

    for group in groups:
        matching_ranks = [
            rank
            for rank, name in enumerate(retrieved, start=1)
            if name in group
        ]

        if matching_ranks:
            matched += 1
            rank = min(matching_ranks)

            if first_rank is None or rank < first_rank:
                first_rank = rank

    recall = matched / len(groups)
    reciprocal_rank = 1 / first_rank if first_rank else 0

    return {
        "id": item.get("id", ""),
        "question": item["question"],
        "category": item.get("category", "unknown"),
        "required_sources": len(groups),
        "matched_sources": matched,
        "recall_at_10": recall,
        "mrr_contribution": reciprocal_rank,
        "complete_evidence_at_10": int(matched == len(groups)),
        "retrieved_docs": json.dumps(retrieved)
    }


def main():
    questions = json.loads(
        TEST_FILE.read_text(encoding="utf-8")
    )

    if not questions:
        raise ValueError("Evaluation dataset is empty")

    results = []

    for index, item in enumerate(questions, start=1):
        result = evaluate_question(item, k=10)
        results.append(result)

        print(
            f"[{index}/{len(questions)}] "
            f"Recall@10={result['recall_at_10']:.2f} "
            f"MRR={result['mrr_contribution']:.2f} "
            f"Complete={result['complete_evidence_at_10']}",
            flush=True
        )

    n = len(results)

    mean_recall = sum(
        result["recall_at_10"] for result in results
    ) / n

    mrr = sum(
        result["mrr_contribution"] for result in results
    ) / n

    complete_rate = sum(
        result["complete_evidence_at_10"] for result in results
    ) / n

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 40)
    print("RETRIEVAL EVALUATION RESULTS")
    print("=" * 40)
    print(f"Questions: {n}")
    print(f"Recall@10: {mean_recall:.3f}")
    print(f"MRR@10: {mrr:.3f}")
    print(f"Complete Evidence@10: {complete_rate:.3f}")
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
