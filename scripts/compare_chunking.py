import statistics
from engine.core import chunk_text


def measure_strategy(text, strategy):
    chunks = chunk_text(
        text,
        size=850,
        overlap=130,
        strategy=strategy
    )

    lengths = [len(chunk) for chunk in chunks]

    return {
        "strategy": strategy,
        "chunk_count": len(chunks),
        "average_size": round(statistics.mean(lengths), 1) if lengths else 0,
        "minimum_size": min(lengths) if lengths else 0,
        "maximum_size": max(lengths) if lengths else 0,
        "oversized_chunks": sum(length > 850 for length in lengths)
    }


def main():
    text = (
        "The payment service experienced an outage due to a database connection failure. "
        "Engineers investigated the incident and discovered that connection pooling "
        "was configured incorrectly.\n\n"
        "The team restarted the affected services and updated the connection pool "
        "configuration to prevent future outages.\n\n"
        "A follow-up investigation identified missing monitoring alerts. "
        "The engineering team introduced new alerts and documented the incident.\n\n"
    ) * 100

    for strategy in ["characters", "paragraphs"]:
        print(measure_strategy(text, strategy))


if __name__ == "__main__":
    main()