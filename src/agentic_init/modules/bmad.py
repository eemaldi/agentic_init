import shutil
import subprocess
from pathlib import Path

INSTALL_DIRS = ("_bmad", ".bmad-core", "bmad")
INSTALL_COMMAND = ["npx", "bmad-method@latest", "install"]


def is_installed(root: Path) -> bool:
    return any((root / d).is_dir() for d in INSTALL_DIRS)


def can_install() -> bool:
    return shutil.which("npx") is not None


def install(root: Path) -> int:
    return subprocess.run(INSTALL_COMMAND, cwd=root).returncode
