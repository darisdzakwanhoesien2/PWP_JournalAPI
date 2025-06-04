# PWP_JournalAPI/client/comments_cli.py
"""CLI commands for managing comments in the Journal API."""
import typer
import requests
from .auth import get_auth
from .config import API_URL, REQUEST_TIMEOUT
from journalapi.utils import handle_error

comment_app = typer.Typer()

@comment_app.command()
def add(entry_id: int, content: str):
    """Add a comment to a journal entry."""
    try:
        response = requests.post(
            f"{API_URL}/entries/{entry_id}/comments",
            json={"content": content},
            headers=get_auth(),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        typer.echo("Comment added successfully")
    except requests.RequestException as e:
        error_data = handle_error(response, e, "Failed to add comment")
        typer.echo(f"Error: {error_data}")

@comment_app.command()
def list(entry_id: int):
    """List comments for a journal entry."""
    try:
        response = requests.get(
            f"{API_URL}/entries/{entry_id}/comments",
            headers=get_auth(),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        typer.echo(response.json())
    except requests.RequestException as e:
        error_data = handle_error(response, e, "Failed to list comments")
        typer.echo(f"Error: {error_data}")