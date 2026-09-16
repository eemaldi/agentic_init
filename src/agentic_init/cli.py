from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from agentic_init import __version__, catalog, doctor, enrich, wizard, writer
from agentic_init.config import CONFIG_FILE, Config, ConfigError, Kind, load_config, save_config
from agentic_init.detect import detect
from agentic_init.engine import build
from agentic_init.modules import bmad

app = typer.Typer(no_args_is_help=True, add_completion=False, help="Bootstrap your repository for agentic development.")
console = Console()

Root = Annotated[Path, typer.Argument(help="Project directory", file_okay=False, resolve_path=True)]
DryRun = Annotated[bool, typer.Option("--dry-run", help="Show what would change without writing")]
Force = Annotated[bool, typer.Option("--force", help="Overwrite files modified locally or not managed by agentic_init")]

STYLES = {
    writer.Action.CREATE: "green",
    writer.Action.UPDATE: "yellow",
    writer.Action.DELETE: "red",
    writer.Action.SKIP: "magenta",
}
MARKS = {doctor.Level.OK: "[green]✓[/]", doctor.Level.WARN: "[yellow]![/]", doctor.Level.ERROR: "[red]✗[/]"}


def _fail(message: str) -> typer.Exit:
    console.print(f"[red]{message}[/]")
    return typer.Exit(1)


def _summarize(plan: writer.Plan) -> None:
    table = Table(show_header=False, box=None, pad_edge=False)
    for change in (*plan.pending, *plan.skipped):
        style = STYLES[change.action]
        table.add_row(f"[{style}]{change.action}[/]", change.path, f"[dim]{change.reason}[/]")
    if table.row_count:
        console.print(table)
    else:
        console.print("[green]Everything is up to date.[/]")


def _next_steps(root: Path, config: Config) -> None:
    blueprint = build(root, config).blueprint
    steps = []
    for server in blueprint.of(Kind.MCP):
        steps += [f"export {variable}=…  (for the {server.name} MCP server)" for variable in server.meta.get("env", [])]
    if config.enrich:
        steps.append("agentic_init enrich  (let Claude map the codebase into the generated docs)")
    if config.modules.bmad and not bmad.is_installed(root):
        steps.append(f"{' '.join(bmad.INSTALL_COMMAND)}  (install BMAD planning workflows)")
    steps += ["agentic_init doctor", "claude"]
    console.print("\n[bold]Next[/]")
    for step in steps:
        console.print(f"  [cyan]{step}[/]")


def _apply(root: Path, config: Config, dry_run: bool, force: bool) -> None:
    result = build(root, config, force)
    _summarize(result.plan)
    if dry_run:
        return
    writer.apply(root, result.plan)
    wants_bmad = config.modules.bmad and not bmad.is_installed(root) and bmad.can_install()
    if wants_bmad and console.is_interactive and typer.confirm("Install BMAD now via npx?", default=True):
        bmad.install(root)
    _next_steps(root, config)


@app.command()
def init(
    root: Root = Path("."),
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Accept detected defaults without prompting")] = False,
    dry_run: DryRun = False,
    force: Force = False,
) -> None:
    """Detect the project, ask a few questions, write agentic_init.yaml and apply it."""
    if (root / CONFIG_FILE).exists():
        if yes:
            raise _fail(f"{CONFIG_FILE} exists; run `agentic_init apply`, or delete it to start over.")
        if not typer.confirm(f"{CONFIG_FILE} exists. Reconfigure?"):
            raise typer.Exit()
    detection = detect(root)
    config = wizard.defaults(root.name, detection) if yes else wizard.run(root.name, detection)
    if not dry_run:
        console.print(f"[green]wrote[/] {save_config(root, config).name}")
    _apply(root, config, dry_run, force)


@app.command(name="apply")
def apply_command(root: Root = Path("."), dry_run: DryRun = False, force: Force = False) -> None:
    """Regenerate the agent setup from agentic_init.yaml."""
    try:
        _apply(root, load_config(root), dry_run, force)
    except ConfigError as error:
        raise _fail(str(error)) from error


@app.command()
def diff(root: Root = Path(".")) -> None:
    """Show pending changes as a unified diff."""
    try:
        plan = build(root).plan
    except ConfigError as error:
        raise _fail(str(error)) from error
    for change in plan.pending:
        console.print(Syntax(change.diff(), "diff", theme="ansi_dark", background_color="default"))
    _summarize(plan)


@app.command(name="doctor")
def doctor_command(root: Root = Path(".")) -> None:
    """Check the agent setup against best practices."""
    findings = doctor.diagnose(root)
    for finding in findings:
        console.print(f"{MARKS[finding.level]} {finding.message}")
    if any(f.level == doctor.Level.ERROR for f in findings):
        raise typer.Exit(1)


@app.command(name="enrich")
def enrich_command(root: Root = Path(".")) -> None:
    """Run Claude Code headless to map the codebase into the generated docs."""
    if not enrich.available():
        raise _fail("`claude` is not on PATH. Install Claude Code first.")
    if not (root / ".claude" / "skills" / enrich.SKILL).exists():
        raise _fail(f"Set `enrich: true` in {CONFIG_FILE} and run `agentic_init apply` first.")
    raise typer.Exit(enrich.run(root))


@app.command(name="catalog")
def catalog_command() -> None:
    """List available skills, agents, hooks, rules, MCP servers and docs."""
    for kind in Kind:
        table = Table(title=kind.value, title_justify="left", show_header=False, box=None)
        for name in catalog.available(kind):
            table.add_row(f"[cyan]{name}[/]", catalog.load(kind, name).description)
        console.print(table, "")


@app.command()
def schema() -> None:
    """Print the JSON Schema for agentic_init.yaml."""
    import json

    print(json.dumps(Config.model_json_schema(), indent=2))


@app.command()
def version() -> None:
    """Print the agentic_init version."""
    print(__version__)
