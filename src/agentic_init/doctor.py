import json
import os
import re
import shutil
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

import yaml

from agentic_init.config import ConfigError
from agentic_init.engine import Build, build
from agentic_init.lock import Lock, digest

CLAUDE_MD_MAX_LINES = 300
MIN_DESCRIPTION_WORDS = 8
HOOK_SCRIPT = re.compile(r'\$CLAUDE_PROJECT_DIR/([^"\s]+)')


class Level(StrEnum):
    OK = "ok"
    WARN = "warn"
    ERROR = "error"


@dataclass(frozen=True)
class Finding:
    level: Level
    message: str


def _frontmatter(path: Path) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S)
    try:
        fields = yaml.safe_load(match.group(1)) if match else {}
    except yaml.YAMLError:
        return {}
    return fields if isinstance(fields, dict) else {}


def _instructions(root: Path) -> list[Finding]:
    claude_md = root / "CLAUDE.md"
    if not claude_md.exists():
        return [Finding(Level.ERROR, "CLAUDE.md is missing")]
    lines = len(claude_md.read_text().splitlines())
    if lines > CLAUDE_MD_MAX_LINES:
        return [Finding(Level.WARN, f"CLAUDE.md has {lines} lines; move procedures into skills and details into docs")]
    return [Finding(Level.OK, f"CLAUDE.md is {lines} lines")]


def _descriptions(root: Path) -> list[Finding]:
    findings = []
    documents = [*root.glob(".claude/agents/*.md"), *root.glob(".claude/skills/*/SKILL.md")]
    for path in documents:
        description = str(_frontmatter(path).get("description", ""))
        if len(description.split()) < MIN_DESCRIPTION_WORDS:
            findings.append(
                Finding(Level.WARN, f"{path.relative_to(root)}: description too vague for reliable delegation")
            )
    return findings or [Finding(Level.OK, f"{len(documents)} skills/agents have usable descriptions")]


def _json(path: Path) -> dict | Finding | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except ValueError as error:
        return Finding(Level.ERROR, f"{path.name} is not valid JSON: {error}")


def _hooks(root: Path) -> list[Finding]:
    settings = _json(root / ".claude" / "settings.json")
    if not isinstance(settings, dict):
        return [settings] if settings else []
    events = settings.get("hooks", {})
    hooks = [hook for entries in events.values() for entry in entries for hook in entry.get("hooks", [])]
    commands = [hook["command"] for hook in hooks if "command" in hook]
    referenced = [script for command in commands for script in HOOK_SCRIPT.findall(command)]
    findings = [
        Finding(Level.ERROR, f"hook script missing: {script}") for script in referenced if not (root / script).is_file()
    ]
    if referenced and not shutil.which("python3"):
        findings.append(Finding(Level.ERROR, "python3 is not on PATH; hooks cannot run"))
    return findings or [Finding(Level.OK, f"{len(hooks)} hooks are configured")]


def _commands(result: Build) -> list[Finding]:
    commands = result.blueprint.commands.model_dump(exclude_none=True)
    missing = {name: cmd for name, cmd in commands.items() if not shutil.which(cmd.split()[0])}
    findings = [Finding(Level.WARN, f"{name} command not runnable here: `{cmd}`") for name, cmd in missing.items()]
    if not commands.get("test"):
        findings.append(Finding(Level.WARN, "no test command: agents cannot verify their work"))
    return findings or [Finding(Level.OK, f"{len(commands)} project commands resolved")]


def _drift(root: Path, result: Build) -> list[Finding]:
    findings = []
    for path, entry in Lock.load(root).files.items():
        file = root / path
        if entry["strategy"] == "owned" and file.exists() and digest(file.read_text()) != entry["hash"]:
            findings.append(Finding(Level.WARN, f"{path} modified locally; `agentic_init apply --force` restores it"))
    pending = result.plan.pending
    if pending:
        findings.append(Finding(Level.WARN, f"{len(pending)} pending changes; run `agentic_init diff`"))
    return findings or [Finding(Level.OK, "generated files match agentic_init.yaml")]


def _mcp_env(root: Path) -> list[Finding]:
    mcp = _json(root / ".mcp.json")
    if not isinstance(mcp, dict):
        return [mcp] if mcp else []
    variables = set(re.findall(r"\$\{(\w+)", json.dumps(mcp)))
    return [
        Finding(Level.WARN, f"MCP needs ${name} in your environment")
        for name in sorted(variables)
        if name not in os.environ
    ]


def diagnose(root: Path) -> list[Finding]:
    try:
        result = build(root)
    except ConfigError as error:
        return [Finding(Level.ERROR, str(error))]
    return [
        *_instructions(root),
        *_descriptions(root),
        *_hooks(root),
        *_commands(result),
        *_mcp_env(root),
        *_drift(root, result),
    ]
