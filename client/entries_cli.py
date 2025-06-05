"""Manage journal entries via CLI."""
import requests
import typer
from rich import print as rprint

from . import auth, config

entry_app = typer.Typer(help="Manage journal entries")

@entry_app.command("list")
def list_entries() -> None:
    """List all your journal entries.

    Raises:
        typer.Exit: If the user is not authenticated or the API request fails.
    """
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit(code=1)
    try:
        res = requests.get(
            url=f"{config.API_URL}/journal_entries",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        res.raise_for_status()
        entries = res.json()
        if not entries:
            rprint("[yellow]⚠️ No entry found.[/yellow]")
            return
        for entry_id in entries:
            rprint(
                f"[bold cyan][{entry_id['id']}][/bold cyan] {entry_id['title']} - "
                f"Tags: {entry_id['tags']}"
            )
            rprint(f"  [dim]Last updated: {entry_id.get('last_updated', 'N/A')}[/dim]")
            rprint("  [dim]-- -- --[/dim]")
    except requests.RequestException as exc:
        rprint(
            f"[red]❌ Failed to list entries: "
            f"{res.json().get('error', 'Request failed')}[/red]"
        )
        raise typer.Exit(code=1) from exc

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

    Raises:
        typer.Exit: If the user is not authenticated, title is empty,
                    or the API request fails.
    """
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit(code=1)
    if not title.strip():
        rprint("[red]❌ Title cannot be empty[/red]")
        raise typer.Exit(code=1)
    try:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        res = requests.post(
            url=f"{config.API_URL}/journal_entries",
            json={"title": title, "content": content, "tags": tag_list},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if res.status_code == 201:
            rprint("[green]✅ Entry created successfully![/green]")
        else:
            rprint(
                f"[red]❌ Failed to create entry: "
                f"{res.json().get('error', 'Request failed')}[/red]"
            )
            raise requests.RequestException("API request failed")
    except requests.RequestException as exc:
        raise typer.Exit(code=1) from exc

@entry_app.command("delete")
def delete(entry_id: int = typer.Argument(..., help="ID of the entry to delete")) -> None:
    """Delete a journal entry by ID.

    Args:
        entry_id: The ID of the journal entry to delete.

    Raises:
        typer.Exit: If the user is not authenticated or the API request fails.
    """
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit(code=1)
    try:
        res = requests.delete(
            url=f"{config.API_URL}/journal_entries/{entry_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if res.status_code == 200:
            rprint("[green]✅ Entry deleted successfully.[/green]")
        elif res.status_code == 404:
            rprint("[yellow]⚠️ Entry not found.[/yellow]")
        else:
            rprint(
                f"[red]❌ Failed to delete entry: "
                f"{res.json().get('error', 'Request failed')}[/red]"
            )
            raise requests.RequestException("API request failed")
    except requests.RequestException as exc:
        raise typer.Exit(code=1) from exc