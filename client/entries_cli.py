# PWP_JournalAPI/client/entries_cli.py
"""CLI commands for managing journal entries in the Journal API."""
import logging

import requests
import typer
from rich.console import Console

import auth
import config
from utils import handle_error

console = Console()
entry_app = typer.Typer(help="Manage journal entries in Journal API")
logger = logging.getLogger(__name__)

@entry_app.command("list")
def list_entries() -> None:
    """List all your journal entries."""
    auth_headers = auth.get_auth()
    if not auth_headers:
        console.print("[red]❌ Please login first.[/red]")
        raise typer.Exit()
    try:
        res = requests.get(
            f"{config.API_URL}/entries",
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        entries = res.json()
        if not entries:
            console.print("[yellow]⚠️ No journal entries found.[/yellow]")
            return
        for entry in entries:
            console.print(
                f"[bold cyan][{entry['id']}][/bold cyan] {entry['title']} - "
                f"Tags: {', '.join(entry['tags'])}"
            )
            console.print(
                f"  [dim]Last updated: {entry.get('last_updated', 'N/A')}[/dim]"
            )
            console.print("  [dim]-- -- --[/dim]")
        logger.info("Listed journal entries")
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to list entries")

@entry_app.command("create")
def create(
    title: str = typer.Argument(..., help="Title of the journal entry"),
    content: str = typer.Argument(..., help="Content of the journal entry"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags"),
) -> None:
    """Create a new journal entry."""
    auth_headers = auth.get_auth()
    if not auth_headers:
        console.print("[red]❌ Please login first.[/red]")
        raise typer.Exit()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    try:
        res = requests.post(
            f"{config.API_URL}/entries",
            json={"title": title, "content": content, "tags": tag_list},
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        console.print("[green]✅ Entry created successfully![/green]")
        logger.info("Created entry: %s", title)
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to create entry")

@entry_app.command("delete")
def delete(entry_id: int = typer.Argument(..., help="ID of the entry to delete")) -> None:
    """Delete a journal entry by ID."""
    auth_headers = auth.get_auth()
    if not auth_headers:
        console.print("[red]❌ Please login first.[/red]")
        raise typer.Exit()
    try:
        res = requests.delete(
            f"{config.API_URL}/entries/{entry_id}",
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        console.print("[green]✅ Entry deleted successfully![/green]")
        logger.info("Deleted entry ID %s", entry_id)
    except requests.HTTPError as e:
        if res.status_code == 404:
            console.print("[yellow]⚠️ Entry not found.[/yellow]")
        else:
            handle_error(res, e, "Failed to delete entry")