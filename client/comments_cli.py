# PWP_JournalAPI/client/comments_cli.py
"""CLI commands for managing comments in the Journal API."""
import logging

import requests
import typer
from rich.console import Console

from client import auth
from client import config
from client.utils import ensure_auth, handle_error

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
console = Console()
comment_app = typer.Typer(help="Manage comments in Journal API")
logger = logging.getLogger(__name__)

@comment_app.command("list")
def list_comments(entry_id: int) -> None:
    """List all comments for a journal entry.

    Args:
        entry_id: ID of the journal entry.
    """
    auth_headers = ensure_auth()
    try:
        res = requests.get(
            f"{config.API_URL}/journal_entries/{entry_id}/comments",
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        comments = res.json()
        if not comments:
            console.print("[yellow]⚠️ No comments found.[/yellow]")
            return
        for c in comments:
            console.print(
                f"[bold cyan][{c['id']}][/bold cyan] {c['content']} "
                f"(by user {c['user_id']})"
            )
        logger.info("Listed comments for entry ID %s", entry_id)
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to list comments")

@comment_app.command("add")
def add_comment(
    entry_id: int,
    content: str = typer.Argument(..., help="Comment content"),
) -> None:
    """Add a comment to a journal entry.

    Args:
        entry_id: ID of the journal entry.
        content: Content of the comment.
    """
    auth_headers = ensure_auth()
    try:
        res = requests.post(
            f"{config.API_URL}/journal_entries/{entry_id}/comments",
            json={"content": content},
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        console.print("[green]✅ Comment added successfully![/green]")
        logger.info("Added comment to entry ID %s", entry_id)
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to add comment")

@comment_app.command("delete")
def delete_comment(entry_id: int, comment_id: int) -> None:
    """Delete a comment from a journal entry.

    Args:
        entry_id: ID of the journal entry.
        comment_id: ID of the comment to delete.
    """
    auth_headers = ensure_auth()
    try:
        res = requests.delete(
            f"{config.API_URL}/journal_entries/{entry_id}/comments/{comment_id}",
            headers=auth_headers,
            timeout=config.REQUEST_TIMEOUT,
        )
        res.raise_for_status()
        console.print("[green]✅ Comment deleted successfully![/green]")
        logger.info("Deleted comment ID %s from entry ID %s", comment_id, entry_id)
    except requests.HTTPError as e:
        handle_error(res, e, "Failed to delete comment")