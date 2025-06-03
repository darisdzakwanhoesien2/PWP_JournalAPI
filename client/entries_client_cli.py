# PWP_JournalAPI/client/entries_client_cli.py
"""CLI commands for managing journal entries in the Journal API."""
import typer
import requests
from rich.console import Console
from client import auth
from client import config

console = Console()
entries_app = typer.Typer(help="Journal Entries")

@entries_app.command("list")
def list_entries() -> None:
    """List all your journal entries."""
    auth_headers = auth.get_auth()
    if not auth_headers:
        console.print("[red]❌ Please login first.[/red]")
        raise typer.Exit()

    resp = requests.get(
        f"{config.API_URL}/journal_entries",
        headers=auth_headers,
        timeout=5
    )
    if resp.status_code == 200:
        entries = resp.json()
        for entry in entries:
            console.print(
                f"[bold cyan]{entry['title']}[/bold cyan] (ID: {entry['id']})"
            )
            console.print(
                f"  Tags: {entry['tags']} | Updated: {entry['last_updated']}"
            )
            console.print("  [dim]-- -- --[/dim]\n")
    else:
        console.print(f"[red]❌ Failed to fetch entries: {resp.json()}[/red]")

@entries_app.command("create")
def create_entry(
    title: str = typer.Option(...),
    content: str = typer.Option(...),
    tags: str = typer.Option("")
) -> None:
    """Create a new journal entry."""
    auth_headers = auth.get_auth()
    if not auth_headers:
        console.print("[red]❌ Please login first.[/red]")
        raise typer.Exit()

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    resp = requests.post(
        f"{config.API_URL}/journal_entries",
        json={
            "title": title,
            "content": content,
            "tags": tag_list
        },
        headers=auth_headers,
        timeout=5
    )

    if resp.status_code == 201:
        console.print("[green]✅ Entry created successfully![/green]")
    else:
        console.print(f"[red]❌ Failed to create entry: {resp.json()}[/red]")