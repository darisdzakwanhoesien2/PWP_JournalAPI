# client/entries_cli.py
"""Manage journal entries via CLI."""
import json

import requests
import typer
from rich import print as rprint

from . import auth, config

entry_app = typer.Typer(help="Manage journal entries")

@entry_app.command("list")
def list_entries() -> None:
    """List all your journal entries."""
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    res = requests.get(
        f"{config.API_URL}/journal_entries",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if res.status_code == 200:
        entries = res.json()
        if not entries:
            rprint("[yellow]⚠️ No journal entries found.[/yellow]")
        for entry in entries:
            rprint(f"[bold cyan][{entry['id']}][/bold cyan] {entry['title']} - Tags: {entry['tags']}")
            rprint(f"  [dim]Last updated: {entry.get('last_updated', 'N/A')}[/dim]")
            rprint("  [dim]-- -- --[/dim]")
    else:
        rprint(f"[red]❌ Failed to list entries: {res.json()}[/red]")

@entry_app.command("create")
def create(
    title: str = typer.Argument(..., help="Title of the journal entry"),
    content: str = typer.Argument(..., help="Content of the journal entry"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags")
) -> None:
    """Create a new journal entry.
    
    Args:
        title: The title of the journal entry.
        content: The content of the journal entry.
        tags: Comma-separated tags.
    """
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    res = requests.post(
        f"{config.API_URL}/journal_entries",
        json={"title": title, "content": content, "tags": tag_list},
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if res.status_code == 201:
        rprint("[green]✅ Entry created successfully![/green]")
    else:
        rprint(f"[red]❌ Failed to create entry: {res.json()}[/red]")

@entry_app.command("delete")
def delete(entry_id: int = typer.Argument(..., help="ID of the entry to delete")) -> None:
    """Delete a journal entry by ID.
    
    Args:
        entry_id: The ID of the journal entry to delete.
    """
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    res = requests.delete(
        f"{config.API_URL}/journal_entries/{entry_id}",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    if res.status_code == 200:
        rprint("[green]✅ Entry deleted successfully.[/green]")
    elif res.status_code == 404:
        rprint("[yellow]⚠️ Entry not found.[/yellow]")
    else:
        rprint(f"[red]❌ Failed to delete entry: {res.json()}[/red]")