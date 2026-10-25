from dataclasses import dataclass
from pathlib import Path

from agentic_init.config import Commands, Mode
from agentic_init.detect.commands import detect_commands
from agentic_init.detect.git import GitInfo, detect_git
from agentic_init.detect.project import Identity, detect_identity, detect_workspaces
from agentic_init.detect.stack import Stack, count_source_files, detect_stack

BROWNFIELD_COMMITS = 20
BROWNFIELD_SOURCE_FILES = 30


@dataclass(frozen=True)
class Detection:
    stack: Stack
    commands: Commands
    git: GitInfo
    source_files: int
    identity: Identity = Identity()
    workspaces: tuple[str, ...] = ()

    @property
    def monorepo(self) -> bool:
        return len(self.workspaces) > 1

    @property
    def mode(self) -> Mode:
        established = self.git.commits >= BROWNFIELD_COMMITS or self.source_files >= BROWNFIELD_SOURCE_FILES
        return Mode.BROWNFIELD if established else Mode.GREENFIELD

    @property
    def suggested_level(self) -> int:
        if self.monorepo:
            return 3
        return 1 if self.source_files < 50 else 2


def detect(root: Path) -> Detection:
    stack = detect_stack(root)
    return Detection(
        stack=stack,
        commands=detect_commands(root, stack),
        git=detect_git(root),
        source_files=count_source_files(root),
        identity=detect_identity(root),
        workspaces=detect_workspaces(root),
    )
