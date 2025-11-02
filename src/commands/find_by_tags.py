"""
Find contacts that have ALL specified tags (AND).
Controller+View: parse args, call service, handle errors, print results.
"""

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console
from rich.table import Table

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import handle_service_errors

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
def _find_by_tags_impl(
    tags: str,
    service: ContactService = Provide[Container.contact_service],
):
    # service receives str or List[str]
    result = service.find_by_tags_all(tags)
    if not result:
        console.print("[yellow]No contacts found[/yellow]")
        return

    table = Table(title="Contacts with ALL tags")
    table.add_column("Name", style="bold")
    table.add_column("Tags")

    for name, rec in result:
        table.add_row(name, ", ".join(rec.tags_list()))
    console.print(table)


@app.command(name="find-by-tags")
def find_by_tags_command(
    tags: str = typer.Argument(..., help='Comma-separated: "ai,ml"'),
):
    """Find contacts that have ALL given tags (AND)."""
    return _find_by_tags_impl(tags)
