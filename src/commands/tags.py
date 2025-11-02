"""
Tags commands — manage tags for a contact.

Commands act as Controller + View:
- get user input, call service, handle errors, print results.
"""

import typer
from dependency_injector.wiring import Provide, inject
from rich.console import Console

from src.container import Container
from src.services.contact_service import ContactService
from src.utils.command_decorators import auto_save, handle_service_errors
from src.utils.validators import validate_tag

app = typer.Typer()
console = Console()


@inject
@handle_service_errors
@auto_save
def _tag_add_impl(
    name: str,
    tag: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    msg = service.add_tag(name, tag)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="tag-add")
def tag_add_command(
    name: str = typer.Argument(..., help="Contact name"),
    tag: str = typer.Argument(..., help="Tag (a-z0-9_-, 1..32)", callback=validate_tag),
):
    """Add a tag to a contact."""
    return _tag_add_impl(name, tag)


@inject
@handle_service_errors
@auto_save
def _tag_remove_impl(
    name: str,
    tag: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    msg = service.remove_tag(name, tag)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="tag-remove")
def tag_remove_command(
    name: str = typer.Argument(..., help="Contact name"),
    tag: str = typer.Argument(..., help="Tag", callback=validate_tag),
):
    """Remove a tag from a contact."""
    return _tag_remove_impl(name, tag)


@inject
@handle_service_errors
@auto_save
def _tag_clear_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
    filename: str = Provide[Container.config.storage.filename],
):
    msg = service.clear_tags(name)
    console.print(f"[bold green]{msg}[/bold green]")


@app.command(name="tag-clear")
def tag_clear_command(
    name: str = typer.Argument(..., help="Contact name"),
):
    """Clear all tags for a contact."""
    return _tag_clear_impl(name)


@inject
@handle_service_errors
def _tag_list_impl(
    name: str,
    service: ContactService = Provide[Container.contact_service],
):
    tags = service.list_tags(name)
    console.print(", ".join(tags) if tags else "(no tags)")


@app.command(name="tag-list")
def tag_list_command(
    name: str = typer.Argument(..., help="Contact name"),
):
    """List tags of a contact."""
    return _tag_list_impl(name)
