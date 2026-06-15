# src/windows/quick_actions.py
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

        ttk.Label(self, text="Быстрые действия", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=4, pady=4
        )

        for action_id, label in self.ACTIONS:
            btn = ttk.Button(self, text=label, command=lambda a=action_id: self._emit(a))
            btn.pack(fill="x", padx=4, pady=2)
            self._buttons[action_id] = btn

    def _emit(self, action: str) -> None:
        if self.on_action:
            self.on_action(action)
