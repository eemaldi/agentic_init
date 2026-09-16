from agentinit.blueprint import Blueprint
from agentinit.config import Kind
from agentinit.targets.base import Block, FileOp, Strategy

IGNORED = (".claude/settings.local.json", ".claude/state/")


def render_shared(blueprint: Blueprint) -> list[FileOp]:
    seeds = [
        FileOp(path, Strategy.SEED, content=content)
        for doc in blueprint.of(Kind.DOCS)
        for path, content in doc.files.items()
    ]
    gitignore = FileOp(".gitignore", Strategy.BLOCKS, blocks=(Block("agent-state", "\n".join(IGNORED)),))
    return [*seeds, gitignore]
