#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
LOG = ROOT / ".claude" / "state" / "audit.jsonl"
MAX_VALUE = 500


def truncate(value):
    if isinstance(value, str):
        return value if len(value) <= MAX_VALUE else f"{value[:MAX_VALUE]}… ({len(value)} chars)"
    if isinstance(value, dict):
        return {key: truncate(item) for key, item in value.items()}
    if isinstance(value, list):
        return [truncate(item) for item in value]
    return value


def main() -> int:
    payload = json.load(sys.stdin)
    record = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session": payload.get("session_id"),
        "agent": payload.get("agent_type"),
        "tool": payload.get("tool_name"),
        "input": truncate(payload.get("tool_input", {})),
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a") as log:
        log.write(json.dumps(record) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
