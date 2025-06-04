# PWP_JournalAPI/client/entries_cli.py
"""CLI commands for managing journal entries in the Journal API."""
import typer
from rich.console import Console
from .entries import create_entry, get_entry
from .auth import get_auth
from journalapi.utils import handle_error

console = Console()
entry_app = typer.Typer()

@entry_app.command()
def create(title: str, content: str, tags: str = ""):
    """Create a new journal entry."""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    result = create_entry(title, content, tag_list)
    if isinstance(result, dict) and "id" in result:
        console.print(f"Entry created with ID: {result['id']}")
    else:
        console.print(f"Error: {result}")

@entry_app.command()
def get(entry_id: int):
    """Retrieve a journal entry by ID."""
    result = get_entry(entry_id)
    if isinstance(result, dict) and "title" in result:
        console.print(result)
    else:
        console.print(f"Error: {result}")