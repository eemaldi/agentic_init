#!/usr/bin/env python3
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

SECRET = re.compile(
    r"(^|/)(\.env(\.[\w.-]+)?|[^/]*\.(pem|key|p12|pfx|keystore)|id_(rsa|ecdsa|ed25519)"
    r"|\.aws/credentials|\.netrc|\.pgpass|credentials\.json|service-account[^/]*\.json)$|^(\./)?secrets?/."
)
TEMPLATE = re.compile(r"\.env\.(example|sample|template|dist)$")
SAMPLE_SECRETS = (".env", ".env.local", "id_rsa", "server.pem", "server.key", "credentials.json", "secrets/token")
ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR", ".")).resolve()
MESSAGE_ARGUMENT = re.compile(r"""(-m|--message|--title|--body)(\s+|=)('[^']*'|"[^"$`]*")""")
LITERAL_HEREDOC = re.compile(r"""<<-?\s*(['"])(\w+)\1[^\n]*\n.*?\n\s*\2(?=\s|$)""", re.S)
SEGMENT_SEPARATORS = re.compile(r"\|\|?|&&?|;|\n|\$\(|<\(|>\(|`|\(|\)")
FILTER_ARGUMENT = re.compile(r"(^|\s)(--include|--exclude|--exclude-dir|--glob|-g|-i?name|-i?path)(\s+|=)\S*[*?\[]\S*")
WORD = re.compile(r"[^\s<>=,:\[\]{}]+")
REDIRECT_TARGET = re.compile(r">>?\s*([^\s]+)")
PRINTERS = {"echo", "printf"}


def relative(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute() and candidate.resolve().is_relative_to(ROOT):
        return candidate.resolve().relative_to(ROOT).as_posix()
    return path


def matches(path: str) -> bool:
    return bool(SECRET.search(path)) and not TEMPLATE.search(path)


def is_secret(path: str) -> bool:
    path = relative(path)
    if any(glob in path for glob in "*?["):
        return is_secret_glob(path)
    return matches(path)


def is_secret_glob(pattern: str) -> bool:
    """Block a glob that can sweep up a secret: one whose own shape matches a secret name
    (`*.json`, `deploy/*.pem`), or that currently expands onto a real secret file. A pattern
    that says nothing about secrets, such as `tests/*` or a bare `*` in a directory that holds
    none, is ordinary work and stays allowed."""
    pattern = pattern.removeprefix("./")
    directory, _, name = pattern.rpartition("/")
    candidates = {pattern}
    if directory and re.sub(r"[*?\[\]]", "", name):
        candidates.add(name)
    # A pure wildcard (`*`, `./*`, `*/*`) says nothing about secrets on its own; only the files it
    # actually expands onto do. Judging it by shape blocks every ordinary glob in the repository.
    if re.sub(r"[*?\[\]/]", "", pattern) and any(
        fnmatch.fnmatch(sample, candidate) for sample in SAMPLE_SECRETS for candidate in candidates
    ):
        return True
    try:
        return any(matches(match.relative_to(ROOT).as_posix()) for match in ROOT.glob(pattern))
    except (OSError, ValueError, IndexError, NotImplementedError):
        return False


def shell_targets(command: str) -> list[str]:
    command = LITERAL_HEREDOC.sub("", MESSAGE_ARGUMENT.sub("", command))
    command = FILTER_ARGUMENT.sub(" ", re.sub(r"""['"\\]""", "", command))
    targets = []
    for segment in SEGMENT_SEPARATORS.split(command):
        words = WORD.findall(segment)
        if words and words[0] in PRINTERS and REDIRECT_TARGET.search(segment):
            targets += REDIRECT_TARGET.findall(segment)
        else:
            targets += words
    return targets


def main() -> int:
    payload = json.load(sys.stdin)
    tool_input = payload.get("tool_input", {})
    if payload.get("tool_name") == "Bash":
        candidates = shell_targets(tool_input.get("command", ""))
    else:
        candidates = [tool_input.get("file_path", ""), tool_input.get("path", "")]
    blocked = [path for path in candidates if path and is_secret(path)]
    if blocked:
        print(
            f"Blocked by agentic_init: {blocked[0]} is a secret file. Ask the human for the specific non-secret value you need.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
