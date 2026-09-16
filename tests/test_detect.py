from agentinit.config import Mode
from agentinit.detect import detect


def test_python_uv_project(python_project):
    detection = detect(python_project)

    assert detection.stack.languages == ("python",)
    assert "uv" in detection.stack.package_managers
    assert "FastAPI" in detection.stack.frameworks
    assert detection.commands.test == "uv run pytest"
    assert detection.commands.lint == "uv run ruff check ."
    assert detection.commands.typecheck == "uv run mypy ."


def test_node_project_uses_lockfile_manager_and_scripts(node_project):
    detection = detect(node_project)

    assert detection.stack.languages == ("javascript", "typescript")
    assert detection.commands.test == "pnpm test"
    assert detection.commands.lint == "pnpm run lint"
    assert detection.commands.test_one == "pnpm exec vitest run path/to/file.test.ts"
    assert detection.commands.e2e == "pnpm exec playwright test"
    assert "React" in detection.stack.frameworks


def test_task_runner_takes_precedence_over_language_defaults(python_project):
    (python_project / "Makefile").write_text("test:\n\tuv run pytest -x\nlint:\n\truff check\nVAR := 1\n")

    commands = detect(python_project).commands

    assert commands.test == "make test"
    assert commands.lint == "make lint"
    assert commands.typecheck == "uv run mypy ."


def test_mode_is_brownfield_for_established_codebases(python_project):
    assert detect(python_project).mode == Mode.GREENFIELD

    for n in range(40):
        (python_project / f"module_{n}.py").write_text("")

    assert detect(python_project).mode == Mode.BROWNFIELD
