import json
import os
import subprocess

from conftest import apply, configure

from agentic_init.config import Kind, Mode, Modules
from agentic_init.engine import build
from agentic_init.writer import Action


def test_apply_is_idempotent(python_project):
    configure(python_project, level=3, mode=Mode.BROWNFIELD, modules=Modules(aidlc=True))
    apply(python_project)

    assert build(python_project).plan.pending == []


def test_user_content_in_claude_md_and_settings_survives(python_project):
    (python_project / "CLAUDE.md").write_text("# Team notes\nDeploy on Fridays never.\n")
    (python_project / ".claude").mkdir()
    (python_project / ".claude/settings.json").write_text(json.dumps({"env": {"FOO": "bar"}}))
    configure(python_project)

    apply(python_project)

    claude_md = (python_project / "CLAUDE.md").read_text()
    assert claude_md.startswith("# Team notes\nDeploy on Fridays never.\n")
    assert "<!-- agentic_init:begin commands -->" in claude_md
    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert settings["env"] == {"FOO": "bar"}
    assert "Bash(uv run pytest)" in settings["permissions"]["allow"]


def test_locally_modified_and_unmanaged_files_are_not_overwritten(python_project):
    configure(python_project)
    apply(python_project)
    skill = python_project / ".claude/skills/implement/SKILL.md"
    skill.write_text("my own procedure\n")
    unmanaged = python_project / ".claude/agents/reviewer.md"
    unmanaged.unlink()
    unmanaged.write_text("hand written\n")
    (python_project / ".agentic_init.lock").write_text(
        (python_project / ".agentic_init.lock").read_text().replace('".claude/agents/reviewer.md"', '"gone.md"')
    )

    plan = build(python_project).plan

    skipped = {c.path: c.reason for c in plan.skipped}
    assert skipped[".claude/skills/implement/SKILL.md"] == "modified locally"
    assert skipped[".claude/agents/reviewer.md"] == "exists and is not managed by agentic_init"
    assert build(python_project, force=True).plan.skipped == []


def test_downgrading_level_retires_generated_files_and_settings(python_project):
    configure(python_project, level=2)
    apply(python_project)
    assert (python_project / ".claude/agents/test-engineer.md").exists()

    configure(python_project, level=1)
    plan = apply(python_project)

    assert (python_project / ".claude/agents/test-engineer.md").exists() is False
    assert (python_project / ".claude/rules").exists() is False
    assert any(c.path == ".claude/hooks/post-edit-format.py" and c.action == Action.DELETE for c in plan.changes)
    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert "PostToolUse" not in settings["hooks"]
    assert (python_project / "docs/architecture/system-overview.md").exists()


def test_excluding_everything_removes_mcp_file(python_project):
    configure(python_project)
    apply(python_project)
    assert (python_project / ".mcp.json").exists()

    configure(python_project, exclude={"mcp": ["github"]})
    apply(python_project)

    assert not (python_project / ".mcp.json").exists()


def test_invalid_json_that_is_no_longer_generated_is_skipped_and_stays_tracked(python_project):
    configure(python_project)
    apply(python_project)
    mcp = python_project / ".mcp.json"
    mcp.write_text("{broken")
    configure(python_project, exclude={"mcp": ["github"]})

    plan = apply(python_project)

    assert [(c.path, c.reason) for c in plan.skipped] == [(".mcp.json", "invalid JSON, fix it and re-run")]
    assert mcp.read_text() == "{broken"
    generated = json.loads(
        json.dumps(build(python_project, configure(python_project)).blueprint.of(Kind.MCP)[0].meta["server"])
    )
    configure(python_project, exclude={"mcp": ["github"]})
    mcp.write_text(json.dumps({"mcpServers": {"github": generated, "mine": {"command": "x"}}}))

    apply(python_project)

    assert json.loads(mcp.read_text()) == {"mcpServers": {"mine": {"command": "x"}}}


def test_null_command_disables_a_detected_command(python_project):
    configure(python_project, commands={"test": None})
    apply(python_project)

    assert build(python_project).blueprint.commands.test is None
    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert not any("pytest" in rule for rule in settings["permissions"]["allow"])
    assert "test: null" in (python_project / "agentic_init.yaml").read_text()


def test_enterprise_level_sandboxes_audits_and_allowlists_mcp(python_project):
    configure(python_project, level=4)
    apply(python_project)

    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert settings["sandbox"]["enabled"] and not settings["sandbox"]["allowUnsandboxedCommands"]
    assert settings["permissions"]["disableBypassPermissionsMode"] == "disable"
    servers = ["github", "linear", "sentry", "playwright"]
    assert settings["enabledMcpjsonServers"] == servers
    assert settings["allowedMcpServers"] == [{"serverName": name} for name in servers]
    assert "audit-log.py" in json.dumps(settings["hooks"]["PostToolUse"])

    configure(python_project, level=3)
    apply(python_project)

    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert not {"enabledMcpjsonServers", "allowedMcpServers"} & set(settings)
    assert not {"failIfUnavailable", "allowUnsandboxedCommands"} & set(settings["sandbox"])
    assert "disableBypassPermissionsMode" not in settings["permissions"]


def test_production_level_sandboxes_secrets_without_loosening_approvals(python_project):
    configure(python_project, level=2)
    apply(python_project)

    sandbox = json.loads((python_project / ".claude/settings.json").read_text())["sandbox"]
    assert sandbox["enabled"] and sandbox["autoAllowBashIfSandboxed"] is False
    assert {"./.env", "./secrets", "./**/*.pem"} <= set(sandbox["filesystem"]["denyRead"])
    assert "failIfUnavailable" not in sandbox

    configure(python_project, level=1)
    apply(python_project)

    assert "sandbox" not in json.loads((python_project / ".claude/settings.json").read_text())


def test_enterprise_level_without_mcp_blocks_unlisted_servers_and_keeps_user_approvals(python_project):
    (python_project / ".claude").mkdir()
    (python_project / ".claude/settings.json").write_text(json.dumps({"enableAllProjectMcpServers": True}))
    configure(
        python_project,
        level=4,
        exclude={"mcp": ["github", "linear", "sentry", "playwright"], "hooks": ["audit-log"]},
    )
    apply(python_project)

    settings = json.loads((python_project / ".claude/settings.json").read_text())
    assert settings["allowedMcpServers"] == [] and settings["enableAllProjectMcpServers"] is True
    assert "audit.jsonl" not in (python_project / "CLAUDE.md").read_text()


def test_generated_hooks_do_not_break_a_python_projects_lint_command(python_project):
    configure(python_project, level=2)
    apply(python_project)

    assert (python_project / ".claude/ruff.toml").exists()
    result = subprocess.run(
        ["ruff", "check", "."], cwd=python_project, capture_output=True, text=True, env={"PATH": os.environ["PATH"]}
    )

    assert result.returncode == 0, result.stdout


def test_no_ruff_config_for_a_project_without_python(node_project):
    configure(node_project, level=2)
    apply(node_project)

    assert not (node_project / ".claude/ruff.toml").exists()
