import questionary
from questionary import Choice

from agentic_init import catalog, enrich
from agentic_init.config import Commands, Config, Kind, Mode, Modules, Project, Selection
from agentic_init.detect import Detection
from agentic_init.presets import AUTONOMY, AUTONOMY_SCOPE, LEVELS, default_autonomy, preset, suggested_modules

COMMAND_NAMES = list(Commands.model_fields)


def defaults(name: str, detection: Detection) -> Config:
    level, mode = detection.suggested_level, detection.mode
    return Config(
        project=Project(
            name=detection.identity.name or name,
            description=detection.identity.description or "",
        ),
        level=level,
        mode=mode,
        modules=Modules(**suggested_modules(level)),
    )


def _ask_commands(detected: Commands) -> Commands:
    detected_values = detected.model_dump()
    listing = "\n".join(f"    {n}: {c}" for n, c in detected_values.items() if c) or "    (none)"
    if questionary.confirm(f"Detected commands:\n{listing}\n  Use these?", default=True).unsafe_ask():
        return Commands()
    overrides = {}
    for name in COMMAND_NAMES:
        answer = questionary.text(f"{name} (empty to disable):", default=detected_values[name] or "").unsafe_ask()
        if answer.strip() != (detected_values[name] or ""):
            overrides[name] = answer
    return Commands(**overrides)


def _mcp_overrides(level: int, mode: Mode, suggest_github: bool) -> tuple[list[str], list[str]]:
    preset_mcp = preset(level, mode).mcp
    choices = [
        Choice(
            f"{name}: {catalog.load(Kind.MCP, name).description}",
            value=name,
            checked=name in preset_mcp or (name == "github" and suggest_github),
        )
        for name in catalog.available(Kind.MCP)
    ]
    chosen = questionary.checkbox("MCP servers", choices=choices).unsafe_ask()
    return [n for n in chosen if n not in preset_mcp], [n for n in preset_mcp if n not in chosen]


def run(name: str, detection: Detection) -> Config:
    base = defaults(name, detection)
    project = Project(
        name=questionary.text("Project name", default=base.project.name).unsafe_ask(),
        description=questionary.text("One-line description (optional)", default=base.project.description).unsafe_ask(),
    )
    mode = questionary.select(
        "Project type",
        choices=[
            Choice("Greenfield: new project, you control the architecture", value=Mode.GREENFIELD),
            Choice("Brownfield: existing codebase, understand before changing", value=Mode.BROWNFIELD),
        ],
        default=base.mode,
    ).unsafe_ask()
    level = questionary.select(
        "Project size",
        choices=[Choice(f"L{n}  {label}", value=n) for n, label in LEVELS.items()],
        default=base.level,
    ).unsafe_ask()
    suggested_autonomy = default_autonomy(level, mode)
    autonomy = questionary.select(
        "Default autonomy",
        choices=[Choice(f"A{n}  {label}: {AUTONOMY_SCOPE[n]}", value=n) for n, label in AUTONOMY.items()],
        default=suggested_autonomy,
    ).unsafe_ask()
    suggested = suggested_modules(level)
    modules = questionary.checkbox(
        "Modules",
        choices=[
            Choice(
                "AIDLC: evidence-gated delivery (verification hook + evidence skill)",
                value="aidlc",
                checked=suggested["aidlc"],
            ),
            Choice(
                "BMAD: structured planning (brief → PRD → architecture → stories, via npx)",
                value="bmad",
                checked=suggested["bmad"],
            ),
        ],
    ).unsafe_ask()
    include_mcp, exclude_mcp = _mcp_overrides(level, mode, detection.git.on_github)
    commands = _ask_commands(detection.commands)
    enrich_pass = (
        enrich.available()
        and questionary.confirm(
            "Add a Claude pass that maps the codebase into the generated docs (`agentic_init enrich`)?",
            default=mode == Mode.BROWNFIELD,
        ).unsafe_ask()
    )

    return Config(
        project=project,
        level=level,
        mode=mode,
        autonomy=None if autonomy == suggested_autonomy else autonomy,
        modules=Modules(aidlc="aidlc" in modules, bmad="bmad" in modules),
        include=Selection(mcp=include_mcp),
        exclude=Selection(mcp=exclude_mcp),
        commands=commands,
        enrich=enrich_pass,
    )
