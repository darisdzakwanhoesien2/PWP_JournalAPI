# PWP_JournalAPI/client/entries_client_cli.py
import typer
import requests
from rich import print
from PWP_JournalAPI.client import token_utlis

entries_app = typer.Typer(help="Journal Entries")

API_URL = "http://localhost:8000"

@entries_app.command("list")
def list_entries():
    """List all your journal entries"""
    auth = token_utlis.get_auth()
    if not auth:
        print("[red]❌ Please login first.[/red]")
        raise typer.Exit()

    resp = requests.get(f"{API_URL}/entries/", headers=auth)
    if resp.status_code == 200:
        entries = resp.json()
        for entry in entries:
            print(f"[bold cyan]{entry['title']}[/bold cyan] (ID: {entry['id']})")
            print(f"  Tags: {entry['tags']} | Updated: {entry['last_updated']}")
            print("  [dim]-- -- --[/dim]\n")
    else:
        print(f"[red]❌ Failed to fetch entries: {resp.json()}[/red]")

@entries_app.command("create")
def create_entry(
    title: str = typer.Option(...),
    content: str = typer.Option(...),
    tags: str = typer.Option("")
):
    """Create a new journal entry"""
    auth = token_utlis.get_auth()
    if not auth:
        print("[red]❌ Please login first.[/red]")
        raise typer.Exit()

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]

    resp = requests.post(f"{API_URL}/entries/", json={
        "title": title,
        "content": content,
        "tags": tag_list
    }, headers=auth)

    if resp.status_code == 201:
        print("[green]✅ Entry created successfully![/green]")
    else:
        print(f"[red]❌ Failed to create entry: {resp.json()}[/red]")
