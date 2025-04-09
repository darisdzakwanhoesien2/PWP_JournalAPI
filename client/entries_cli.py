# PWP_JournalAPI/client/entries_cli.py
import typer
import requests
from rich import print
import auth, config # from client 

entry_app = typer.Typer(help="Manage journal entries")

@entry_app.command("list")
def list_entries():
    res = requests.get(f"{config.API_URL}/entries/", headers={"Authorization": f"Bearer {auth.get_token()}"})
    for entry in res.json():
        print(f"[{entry['id']}] {entry['title']} - Tags: {entry['tags']}")

@entry_app.command("create")
def create(title: str, content: str, tags: str = ""):
    res = requests.post(f"{config.API_URL}/entries/", json={
        "title": title, "content": content, "tags": tags.split(',')
    }, headers={"Authorization": f"Bearer {auth.get_token()}"})
    print("[green]✅ Created![/green]" if res.ok else f"[red]❌ {res.json()}[/red]")

@entry_app.command("delete")
def delete(entry_id: int):
    res = requests.delete(f"{config.API_URL}/entries/{entry_id}", headers={"Authorization": f"Bearer {auth.get_token()}"})
    print("[green]✅ Deleted[/green]" if res.ok else f"[red]❌ {res.json()}[/red]")
