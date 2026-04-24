from __future__ import annotations

from uuid import uuid4

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mindclaw import __version__
from mindclaw.config import load_settings
from mindclaw.state import JsonStateStore
from mindclaw.task import Task, TaskPriority
from mindclaw.team import AgentRole, Team, TeamMember

app = typer.Typer(
    name="mindclaw",
    help="MindClaw: a multi-agent orchestration shell built on top of a runtime core.",
    no_args_is_help=True,
)
state_app = typer.Typer(help="Inspect local state storage.")
team_app = typer.Typer(help="Manage MindClaw teams.")
task_app = typer.Typer(help="Manage MindClaw tasks.")
console = Console()

app.add_typer(state_app, name="state")
app.add_typer(team_app, name="team")
app.add_typer(task_app, name="task")


def _store() -> JsonStateStore:
    store = JsonStateStore(load_settings())
    store.ensure()
    return store


def _task_priority(value: str) -> TaskPriority:
    try:
        return TaskPriority(value.lower())
    except ValueError as exc:
        raise typer.BadParameter("priority must be one of: low, medium, high") from exc


@app.callback()
def main() -> None:
    """MindClaw command line interface."""


@app.command("version")
def version() -> None:
    """Show the current MindClaw version."""
    console.print(f"MindClaw v{__version__}")


@app.command("doctor")
def doctor() -> None:
    """Show basic repository bootstrap status."""
    console.print(
        Panel.fit(
            "MindClaw repository scaffold is ready.\n\n"
            "Current foundation:\n"
            "- domain model packages are present\n"
            "- runtime adapter interface is defined\n"
            "- orchestration skeleton is in place\n\n"
            "Next steps:\n"
            "- implement richer local orchestration flows\n"
            "- add worker lifecycle actions and registries\n"
            "- connect a concrete runtime adapter",
            title="MindClaw Doctor",
        )
    )


@app.command("init")
def init() -> None:
    """Print the initial implementation direction."""
    console.print(
        Panel.fit(
            "MindClaw starts as a clean root-level project.\n"
            "The current repository is set up for open-source development, domain modeling, and runtime-oriented orchestration work.",
            title="MindClaw Init",
        )
    )


@app.command("modules")
def modules() -> None:
    """Show the current core package layout."""
    table = Table(title="MindClaw Core Modules")
    table.add_column("Module", style="cyan")
    table.add_column("Responsibility", style="green")

    table.add_row("mindclaw.config", "Settings and local state paths")
    table.add_row("mindclaw.state", "JSON-backed local persistence")
    table.add_row("mindclaw.team", "Team and member models")
    table.add_row("mindclaw.task", "Task state and dependency modeling")
    table.add_row("mindclaw.messaging", "Inter-agent message models")
    table.add_row("mindclaw.workspace", "Workspace ownership and assignment models")
    table.add_row("mindclaw.runtime", "Runtime adapter interface and registry")
    table.add_row("mindclaw.orchestrator", "Shell-level orchestration plan and state")

    console.print(table)


@state_app.command("where")
def state_where() -> None:
    """Show the current local state directory."""
    settings = load_settings()
    table = Table(title="MindClaw Local State")
    table.add_column("Item", style="cyan")
    table.add_column("Path", style="green")
    table.add_row("home", str(settings.home_dir))
    table.add_row("teams", str(settings.teams_file))
    table.add_row("tasks", str(settings.tasks_file))
    console.print(table)


@team_app.command("create")
def team_create(
    name: str = typer.Argument(..., help="Team name."),
    goal: str = typer.Option("", "--goal", help="High-level team goal."),
    leader: str = typer.Option("leader", "--leader", help="Leader agent name."),
    runtime: str = typer.Option("default", "--runtime", help="Default runtime name."),
) -> None:
    """Create a team in the local state store."""
    store = _store()
    team = Team(name=name, goal=goal)
    team.add_member(
        TeamMember(
            name=leader,
            agent_id=f"{name}-{uuid4().hex[:8]}",
            role=AgentRole.LEADER,
            runtime=runtime,
        )
    )
    try:
        store.save_team(team)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]已创建团队[/green] {name}")


@team_app.command("list")
def team_list() -> None:
    """List teams from the local state store."""
    store = _store()
    teams = store.list_teams()
    table = Table(title="MindClaw Teams")
    table.add_column("Name", style="cyan")
    table.add_column("Goal", style="green")
    table.add_column("Leader", style="magenta")
    table.add_column("Members", justify="right")

    for team in teams:
        leader = team.leader().name if team.leader() else "-"
        table.add_row(team.name, team.goal or "-", leader, str(len(team.members)))

    if not teams:
        console.print("[yellow]当前还没有团队。[/yellow]")
        return
    console.print(table)


@task_app.command("create")
def task_create(
    title: str = typer.Argument(..., help="Task title."),
    team: str = typer.Option(..., "--team", help="Owning team name."),
    description: str = typer.Option("", "--description", help="Task description."),
    owner: str = typer.Option("", "--owner", help="Assigned member name."),
    priority: str = typer.Option("medium", "--priority", help="Task priority."),
    task_id: str = typer.Option("", "--task-id", help="Optional task identifier."),
) -> None:
    """Create a task in the local state store."""
    store = _store()
    if store.get_team(team) is None:
        console.print(f"[red]团队 '{team}' 不存在。[/red]")
        raise typer.Exit(code=1)

    task = Task(
        task_id=task_id or uuid4().hex[:8],
        title=title,
        team_name=team,
        description=description,
        owner=owner,
        priority=_task_priority(priority),
    )
    try:
        store.save_task(task)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]已创建任务[/green] {task.task_id} ({title})")


@task_app.command("list")
def task_list(
    team: str = typer.Option("", "--team", help="Filter by team name."),
) -> None:
    """List tasks from the local state store."""
    store = _store()
    tasks = store.list_tasks(team_name=team or None)
    table = Table(title="MindClaw Tasks")
    table.add_column("ID", style="cyan")
    table.add_column("Team", style="green")
    table.add_column("Title")
    table.add_column("Status", style="magenta")
    table.add_column("Owner")
    table.add_column("Priority")

    for task in tasks:
        table.add_row(
            task.task_id,
            task.team_name or "-",
            task.title,
            task.status.value,
            task.owner or "-",
            task.priority.value,
        )

    if not tasks:
        console.print("[yellow]当前还没有任务。[/yellow]")
        return
    console.print(table)
