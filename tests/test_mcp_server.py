import tempfile
from pathlib import Path


def test_mcp_server_has_list_documents_tool():
    from mcp_server.methodist_mcp_server import list_documents

    with tempfile.TemporaryDirectory() as tmpdir:
        open(Path(tmpdir) / "test.docx", "w").close()
        result = list_documents(folder=tmpdir)
        assert any("test.docx" in item for item in result)
