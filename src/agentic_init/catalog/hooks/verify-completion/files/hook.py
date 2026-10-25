#!/usr/bin/env python3
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CHECKS = {{ [["lint", commands.lint], ["typecheck", commands.typecheck], ["test", commands.test]] | selectattr(1) | list | tojson }}
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
STATE = ROOT / ".claude" / "state" / "verification.json"
TIMEOUT_SECONDS = 900
MISSING_COMMAND = 127
MAX_CONSECUTIVE_BLOCKS = 3
OUTPUT_TAIL = 3000


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""


def fingerprint() -> str | None:
    if not git("rev-parse", "--is-inside-work-tree").strip():
        return None
    head = git("rev-parse", "HEAD")
    tracked = git("diff", "HEAD") if head else git("ls-files", "--stage") + git("diff")
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    stats = "".join(f"{p}:{(ROOT / p).stat().st_mtime_ns}" for p in untracked if (ROOT / p).is_file())
    return hashlib.sha256((head + tracked + stats).encode()).hexdigest()


def run(name: str, command: str) -> dict:
    started = time.monotonic()
    try:
        result = subprocess.run(command, shell=True, cwd=ROOT, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        code, output = result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        code, output = 124, f"timed out after {TIMEOUT_SECONDS}s"
    return {
        "check": name,
        "command": command,
        "exit_code": code,
        "available": not (code == MISSING_COMMAND or "command not found" in output or "No such file" in output[:200]),
        "seconds": round(time.monotonic() - started, 1),
        "output_tail": output[-OUTPUT_TAIL:],
    }


def main() -> int:
    payload = json.load(sys.stdin)
    current = fingerprint()
    if not CHECKS or current is None:
        return 0
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    if state.get("fingerprint") == current and state.get("passed"):
        return 0
    blocks = state.get("consecutive_blocks", 0)
    if payload.get("stop_hook_active") and blocks >= MAX_CONSECUTIVE_BLOCKS:
        print(json.dumps({"systemMessage": "agentic_init: checks still failing after repeated attempts; human attention needed."}))
        return 0

    results = [run(name, command) for name, command in CHECKS]
    # A missing toolchain is not a failed check: it means nothing was verified here, and
    # blocking on it would deadlock the session instead of telling the human what is wrong.
    unavailable = [r for r in results if not r["available"]]
    passed = all(r["exit_code"] == 0 for r in results if r["available"])
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({
        "fingerprint": current,
        "passed": passed,
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "consecutive_blocks": 0 if passed else blocks + 1,
        "results": results,
    }, indent=2))
    if passed:
        if unavailable:
            missing = ", ".join(f"`{r['command']}`" for r in unavailable)
            print(json.dumps({"systemMessage": f"agentic_init: could not run {missing}; that check is unverified."}))
        return 0

    failures = "\n\n".join(
        f"$ {r['command']} (exit {r['exit_code']})\n{r['output_tail']}"
        for r in results
        if r["exit_code"] and r["available"]
    )
    print(json.dumps({"decision": "block", "reason": f"Verification failed. Fix before finishing:\n\n{failures}"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
