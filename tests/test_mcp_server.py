import pytest


def test_mcp_server_has_list_documents_tool(monkeypatch, tmp_path):
    from mcp_server import methodist_mcp_server
    from mcp_server.methodist_mcp_server import list_documents

    monkeypatch.setattr(methodist_mcp_server, "_project_root", lambda: tmp_path)
    subdir = tmp_path / "docs"
    subdir.mkdir()
    (subdir / "test.docx").touch()
    result = list_documents(folder=str(subdir))
    assert any("test.docx" in item for item in result)


def test_mcp_create_document_tool_exists():
    from mcp_server.methodist_mcp_server import create_document

    assert callable(create_document)


def test_mcp_create_document_executes(monkeypatch, tmp_path):
    from mcp_server import methodist_mcp_server

    monkeypatch.setattr(methodist_mcp_server, "_project_root", lambda: tmp_path)
    output = tmp_path / "test.docx"
    result = methodist_mcp_server.create_document(
        doc_type="docx",
        output_path=str(output),
        parameters={"title": "MCP Test"},
    )
    assert output.exists()
    assert "created" in result.lower() or "готово" in result.lower()


def test_mcp_read_document_rejects_outside_sandbox(monkeypatch, tmp_path):
    from mcp_server import methodist_mcp_server

    monkeypatch.setattr(methodist_mcp_server, "_project_root", lambda: tmp_path)
    with pytest.raises((PermissionError, ValueError)):
        methodist_mcp_server.read_document("/etc/passwd")
