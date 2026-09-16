from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

import yaml

from agentinit.blueprint import Blueprint


class Strategy(StrEnum):
    OWNED = "owned"
    BLOCKS = "blocks"
    JSON = "json"
    SEED = "seed"


@dataclass(frozen=True)
class Block:
    id: str
    body: str


@dataclass(frozen=True)
class FileOp:
    path: str
    strategy: Strategy
    content: str = ""
    blocks: tuple[Block, ...] = ()
    data: dict = field(default_factory=dict)
    executable: bool = False


class Target(Protocol):
    name: str

    def render(self, blueprint: Blueprint) -> list[FileOp]: ...


def frontmatter(fields: dict, body: str) -> str:
    present = {k: v for k, v in fields.items() if v not in (None, [], "")}
    if not present:
        return body
    header = yaml.safe_dump(present, sort_keys=False, allow_unicode=True, width=1000)
    return f"---\n{header}---\n\n{body}"
