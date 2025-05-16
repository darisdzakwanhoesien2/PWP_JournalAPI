# PWP_JournalAPI/client/comments_cli.py
import typer
import requests
from rich import print
import auth, config

comment_app = typer.Typer(help="Manage comments")

@comment_app.command("list")
def list_comments(entry_id: int):
    res = requests.get(f"{config.API_URL}/entries/{entry_id}/comments", headers={"Authorization": f"Bearer {auth.get_token()}"})
    comments = res.json().get('comments', [])  # Access 'comments' key, default to empty list
    if not comments:
        print("[yellow]⚠️ No comments found.[/yellow]")
    for c in comments:
        print(f"[{c['id']}] {c['content']}")

@comment_app.command("add")
def add_comment(entry_id: int, content: str):
    res = requests.post(f"{config.API_URL}/entries/{entry_id}/comments", json={"content": content}, headers={"Authorization": f"Bearer {auth.get_token()}"})
    print("[green]✅ Comment added[/green]" if res.ok else f"[red]❌ {res.json()}[/red]")

@comment_app.command("delete")
def delete_comment(entry_id: int, comment_id: int):
    res = requests.delete(f"{config.API_URL}/entries/{entry_id}/comments/{comment_id}", headers={"Authorization": f"Bearer {auth.get_token()}"})
    print("[green]✅ Deleted[/green]" if res.ok else f"[red]❌ {res.json()}[/red]")