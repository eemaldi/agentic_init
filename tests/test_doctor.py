import json

from conftest import apply, configure

from agentinit.doctor import Level, diagnose


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
