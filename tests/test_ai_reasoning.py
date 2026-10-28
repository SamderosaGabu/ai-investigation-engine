import uuid

from engine.core import (
    ingest_text,
    delete_document,
    search,
    all_chunks,
)


def test_ai_reasoning():
    # Create a unique fictional project
    tag = uuid.uuid4().hex[:12]
    project = f"ProjectZebra{tag}"

    first_name = f"{project}_A.txt"
    second_name = f"{project}_B.txt"

    # Create the first document
    first = ingest_text(
        name=first_name,
        text=f"{project} launched on March 10, 2025."
    )

    second = None

    try:
        # Create a second document with conflicting information
        second = ingest_text(
            name=second_name,
            text=f"{project} launched on April 20, 2025."
        )

        question = (
            f"What is the launch date of {project}? "
            "Do the sources disagree?"
        )

        # STEP 1: Verify both documents are stored
        stored = all_chunks()

        first_stored = any(
            p["name"] == first_name for p in stored
        )

        second_stored = any(
            p["name"] == second_name for p in stored
        )

        print("\n========== DATABASE CHECK ==========")
        print("First document stored:", first_stored)
        print("Second document stored:", second_stored)

        assert first_stored, "First document was not stored"
        assert second_stored, "Second document was not stored"

        # STEP 2: Retrieve up to 200 results
        retrieved = search(
            question,
            k=200,
            pool=200
        )

        # STEP 3: Find the rank of each test document
        first_rank = None
        second_rank = None

        for i, item in enumerate(retrieved, 1):
            if item["name"] == first_name:
                first_rank = i
                print(
                    "TEST DOCUMENT RANK:",
                    i,
                    "|",
                    first_name,
                    "| SCORE:",
                    item["score"]
                )

            if item["name"] == second_name:
                second_rank = i
                print(
                    "TEST DOCUMENT RANK:",
                    i,
                    "|",
                    second_name,
                    "| SCORE:",
                    item["score"]
                )

        print("\n========== RETRIEVAL CHECK ==========")
        print("First document rank:", first_rank)
        print("Second document rank:", second_rank)

        print(
            "First document in top 20:",
            first_rank is not None and first_rank <= 20
        )

        print(
            "Second document in top 20:",
            second_rank is not None and second_rank <= 20
        )

        # STEP 4: Verify both documents are in the top 200
        assert first_rank is not None, (
            "First document missing from top 200"
        )

        assert second_rank is not None, (
            "Second document missing from top 200"
        )

    finally:
        # Always remove temporary test documents
        delete_document(first["doc_id"])

        if second is not None:
            delete_document(second["doc_id"])