
from pathlib import Path

from qdrant_client import QdrantClient


def test_development_database():
    root = Path(__file__).resolve().parents[1]
    database_path = root / "data" / "qdrant_dev"

    client = QdrantClient(path=str(database_path))

    try:
        collection = "investigation_chunks"

        assert client.collection_exists(collection), (
            "Development collection does not exist"
        )

        count = client.count(
            collection_name=collection,
            exact=True,
        ).count

        assert count == 2000, (
            f"Expected 2000 records, found {count}"
        )
    finally:
        client.close()


from engine.core import search


def test_search_returns_results():
    results = search(
        query="What happened during the payment service outage?",
        k=5
    )

    assert isinstance(results, list), (
        "Search should return a list"
    )

    assert len(results) > 0, (
        "Search returned no results"
    )

    for result in results:
        assert "text" in result, (
            "Search result is missing text"
        )

        assert "score" in result, (
            "Search result is missing a ranking score"
        )

import uuid

from engine.core import ingest_text, documents, delete_document


def test_document_ingestion_and_deletion():
    unique_id = uuid.uuid4().hex[:8]
    filename = f"pytest_document_{unique_id}.txt"

    text = (
        "Project Phoenix is a fictional research initiative. "
        "Its primary goal is to investigate renewable energy systems."
    )

    # 1. Add a document
    result = ingest_text(filename, text)

    doc_id = result["doc_id"]

    try:
        # 2. Check ingestion
        assert doc_id is not None
        assert result["chunks"] > 0

        # 3. Check that the document appears in the database
        stored_documents = documents()

        assert any(
            doc["doc_id"] == doc_id
            for doc in stored_documents
        ), "Ingested document was not found"

    finally:
        # 4. Delete the test document
        delete_document(doc_id)

    # 5. Verify deletion
    stored_documents = documents()

    assert not any(
        doc["doc_id"] == doc_id
        for doc in stored_documents
    ), "Document was not deleted"
