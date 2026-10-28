import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

source = QdrantClient(path=str(ROOT / "data" / "qdrant"))
target = QdrantClient(path=str(ROOT / "data" / "qdrant_dev"))

collection = "investigation_chunks"

source_info = source.get_collection(collection)
vectors_config = source_info.config.params.vectors

if not target.collection_exists(collection):
    target.create_collection(
        collection_name=collection,
        vectors_config=vectors_config,
    )

offset = None
copied = 0

while copied < 2000:
    points, offset = source.scroll(
        collection_name=collection,
        limit=min(100, 2000 - copied),
        offset=offset,
        with_payload=True,
        with_vectors=True,
    )

    if not points:
        break

    target.upsert(
        collection_name=collection,
        points=[
            models.PointStruct(
                id=p.id,
                vector=p.vector,
                payload=p.payload,
            )
            for p in points
        ],
        wait=True,
    )

    copied += len(points)
    print(f"Copied {copied}/2000")

    if offset is None:
        break

print(f"\nDevelopment database ready: {copied} records")