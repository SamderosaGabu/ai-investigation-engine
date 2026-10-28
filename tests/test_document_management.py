import uuid

from engine.core import ingest_text, all_chunks, delete_document


def test_document_update():
    name = f"UpdateTest_{uuid.uuid4().hex}.txt"

    try:
        first = ingest_text(name, "The project budget is 100 euros.")
        doc_id = first["doc_id"]

        # Re-ingest the same document with updated content
        ingest_text(name, "The project budget is 250 euros.")

        chunks = [
            p for p in all_chunks()
            if p["doc_id"] == doc_id
        ]

        assert chunks, "Updated document is missing"
        assert any("250 euros" in p["text"] for p in chunks)
        assert not any("100 euros" in p["text"] for p in chunks)

    finally:
        delete_document(doc_id)


def test_document_deduplication():
    name = f"DedupTest_{uuid.uuid4().hex}.txt"
    doc_id = None

    try:
        first = ingest_text(name, "This is a unique test document.")
        doc_id = first["doc_id"]

        # Ingest identical content again
        ingest_text(name, "This is a unique test document.")

        chunks = [
            p for p in all_chunks()
            if p["doc_id"] == doc_id
        ]

        assert len(chunks) == 1, (
            f"Expected 1 chunk, found {len(chunks)}"
        )

    finally:
        if doc_id is not None:
            delete_document(doc_id)