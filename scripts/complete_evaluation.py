
import json
import re
from pathlib import Path

from datasets import load_dataset
from engine.core import ingest_text

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data" / "evaluation_questions.json"
TARGET = 50


def normalize(text):
    return re.sub(r"\s+", " ", text).strip().casefold()


def main():
    questions = json.loads(FILE.read_text(encoding="utf-8"))
    seen = {item["question"] for item in questions}

    dataset = load_dataset(
        "hotpotqa/hotpot_qa",
        "distractor",
        split="train",
        streaming=True
    )

    for row in dataset:
        if len(questions) >= TARGET:
            break

        question = row["question"].strip()

        if question in seen:
            continue

        supporting_titles = list(
            dict.fromkeys(row["supporting_facts"]["title"])
        )

        if len(supporting_titles) != 2:
            continue

        context_titles = row["context"]["title"]
        context_sentences = row["context"]["sentences"]

        expected_docs = []
        valid = True

        for title in supporting_titles:
            matches = [
                i for i, context_title in enumerate(context_titles)
                if normalize(context_title) == normalize(title)
            ]

            if not matches:
                valid = False
                break

            index = matches[0]
            body = " ".join(context_sentences[index])

            # Unique name to prevent overwriting existing records.
            name = f"eval_{row['id']}_{len(expected_docs)}.txt"

            ingest_text(name, body)

            expected_docs.append(name)

        if not valid:
            continue

        questions.append({
            "id": row["id"],
            "question": question,
            "answer": row["answer"],
            "supporting_titles": supporting_titles,
            "expected_docs": expected_docs,
            "category": "multi_hop"
        })

        seen.add(question)

        print(f"Prepared {len(questions)}/{TARGET}", flush=True)

    FILE.write_text(
        json.dumps(questions, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nFinished.")
    print("Total questions:", len(questions))


if __name__ == "__main__":
    main()
