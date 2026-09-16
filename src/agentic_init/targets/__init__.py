from agentic_init.targets.base import Target
from agentic_init.targets.claude_code import ClaudeCodeTarget

TARGETS: dict[str, type[Target]] = {
    ClaudeCodeTarget.name: ClaudeCodeTarget,
}
