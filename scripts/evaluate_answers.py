
import argparse
import csv
import json
import re
import time
from pathlib import Path

from engine.core import investigate

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "evaluation_questions.json"
OUTPUT = ROOT / "data" / "answer_evaluation.csv"
PROGRESS = ROOT / "data" / "answer_evaluation_progress.json"


def normalize(text):
    """Normalize text for simple answer comparison."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\b(a|an|the)\b", " ", text)
    return " ".join(text.split())


def answer_correctness(predicted, expected):
    """
    Compute exact match and token-level F1.

    These are automated proxy metrics, not proof that
    the answer is factually correct.
    """
    prediction = normalize(predicted)
    reference = normalize(expected)

    exact_match = int(prediction == reference)

    pred_tokens = prediction.split()
    ref_tokens = reference.split()

    if not pred_tokens or not ref_tokens:
        f1 = float(pred_tokens == ref_tokens)
        return exact_match, f1

    from collections import Counter

    common = Counter(pred_tokens) & Counter(ref_tokens)
    overlap = sum(common.values())

    if overlap == 0:
        return exact_match, 0.0

    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)

    f1 = 2 * precision * recall / (precision + recall)

    return exact_match, f1


def citation_metrics(answer, sources):
    """
    Validate citation markers and calculate how many
    source markers are referenced.

    Does NOT verify semantic support.
    """
    cited = set(re.findall(r"\[S\d+\]", answer))

    available = {
        f"[{source['ref']}]"
        for source in sources
        if source.get("ref")
    }

    valid = cited & available
    invalid = cited - available

    return {
        "citation_count": len(cited),
        "valid_citations": len(valid),
        "invalid_citations": len(invalid),
        "citation_validity": (
            len(valid) / len(cited) if cited else 0.0
        ),
        "has_citation": int(bool(cited)),
    }


def is_abstention(answer):
    """Heuristic detection of insufficient-evidence responses."""
    text = answer.lower()

    phrases = [
        "insufficient evidence",
        "not enough information",
        "cannot determine",
        "can't determine",
        "unable to determine",
        "no evidence available",
        "the evidence does not",
        "the documents do not",
    ]

    return int(any(phrase in text for phrase in phrases))


def load_previous_results():
    if PROGRESS.exists():
        return json.loads(PROGRESS.read_text(encoding="utf-8"))
    return {}


def save_progress(results):
    PROGRESS.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def evaluate_one(item):
    question = item["question"]
    expected = str(item.get("answer", ""))

    started = time.perf_counter()

    try:
        response = investigate(question, k=8)
        latency = time.perf_counter() - started

        status = response.get("status", "unknown")
        answer = response.get("answer") or ""
        sources = response.get("sources") or []

        # Never score an API fallback as a generated answer.
        if status != "ok":
            return {
                "id": item.get("id", ""),
                "question": question,
                "expected_answer": expected,
                "generated_answer": answer,
                "status": status,
                "exact_match": 0,
                "token_f1": 0.0,
                "citation_count": 0,
                "valid_citations": 0,
                "invalid_citations": 0,
                "citation_validity": 0.0,
                "has_citation": 0,
                "abstained": 0,
                "latency_seconds": round(latency, 2),
                "sources_json": json.dumps(sources, ensure_ascii=False),
                "error": "",
            }

        exact, f1 = answer_correctness(answer, expected)
        citations = citation_metrics(answer, sources)

        return {
            "id": item.get("id", ""),
            "question": question,
            "expected_answer": expected,
            "generated_answer": answer,
            "status": status,
            "exact_match": exact,
            "token_f1": round(f1, 4),
            **citations,
            "abstained": is_abstention(answer),
            "latency_seconds": round(latency, 2),
            "sources_json": json.dumps(sources, ensure_ascii=False),
            "error": "",
        }

    except Exception as exc:
        return {
            "id": item.get("id", ""),
            "question": question,
            "expected_answer": expected,
            "generated_answer": "",
            "status": "api_error",
            "exact_match": 0,
            "token_f1": 0.0,
            "citation_count": 0,
            "valid_citations": 0,
            "invalid_citations": 0,
            "citation_validity": 0.0,
            "has_citation": 0,
            "abstained": 0,
            "latency_seconds": round(time.perf_counter() - started, 2),
            "sources_json": "[]",
            "error": f"{type(exc).__name__}: {str(exc)[:250]}",
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of questions to evaluate (default: 5)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3,
        help="Delay between API calls in seconds"
    )
    args = parser.parse_args()

    questions = json.loads(INPUT.read_text(encoding="utf-8"))
    questions = questions[:args.limit]

    results = load_previous_results()

    for index, item in enumerate(questions, start=1):
        key = item.get("id") or item["question"]

        if key in results and results[key]["status"] == "ok":
            print(f"[{index}/{len(questions)}] Already completed")
            continue

        print(
            f"[{index}/{len(questions)}] "
            f"Evaluating: {item['question'][:70]}",
            flush=True
        )

        result = evaluate_one(item)
        results[key] = result
        save_progress(results)

        print(
            f"Status={result['status']} "
            f"EM={result['exact_match']} "
            f"F1={result['token_f1']:.3f} "
            f"Citations={result['citation_count']}",
            flush=True
        )

        if result["status"] == "api_error":
            print("ERROR:", result["error"])

        if index < len(questions):
            time.sleep(args.delay)

    selected_keys = [
        item.get("id") or item["question"]
        for item in questions
    ]

    selected = [
        results[key]
        for key in selected_keys
        if key in results
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(selected[0].keys())
        )
        writer.writeheader()
        writer.writerows(selected)

    successful = [
        result for result in selected
        if result["status"] == "ok"
    ]

    print("\n" + "=" * 45)
    print("ANSWER EVALUATION RESULTS")
    print("=" * 45)
    print("Questions attempted:", len(selected))
    print("Successful generations:", len(successful))
    print(
        "API success rate:",
        f"{len(successful) / len(selected):.1%}"
    )

    if successful:
        n = len(successful)

        print(
            "Exact Match:",
            f"{sum(r['exact_match'] for r in successful) / n:.3f}"
        )
        print(
            "Token F1:",
            f"{sum(r['token_f1'] for r in successful) / n:.3f}"
        )
        print(
            "Citation marker validity:",
            f"{sum(r['citation_validity'] for r in successful) / n:.3f}"
        )
        print(
            "Answers with citations:",
            f"{sum(r['has_citation'] for r in successful) / n:.1%}"
        )
        print(
            "Abstention rate:",
            f"{sum(r['abstained'] for r in successful) / n:.1%}"
        )

    print("Saved to:", OUTPUT)


if __name__ == "__main__":
    main()
