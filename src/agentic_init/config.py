from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

CONFIG_FILE = "agentic_init.yaml"


class ConfigError(Exception):
    pass


class Mode(StrEnum):
    GREENFIELD = "greenfield"
    BROWNFIELD = "brownfield"


class Kind(StrEnum):
    SKILLS = "skills"
    AGENTS = "agents"
    HOOKS = "hooks"
    RULES = "rules"
    MCP = "mcp"
    DOCS = "docs"


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Project(Strict):
    name: str
    description: str = ""


class Selection(Strict):
    skills: list[str] = []
    agents: list[str] = []
    hooks: list[str] = []
    rules: list[str] = []
    mcp: list[str] = []
    docs: list[str] = []

    def of(self, kind: Kind) -> list[str]:
        return getattr(self, kind.value)


class Modules(Strict):
    aidlc: bool = Field(False, description="Evidence-gated delivery: verification hook + evidence skill.")
    bmad: bool = Field(False, description="BMAD planning workflows, installed via npx bmad-method.")


class Commands(Strict):
    install: str | None = None
    dev: str | None = None
    build: str | None = None
    test: str | None = None
    test_one: str | None = None
    lint: str | None = None
    format: str | None = None
    typecheck: str | None = None
    e2e: str | None = None

    @field_validator("*", mode="before")
    @classmethod
    def blank_is_none(cls, value: str | None) -> str | None:
        return value.strip() or None if isinstance(value, str) else value

    def overridden(self) -> dict[str, str | None]:
        return self.model_dump(include=self.model_fields_set)

    def overlay(self, overrides: "Commands") -> "Commands":
        return Commands(**{**self.model_dump(), **overrides.overridden()})


class Config(Strict):
    version: Literal[1] = 1
    project: Project
    level: int = Field(ge=0, le=4, description="0 tiny · 1 small app · 2 production · 3 large · 4 enterprise")
    mode: Mode
    autonomy: int | None = Field(None, ge=0, le=5, description="A0–A5; omit to use the preset default")
    targets: list[str] = ["claude-code"]
    modules: Modules = Modules()
    include: Selection = Selection()
    exclude: Selection = Selection()
    commands: Commands = Field(Commands(), description="Override detected commands; set one to null to disable it.")
    ci: bool | None = Field(None, description="Generate a CI workflow; omit to decide from the repository.")
    enrich: bool = Field(False, description="Generate the agentic_init-enrich skill for a Claude mapping pass.")

    @field_validator("targets")
    @classmethod
    def known_targets(cls, targets: list[str]) -> list[str]:
        from agentic_init.targets import TARGETS

        unknown = set(targets) - TARGETS.keys()
        if unknown:
            raise ValueError(f"unknown targets {sorted(unknown)}; available: {sorted(TARGETS)}")
        return targets


def load_config(root: Path) -> Config:
    path = root / CONFIG_FILE
    if not path.exists():
        raise ConfigError(f"{CONFIG_FILE} not found in {root}. Run `agentic_init init` first.")
    try:
        return Config.model_validate(yaml.safe_load(path.read_text()) or {})
    except ValidationError as error:
        raise ConfigError(f"Invalid {CONFIG_FILE}:\n{error}") from error


def save_config(root: Path, config: Config) -> Path:
    data = config.model_dump(mode="json", exclude_none=True)
    if not data["project"]["description"]:
        del data["project"]["description"]
    data["commands"] = config.commands.overridden()
    for key in ("include", "exclude"):
        data[key] = {k: v for k, v in data[key].items() if v}
    for key in ("include", "exclude", "commands"):
        if not data[key]:
            del data[key]
    path = root / CONFIG_FILE
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return path
