import uuid

from engine.core import (
    ingest_text,
    delete_document,
    investigate,
    search,
)


def test_gemini_reasoning():
    tag = uuid.uuid4().hex[:12]
    project = f"ProjectZebra{tag}"

    first = ingest_text(
        name=f"{project}_A.txt",
        text=f"{project} launched on March 10, 2025."
    )

    second = None

    try:
        second = ingest_text(
            name=f"{project}_B.txt",
            text=f"{project} launched on April 20, 2025."
        )

        # TEST 1: CONTRADICTION DETECTION
        question = (
            f"What is the launch date of {project}? "
            "Do the sources disagree?"
        )

        # Verify retrieval BEFORE spending Gemini quota
        retrieved = search(question, k=8)
        names = {item["name"] for item in retrieved}

        assert f"{project}_A.txt" in names, (
            "First source missing from top 8"
        )
        assert f"{project}_B.txt" in names, (
            "Second source missing from top 8"
        )

        contradiction = investigate(question, k=8)

        print("\n========== CONTRADICTION ANSWER ==========")
        print(contradiction["answer"])
        print("Status:", contradiction["status"])

        assert contradiction["status"] == "ok", (
            f"Gemini unavailable: {contradiction['status']}"
        )

        answer = contradiction["answer"].lower()

        assert "march 10" in answer
        assert "april 20" in answer
        assert "[s" in answer, "Missing source citations"

        # TEST 2: ABSTENTION
        question_unknown = (
            f"What was the exact launch budget of {project}?"
        )

        # Verify relevant evidence is retrieved
        unknown_results = search(question_unknown, k=8)
        unknown_names = {item["name"] for item in unknown_results}

        assert (
            f"{project}_A.txt" in unknown_names
            or f"{project}_B.txt" in unknown_names
        ), "Project evidence missing from abstention search"

        abstention = investigate(question_unknown, k=8)

        print("\n========== ABSTENTION ANSWER ==========")
        print(abstention["answer"])
        print("Status:", abstention["status"])

        assert abstention["status"] == "ok", (
            f"Gemini unavailable: {abstention['status']}"
        )

        answer_unknown = abstention["answer"].lower()

        abstention_phrases = [
            "not provided",
            "not specified",
            "not stated",
            "insufficient evidence",
            "does not contain information",
            "cannot determine",
            "does not mention",
            "no information",
            "not available",
            "unknown",
        ]

        assert any(
            phrase in answer_unknown
            for phrase in abstention_phrases
        ), "Gemini did not clearly abstain"

    finally:
        # Remove temporary test documents
        delete_document(first["doc_id"])

        if second is not None:
            delete_document(second["doc_id"])