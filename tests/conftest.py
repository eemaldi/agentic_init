import json
from pathlib import Path

import pytest

from agentic_init import writer
from agentic_init.config import Config, Mode, Project, save_config
from agentic_init.engine import build


@pytest.fixture
def python_project(tmp_path: Path) -> Path:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "shop"\ndependencies = ["fastapi"]\n[dependency-groups]\ndev = ["pytest", "ruff", "mypy"]\n'
    )
    (tmp_path / "uv.lock").write_text("")
    return tmp_path


@pytest.fixture
def node_project(tmp_path: Path) -> Path:
    package = {
        "scripts": {"dev": "vite", "build": "vite build", "test": "vitest", "lint": "eslint ."},
        "devDependencies": {"vitest": "1", "react": "18", "@playwright/test": "1"},
    }
    (tmp_path / "package.json").write_text(json.dumps(package))
    (tmp_path / "pnpm-lock.yaml").write_text("")
    (tmp_path / "tsconfig.json").write_text("{}")
    return tmp_path


def configure(root: Path, level: int = 1, mode: Mode = Mode.GREENFIELD, **overrides) -> Config:
    config = Config(project=Project(name="shop"), level=level, mode=mode, **overrides)
    save_config(root, config)
    return config


def apply(root: Path, force: bool = False) -> writer.Plan:
    plan = build(root, force=force).plan
    writer.apply(root, plan)
    return plan
