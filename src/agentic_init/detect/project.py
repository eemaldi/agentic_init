"""Project identity and workspace layout, read from the repository's own manifests."""

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

from agentic_init.detect.stack import read_package_json

WORKSPACE_CAP = 12
GO_MODULE = re.compile(r"^module\s+(\S+)", re.M)


@dataclass(frozen=True)
class Identity:
    name: str | None = None
    description: str | None = None


def _npm(root: Path) -> Identity:
    package = read_package_json(root)
    name = str(package.get("name") or "").split("/")[-1]
    return Identity(name or None, str(package.get("description") or "") or None)


def _pyproject(root: Path) -> Identity:
    data = _toml(root / "pyproject.toml").get("project", {})
    return Identity(data.get("name"), data.get("description"))


def _cargo(root: Path) -> Identity:
    data = _toml(root / "Cargo.toml").get("package", {})
    return Identity(data.get("name"), data.get("description"))


def _go(root: Path) -> Identity:
    match = GO_MODULE.search(_read(root / "go.mod"))
    return Identity(match.group(1).split("/")[-1] if match else None)


def _toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def _read(path: Path) -> str:
    try:
        return path.read_text()
    except OSError:
        return ""


def detect_identity(root: Path) -> Identity:
    for source in (_npm, _pyproject, _cargo, _go):
        identity = source(root)
        if identity.name:
            return identity
    return Identity()


def _globs(root: Path, patterns: list[str]) -> list[str]:
    found = []
    for pattern in patterns:
        if not isinstance(pattern, str) or pattern.startswith("!"):
            continue
        for match in sorted(root.glob(pattern.rstrip("/"))):
            if match.is_dir() and any((match / m).exists() for m in ("package.json", "pyproject.toml", "Cargo.toml")):
                found.append(match.relative_to(root).as_posix())
    return found


def detect_workspaces(root: Path) -> tuple[str, ...]:
    """Workspace member directories of a monorepo, as declared by its manifests."""
    patterns: list[str] = []
    package = read_package_json(root)
    workspaces = package.get("workspaces")
    patterns += workspaces.get("packages", []) if isinstance(workspaces, dict) else workspaces or []

    pnpm = _read(root / "pnpm-workspace.yaml")
    patterns += re.findall(r"^\s*-\s*['\"]?([^'\"\n]+)", pnpm, re.M)

    pyproject = _toml(root / "pyproject.toml")
    patterns += pyproject.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
    patterns += _toml(root / "Cargo.toml").get("workspace", {}).get("members", [])

    return tuple(dict.fromkeys(_globs(root, patterns)))[:WORKSPACE_CAP]
