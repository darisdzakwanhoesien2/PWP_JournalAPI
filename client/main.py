# PWP_JournalAPI/client/main.py
import typer 
from auth_cli import auth_app # client.
from entries_cli import entry_app # client.
from comments_cli import comment_app # client.

app = typer.Typer(help="Journal API CLI")
app.add_typer(auth_app, name="auth")
app.add_typer(entry_app, name="entry")
app.add_typer(comment_app, name="comment")

if __name__ == "__main__":
    app()
