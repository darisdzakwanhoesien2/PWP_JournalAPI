# PWP_JournalAPI/client/auth_cli.py
# PWP_JournalAPI/client/auth_cli.py
"""CLI commands for authentication in the Journal API."""
import typer
import requests
from rich.console import Console
from client import auth
from client import config
import logging

console = Console()
auth_app = typer.Typer(help="Authentication commands for Journal API")
logger = logging.getLogger(__name__)

@auth_app.command("register")
def register(
    username: str = typer.Option(..., "--username", "-u", help="Desired username"),
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="Password")
) -> None:
    """Register a new user with username, email, and password."""
    try:
        res = requests.post(
            f"{config.API_URL}/users/register",
            json={"username": username, "email": email, "password": password},
            timeout=config.REQUEST_TIMEOUT
        )
        res.raise_for_status()
        console.print("[green]✅ Registered successfully![/green]")
        logger.info(f"User registered: {username}")
    except requests.HTTPError as e:
        handle_error(res, e, "Registration failed")

@auth_app.command("login")
def login(
    email: str = typer.Option(..., "--email", "-e", help="Email address"),
    password: str = typer.Option(..., "--password", "-p", hide_input=True, help="Password")
) -> None:
    """Log in and store the JWT token."""
    try:
        res = requests.post(
            f"{config.API_URL}/users/login",
            json={"email": email, "password": password},
            timeout=config.REQUEST_TIMEOUT
        )
        res.raise_for_status()
        auth.save_token(res.json()["token"])
        console.print("[green]✅ Logged in successfully![/green]")
        logger.info(f"User logged in: {email}")
    except requests.HTTPError as e:
        handle_error(res, e, "Login failed")

@auth_app.command("logout")
def logout() -> None:
    """Remove saved token (logout)."""
    auth.clear_token()
    console.print("[yellow]🔓 Logged out successfully![/yellow]")
    logger.info("User logged out")

@auth_app.command("me")
def me() -> None:
    """Check if you're logged in."""
    token = auth.get_token()
    if token:
        console.print("[green]🔐 Logged in[/green]")
        logger.debug("Checked login status: logged in")
    else:
        console.print("[red]🔓 Not logged in[/red]")
        logger.debug("Checked login status: not logged in")

def handle_error(res: requests.Response, error: Exception, message: str) -> None:
    """Handle HTTP request errors and display appropriate messages."""
    try:
        err = res.json()
        console.print(f"[red]❌ {message}: {err.get('error', err.get('errors', 'Unknown error'))}[/red]")
        logger.error(f"{message}: {err}")
    except (requests.JSONDecodeError, ValueError):
        console.print(f"[red]❌ Server error: {res.text}[/red]")
        logger.error(f"{message}: {res.text}, {error}")