import json

from conftest import apply, configure

from agentic_init.config import Mode
from agentic_init.doctor import Level, diagnose


def test_fresh_setup_has_no_errors_and_detects_breakage(python_project):
    configure(python_project, level=3)
    apply(python_project)

    assert [f.message for f in diagnose(python_project) if f.level == Level.ERROR] == []

    (python_project / ".claude/hooks/protect-secrets.py").unlink()
    (python_project / ".claude/skills/test/SKILL.md").write_text("changed")

    messages = [f.message for f in diagnose(python_project)]
    assert "hook script missing: .claude/hooks/protect-secrets.py" in messages
    assert any("SKILL.md modified locally" in m for m in messages)


def test_missing_config_is_an_error(tmp_path):
    [finding] = diagnose(tmp_path)

    assert finding.level == Level.ERROR


def test_unknown_component_is_reported_not_raised(python_project):
    configure(python_project, include={"skills": ["implemnt"]})

    [finding] = diagnose(python_project)

    assert finding.level == Level.ERROR
    assert "Unknown skill 'implemnt'" in finding.message


def test_non_command_hooks_and_invalid_mcp_json_are_tolerated(python_project):
    configure(python_project)
    apply(python_project)
    settings_path = python_project / ".claude/settings.json"
    settings = json.loads(settings_path.read_text())
    settings["hooks"]["Stop"] = [{"hooks": [{"type": "prompt", "prompt": "Is the work verified?"}]}]
    settings_path.write_text(json.dumps(settings))
    (python_project / ".mcp.json").write_text("{broken")

    findings = diagnose(python_project)

    assert any(f.level == Level.ERROR and ".mcp.json is not valid JSON" in f.message for f in findings)
    assert not any("hook script missing" in f.message for f in findings)


def test_untouched_doc_templates_are_reported(python_project):
    configure(python_project, level=2, mode=Mode.BROWNFIELD)
    apply(python_project)

    findings = diagnose(python_project)

    assert any("still hold the template" in f.message for f in findings)

    for doc in (python_project / "docs").rglob("*.md"):
        doc.write_text("# Real content\n\nThe order service owns checkout.\n")

    assert not any("still hold the template" in f.message for f in diagnose(python_project))


def test_missing_ci_is_a_warning_and_generated_ci_is_checked(python_project):
    configure(python_project, level=2)
    apply(python_project)

    assert any("no CI workflow" in f.message for f in diagnose(python_project))

    configure(python_project, level=2, ci=True)
    apply(python_project)
    findings = diagnose(python_project)

    assert any(f.level == Level.OK and "CI runs" in f.message for f in findings)

    workflow = python_project / ".github/workflows/agentic-checks.yml"
    workflow.write_text(workflow.read_text().replace("uv run pytest", "echo skipped"))

    assert any("CI does not run the test command" in f.message for f in diagnose(python_project))
