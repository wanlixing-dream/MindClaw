from __future__ import annotations

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mindclaw import __version__

app = typer.Typer(
    name="mindclaw",
    help="MindClaw: a multi-agent orchestration shell built on top of a runtime core.",
    no_args_is_help=True,
)
console = Console()


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
            "- add persistent state and registries\n"
            "- implement local orchestration flows\n"
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

    table.add_row("mindclaw.team", "Team and member models")
    table.add_row("mindclaw.task", "Task state and dependency modeling")
    table.add_row("mindclaw.messaging", "Inter-agent message models")
    table.add_row("mindclaw.workspace", "Workspace ownership and assignment models")
    table.add_row("mindclaw.runtime", "Runtime adapter interface and registry")
    table.add_row("mindclaw.orchestrator", "Shell-level orchestration plan and state")

    console.print(table)
