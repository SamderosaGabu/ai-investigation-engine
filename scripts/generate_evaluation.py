
import json
import re
from pathlib import Path

from datasets import load_dataset
from engine.core import client, COLLECTION

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "evaluation_questions.json"
TARGET = 50


def normalize(text):
    return re.sub(r"\s+", " ", text).strip().casefold()


def indexed_documents():
    """Build a lookup of titles actually present in Qdrant."""
    db = client()
    names = {}

    offset = None

    while True:
        points, offset = db.scroll(
            collection_name=COLLECTION,
            limit=1000,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        for point in points:
            payload = point.payload or {}
            name = payload.get("name", "")

            # Hotpot importer uses Title__number.txt
            if name.endswith(".txt") and "__" in name:
                title = name.rsplit("__", 1)[0]
                names.setdefault(normalize(title), set()).add(name)

        if offset is None:
            break

    return names


def main():
    print("Reading indexed document titles...")
    available = indexed_documents()

    print("Indexed HotpotQA titles:", len(available))
    print("Loading HotpotQA questions...")

    dataset = load_dataset(
        "hotpotqa/hotpot_qa",
        "distractor",
        split="train",
        streaming=True
    )

    questions = []
    seen = set()

    for row in dataset:
        question = row["question"].strip()

        if question in seen:
            continue

        supporting_titles = list(
            dict.fromkeys(row["supporting_facts"]["title"])
        )

        # Keep questions requiring two distinct source documents.
        if len(supporting_titles) != 2:
            continue

        expected_docs = []
        valid = True

        for title in supporting_titles:
            matches = available.get(normalize(title), set())

            if not matches:
                valid = False
                break

            # The importer normally creates one record per title
            # occurrence; keep all possible matches for inspection.
            expected_docs.append(sorted(matches))

        if not valid:
            continue

        questions.append({
            "id": row["id"],
            "question": question,
            "answer": row["answer"],
            "supporting_titles": supporting_titles,
            "expected_doc_candidates": expected_docs,
            "category": "multi_hop"
        })

        seen.add(question)

        print(f"Collected {len(questions)}/{TARGET}")

        if len(questions) >= TARGET:
            break

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT.write_text(
        json.dumps(questions, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nFinished.")
    print("Questions generated:", len(questions))
    print("Saved to:", OUTPUT)

    if len(questions) < TARGET:
        print(
            "WARNING: Fewer than 50 eligible questions were found. "
            "Do not claim a 50-question evaluation yet."
        )


if __name__ == "__main__":
    main()
