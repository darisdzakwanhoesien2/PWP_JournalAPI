# PWP_JournalAPI/client/main.py
"""Main CLI application for the Journal API."""
import typer
import logging
from .auth_cli import auth_app
from .entries_cli import entry_app
from .comments_cli import comment_app

app = typer.Typer()
logger = logging.getLogger(__name__)

app.add_typer(auth_app, name="auth")
app.add_typer(entry_app, name="entry")
app.add_typer(comment_app, name="comment")

if __name__ == "__main__":
    app()