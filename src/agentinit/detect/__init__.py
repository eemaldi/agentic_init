from dataclasses import dataclass
from pathlib import Path

from agentinit.config import Commands, Mode
from agentinit.detect.commands import detect_commands
from agentinit.detect.git import GitInfo, detect_git
from agentinit.detect.stack import Stack, count_source_files, detect_stack

BROWNFIELD_COMMITS = 20
BROWNFIELD_SOURCE_FILES = 30


@dataclass(frozen=True)
class Detection:
    stack: Stack
    commands: Commands
    git: GitInfo
    source_files: int

    @property
    def mode(self) -> Mode:
        established = self.git.commits >= BROWNFIELD_COMMITS or self.source_files >= BROWNFIELD_SOURCE_FILES
        return Mode.BROWNFIELD if established else Mode.GREENFIELD

    @property
    def suggested_level(self) -> int:
        return 1 if self.source_files < 50 else 2


def detect(root: Path) -> Detection:
    stack = detect_stack(root)
    return Detection(
        stack=stack,
        commands=detect_commands(root, stack),
        git=detect_git(root),
        source_files=count_source_files(root),
    )
