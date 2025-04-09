import typer
import requests
from rich import print
from client import token

API_URL = "http://localhost:8000"  # Adjust if deployed

auth_app = typer.Typer(help="Authentication: Register and Login")

@auth_app.command("register")
def register(username: str = typer.Option(...), email: str = typer.Option(...), password: str = typer.Option(..., hide_input=True, prompt=True)):
    """
    Register a new user
    """
    response = requests.post(f"{API_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    if response.status_code == 201:
        print("[green]✅ Registered successfully! You can now login.[/green]")
    else:
        print(f"[red]❌ Registration failed: {response.json()}[/red]")

@auth_app.command("login")
def login(email: str = typer.Option(...), password: str = typer.Option(..., hide_input=True, prompt=True)):
    """
    Login and save JWT token
    """
    response = requests.post(f"{API_URL}/users/login", json={
        "email": email,
        "password": password
    })

    if response.status_code == 200:
        token_data = response.json()
        token.save_token(token_data["token"])
        print("[green]✅ Login successful. Token saved![/green]")
    else:
        print(f"[red]❌ Login failed: {response.json()}[/red]")
