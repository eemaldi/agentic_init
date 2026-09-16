import re
from collections.abc import Callable
from pathlib import Path

from agentinit.config import Commands
from agentinit.detect.stack import Stack, read_package_json

TASK_ALIASES = {
    "install": ("install", "setup", "bootstrap"),
    "dev": ("dev", "start", "serve"),
    "build": ("build",),
    "test": ("test", "tests"),
    "lint": ("lint",),
    "format": ("format", "fmt"),
    "typecheck": ("typecheck", "type-check", "types", "check-types", "tsc"),
    "e2e": ("e2e", "test:e2e", "test-e2e", "e2e-test"),
}

MAKE_TARGET = re.compile(r"^([A-Za-z0-9_.:-]+)\s*:(?!=)", re.M)
JUST_RECIPE = re.compile(r"^@?([A-Za-z0-9_-]+)(?:\s+[^:=\n]*)?:(?!=)", re.M)


def _from_tasks(tasks: set[str], runner: str) -> dict[str, str]:
    found = {}
    for command, aliases in TASK_ALIASES.items():
        task = next((alias for alias in aliases if alias in tasks), None)
        if task:
            found[command] = f"{runner} {task}"
    return found


def _makefile(root: Path, _: Stack) -> dict[str, str]:
    makefile = next((root / n for n in ("Makefile", "makefile", "GNUmakefile") if (root / n).exists()), None)
    return _from_tasks(set(MAKE_TARGET.findall(makefile.read_text())), "make") if makefile else {}


def _justfile(root: Path, _: Stack) -> dict[str, str]:
    justfile = next((root / n for n in ("justfile", "Justfile", ".justfile") if (root / n).exists()), None)
    return _from_tasks(set(JUST_RECIPE.findall(justfile.read_text())), "just") if justfile else {}


def _package_scripts(root: Path, stack: Stack) -> dict[str, str]:
    package = read_package_json(root)
    if not package:
        return {}
    manager = stack.manager("pnpm", "yarn", "bun", "npm") or "npm"
    found = _from_tasks(set(package.get("scripts", {})), f"{manager} run")
    found["install"] = f"{manager} install"
    if found.get("test") and manager in ("npm", "pnpm", "yarn", "bun"):
        found["test"] = f"{manager} test"
    dependencies = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    runner = {"npm": "npx", "pnpm": "pnpm exec", "yarn": "yarn", "bun": "bunx"}[manager]
    if "vitest" in dependencies:
        found["test_one"] = f"{runner} vitest run path/to/file.test.ts"
    elif "jest" in dependencies:
        found["test_one"] = f"{runner} jest path/to/file.test.ts"
    if "@playwright/test" in dependencies:
        found.setdefault("e2e", f"{runner} playwright test")
    return found


def _python(root: Path, stack: Stack) -> dict[str, str]:
    if not stack.uses("python"):
        return {}
    manifest = " ".join((root / n).read_text() for n in ("pyproject.toml", "requirements.txt") if (root / n).exists())
    manager = stack.manager("uv", "poetry", "pipenv")
    run = {"uv": "uv run ", "poetry": "poetry run ", "pipenv": "pipenv run "}.get(manager, "")
    install = {"uv": "uv sync", "poetry": "poetry install", "pipenv": "pipenv install --dev"}
    found = {"install": install.get(manager, "pip install -e .")}
    if "pytest" in manifest:
        found["test"] = f"{run}pytest"
        found["test_one"] = f"{run}pytest path/to/test_file.py::test_name"
    if "ruff" in manifest:
        found["lint"] = f"{run}ruff check ."
        found["format"] = f"{run}ruff format ."
    if "mypy" in manifest:
        found["typecheck"] = f"{run}mypy ."
    elif "pyright" in manifest:
        found["typecheck"] = f"{run}pyright"
    return found


def _rust(_: Path, stack: Stack) -> dict[str, str]:
    if not stack.uses("rust"):
        return {}
    return {
        "build": "cargo build",
        "test": "cargo test",
        "test_one": "cargo test test_name",
        "lint": "cargo clippy --all-targets -- -D warnings",
        "format": "cargo fmt",
        "typecheck": "cargo check",
    }


def _go(_: Path, stack: Stack) -> dict[str, str]:
    if not stack.uses("go"):
        return {}
    return {
        "build": "go build ./...",
        "test": "go test ./...",
        "test_one": "go test ./path/to/pkg -run TestName",
        "lint": "go vet ./...",
        "format": "gofmt -w .",
    }


SOURCES: tuple[Callable[[Path, Stack], dict[str, str]], ...] = (
    _makefile,
    _justfile,
    _package_scripts,
    _python,
    _rust,
    _go,
)


def detect_commands(root: Path, stack: Stack) -> Commands:
    found: dict[str, str] = {}
    for source in SOURCES:
        for name, command in source(root, stack).items():
            found.setdefault(name, command)
    return Commands(**found)
