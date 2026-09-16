#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
WEB = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".css", ".scss", ".vue", ".svelte")
FORMATTERS = {
    (".py",): [["ruff", "format", "--quiet"], ["black", "--quiet"]],
    WEB: [["prettier", "--write", "--log-level", "warn"], ["biome", "format", "--write"]],
    (".go",): [["gofmt", "-w"]],
    (".rs",): [["rustfmt"]],
}
LOCAL_BINS = (ROOT / "node_modules" / ".bin", ROOT / ".venv" / "bin")


def locate(tool: str) -> str | None:
    local = next((str(d / tool) for d in LOCAL_BINS if (d / tool).exists()), None)
    return local or shutil.which(tool)


def main() -> int:
    path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    if not path or not Path(path).is_file():
        return 0
    for extensions, candidates in FORMATTERS.items():
        if not path.endswith(extensions):
            continue
        for tool, *args in candidates:
            if executable := locate(tool):
                subprocess.run([executable, *args, path], cwd=ROOT, capture_output=True, timeout=60)
                return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
