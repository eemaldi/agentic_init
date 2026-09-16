from agentic_init.config import Kind, Mode, Selection

LEVELS = {
    0: "Tiny script / one-off",
    1: "Small application",
    2: "Production application",
    3: "Large system / monorepo",
    4: "Enterprise / regulated",
}

AUTONOMY = {
    0: "Assistant",
    1: "Guided execution",
    2: "Delegated implementation",
    3: "Feature delivery",
    4: "Autonomous integration",
    5: "Autonomous deployment",
}

AUTONOMY_SCOPE = {
    0: "Claude proposes, the human executes",
    1: "Claude implements, the human approves each change",
    2: "Claude plans, implements and tests; the human merges",
    3: "Claude owns the task through a pull request",
    4: "Claude merges after automated verification",
    5: "Claude deploys, monitors and rolls back",
}

_LEVEL_AUTONOMY = {0: 4, 1: 3, 2: 3, 3: 3, 4: 2}

_CUMULATIVE: dict[int, dict[Kind, list[str]]] = {
    0: {},
    1: {
        Kind.SKILLS: ["implement", "test", "review"],
        Kind.AGENTS: ["reviewer"],
        Kind.HOOKS: ["block-dangerous-commands", "protect-secrets"],
        Kind.MCP: ["github"],
    },
    2: {
        Kind.SKILLS: ["debug", "spec", "security-review"],
        Kind.AGENTS: ["test-engineer", "security-reviewer"],
        Kind.HOOKS: ["post-edit-format"],
        Kind.RULES: ["architecture", "testing", "security"],
        Kind.DOCS: ["architecture", "decisions", "stories", "operations"],
    },
    3: {
        Kind.SKILLS: ["discover", "release"],
        Kind.AGENTS: ["explorer", "architect"],
        Kind.HOOKS: ["verify-completion"],
    },
    4: {
        Kind.HOOKS: ["audit-log"],
    },
}

_BROWNFIELD: dict[Kind, list[str]] = {
    Kind.SKILLS: ["discover", "brownfield-change"],
    Kind.DOCS: ["brownfield"],
}


def default_autonomy(level: int, mode: Mode) -> int:
    penalty = 1 if mode == Mode.BROWNFIELD else 0
    return max(1, _LEVEL_AUTONOMY[level] - penalty)


def suggested_modules(level: int) -> dict[str, bool]:
    return {"aidlc": level >= 2, "bmad": level >= 3}


def preset(level: int, mode: Mode) -> Selection:
    selection: dict[str, list[str]] = {kind.value: [] for kind in Kind}
    layers = [_CUMULATIVE[n] for n in range(level + 1)]
    if mode == Mode.BROWNFIELD:
        layers.append(_BROWNFIELD)
    for layer in layers:
        for kind, names in layer.items():
            selection[kind.value] += [n for n in names if n not in selection[kind.value]]
    return Selection(**selection)
