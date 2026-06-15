"""Main workspace window for Methodist Agent."""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Union

from core.config import Config
from core.context_manager import ContextManager
from core.model_router import ModelRouter
from core.orchestrator import Orchestrator
from core.event_bus import EventBus
from windows.chat_panel import ChatPanel
from windows.quick_actions import QuickActionsPanel
from windows.file_panel import FilePanel
from windows.approval_dialog import ApprovalDialog


class MethodistWorkspace:
    def __init__(
        self,
        master: Optional[Union[tk.Tk, Config]] = None,
        config: Optional[Config] = None,
    ):
        # Support both `MethodistWorkspace(root)` and `MethodistWorkspace(config=...)`
        if isinstance(master, Config):
            config = master
            master = None

        self.root = master or tk.Tk()
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
        self.quick_actions.configure(width=200)
        main_frame.add(self.quick_actions)

        center_frame = ttk.Frame(self.root)
        self.chat_panel = ChatPanel(center_frame, on_send=self._on_chat_send)
        self.chat_panel.pack(fill="both", expand=True)
        main_frame.add(center_frame, weight=1)

        output_path = getattr(self.config.documents, "output_path", None)
        self.file_panel = FilePanel(self.root, root_path=output_path)
        self.file_panel.configure(width=250)
        main_frame.add(self.file_panel)

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
        self.root.wait_window(dialog)
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
