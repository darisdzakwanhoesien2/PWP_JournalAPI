# PWP_JournalAPI/client/main.py
"""Main CLI application for the Journal API."""
import logging

import typer

from client.auth_cli import auth_app
from client.entries_cli import entry_app
from client.comments_cli import comment_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = typer.Typer(help="PWP Journal API CLI - Manage your journal entries")
app.add_typer(auth_app, name="auth", help="Manage user authentication")
app.add_typer(entry_app, name="entry", help="Manage journal entries")
app.add_typer(comment_app, name="comment", help="Manage comments")

if __name__ == "__main__":
    logger.info("Starting Journal API CLI")
    app()