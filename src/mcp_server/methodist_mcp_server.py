from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("methodist-agent")


def _project_root() -> Path:
    return Path.home() / "Documents" / "Методист-Агент"


@mcp.tool()
def list_documents(folder: Optional[str] = None) -> list[str]:
    """List document files in a workspace folder."""
    root = Path(folder).expanduser() if folder else _project_root()
    if not root.exists():
        return []
    return [str(p) for p in root.rglob("*") if p.is_file()]


if __name__ == "__main__":
    mcp.run(transport="stdio")
