
import csv
import json
from pathlib import Path

from engine.core import search, search_improved
from scripts.evaluate import expected_groups

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "data" / "evaluation_questions.json"
OUTPUT_FILE = ROOT / "data" / "ranking_comparison.csv"


def calculate_metrics(results, groups):
    retrieved = [item["name"] for item in results]

    matched = 0
    first_rank = None

    for group in groups:
        ranks = [
            rank
            for rank, name in enumerate(retrieved, start=1)
            if name in group
        ]

        if ranks:
            matched += 1
            rank = min(ranks)

            if first_rank is None or rank < first_rank:
                first_rank = rank

    return {
        "recall": matched / len(groups),
        "mrr": 1 / first_rank if first_rank else 0.0,
        "complete": int(matched == len(groups))
    }


def main():
    questions = json.loads(
        TEST_FILE.read_text(encoding="utf-8")
    )

    rows = []

    for index, item in enumerate(questions, start=1):
        groups = expected_groups(item)

        baseline = search(item["question"], k=10)
        improved = search_improved(item["question"], k=10)

        baseline_metrics = calculate_metrics(baseline, groups)
        improved_metrics = calculate_metrics(improved, groups)

        rows.append({
            "question": item["question"],
            "baseline_recall": baseline_metrics["recall"],
            "improved_recall": improved_metrics["recall"],
            "baseline_mrr": baseline_metrics["mrr"],
            "improved_mrr": improved_metrics["mrr"],
            "baseline_complete": baseline_metrics["complete"],
            "improved_complete": improved_metrics["complete"]
        })

        print(
            f"[{index}/{len(questions)}] "
            f"Baseline={baseline_metrics['recall']:.2f} "
            f"Improved={improved_metrics['recall']:.2f}",
            flush=True
        )

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file, fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

    print("\nFINAL COMPARISON")
    print("-" * 45)

    for metric in ("recall", "mrr", "complete"):
        a = sum(row[f"baseline_{metric}"] for row in rows) / len(rows)
        b = sum(row[f"improved_{metric}"] for row in rows) / len(rows)

        print(
            f"{metric.upper():10s} "
            f"Baseline: {a:.3f} | "
            f"Improved: {b:.3f} | "
            f"Change: {b-a:+.3f}"
        )

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
