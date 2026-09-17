import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitInfo:
    is_repo: bool = False
    commits: int = 0
    remote: str | None = None
    default_branch: str = "main"

    @property
    def on_github(self) -> bool:
        return bool(self.remote and "github.com" in self.remote)


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def detect_git(root: Path) -> GitInfo:
    if _git(root, "rev-parse", "--is-inside-work-tree") != "true":
        return GitInfo()
    commits = _git(root, "rev-list", "--count", "HEAD")
    return GitInfo(
        is_repo=True,
        commits=int(commits) if commits and commits.isdigit() else 0,
        remote=_git(root, "remote", "get-url", "origin"),
        default_branch=_default_branch(root),
    )


def _default_branch(root: Path) -> str:
    remote_head = _git(root, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if remote_head:
        return remote_head.rsplit("/", 1)[-1]
    branches = (_git(root, "branch", "--format=%(refname:short)") or "").split()
    conventional = next((name for name in ("main", "master") if name in branches), None)
    return conventional or _git(root, "branch", "--show-current") or "main"
