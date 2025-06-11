"""CLI commands for authentication."""
import typer
import requests
from rich import print as rprint
from client import auth, config

auth_app = typer.Typer(name="auth")

@auth_app.command()
def register(
    username: str = typer.Option(..., prompt=True),
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    """Register a new user."""
    try:
        response = requests.post(
            f"{config.API_URL}/users/register",
            json={"username": username, "email": email, "password": password}
        )
        response.raise_for_status()
        rprint("[green]✅ Registered![/green]")
    except requests.exceptions.HTTPError as e:
        try:
            error_message = e.response.json()['error']
        except:
            error_message = str(e)
        rprint(f"[red]❌ Registration failed: {error_message}[/red]")

@auth_app.command()
def login(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(..., prompt=True, hide_input=True)
):
    """Log in and save token."""
    try:
        response = requests.post(
            f"{config.API_URL}/users/login",
            json={"email": email, "password": password}
        )
        response.raise_for_status()
        token = response.json()["token"]
        auth.save_token(token)
        rprint("[green]✅ Logged in[/green]")
    except requests.exceptions.HTTPError as e:
        rprint(f"[red]❌ Login failed: {e.response.json()['error']}[/red]")

@auth_app.command()
def logout():
    """Log out and remove token."""
    if auth.get_token():
        auth.remove_token()
        rprint("[green]🔓 Logged out[/green]")
    else:
        rprint("[yellow]⚠️ Not logged in[/yellow]")