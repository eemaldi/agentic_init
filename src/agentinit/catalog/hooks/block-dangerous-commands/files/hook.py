#!/usr/bin/env python3
import json
import re
import sys

DANGEROUS = [
    (r"\brm\s+(-\w+\s+)*-\w*[rR]\w*\s+(-\w+\s+)*(/|~|\$HOME|\*|\.{1,2})/?(\s|$)", "recursive delete of a root, home, parent or wildcard path"),
    (r"\bgit\s+push\b.*\s(--force(?!-with-lease)|-f)(\s|$)", "force push; use --force-with-lease on your own branch if truly needed"),
    (r"\bgit\s+push\b.*\s\+\S+", "force push via refspec"),
    (r"(?i)\b(drop|truncate)\s+(table|database|schema)\b", "destructive SQL"),
    (r"\b(curl|wget)\b[^|;&]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", "piping a remote script into a shell"),
    (r"\bmkfs(\.\w+)?\b|\bdd\b.*\bof=/dev/", "writing to a raw device"),
    (r"\bchmod\s+(-R\s+)?0?777\b", "world-writable permissions"),
    (r"\bterraform\s+(apply|destroy)\b|\bkubectl\s+(delete|apply)\b|\bhelm\s+(uninstall|upgrade|install)\b", "infrastructure mutation outside the release workflow"),
]


def main() -> int:
    command = json.load(sys.stdin).get("tool_input", {}).get("command", "")
    for pattern, reason in DANGEROUS:
        if re.search(pattern, command):
            print(f"Blocked by agentinit: {reason}. If this is required, ask the human to run it.", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
