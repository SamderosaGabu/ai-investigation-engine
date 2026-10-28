import re
from engine.core import search, documents


def search_evidence(question, k=8):
    """Retrieve relevant evidence from the database."""
    return search(question, k=k)


def list_documents():
    """Return indexed documents."""
    return documents()


def count_documents():
    """Count indexed documents."""
    return len(documents())


def select_tool(question):
    """Choose a tool using simple rule-based routing."""
    q = question.lower().strip()

    if re.search(r"\b(how many|number of|count|total)\b", q) and \
            re.search(r"\b(documents|files)\b", q):
        return "count_documents"

    if re.search(r"\b(list|show|display)\b", q) and \
            re.search(r"\b(documents|files)\b", q):
        return "list_documents"

    return "search_evidence"


def execute_tool(question, k=8):
    """Select and execute a tool."""
    tool = select_tool(question)

    if tool == "count_documents":
        result = count_documents()

    elif tool == "list_documents":
        result = list_documents()

    else:
        result = search_evidence(question, k=k)

    return {
        "tool": tool,
        "result": result
    }