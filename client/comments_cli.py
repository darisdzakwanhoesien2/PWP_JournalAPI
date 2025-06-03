# PWP_JournalAPI/client/comments_cli.py
"""CLI commands for managing comments in the Journal API."""
import typer
import requests
from rich.console import Console
from client import auth
from client import config
import logging

console = Console()
comment_app = typer.Typer(help="Manage comments in Journal API")
logger = logging.getLogger(__name__)

@comment_app.command("list")
def list_comments(entry_id: int) -> None:
    """List all comments for a journal entry.

    Args:
        entry_id: ID of the journal entry.
    """
    try:
        res = requests.get(
            f"{config.API_URL}/journal_entries/{entry_id}/comments",
            headers=auth.get_auth(),
            timeout=config.REQUEST_TIMEOUT
        )
        res.raise_for_status()
        comments = res.json()
        if not comments:
            console.print("[yellow]⚠️ No comments found.[/yellow]")
            return
        for c in comments:
            console.print(f"[bold cyan][{c['id']}][/bold cyan] {c['content']} (by user {c['user_id']})")
        logger.info(f"Listed comments for entry ID {entry_id}")
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to list comments")

@comment_app.command("add")
def add_comment(entry_id: int, content: str = typer.Argument(..., help="Comment content")) -> None:
    """Add a comment to a journal entry.

    Args:
        entry_id: ID of the journal entry.
        content: Content of the comment.
    """
    try:
        res = requests.post(
            f"{config.API_URL}/journal_entries/{entry_id}/comments",
            json={"content": content},
            headers=auth.get_auth(),
            timeout=config.REQUEST_TIMEOUT
        )
        res.raise_for_status()
        console.print("[green]✅ Comment added successfully![/green]")
        logger.info(f"Added comment to entry ID {entry_id}")
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to add comment")

@comment_app.command("delete")
def delete_comment(entry_id: int, comment_id: int) -> None:
    """Delete a comment from a journal entry.

    Args:
        entry_id: ID of the journal entry.
        comment_id: ID of the comment to delete.
    """
    try:
        res = requests.delete(
            f"{config.API_URL}/journal_entries/{entry_id}/comments/{comment_id}",
            headers=auth.get_auth(),
            timeout=config.REQUEST_TIMEOUT
        )
        res.raise_for_status()
        console.print("[green]✅ Comment deleted successfully![/green]")
        logger.info(f"Deleted comment ID {comment_id} from entry ID {entry_id}")
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to delete comment")

def handle_error(res: requests.Response, error: Exception, message: str) -> None:
    """Handle HTTP request errors and display appropriate messages."""
    try:
        err = res.json()
        console.print(f"[red]❌ {message}: {err.get('error', err.get('errors', 'Unknown error'))}[/red]")
        logger.error(f"{message}: {err}")
    except (requests.JSONDecodeError, ValueError):
        console.print(f"[red]❌ Server error: {res.text}[/red]")
        logger.error(f"{message}: {res.text}, {error}")