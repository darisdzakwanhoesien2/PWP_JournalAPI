# PWP_JournalAPI/client/entries_cli.py
import typer
import requests
from rich import print
import auth, config

entry_app = typer.Typer(help="Manage journal entries")


@entry_app.command("list")
def list_entries():
    """
    List all your journal entries.
    """
    token = auth.get_token()
    if not token:
        print("[red]❌ You must login first[/red]")
        raise typer.Exit()

    res = requests.get(f"{config.API_URL}/entries/", headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 200:
        entries = res.json()
        if not entries:
            print("[yellow]⚠️ No journal entries found.[/yellow]")
        for entry in entries:
            print(f"[bold cyan][{entry['id']}][/bold cyan] {entry['title']} - Tags: {entry['tags']}")
            print(f"  [dim]Last updated: {entry.get('last_updated', 'N/A')}[/dim]")
            print("  [dim]-- -- --[/dim]")
    else:
        print(f"[red]❌ Failed to list entries: {res.json()}[/red]")


@entry_app.command("create")
def create(
    title: str = typer.Argument(..., help="Title of the journal entry"),
    content: str = typer.Argument(..., help="Content of the journal entry"),
    tags: str = typer.Option("", "--tags", "-t", help="Comma-separated tags")
):
    """
    Create a new journal entry.
    """
    token = auth.get_token()
    if not token:
        print("[red]❌ You must login first[/red]")
        raise typer.Exit()

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    res = requests.post(f"{config.API_URL}/entries/", json={
        "title": title,
        "content": content,
        "tags": tag_list
    }, headers={"Authorization": f"Bearer {token}"})

    if res.status_code == 201:
        print("[green]✅ Entry created successfully![/green]")
    else:
        print(f"[red]❌ Failed to create entry: {res.json()}[/red]")


@entry_app.command("delete")
def delete(entry_id: int = typer.Argument(..., help="ID of the entry to delete")):
    """
    Delete a journal entry by ID.
    """
    token = auth.get_token()
    if not token:
        print("[red]❌ You must login first[/red]")
        raise typer.Exit()

    res = requests.delete(f"{config.API_URL}/entries/{entry_id}", headers={"Authorization": f"Bearer {token}"})
    if res.status_code == 200:
        print("[green]✅ Entry deleted successfully.[/green]")
    elif res.status_code == 404:
        print("[yellow]⚠️ Entry not found.[/yellow]")
    else:
        print(f"[red]❌ Failed to delete entry: {res.json()}[/red]")