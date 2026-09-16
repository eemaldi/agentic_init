from dataclasses import dataclass, field
from typing import Literal

from agentic_init.config import Commands, Config, Kind
from agentic_init.detect import Detection


@dataclass(frozen=True)
class Component:
    kind: Kind
    name: str
    description: str
    meta: dict
    body: str = ""
    files: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Section:
    id: str
    body: str


@dataclass(frozen=True)
class Policy:
    edits: Literal["propose", "ask", "auto"]
    allowed_commands: tuple[str, ...]
    ask_commands: tuple[str, ...]
    denied_commands: tuple[str, ...]
    protected_paths: tuple[str, ...]
    enterprise: bool = False
    sandbox: Literal["off", "soft", "strict"] = "off"


@dataclass(frozen=True)
class Blueprint:
    config: Config
    detection: Detection
    commands: Commands
    autonomy: int
    sections: tuple[Section, ...]
    components: tuple[Component, ...]
    policy: Policy

    def of(self, kind: Kind) -> list[Component]:
        return [c for c in self.components if c.kind == kind]

    def has(self, kind: Kind, name: str) -> bool:
        return any(c.name == name for c in self.of(kind))
