# Methodist Agent v2 — Wave 1: tkinter Workspace UI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать минимальное tkinter-рабочее пространство с чатом, быстрыми действиями, панелью файлов и approval-диалогами. Интерфейс становится основной точкой входа, System Tray открывает workspace по левому клику.

**Architecture:** Окно `MethodistWorkspace` объединяет три панели: `QuickActionsPanel` (кнопки), `ChatPanel` (история + ввод), `FilePanel` (дерево файлов). Approval-диалог показывается поверх чата. Все панели общаются с основным окном через callbacks и `EventBus`.

**Tech Stack:** Python 3.11+, tkinter (stdlib), pytest, pytest-asyncio (опционально), Rich/Typer уже в проекте.

---

## Task 1: EventBus foundation

**Files:**
- Create: `src/core/event_bus.py`
- Test: `tests/test_event_bus.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_event_bus.py
import pytest
from core.event_bus import EventBus, Event


def test_event_bus_subscribe_and_publish():
    bus = EventBus()
    received = []

    def handler(event: Event):
        received.append(event)

    bus.subscribe("test_topic", handler)
    bus.publish("test_topic", {"key": "value"})

    assert len(received) == 1
    assert received[0].topic == "test_topic"
    assert received[0].payload == {"key": "value"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_event_bus.py::test_event_bus_subscribe_and_publish -v`
Expected: FAIL (ImportError or EventBus not defined)

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/event_bus.py
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    topic: str
    payload: Any = None


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, topic: str, handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic: str, payload: Any = None) -> None:
        for handler in self._subscribers.get(topic, []):
            try:
                handler(Event(topic=topic, payload=payload))
            except Exception:
                # Subscriber errors should not break the bus.
                pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_event_bus.py::test_event_bus_subscribe_and_publish -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_event_bus.py src/core/event_bus.py
git commit -m "feat(core): add EventBus foundation"
```

---

## Task 2: ChatPanel widget

**Files:**
- Create: `src/windows/chat_panel.py`
- Test: `tests/test_chat_panel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_chat_panel.py
import tkinter as tk
import pytest
from windows.chat_panel import ChatPanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_chat_panel_adds_message(root):
    panel = ChatPanel(root)
    panel.add_message("user", "Привет")
    assert "Привет" in panel.get_text()
    assert "user" in panel.get_text()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_chat_panel.py::test_chat_panel_adds_message -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/chat_panel.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional


class ChatPanel(ttk.Frame):
    def __init__(self, master, on_send: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        self.on_send = on_send

        self.history = scrolledtext.ScrolledText(self, state="disabled", wrap="word")
        self.history.pack(fill="both", expand=True, padx=4, pady=4)

        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=4, pady=4)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_var)
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>", self._on_send)

        self.send_button = ttk.Button(input_frame, text="Отправить", command=self._on_send)
        self.send_button.pack(side="left", padx=(4, 0))

    def add_message(self, role: str, text: str) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", f"{role}: {text}\n\n")
        self.history.configure(state="disabled")
        self.history.see("end")

    def get_text(self) -> str:
        return self.history.get("1.0", "end")

    def _on_send(self, event=None) -> None:
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self.add_message("user", text)
        if self.on_send:
            self.on_send(text)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_chat_panel.py::test_chat_panel_adds_message -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_chat_panel.py src/windows/chat_panel.py
git commit -m "feat(windows): add ChatPanel widget"
```

---

## Task 3: QuickActions panel

**Files:**
- Create: `src/windows/quick_actions.py`
- Test: `tests/test_quick_actions.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_quick_actions.py
import tkinter as tk
import pytest
from windows.quick_actions import QuickActionsPanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_quick_actions_emits_callback(root):
    clicked = []
    panel = QuickActionsPanel(root, on_action=lambda action: clicked.append(action))
    panel._buttons["curriculum"].invoke()
    assert clicked == ["curriculum"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_quick_actions.py::test_quick_actions_emits_callback -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/quick_actions.py
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class QuickActionsPanel(ttk.Frame):
    ACTIONS = [
        ("curriculum", "Рабочая программа"),
        ("grade_sheet", "Ведомость"),
        ("presentation", "Презентация"),
        ("report", "Отчёт"),
        ("adapt", "Адаптировать документ"),
    ]

    def __init__(self, master, on_action: Optional[Callable[[str], None]] = None):
        super().__init__(master)
        self.on_action = on_action
        self._buttons = {}

        ttk.Label(self, text="Быстрые действия", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=4, pady=4)

        for action_id, label in self.ACTIONS:
            btn = ttk.Button(self, text=label, command=lambda a=action_id: self._emit(a))
            btn.pack(fill="x", padx=4, pady=2)
            self._buttons[action_id] = btn

    def _emit(self, action: str) -> None:
        if self.on_action:
            self.on_action(action)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_quick_actions.py::test_quick_actions_emits_callback -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_quick_actions.py src/windows/quick_actions.py
git commit -m "feat(windows): add QuickActionsPanel widget"
```

---

## Task 4: FilePanel widget

**Files:**
- Create: `src/windows/file_panel.py`
- Test: `tests/test_file_panel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_file_panel.py
import os
import tempfile
import tkinter as tk
import pytest
from windows.file_panel import FilePanel


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_file_panel_lists_files(root):
    with tempfile.TemporaryDirectory() as tmpdir:
        open(os.path.join(tmpdir, "test.docx"), "w").close()
        panel = FilePanel(root, root_path=tmpdir)
        items = panel.get_items()
        assert any("test.docx" in item for item in items)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_file_panel.py::test_file_panel_lists_files -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/file_panel.py
import os
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional


class FilePanel(ttk.Frame):
    def __init__(self, master, root_path: Optional[str] = None):
        super().__init__(master)
        self.root_path = Path(root_path).expanduser() if root_path else Path.home() / "Documents" / "Методист-Агент"

        ttk.Label(self, text="Файлы проекта", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=4, pady=4)

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.refresh()

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if not self.root_path.exists():
            return
        self._insert_node("", self.root_path)

    def _insert_node(self, parent: str, path: Path) -> None:
        node = self.tree.insert(parent, "end", text=path.name, open=True)
        if path.is_dir():
            try:
                for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                    self._insert_node(node, child)
            except PermissionError:
                pass

    def get_items(self) -> list:
        return [self.tree.item(item, "text") for item in self.tree.get_children("")]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_file_panel.py::test_file_panel_lists_files -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_file_panel.py src/windows/file_panel.py
git commit -m "feat(windows): add FilePanel widget"
```

---

## Task 5: Approval dialog

**Files:**
- Create: `src/windows/approval_dialog.py`
- Test: `tests/test_approval_dialog.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_approval_dialog.py
import tkinter as tk
import pytest
from windows.approval_dialog import ApprovalDialog


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_approval_dialog_returns_approved(root):
    dialog = ApprovalDialog(root, plan_text="1. Создать документ")
    # Simulate approval without blocking.
    dialog._approved = True
    dialog._close()
    assert dialog.result is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_approval_dialog.py::test_approval_dialog_returns_approved -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/approval_dialog.py
import tkinter as tk
from tkinter import ttk
from typing import Optional


class ApprovalDialog(tk.Toplevel):
    def __init__(self, master, plan_text: str, title: str = "Подтвердите действие"):
        super().__init__(master)
        self.title(title)
        self.transient(master)
        self.grab_set()
        self.result: Optional[bool] = None
        self._approved = False

        ttk.Label(self, text="🤖 План действий:", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=8, pady=8)

        text = tk.Text(self, wrap="word", height=10, width=50)
        text.insert("1.0", plan_text)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=8, pady=4)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=8)

        ttk.Button(btn_frame, text="Подтвердить", command=self._approve).pack(side="right", padx=(4, 0))
        ttk.Button(btn_frame, text="Отменить", command=self._cancel).pack(side="right")

    def _approve(self) -> None:
        self._approved = True
        self.result = True
        self._close()

    def _cancel(self) -> None:
        self.result = False
        self._close()

    def _close(self) -> None:
        self.grab_release()
        self.destroy()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_approval_dialog.py::test_approval_dialog_returns_approved -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_approval_dialog.py src/windows/approval_dialog.py
git commit -m "feat(windows): add ApprovalDialog"
```

---

## Task 6: MethodistWorkspace main window

**Files:**
- Create: `src/windows/workspace.py`
- Modify: `src/windows/tray_app.py`
- Test: `tests/test_workspace.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_workspace.py
import tkinter as tk
import pytest
from windows.workspace import MethodistWorkspace


@pytest.fixture
def root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


def test_workspace_creates_panels(root):
    ws = MethodistWorkspace(root)
    assert ws.chat_panel is not None
    assert ws.quick_actions is not None
    assert ws.file_panel is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workspace.py::test_workspace_creates_panels -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/windows/workspace.py
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional

from core.config import Config, get_data_dir
from core.context_manager import ContextManager
from core.model_router import ModelRouter
from core.orchestrator import Orchestrator
from core.event_bus import EventBus
from windows.chat_panel import ChatPanel
from windows.quick_actions import QuickActionsPanel
from windows.file_panel import FilePanel
from windows.approval_dialog import ApprovalDialog


class MethodistWorkspace:
    def __init__(self, config: Optional[Config] = None):
        self.root = tk.Tk()
        self.root.title("Методист-Агент")
        self.root.geometry("900x700")

        self.config = config or Config()
        self.event_bus = EventBus()
        self.context_manager = ContextManager(self.config)
        self.model_router = ModelRouter(self.config)
        self.orchestrator = Orchestrator(self.config, self.model_router, self.context_manager)

        self._build_ui()

    def _build_ui(self) -> None:
        main_frame = ttk.PanedWindow(self.root, orient="horizontal")
        main_frame.pack(fill="both", expand=True)

        self.quick_actions = QuickActionsPanel(self.root, on_action=self._on_quick_action)
        main_frame.add(self.quick_actions, width=200)

        center_frame = ttk.Frame(self.root)
        self.chat_panel = ChatPanel(center_frame, on_send=self._on_chat_send)
        self.chat_panel.pack(fill="both", expand=True)
        main_frame.add(center_frame, weight=1)

        output_path = getattr(self.config.documents, "output_path", None)
        self.file_panel = FilePanel(self.root, root_path=output_path)
        main_frame.add(self.file_panel, width=250)

        self.root.protocol("WM_DELETE_WINDOW", self.hide)

    def _on_quick_action(self, action: str) -> None:
        self.chat_panel.add_message("system", f"Выбрано действие: {action}")

    def _on_chat_send(self, text: str) -> None:
        plan = self.orchestrator.create_plan(text)
        self.chat_panel.add_message("assistant", self.orchestrator.present_plan(plan))
        if plan.requires_approval:
            self.root.after(100, lambda: self._show_approval(plan))

    def _show_approval(self, plan) -> None:
        dialog = ApprovalDialog(self.root, plan_text=self.orchestrator.present_plan(plan))
        if dialog.result:
            self.orchestrator.approve_plan(plan)
            self.chat_panel.add_message("system", "План подтверждён. Выполняю...")
        else:
            self.chat_panel.add_message("system", "План отменён.")

    def show(self) -> None:
        self.root.deiconify()
        self.root.lift()

    def hide(self) -> None:
        self.root.withdraw()

    def run(self) -> None:
        self.show()
        self.root.mainloop()
```

- [ ] **Step 4: Modify tray_app.py to open workspace**

```python
# Add to src/windows/tray_app.py near imports
from windows.workspace import MethodistWorkspace

# In TrayApp.__init__ or setup, store workspace instance
self.workspace = None

# In left-click handler (or create one)
def _on_left_click(self):
    if self.workspace is None:
        self.workspace = MethodistWorkspace(self.config)
    self.workspace.show()

# Ensure right-click menu has "Открыть рабочее пространство"
```

Because tray_app.py structure varies, read the file first and add the workspace toggle in the existing menu.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_workspace.py::test_workspace_creates_panels -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_workspace.py src/windows/workspace.py src/windows/tray_app.py
git commit -m "feat(windows): add MethodistWorkspace and tray integration"
```

---

## Task 7: UI texts

**Files:**
- Modify: `src/core/ui_text.py`
- Test: `tests/test_ui_text.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_ui_text.py
def test_workspace_strings_exist():
    from core import ui_text
    assert callable(getattr(ui_text, "workspace_title", None))
    assert callable(getattr(ui_text, "workspace_quick_actions", None))
    assert callable(getattr(ui_text, "workspace_approved", None))
    assert callable(getattr(ui_text, "workspace_cancelled", None))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_ui_text.py::test_workspace_strings_exist -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/core/ui_text.py — add functions

def workspace_title() -> str:
    return "Методист-Агент"


def workspace_quick_actions() -> str:
    return "Быстрые действия"


def workspace_file_panel() -> str:
    return "Файлы проекта"


def workspace_approved() -> str:
    return "План подтверждён. Выполняю..."


def workspace_cancelled() -> str:
    return "План отменён."
```

- [ ] **Step 4: Update workspace.py to use ui_text helpers**

Replace hardcoded strings in `workspace.py` with calls to the new helpers.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_ui_text.py::test_workspace_strings_exist -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tests/test_ui_text.py src/core/ui_text.py src/windows/workspace.py
git commit -m "feat(ui_text): add workspace strings"
```

---

## Task 8: CLI command `workspace`

**Files:**
- Modify: `src/main.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_cli.py
def test_workspace_command_exists():
    from typer.testing import CliRunner
    from src.main import app
    runner = CliRunner()
    result = runner.invoke(app, ["workspace", "--help"])
    assert result.exit_code == 0
    assert "workspace" in result.output.lower() or "Открыть" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_cli.py::test_workspace_command_exists -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# src/main.py — add command
from windows.workspace import MethodistWorkspace

@app.command()
def workspace():
    """Открыть рабочее пространство Методист-Агента."""
    console.print("[info]Открываю рабочее пространство...[/info]")
    ws = MethodistWorkspace()
    ws.run()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_cli.py::test_workspace_command_exists -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/main.py
git commit -m "feat(cli): add workspace command"
```

---

## Task 9: Smoke / integration test

**Files:**
- Test: `tests/test_workspace_smoke.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_workspace_smoke.py
import tkinter as tk
import pytest
from windows.workspace import MethodistWorkspace
from unittest.mock import patch


@patch("windows.workspace.MethodistWorkspace._build_ui")
def test_workspace_smoke_init(mock_build_ui):
    ws = MethodistWorkspace()
    assert ws.root.title() == "Методист-Агент"
    ws.root.destroy()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_workspace_smoke.py::test_workspace_smoke_init -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

The test itself is the implementation; ensure `MethodistWorkspace` initializes without blocking. No code change required beyond what Task 6 already did.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_workspace_smoke.py::test_workspace_smoke_init -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_workspace_smoke.py
git commit -m "test(windows): add workspace smoke test"
```

---

## Task 10: Final lint / test / commit

**Files:**
- All files created or modified above.

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests pass

- [ ] **Step 2: Run ruff on changed files**

Run: `ruff check src/core/event_bus.py src/windows/chat_panel.py src/windows/quick_actions.py src/windows/file_panel.py src/windows/approval_dialog.py src/windows/workspace.py src/core/ui_text.py src/main.py tests/`
Expected: clean

- [ ] **Step 3: Commit final wave**

```bash
git add .
git commit -m "feat(workspace): complete Wave 1 tkinter workspace UI"
```

---

## Self-review checklist

- [ ] Spec coverage: every UI element from the design doc maps to a task.
- [ ] Placeholder scan: no TBD/TODO in task steps.
- [ ] Type consistency: `MethodistWorkspace`, `ChatPanel`, etc. use the same names across tasks.
- [ ] Test commands: each task has exact pytest command and expected result.
