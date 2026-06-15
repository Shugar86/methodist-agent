from pathlib import Path
from typing import Union


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
