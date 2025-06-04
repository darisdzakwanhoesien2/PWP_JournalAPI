"""Journal API CLI client."""
import typer

from .auth_cli import auth_app
from .entries_cli import entry_app
from .comments_cli import comment_app

app = typer.Typer()
app.add_typer(auth_app, name="auth")
app.add_typer(entry_app, name="entry")
app.add_typer(comment_app, name="comment")

if __name__ == "__main__":
    app()