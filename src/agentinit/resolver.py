from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from agentinit import catalog
from agentinit.blueprint import Blueprint, Component, Section
from agentinit.catalog import CATALOG_DIR, CatalogItem
from agentinit.config import Config, Kind
from agentinit.detect import Detection, detect
from agentinit.modules import module_selections
from agentinit.policy import build_policy
from agentinit.presets import AUTONOMY, LEVELS, default_autonomy, preset

SECTIONS = ("project", "commands", "workflow", "verification", "context")
BODY = "body.md"
FILES_DIR = "files"

templates = Environment(
    loader=FileSystemLoader(CATALOG_DIR),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def select(config: Config) -> dict[Kind, list[str]]:
    layers = [preset(config.level, config.mode), *module_selections(config), config.include]
    selected = {}
    for kind in Kind:
        names = list(dict.fromkeys(name for layer in layers for name in layer.of(kind)))
        selected[kind] = [n for n in names if n not in config.exclude.of(kind)]
    return selected


def _render_component(item: CatalogItem, context: dict) -> Component:
    body, files = "", {}
    for name in item.template_names():
        relative = Path(name).relative_to(Path(item.kind.value) / item.name).as_posix()
        rendered = templates.get_template(name).render(context)
        if relative == BODY:
            body = rendered
        else:
            files[relative.removeprefix(f"{FILES_DIR}/")] = rendered
    return Component(item.kind, item.name, item.description, item.meta, body, files)


def resolve(config: Config, root: Path, detection: Detection | None = None) -> Blueprint:
    detection = detection or detect(root)
    commands = detection.commands.overlay(config.commands)
    autonomy = config.autonomy if config.autonomy is not None else default_autonomy(config.level, config.mode)
    items = [catalog.load(kind, name) for kind, names in select(config).items() for name in names]

    context = {
        "project": config.project,
        "level": config.level,
        "level_name": LEVELS[config.level],
        "mode": config.mode.value,
        "autonomy": autonomy,
        "autonomy_name": AUTONOMY[autonomy],
        "modules": config.modules,
        "stack": detection.stack,
        "commands": commands.model_dump(),
        "selected": {kind.value: {i.name: i.description for i in items if i.kind == kind} for kind in Kind},
    }
    sections = tuple(
        Section(name, body)
        for name in SECTIONS
        if (body := templates.get_template(f"instructions/{name}.md").render(context)).strip()
    )
    return Blueprint(
        config=config,
        detection=detection,
        commands=commands,
        autonomy=autonomy,
        sections=sections,
        components=tuple(_render_component(item, context) for item in items),
        policy=build_policy(autonomy, config.level, commands),
    )
