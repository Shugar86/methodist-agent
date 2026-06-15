from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from core.document_environment import DocumentEnvironment, DocumentRequest
from core.sandbox import Sandbox
from drivers.com_driver import COMDriver
from drivers.native_driver import NativeDriver

mcp = FastMCP("methodist-agent")


def _project_root() -> Path:
    return Path.home() / "Documents" / "Методист-Агент"


def _get_env(output_path: Optional[str] = None) -> DocumentEnvironment:
    root = _project_root()
    if output_path:
        target = Path(output_path).expanduser().resolve()
        try:
            target.relative_to(root)
        except ValueError:
            root = target.parent
    return DocumentEnvironment(
        sandbox=Sandbox(root),
        drivers=[COMDriver(), NativeDriver()],
    )


@mcp.tool()
def list_documents(folder: Optional[str] = None) -> list[str]:
    """List document files in a workspace folder."""
    root = Path(folder).expanduser() if folder else _project_root()
    if not root.exists():
        return []
    return [str(p) for p in root.rglob("*") if p.is_file()]


@mcp.tool()
def create_document(doc_type: str, output_path: str, parameters: dict) -> str:
    """Create a document from parameters."""
    env = _get_env(output_path)
    req = DocumentRequest(
        action="create",
        doc_type=doc_type,
        output_path=output_path,
        parameters=parameters,
    )
    result = env.execute(req)
    if result.success:
        return f"Created: {result.output_path}"
    return f"Failed: {result.message}"


@mcp.tool()
def read_document(path: str) -> str:
    """Read text from a DOCX file."""
    from docx import Document

    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


@mcp.tool()
def convert_to_pdf(input_path: str, output_path: str) -> str:
    """Convert a document to PDF (stub)."""
    return f"PDF conversion not yet implemented for {input_path}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
