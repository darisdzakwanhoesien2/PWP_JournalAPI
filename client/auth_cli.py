# PWP_JournalAPI/client/auth_cli.py
"""CLI commands for authentication in the Journal API."""
import typer
import requests
from .auth import save_token, clear_token, get_auth
from .config import API_URL, REQUEST_TIMEOUT
from journalapi.utils import handle_error

auth_app = typer.Typer()

@auth_app.command()
def register(username: str, password: str):
    """Register a new user."""
    try:
        response = requests.post(
            f"{API_URL}/users/register",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        typer.echo("Registration successful")
    except requests.RequestException as e:
        error_data = handle_error(response, e, "Registration failed")
        typer.echo(f"Error: {error_data}")

@auth_app.command()
def login(username: str, password: str):
    """Log in and save token."""
    try:
        response = requests.post(
            f"{API_URL}/users/login",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        token = response.json().get("access_token")
        save_token(token)
        typer.echo("Login successful")
    except requests.RequestException as e:
        error_data = handle_error(response, e, "Login failed")
        typer.echo(f"Error: {error_data}")

@auth_app.command()
def logout():
    """Log out and clear token."""
    clear_token()
    typer.echo("Logged out")

@auth_app.command()
def me():
    """Get current user info."""
    try:
        response = requests.get(
            f"{API_URL}/users/me",
            headers=get_auth(),
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        typer.echo(response.json())
    except requests.RequestException as e:
        error_data = handle_error(response, e, "Failed to fetch user info")
        typer.echo(f"Error: {error_data}")