import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from agentic_init import __version__

LOCK_FILE = ".agentic_init.lock"


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


@dataclass
class Lock:
    files: dict[str, dict] = field(default_factory=dict)
    version: str = __version__

    @classmethod
    def load(cls, root: Path) -> "Lock":
        path = root / LOCK_FILE
        if not path.exists():
            return cls()
        data = json.loads(path.read_text())
        return cls(files=data.get("files", {}), version=data.get("version", __version__))

    def save(self, root: Path) -> None:
        data = {"version": __version__, "files": dict(sorted(self.files.items()))}
        (root / LOCK_FILE).write_text(json.dumps(data, indent=2) + "\n")
