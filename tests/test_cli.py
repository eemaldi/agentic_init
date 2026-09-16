from conftest import configure
from typer.testing import CliRunner

from agentic_init.cli import app


def test_init_yes_refuses_to_overwrite_existing_config(python_project):
    configure(python_project, level=3, include={"skills": ["release"]})
    config = (python_project / "agentic_init.yaml").read_text()

    result = CliRunner().invoke(app, ["init", str(python_project), "--yes"])

    assert result.exit_code == 1
    assert "agentic_init apply" in result.output
    assert (python_project / "agentic_init.yaml").read_text() == config
    assert not (python_project / ".claude").exists()


def test_doctor_reports_unknown_component_without_traceback(python_project):
    configure(python_project, include={"skills": ["implemnt"]})

    result = CliRunner().invoke(app, ["doctor", str(python_project)])

    assert result.exit_code == 1
    assert "Unknown skill 'implemnt'" in result.output
    assert result.exception is None or isinstance(result.exception, SystemExit)
