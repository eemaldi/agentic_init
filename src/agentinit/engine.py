from dataclasses import dataclass
from pathlib import Path

from agentinit import writer
from agentinit.blueprint import Blueprint
from agentinit.config import Config, load_config
from agentinit.detect import Detection
from agentinit.lock import Lock
from agentinit.resolver import resolve
from agentinit.targets import TARGETS
from agentinit.targets.shared import render_shared


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
