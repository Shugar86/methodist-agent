from tkinter import ttk
from pathlib import Path
from typing import Optional


class FilePanel(ttk.Frame):
    def __init__(self, master, root_path: Optional[str] = None):
        super().__init__(master)
        self.root_path = (
            Path(root_path).expanduser()
            if root_path
            else Path.home() / "Documents" / "Методист-Агент"
        )

        ttk.Label(self, text="Файлы проекта", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=4, pady=4
        )

        self.tree = ttk.Treeview(self, show="tree")
        self.tree.pack(fill="both", expand=True, padx=4, pady=4)

        self.refresh()

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        if not self.root_path.exists():
            return
        try:
            for child in sorted(
                self.root_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())
            ):
                self._insert_node("", child)
        except PermissionError:
            pass

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

    def _get_all_items(self) -> list:
        def collect(parent):
            items = []
            for item in self.tree.get_children(parent):
                items.append(self.tree.item(item, "text"))
                items.extend(collect(item))
            return items

        return collect("")
