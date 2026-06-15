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

    def start_stream(self) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", "assistant: ")
        self.history.configure(state="disabled")
        self._stream_buffer = ""

    def append_stream_chunk(self, text: str) -> None:
        if not text:
            return
        self._stream_buffer += text
        self.history.configure(state="normal")
        self.history.insert("end", text)
        self.history.configure(state="disabled")
        self.history.see("end")

    def finish_stream(self) -> None:
        self.history.configure(state="normal")
        self.history.insert("end", "\n\n")
        self.history.configure(state="disabled")

    def _on_send(self, event=None) -> None:
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self.add_message("user", text)
        if self.on_send:
            self.on_send(text)
