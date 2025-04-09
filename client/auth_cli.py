# PWP_JournalAPI/client/auth_cli.py
import typer
import requests
from rich import print
import auth, config # from client 

auth_app = typer.Typer(help="Authentication commands")

@auth_app.command("register")
def register(username: str, email: str, password: str = typer.Option(..., hide_input=True)):
    res = requests.post(f"{config.API_URL}/users/register", json={"username": username, "email": email, "password": password})
    print("[green]✅ Registered![/green]" if res.ok else f"[red]❌ Error: {res.json()}[/red]")

@auth_app.command("login")
def login(email: str, password: str = typer.Option(..., hide_input=True)):
    res = requests.post(f"{config.API_URL}/users/login", json={"email": email, "password": password})
    if res.ok:
        auth.save_token(res.json()["token"])
        print("[green]✅ Logged in[/green]")
    else:
        print(f"[red]❌ Error: {res.json()}[/red]")

@auth_app.command("logout")
def logout():
    auth.clear_token()
    print("[yellow]🔓 Logged out[/yellow]")

@auth_app.command("me")
def me():
    token = auth.get_token()
    print("[green]🔐 Logged in[/green]" if token else "[red]🔓 Not logged in[/red]")
