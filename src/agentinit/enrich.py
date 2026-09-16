import shutil
import subprocess
from pathlib import Path

SKILL = "agentinit-enrich"


def available() -> bool:
    return shutil.which("claude") is not None


def run(root: Path) -> int:
    command = ["claude", "-p", f"/{SKILL}", "--permission-mode", "acceptEdits"]
    return subprocess.run(command, cwd=root).returncode
