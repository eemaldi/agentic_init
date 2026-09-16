from dataclasses import dataclass
from pathlib import Path

from agentic_init import writer
from agentic_init.blueprint import Blueprint
from agentic_init.config import Config, load_config
from agentic_init.detect import Detection
from agentic_init.lock import Lock
from agentic_init.resolver import resolve
from agentic_init.targets import TARGETS
from agentic_init.targets.shared import render_shared


@dataclass(frozen=True)
class Build:
    blueprint: Blueprint
    plan: writer.Plan


def build(root: Path, config: Config | None = None, force: bool = False, detection: Detection | None = None) -> Build:
    config = config or load_config(root)
    blueprint = resolve(config, root, detection)
    ops = render_shared(blueprint)
    for name in config.targets:
        ops += TARGETS[name]().render(blueprint)
    return Build(blueprint, writer.plan(root, ops, Lock.load(root), force))
