# client/main.py
import typer
from client.auth import login, register
from client.journal import list_entries, create_entry
from client.comments import add_comment, list_comments

app = typer.Typer()

@app.command()
def signup():
    """Register a new user."""
    register()

@app.command()
def signin():
    """Login and save token."""
    login()

@app.command()
def entries():
    """List your journal entries."""
    list_entries()

@app.command()
def new():
    """Create a new journal entry."""
    create_entry()

@app.command()
def comment(entry_id: int):
    """Add a comment to a journal entry."""
    add_comment(entry_id)

@app.command()
def comments(entry_id: int):
    """List comments on a journal entry."""
    list_comments(entry_id)

if __name__ == "__main__":
    app()
