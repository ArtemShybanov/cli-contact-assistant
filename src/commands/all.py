"""
All command - Show all contacts in the address book.

Commands are Controllers + View in MVCS pattern.
They handle user input, call services, handle exceptions, and display results.
"""

from typing import Optional

import typer
from dependency_injector.wiring import inject, Provide
from rich.console import Console
from rich.panel import Panel
from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _all_impl(
    sort_by: Optional[str] = None,
    service: ContactService = Provide[Container.contact_service],
):
    if not service.has_contacts():
        console.print("[yellow]No contacts in the address book.[/yellow]")
    else:
        if not sort_by:
            message = service.get_all_contacts(sort_by=sort_by)
            console.print(
                Panel(message, title="[bold]All Contacts[/bold]", border_style="cyan")
            )
        else:
            lines = []
            for name, rec in service.list_contacts(sort_by=sort_by):
                phones = "; ".join(p.value for p in rec.phones) if rec.phones else ""
                tags = ", ".join(rec.tags_list())
                line = f"Contact name: {name}, phones: {phones}"
                if tags:
                    line += f", tags: {tags}"
                lines.append(line)

            console.print(
                Panel(
                    "\n\n".join(lines),
                    title="[bold]All Contacts[/bold]",
                    border_style="cyan",
                )
            )


@app.command(name="all")
def all_command(
    sort_by: Optional[str] = typer.Option(
        None,
        "--sort-by",
        help="Sort by: tag_count or tag_name",
    ),
):
    """
    Show all contacts in the address book.
    
    This command acts as both Controller and View:
    - Controller: Handles exceptions and coordinates service calls
    - View: Formats and displays results using Rich
    """
    return _all_impl(sort_by=sort_by)
