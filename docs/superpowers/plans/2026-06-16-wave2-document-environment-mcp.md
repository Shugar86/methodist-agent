# Methodist Agent v2 — Wave 2: Document Environment + MCP Server

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать центральную абстракцию для работы с документами (`DocumentEnvironment`) с драйверами COM/native, sandbox, hooks/event bus; и MCP server для экспозиции операций с документами.

**Architecture:** `DocumentEnvironment` получает `DocumentRequest`, выбирает драйвер (COM → Native → LibreOffice), работает внутри `Sandbox`, публикует события в `EventBus`. `methodist_mcp_server.py` оборачивает операции в MCP tools/resources/prompts на FastMCP с stdio transport.

**Tech Stack:** Python 3.11+, pydantic, python-docx/openpyxl/python-pptx, pywin32 (опционально), `mcp[cli]`, pytest.

---

## Task 1: Document request/result dataclasses and base driver

**Files:**
- Create: `src/core/document_environment.py`
- Test: `tests/test_document_environment.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_document_environment.py
from core.document_environment import DocumentRequest, DocumentResult, BaseDocumentDriver


def test_document_request_defaults():
    req = DocumentRequest(action="create", doc_type="docx")
    assert req.action == "create"
    assert req.doc_type == "docx"


def test_document_result_fields():
    result = DocumentResult(success=True, output_path="out.docx")
    assert result.success is True
    assert result.output_path == "out.docx"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_document_environment.py::test_document_request_defaults tests/test_document_environment.py::test_document_result_fields -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/document_environment.py
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from pathlib import Path


@dataclass
class DocumentRequest:
    action: str
    doc_type: str
    input_path: Optional[str] = None
    output_path: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentResult:
    success: bool
    output_path: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    events: list = field(default_factory=list)


class BaseDocumentDriver:
    def supports(self, request: DocumentRequest) -> bool:
        return False

    def execute(self, request: DocumentRequest) -> DocumentResult:
        raise NotImplementedError
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_document_environment.py::test_document_request_defaults tests/test_document_environment.py::test_document_result_fields -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_document_environment.py src/core/document_environment.py
git commit -m "feat(core): add DocumentRequest, DocumentResult, BaseDocumentDriver"
```

---

## Task 2: NativeDriver

**Files:**
- Create: `src/drivers/native_driver.py`
- Create: `src/drivers/__init__.py`
- Test: `tests/test_native_driver.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_native_driver.py
from pathlib import Path
import tempfile
from drivers.native_driver import NativeDriver
from core.document_environment import DocumentRequest, DocumentResult


def test_native_driver_creates_docx():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.docx"
        driver = NativeDriver()
        req = DocumentRequest(
            action="create",
            doc_type="docx",
            output_path=str(output),
            parameters={"title": "Hello"},
        )
        result = driver.execute(req)
        assert result.success is True
        assert output.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_native_driver.py::test_native_driver_creates_docx -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/drivers/native_driver.py
from typing import Dict, Any
from pathlib import Path

from core.document_environment import DocumentRequest, DocumentResult, BaseDocumentDriver


class NativeDriver(BaseDocumentDriver):
    def supports(self, request: DocumentRequest) -> bool:
        return request.doc_type in ("docx", "xlsx", "pptx")

    def execute(self, request: DocumentRequest) -> DocumentResult:
        if request.action == "create":
            return self._create(request)
        return DocumentResult(success=False, message=f"Unsupported action: {request.action}")

    def _create(self, request: DocumentRequest) -> DocumentResult:
        output_path = Path(request.output_path) if request.output_path else None
        if not output_path:
            return DocumentResult(success=False, message="output_path required")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        if request.doc_type == "docx":
            from docx import Document
            doc = Document()
            title = request.parameters.get("title", "")
            if title:
                doc.add_heading(title, level=1)
            doc.save(str(output_path))
        elif request.doc_type == "xlsx":
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Sheet1"
            ws["A1"] = request.parameters.get("title", "")
            wb.save(str(output_path))
        elif request.doc_type == "pptx":
            from pptx import Presentation
            prs = Presentation()
            title = request.parameters.get("title", "")
            if title:
                slide = prs.slides.add_slide(prs.slide_layouts[0])
                slide.shapes.title.text = title
            prs.save(str(output_path))
        else:
            return DocumentResult(success=False, message=f"Unsupported doc_type: {request.doc_type}")

        return DocumentResult(success=True, output_path=str(output_path), message="Created")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_native_driver.py::test_native_driver_creates_docx -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/drivers/ tests/test_native_driver.py
git commit -m "feat(drivers): add NativeDriver for docx/xlsx/pptx"
```

---

## Task 3: Sandbox

**Files:**
- Create: `src/core/sandbox.py`
- Test: `tests/test_sandbox.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_sandbox.py
import tempfile
from pathlib import Path
from core.sandbox import Sandbox


def test_sandbox_allows_project_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Sandbox(tmpdir)
        assert sandbox.is_allowed(Path(tmpdir) / "file.docx") is True


def test_sandbox_rejects_parent_escape():
    with tempfile.TemporaryDirectory() as tmpdir:
        sandbox = Sandbox(tmpdir)
        assert sandbox.is_allowed(Path(tmpdir).parent / "outside.docx") is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sandbox.py::test_sandbox_allows_project_path tests/test_sandbox.py::test_sandbox_rejects_parent_escape -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/sandbox.py
import os
from pathlib import Path
from typing import Optional, Union


class Sandbox:
    def __init__(self, root_path: Union[str, Path]):
        self.root_path = Path(root_path).expanduser().resolve()

    def is_allowed(self, path: Union[str, Path]) -> bool:
        target = Path(path).expanduser().resolve()
        try:
            target.relative_to(self.root_path)
            return True
        except ValueError:
            return False

    def normalize(self, path: Union[str, Path]) -> Path:
        target = Path(path).expanduser()
        if not self.is_allowed(target):
            raise PermissionError(f"Path outside sandbox: {target}")
        return target.resolve()

    def backup_path(self, path: Union[str, Path], timestamp: str) -> Path:
        target = self.normalize(path)
        backup_dir = self.root_path / ".backup" / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)
        relative = target.relative_to(self.root_path)
        return backup_dir / relative
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sandbox.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/sandbox.py tests/test_sandbox.py
git commit -m "feat(core): add Sandbox with path allowlist"
```

---

## Task 4: DocumentEnvironment facade

**Files:**
- Modify: `src/core/document_environment.py`
- Test: `tests/test_document_environment.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_document_environment.py — append
from drivers.native_driver import NativeDriver
from core.sandbox import Sandbox


def test_document_environment_selects_native_driver():
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.docx"
        env = DocumentEnvironment(
            sandbox=Sandbox(tmpdir),
            drivers=[NativeDriver()],
        )
        req = DocumentRequest(action="create", doc_type="docx", output_path=str(output), parameters={"title": "Test"})
        result = env.execute(req)
        assert result.success is True
        assert output.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_document_environment.py::test_document_environment_selects_native_driver -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/document_environment.py — add
class DocumentEnvironment:
    def __init__(self, sandbox: Sandbox, drivers=None, event_bus=None):
        self.sandbox = sandbox
        self.drivers = drivers or []
        self.event_bus = event_bus

    def execute(self, request: DocumentRequest) -> DocumentResult:
        if request.output_path:
            self.sandbox.normalize(request.output_path)
        driver = self._select_driver(request)
        if not driver:
            return DocumentResult(success=False, message="No suitable driver found")
        self._publish("before_execute", {"request": request.to_dict()})
        result = driver.execute(request)
        self._publish("after_execute", {"request": request.to_dict(), "result": result.to_dict()})
        return result

    def _select_driver(self, request: DocumentRequest):
        for driver in self.drivers:
            if driver.supports(request):
                return driver
        return None

    def _publish(self, topic: str, payload: dict) -> None:
        if self.event_bus:
            self.event_bus.publish(topic, payload)
```

Also add `to_dict()` methods to `DocumentRequest` and `DocumentResult` for event payloads, or use `dataclasses.asdict`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_document_environment.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/core/document_environment.py tests/test_document_environment.py
git commit -m "feat(core): add DocumentEnvironment facade"
```

---

## Task 5: COMDriver

**Files:**
- Create: `src/drivers/com_driver.py`
- Test: `tests/test_com_driver.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_com_driver.py
from unittest.mock import MagicMock, patch
from drivers.com_driver import COMDriver
from core.document_environment import DocumentRequest


def test_com_driver_available_on_windows_only():
    driver = COMDriver()
    with patch("drivers.com_driver.platform.system", return_value="Linux"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is False
    with patch("drivers.com_driver.platform.system", return_value="Windows"):
        assert driver.supports(DocumentRequest(action="create", doc_type="docx")) is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_com_driver.py::test_com_driver_available_on_windows_only -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/drivers/com_driver.py
import platform
from pathlib import Path
from typing import Optional

from core.document_environment import DocumentRequest, DocumentResult, BaseDocumentDriver


class COMDriver(BaseDocumentDriver):
    def supports(self, request: DocumentRequest) -> bool:
        return platform.system() == "Windows" and request.doc_type in ("docx", "xlsx", "pptx")

    def execute(self, request: DocumentRequest) -> DocumentResult:
        if not self.supports(request):
            return DocumentResult(success=False, message="COM driver not available")
        try:
            import win32com.client
        except ImportError:
            return DocumentResult(success=False, message="pywin32 not installed")
        # Minimal create logic; full COM automation is complex and will be expanded later.
        return self._create(request, win32com.client)

    def _create(self, request: DocumentRequest, win32com_client) -> DocumentResult:
        output_path = Path(request.output_path) if request.output_path else None
        if not output_path:
            return DocumentResult(success=False, message="output_path required")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        app_name = {"docx": "Word.Application", "xlsx": "Excel.Application", "pptx": "PowerPoint.Application"}[request.doc_type]
        app = win32com_client.DispatchEx(app_name)
        try:
            app.Visible = False
            app.DisplayAlerts = False
            if request.doc_type == "docx":
                doc = app.Documents.Add()
                title = request.parameters.get("title", "")
                if title:
                    doc.Content.Text = title
                doc.SaveAs(str(output_path))
                doc.Close()
            elif request.doc_type == "xlsx":
                wb = app.Workbooks.Add()
                ws = wb.Worksheets(1)
                ws.Cells(1, 1).Value = request.parameters.get("title", "")
                wb.SaveAs(str(output_path))
                wb.Close()
            elif request.doc_type == "pptx":
                prs = app.Presentations.Add()
                slide = prs.Slides.Add(1, 12)  # ppLayoutTitle
                slide.Shapes(1).TextFrame.TextRange.Text = request.parameters.get("title", "")
                prs.SaveAs(str(output_path))
                prs.Close()
        finally:
            app.Quit()

        return DocumentResult(success=True, output_path=str(output_path), message="Created via COM")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_com_driver.py::test_com_driver_available_on_windows_only -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/drivers/com_driver.py tests/test_com_driver.py
git commit -m "feat(drivers): add COMDriver for Windows Office"
```

---

## Task 6: Integrate DocumentEnvironment into Workspace and Document Specialist

**Files:**
- Modify: `src/windows/workspace.py`
- Modify: `src/agents/document_specialist.py`
- Test: `tests/test_workspace.py`, `tests/test_document_specialist.py`

- [ ] **Step 1: Write the failing test**

Add to `tests/test_workspace.py`:
```python
def test_workspace_has_document_environment(tmp_path):
    from core.config import Config
    from core.sandbox import Sandbox
    from drivers.native_driver import NativeDriver
    from core.document_environment import DocumentEnvironment

    config = Config()
    ws = MethodistWorkspace(config=config)
    assert isinstance(ws.document_environment, DocumentEnvironment)
    ws.root.destroy()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workspace.py::test_workspace_has_document_environment -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

In `src/windows/workspace.py`:
```python
from core.sandbox import Sandbox
from core.document_environment import DocumentEnvironment
from drivers.native_driver import NativeDriver
from drivers.com_driver import COMDriver

# In __init__:
        self.document_environment = DocumentEnvironment(
            sandbox=Sandbox(get_data_dir(self.config)),
            drivers=[COMDriver(), NativeDriver()],
            event_bus=self.event_bus,
        )
```

In `src/agents/document_specialist.py`, refactor `create_docx`/`create_xlsx`/`create_pptx` to use `DocumentEnvironment.execute(DocumentRequest(...))` where appropriate, keeping backward compatibility.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workspace.py tests/test_document_specialist.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/windows/workspace.py src/agents/document_specialist.py tests/test_workspace.py tests/test_document_specialist.py
git commit -m "feat(integration): wire DocumentEnvironment into workspace and document specialist"
```

---

## Task 7: MCP server skeleton

**Files:**
- Create: `src/mcp_server/methodist_mcp_server.py`
- Create: `src/mcp_server/__init__.py`
- Test: `tests/test_mcp_server.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mcp_server.py
import pytest
from mcp.server.fastmcp import FastMCP


def test_mcp_server_has_list_documents_tool():
    from mcp_server.methodist_mcp_server import mcp
    tools = mcp._tools
    assert any(t.name == "list_documents" for t in tools.values())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mcp_server.py::test_mcp_server_has_list_documents_tool -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/mcp_server/methodist_mcp_server.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mcp_server.py::test_mcp_server_has_list_documents_tool -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/mcp_server/ tests/test_mcp_server.py
git commit -m "feat(mcp): add MCP server skeleton with list_documents tool"
```

---

## Task 8: MCP tools for document operations

**Files:**
- Modify: `src/mcp_server/methodist_mcp_server.py`
- Test: `tests/test_mcp_server.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_mcp_server.py — append
from pathlib import Path
import tempfile


def test_mcp_create_document_tool_exists():
    from mcp_server.methodist_mcp_server import mcp
    tools = mcp._tools
    assert any(t.name == "create_document" for t in tools.values())


def test_mcp_create_document_executes():
    from mcp_server.methodist_mcp_server import create_document
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "test.docx"
        result = create_document(
            doc_type="docx",
            output_path=str(output),
            parameters={"title": "MCP Test"},
        )
        assert output.exists()
        assert "created" in result.lower() or "готово" in result.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_mcp_server.py::test_mcp_create_document_tool_exists tests/test_mcp_server.py::test_mcp_create_document_executes -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/mcp_server/methodist_mcp_server.py — append
from core.document_environment import DocumentEnvironment, DocumentRequest
from core.sandbox import Sandbox
from drivers.native_driver import NativeDriver
from drivers.com_driver import COMDriver


def _get_env() -> DocumentEnvironment:
    return DocumentEnvironment(
        sandbox=Sandbox(_project_root()),
        drivers=[COMDriver(), NativeDriver()],
    )


@mcp.tool()
def create_document(doc_type: str, output_path: str, parameters: dict) -> str:
    """Create a document from parameters."""
    env = _get_env()
    req = DocumentRequest(action="create", doc_type=doc_type, output_path=output_path, parameters=parameters)
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/mcp_server/methodist_mcp_server.py tests/test_mcp_server.py
git commit -m "feat(mcp): add create_document, read_document, convert_to_pdf tools"
```

---

## Task 9: MCP resources and prompts

**Files:**
- Modify: `src/mcp_server/methodist_mcp_server.py`
- Test: `tests/test_mcp_server.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_mcp_server.py — append
from mcp_server.methodist_mcp_server import mcp


def test_mcp_resource_exists():
    resources = mcp._resources
    assert any("doc://" in str(r.uri) for r in resources.values())


def test_mcp_prompt_exists():
    prompts = mcp._prompts
    assert "generate_curriculum" in prompts
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_mcp_server.py::test_mcp_resource_exists tests/test_mcp_server.py::test_mcp_prompt_exists -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/mcp_server/methodist_mcp_server.py — append
from mcp.types import TextContent


@mcp.resource("doc://{relative_path}")
def get_document_resource(relative_path: str) -> str:
    """Read-only access to a project document."""
    path = _project_root() / relative_path
    if not path.exists():
        return f"Document not found: {relative_path}"
    if path.suffix == ".docx":
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs)
    return path.read_text(encoding="utf-8", errors="ignore")


@mcp.prompt()
def generate_curriculum(subject: str, hours: int) -> str:
    """Prompt template for generating a curriculum."""
    return f"Создай рабочую программу дисциплины '{subject}' объёмом {hours} часов."


@mcp.prompt()
def adapt_to_fgos(source_path: str, fgos_version: str = "3++") -> str:
    """Prompt template for adapting a document to FGOS."""
    return f"Адаптируй документ {source_path} под требования ФГОС {fgos_version}."
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/mcp_server/methodist_mcp_server.py tests/test_mcp_server.py
git commit -m "feat(mcp): add resources and prompts"
```

---

## Task 10: Final lint/test/commit

**Files:**
- All Wave 2 files.

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all pass

- [ ] **Step 2: Run ruff on Wave 2 files**

Run: `ruff check src/core/document_environment.py src/core/sandbox.py src/drivers/ src/mcp_server/ tests/test_document_environment.py tests/test_sandbox.py tests/test_native_driver.py tests/test_com_driver.py tests/test_mcp_server.py`
Expected: clean

- [ ] **Step 3: Run ruff format --check**

Run: `ruff format --check src/core/document_environment.py src/core/sandbox.py src/drivers/ src/mcp_server/ tests/test_document_environment.py tests/test_sandbox.py tests/test_native_driver.py tests/test_com_driver.py tests/test_mcp_server.py`
Expected: all formatted

- [ ] **Step 4: Commit final wave**

```bash
git add .
git commit -m "feat(environment): complete Wave 2 Document Environment + MCP server"
```

---

## Self-review checklist

- [ ] DocumentRequest/Result dataclasses tested.
- [ ] NativeDriver creates docx/xlsx/pptx.
- [ ] COMDriver available only on Windows.
- [ ] Sandbox rejects paths outside root.
- [ ] DocumentEnvironment selects driver and executes.
- [ ] EventBus hooks published.
- [ ] MCP server exposes tools/resources/prompts.
- [ ] Full suite passes, lint/format clean.
