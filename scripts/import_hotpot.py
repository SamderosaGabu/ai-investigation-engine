import argparse
from datasets import load_dataset
from engine.core import ingest_batch

parser = argparse.ArgumentParser()
parser.add_argument("--max-records", type=int, default=50000)
parser.add_argument("--batch-size", type=int, default=128)
parser.add_argument(
    "--strategy",
    choices=["original", "characters", "paragraphs"],
    default="original"
)
args = parser.parse_args()

ds = load_dataset(
    "hotpotqa/hotpot_qa",
    "distractor",
    split="train",
    streaming=True
)

seen = set()
buffer = []
count = 0

for row in ds:
    for title, sentences in zip(
        row["context"]["title"],
        row["context"]["sentences"]
    ):
        body = " ".join(sentences).strip()

        if not body:
            continue

        key = body

        if key in seen:
            continue

        seen.add(key)
        buffer.append((title, body))
        count += 1

        if len(buffer) >= args.batch_size:
            ingest_batch(
                buffer,
                batch_size=args.batch_size,
                strategy=None if args.strategy == "original" else args.strategy
            )
            buffer.clear()
            print(f"Indexed {count} records", flush=True)

        if count >= args.max_records:
            break

    if count >= args.max_records:
        break

if buffer:
    ingest_batch(
        buffer,
        batch_size=args.batch_size,
        strategy=None if args.strategy == "original" else args.strategy
    )

print(f"Done: {count} records processed")
