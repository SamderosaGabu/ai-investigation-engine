
from engine.core import client, COLLECTION
from qdrant_client.models import Filter, FieldCondition, MatchText

db = client()

for term in ["incident", "engineering"]:
    points, _ = db.scroll(
        collection_name=COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="name",
                    match=MatchText(text=term)
                )
            ]
        ),
        limit=20,
        with_payload=True,
        with_vectors=False
    )

    print(f"\nDocuments matching '{term}':")
    for point in points:
        print("Name:", point.payload.get("name"))
        print("ID:", point.payload.get("doc_id"))
