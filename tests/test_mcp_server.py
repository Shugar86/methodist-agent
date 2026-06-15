import tempfile
from pathlib import Path


def test_mcp_server_has_list_documents_tool():
    from mcp_server.methodist_mcp_server import list_documents

    with tempfile.TemporaryDirectory() as tmpdir:
        open(Path(tmpdir) / "test.docx", "w").close()
        result = list_documents(folder=tmpdir)
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
