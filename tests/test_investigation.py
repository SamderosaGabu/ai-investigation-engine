
import uuid

from engine.core import ingest_text, search, delete_document


def test_conflicting_evidence_retrieval():
    tag = uuid.uuid4().hex[:8]
    project = f"Project-{tag}"

    first = ingest_text(
        f"{project}_report_A.txt",
        f"{project} launched on March 10, 2025."
    )

    second = None

    try:
        second = ingest_text(
            f"{project}_report_B.txt",
            f"{project} launched on April 20, 2025."
        )

        results = search(
            f"When did {project} launch?",
            k=20
        )

        texts = [r["text"] for r in results]

        assert any(
            "March 10, 2025" in t for t in texts
        ), "First source was not retrieved"

        assert any(
            "April 20, 2025" in t for t in texts
        ), "Conflicting source was not retrieved"

    finally:
        delete_document(first["doc_id"])

        if second is not None:
            delete_document(second["doc_id"])
