from mcp.server.fastmcp import FastMCP  # noqa: F401


def test_mcp_server_has_list_documents_tool():
    from mcp.methodist_mcp_server import mcp

    tools = mcp._tools
    assert any(t.name == "list_documents" for t in tools.values())
