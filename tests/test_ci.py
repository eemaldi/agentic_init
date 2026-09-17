import json

import yaml
from conftest import apply, configure

from agentic_init.ci import PR_TEMPLATE_PATH, WORKFLOW_PATH
from agentic_init.config import Mode


def workflow(root):
    return yaml.safe_load((root / WORKFLOW_PATH).read_text())


def steps(document, job):
    return document["jobs"][job]["steps"]


def test_ci_runs_the_projects_own_commands(python_project):
    configure(python_project, level=2, ci=True)
    apply(python_project)

    document = workflow(python_project)
    runs = [step["run"] for step in steps(document, "checks") if "run" in step]

    assert runs == ["uv sync", "uv run ruff check .", "uv run mypy .", "uv run pytest"]
    assert any(step.get("uses", "").startswith("astral-sh/setup-uv") for step in steps(document, "checks"))
    assert document["on"]["pull_request"] == {}


def test_node_project_gets_matching_setup_and_e2e_job(node_project):
    configure(node_project, level=2, ci=True)
    apply(node_project)

    document = workflow(node_project)
    setup = [step["uses"] for step in steps(document, "checks") if "uses" in step]
    e2e = [step.get("run") for step in steps(document, "e2e")]

    assert "pnpm/action-setup@v4" in setup and "actions/setup-node@v4" in setup
    assert "pnpm exec playwright test" in e2e
    assert "npx playwright install --with-deps" in e2e
    assert "security" in document["jobs"]


def test_level_one_keeps_the_pipeline_minimal(node_project):
    configure(node_project, level=1, ci=True)
    apply(node_project)

    assert set(workflow(node_project)["jobs"]) == {"checks"}


def test_ci_is_generated_for_github_repositories_and_skipped_otherwise(python_project):
    configure(python_project, level=1)
    apply(python_project)

    assert not (python_project / WORKFLOW_PATH).exists()

    (python_project / ".github").mkdir()
    apply(python_project)

    assert (python_project / WORKFLOW_PATH).exists()


def test_pull_request_template_lists_the_evidence_to_fill_in(python_project):
    configure(python_project, level=2, ci=True)
    apply(python_project)

    template = (python_project / PR_TEMPLATE_PATH).read_text()

    assert "| Tests | `uv run pytest` | |" in template
    for heading in ("Architecture impact", "Migration impact", "Evidence", "Residual risk"):
        assert f"## {heading}" in template


def test_pull_request_template_is_a_seed_and_survives_editing(python_project):
    configure(python_project, level=2, ci=True)
    apply(python_project)
    (python_project / PR_TEMPLATE_PATH).write_text("## Our own template\n")

    apply(python_project)

    assert (python_project / PR_TEMPLATE_PATH).read_text() == "## Our own template\n"


def test_disabling_ci_retires_the_generated_workflow(python_project):
    configure(python_project, level=2, ci=True)
    apply(python_project)
    assert (python_project / WORKFLOW_PATH).exists()

    configure(python_project, level=2, ci=False)
    apply(python_project)

    assert not (python_project / WORKFLOW_PATH).exists()


def test_workflow_and_claude_md_agree_on_the_test_command(python_project):
    configure(python_project, level=2, mode=Mode.GREENFIELD, ci=True, commands={"test": "uv run pytest -x"})
    apply(python_project)

    runs = json.dumps(workflow(python_project))

    assert "uv run pytest -x" in runs
    assert "uv run pytest -x" in (python_project / "CLAUDE.md").read_text()
