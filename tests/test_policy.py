from agentic_init.config import Commands, Mode
from agentic_init.policy import build_policy
from agentic_init.presets import default_autonomy

COMMANDS = Commands(test="make test")


def test_autonomy_controls_delivery_and_integration():
    guided = build_policy(1, 1, COMMANDS)
    delivery = build_policy(3, 1, COMMANDS)
    integration = build_policy(4, 1, COMMANDS)

    assert guided.edits == "ask" and "git commit" not in guided.allowed_commands
    assert "git commit" in delivery.allowed_commands and "git push" in delivery.ask_commands
    assert "git push" in integration.allowed_commands and "gh pr merge" in integration.allowed_commands
    assert build_policy(0, 1, COMMANDS).edits == "propose"


def test_destructive_commands_are_always_denied():
    for autonomy in range(6):
        policy = build_policy(autonomy, 1, COMMANDS)
        assert {"rm -rf", "git push --force"} <= set(policy.denied_commands)
        assert ".env" in policy.protected_paths


def test_project_commands_are_allowed_and_enterprise_blocks_network():
    assert "make test" in build_policy(2, 1, COMMANDS).allowed_commands
    assert "curl" in build_policy(2, 4, COMMANDS).denied_commands


def test_sandbox_hardens_with_level():
    assert [build_policy(2, level, COMMANDS).sandbox for level in range(5)] == ["off", "off", "soft", "soft", "strict"]


def test_brownfield_lowers_default_autonomy():
    assert default_autonomy(2, Mode.BROWNFIELD) == default_autonomy(2, Mode.GREENFIELD) - 1
