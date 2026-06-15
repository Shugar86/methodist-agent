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
        self.result = self._approved
        self.grab_release()
        self.destroy()
