import csv
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "chunk_retrieval_comparison.csv"

DATABASES = {
    "characters": "data/qdrant_chunk_test",
    "paragraphs": "data/qdrant_paragraphs",
}


def evaluate_database(strategy, db_path):
    env = os.environ.copy()
    env["QDRANT_DATA_PATH"] = db_path

    code = """
import json
from engine.core import all_chunks, search

chunks = all_chunks()

documents = {}
for chunk in chunks:
    documents.setdefault(chunk["doc_id"], chunk)

questions = []

for doc in list(documents.values())[:30]:
    text = doc["text"]
    words = text.split()

    if len(words) < 12:
        continue

    question = "Find the document containing: " + " ".join(words[:12])

    questions.append({
        "question": question,
        "expected": doc["doc_id"]
    })

results = []

for item in questions:
    retrieved = search(item["question"], k=10)

    ids = [result["doc_id"] for result in retrieved]

    rank = ids.index(item["expected"]) + 1 if item["expected"] in ids else None

    results.append({
        "recall": int(rank is not None),
        "mrr": 1 / rank if rank else 0
    })

print(json.dumps({
    "questions": len(results),
    "recall_at_10": sum(r["recall"] for r in results) / len(results),
    "mrr_at_10": sum(r["mrr"] for r in results) / len(results)
}))
"""

    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    return {
        "strategy": strategy,
        **__import__("json").loads(result.stdout.strip().splitlines()[-1]),
    }


def main():
    results = []

    for strategy, db_path in DATABASES.items():
        print(f"Evaluating {strategy}...", flush=True)
        result = evaluate_database(strategy, db_path)
        results.append(result)
        print(result)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nSaved comparison to: {OUTPUT}")


if __name__ == "__main__":
    main()