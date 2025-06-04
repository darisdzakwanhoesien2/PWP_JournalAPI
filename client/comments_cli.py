"""CLI commands for managing comments."""
import typer
import requests
from rich import print as rprint
from client import auth, config

comment_app = typer.Typer(name="comment")

@comment_app.command()
def list(entry_id: int):
    """List comments for a journal entry."""
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    res = requests.get(
        f"{config.API_URL}/journal_entries/{entry_id}/comments",
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code == 200:
        comments = res.json()
        if not comments:
            rprint("[yellow]⚠️ No comments found[/yellow]")
            return
        for comment in comments:
            rprint(f"[blue]Comment ID: {comment['id']}[/blue]")
            rprint(f"Content: {comment['content']}")
            rprint(f"Timestamp: {comment.get('timestamp', 'N/A')}")
            rprint("---")
    else:
        rprint(f"[red]❌ Error: {res.json()['error']}[/red]")

@comment_app.command()
def add(entry_id: int, content: str):
    """Add a comment to a journal entry."""
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    
    if not content.strip():
        rprint("[red]❌ Validation Error: Content cannot be empty[/red]")
        raise typer.Exit()
    
    res = requests.post(
        f"{config.API_URL}/journal_entries/{entry_id}/comments",
        json={"content": content},
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code == 201:
        rprint("[green]✅ Comment added[/green]")
    else:
        response_data = res.json()
        if 'error' in response_data:
            rprint(f"[red]❌ Error: {response_data['error']}[/red]")
        elif 'errors' in response_data:
            rprint(f"[red]❌ Validation Error: {response_data['errors']}[/red]")
        else:
            rprint(f"[red]❌ Error: {response_data}[/red]")

@comment_app.command()
def update(entry_id: int, comment_id: int, content: str):
    """Update a comment."""
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    res = requests.put(
        f"{config.API_URL}/journal_entries/{entry_id}/comments/{comment_id}",
        json={"content": content},
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code == 200:
        rprint("[green]✅ Comment updated[/green]")
    else:
        rprint(f"[red]❌ Error: {res.json()['error']}[/red]")

@comment_app.command()
def delete(entry_id: int, comment_id: int):
    """Delete a comment."""
    token = auth.get_token()
    if not token:
        rprint("[red]❌ You must login first[/red]")
        raise typer.Exit()
    res = requests.delete(
        f"{config.API_URL}/journal_entries/{entry_id}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    if res.status_code == 200:
        rprint("[green]✅ Comment deleted[/green]")
    else:
        rprint(f"[red]❌ Error: {res.json()['error']}[/red]")