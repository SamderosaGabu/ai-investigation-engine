from engine.tools import select_tool, execute_tool
from engine.core import investigate


def test_investigate_uses_tools():
    result = investigate("How many documents are stored?")

    assert result["status"] == "ok"
    assert result["tool_used"] == "count_documents"
    assert result["answer"].isdigit()

def test_tool_selection():
    assert select_tool(
        "How many documents are stored?"
    ) == "count_documents"

    assert select_tool(
        "List all documents"
    ) == "list_documents"

    assert select_tool(
        "What caused the outage?"
    ) == "search_evidence"


def test_tool_execution():
    result = execute_tool("How many documents are stored?")

    assert result["tool"] == "count_documents"
    assert isinstance(result["result"], int)
    assert result["result"] >= 0