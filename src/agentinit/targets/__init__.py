from agentinit.targets.base import Target
from agentinit.targets.claude_code import ClaudeCodeTarget

TARGETS: dict[str, type[Target]] = {
    ClaudeCodeTarget.name: ClaudeCodeTarget,
}
